"""
FastAPI routes for assignments management.
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import logging
from supabase import create_client, Client
import uuid

from supabase_storage import get_storage_manager, SupabaseStorageManager
from auth_middleware import get_current_user, TokenData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/api/assignments", tags=["assignments"])

# Pydantic models
class AssignmentCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = None
    due_date: datetime
    max_score: Optional[int] = 100
    allow_late_submission: Optional[bool] = False

class AssignmentResponse(BaseModel):
    id: str
    course_id: str
    teacher_id: str
    title: str
    description: Optional[str]
    file_url: Optional[str]
    due_date: datetime
    max_score: int
    allow_late_submission: bool
    status: str
    created_at: datetime
    updated_at: datetime
    course_title: Optional[str] = None
    teacher_name: Optional[str] = None
    submission_count: Optional[int] = 0
    total_students: Optional[int] = 0
    submission_status: Optional[str] = None
    submission_score: Optional[int] = None
    submitted_at: Optional[datetime] = None

class SubmissionCreate(BaseModel):
    assignment_id: str
    student_id: str

class SubmissionResponse(BaseModel):
    id: str
    assignment_id: str
    student_id: str
    file_url: str
    submitted_at: datetime
    score: Optional[int]
    feedback: Optional[str]
    status: str
    graded_by: Optional[str]
    graded_at: Optional[datetime]
    assignment_title: Optional[str] = None
    course_title: Optional[str] = None
    student_name: Optional[str] = None
    student_email: Optional[str] = None
    is_late_submission: Optional[bool] = False

class GradeSubmission(BaseModel):
    score: int
    feedback: Optional[str] = None

# Helper functions
async def get_user_by_id(user_id: str = Query(...)) -> Dict[str, Any]:
    """Get current user from user_id parameter."""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

async def verify_teacher_role(user_id: str):
    """Verify user is a teacher."""
    user = await get_user_by_id(user_id)
    if user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can perform this action")

async def verify_student_role(current_user):
    """Verify user is a student."""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can perform this action")

async def verify_course_ownership(course_id: str, teacher_id: str):
    """Verify teacher owns the course."""
    try:
        response = supabase.table("courses").select("teacher_id").eq("id", course_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if response.data["teacher_id"] != teacher_id:
            raise HTTPException(status_code=403, detail="You don't have permission to access this course")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying course ownership: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify course ownership")

async def verify_student_enrollment(course_id: str, student_id: str):
    """Verify student is enrolled in the course."""
    try:
        response = supabase.table("enrollments").select("*").eq("course_id", course_id).eq("student_id", student_id).eq("status", "active").execute()
        if not response.data:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying enrollment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify enrollment")

# Assignment routes
@router.post("/create", response_model=AssignmentResponse)
async def create_assignment(
    teacher_id: str = Query(...),
    course_id: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: str = Form(...),
    max_score: int = Form(100),
    allow_late_submission: bool = Form(False),
    file: Optional[UploadFile] = File(None),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """Create a new assignment."""
    try:
        # Verify teacher role
        await verify_teacher_role(teacher_id)
        
        # Verify course ownership
        await verify_course_ownership(course_id, teacher_id)
        
        # Handle file upload if provided
        file_url = None
        if file and file.filename:
            # Validate file type (PDF/DOCX only)
            allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
            
            # Validate file size (max 10MB)
            file_content = await file.read()
            if len(file_content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size must be less than 10MB")
            
            # Reset file pointer for S3 upload
            await file.seek(0)
            
            # Upload to Supabase Storage with assignments folder structure
            storage_result = await storage_manager.upload_assignment_file(file, course_id)
            file_url = storage_result["file_url"]

        # Parse due_date
        due_date_parsed = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

        # Create assignment in database
        assignment_data = {
            "course_id": course_id,
            "teacher_id": teacher_id,
            "title": title,
            "description": description,
            "file_url": file_url,
            "due_date": due_date_parsed.isoformat(),
            "max_score": max_score,
            "allow_late_submission": allow_late_submission
        }
        
        response = supabase.table("assignments").insert(assignment_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create assignment")
        
        # Get assignment with details
        assignment_id = response.data[0]["id"]
        detailed_response = supabase.table("assignments_with_details").select("*").eq("id", assignment_id).single().execute()
        
        return AssignmentResponse(**detailed_response.data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create assignment")

@router.get("/teacher/{teacher_id}", response_model=List[AssignmentResponse])
async def get_teacher_assignments(
    teacher_id: str,
    course_id: Optional[str] = Query(None),
    status: Optional[str] = Query("active")
):
    """Get all assignments created by a teacher."""
    try:
        # Verify teacher role
        await verify_teacher_role(teacher_id)
        
        # Build query
        query = supabase.table("assignments_with_details").select("*").eq("teacher_id", teacher_id)
        
        if course_id:
            query = query.eq("course_id", course_id)
        
        if status:
            query = query.eq("status", status)
        
        query = query.order("created_at", desc=True)
        
        response = query.execute()
        
        return [AssignmentResponse(**assignment) for assignment in response.data]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching teacher assignments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch assignments")

@router.get("/student/{student_id}", response_model=List[AssignmentResponse])
async def get_student_assignments(
    student_id: str,
    course_id: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all assignments for courses a student is enrolled in."""
    try:
        # Verify student role
        await verify_student_role(current_user)
        
        # Get enrolled courses
        enrollments_response = supabase.table("enrollments").select("course_id").eq("student_id", student_id).eq("status", "active").execute()
        
        if not enrollments_response.data:
            return []
        
        enrolled_course_ids = [enrollment["course_id"] for enrollment in enrollments_response.data]
        
        # Build query for assignments
        query = supabase.table("assignments").select("*").in_("course_id", enrolled_course_ids).eq("status", "active")
        
        if course_id and course_id in enrolled_course_ids:
            query = query.eq("course_id", course_id)
        
        query = query.order("due_date", desc=False)
        
        response = query.execute()
        
        # Add submission status for each assignment
        assignments = []
        for assignment in response.data:
            # Check if student has submitted
            submission_response = supabase.table("assignment_submissions").select("*").eq("assignment_id", assignment["id"]).eq("student_id", student_id).execute()

            # Prepare assignment data with submission info
            assignment_data = assignment.copy()
            if submission_response.data:
                assignment_data["submission_status"] = submission_response.data[0]["status"]
                assignment_data["submission_score"] = submission_response.data[0]["score"]
                assignment_data["submitted_at"] = submission_response.data[0]["submitted_at"]
            else:
                assignment_data["submission_status"] = "not_submitted"
                assignment_data["submission_score"] = None
                assignment_data["submitted_at"] = None

            assignments.append(AssignmentResponse(**assignment_data))
        
        return assignments

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student assignments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch assignments")

@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(
    assignment_id: str = Form(...),
    student_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """Submit an assignment."""
    try:
        # Verify student role
        await verify_student_role(current_user)

        # Get assignment details
        assignment_response = supabase.table("assignments").select("*").eq("id", assignment_id).single().execute()
        if not assignment_response.data:
            raise HTTPException(status_code=404, detail="Assignment not found")

        assignment = assignment_response.data

        # Verify student enrollment
        await verify_student_enrollment(assignment["course_id"], student_id)

        # Check if already submitted
        existing_submission = supabase.table("assignment_submissions").select("*").eq("assignment_id", assignment_id).eq("student_id", student_id).execute()
        if existing_submission.data:
            raise HTTPException(status_code=400, detail="Assignment already submitted")

        # Check due date
        due_date = datetime.fromisoformat(assignment["due_date"].replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        is_late = current_time > due_date

        if is_late and not assignment["allow_late_submission"]:
            raise HTTPException(status_code=400, detail="Assignment submission deadline has passed")

        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Validate file type (PDF/DOCX only)
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

        # Validate file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")

        # Reset file pointer for S3 upload
        await file.seek(0)

        # Upload to Supabase Storage
        storage_result = await storage_manager.upload_submission_file(file, assignment["course_id"], assignment_id, student_id)

        # Create submission record
        submission_data = {
            "assignment_id": assignment_id,
            "student_id": student_id,
            "file_url": storage_result["file_url"],
            "status": "late" if is_late else "submitted"
        }

        response = supabase.table("assignment_submissions").insert(submission_data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create submission")

        # Get submission with details
        submission_id = response.data[0]["id"]
        detailed_response = supabase.table("assignment_submissions_with_details").select("*").eq("id", submission_id).single().execute()

        return SubmissionResponse(**detailed_response.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting assignment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit assignment")

@router.get("/submissions/{assignment_id}", response_model=List[SubmissionResponse])
async def get_assignment_submissions(
    assignment_id: str,
    teacher_id: str = Query(...)
):
    """Get all submissions for an assignment (teacher only)."""
    try:
        # Verify teacher role
        await verify_teacher_role(teacher_id)

        # Get assignment and verify ownership
        assignment_response = supabase.table("assignments").select("*").eq("id", assignment_id).single().execute()
        if not assignment_response.data:
            raise HTTPException(status_code=404, detail="Assignment not found")

        if assignment_response.data["teacher_id"] != teacher_id:
            raise HTTPException(status_code=403, detail="You don't have permission to view these submissions")

        # Get submissions with details
        response = supabase.table("assignment_submissions_with_details").select("*").eq("assignment_id", assignment_id).order("submitted_at", desc=True).execute()

        return [SubmissionResponse(**submission) for submission in response.data]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching submissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch submissions")

@router.put("/grade/{submission_id}", response_model=SubmissionResponse)
async def grade_submission(
    submission_id: str,
    grade_data: GradeSubmission,
    teacher_id: str = Query(...)
):
    """Grade a student submission."""
    try:
        # Verify teacher role
        await verify_teacher_role(teacher_id)

        # Get submission details
        submission_response = supabase.table("assignment_submissions_with_details").select("*").eq("id", submission_id).single().execute()
        if not submission_response.data:
            raise HTTPException(status_code=404, detail="Submission not found")

        submission = submission_response.data

        # Get assignment to verify teacher ownership and max score
        assignment_response = supabase.table("assignments").select("*").eq("id", submission["assignment_id"]).single().execute()
        if not assignment_response.data:
            raise HTTPException(status_code=404, detail="Assignment not found")

        assignment = assignment_response.data

        if assignment["teacher_id"] != teacher_id:
            raise HTTPException(status_code=403, detail="You don't have permission to grade this submission")

        # Validate score
        if grade_data.score < 0 or grade_data.score > assignment["max_score"]:
            raise HTTPException(status_code=400, detail=f"Score must be between 0 and {assignment['max_score']}")

        # Update submission with grade
        update_data = {
            "score": grade_data.score,
            "feedback": grade_data.feedback,
            "status": "reviewed",
            "graded_by": teacher_id,
            "graded_at": datetime.now(timezone.utc).isoformat()
        }

        response = supabase.table("assignment_submissions").update(update_data).eq("id", submission_id).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to grade submission")

        # Get updated submission with details
        detailed_response = supabase.table("assignment_submissions_with_details").select("*").eq("id", submission_id).single().execute()

        return SubmissionResponse(**detailed_response.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error grading submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to grade submission")

@router.get("/download/{file_type}/{file_id}")
async def download_file(
    file_type: str,  # 'assignment' or 'submission'
    file_id: str,
    user_id: str = Query(...),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """Generate download URL for assignment or submission file."""
    try:
        user = await get_user_by_id(user_id)

        if file_type == "assignment":
            # Get assignment details
            assignment_response = supabase.table("assignments").select("*").eq("id", file_id).single().execute()
            if not assignment_response.data:
                raise HTTPException(status_code=404, detail="Assignment not found")

            assignment = assignment_response.data

            # Check permissions
            if user["role"] == "teacher":
                # Teacher can download their own assignment files
                if assignment["teacher_id"] != user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            elif user["role"] == "student":
                # Student can download if enrolled in course
                await verify_student_enrollment(assignment["course_id"], user_id)
            else:
                raise HTTPException(status_code=403, detail="Permission denied")

            if not assignment["file_url"]:
                raise HTTPException(status_code=404, detail="No file attached to this assignment")

            # Generate download URL (Supabase URLs are already public)
            download_url = storage_manager.get_file_download_url(assignment["file_url"], "assignments")
            return {"download_url": download_url}

        elif file_type == "submission":
            # Get submission details
            submission_response = supabase.table("assignment_submissions_with_details").select("*").eq("id", file_id).single().execute()
            if not submission_response.data:
                raise HTTPException(status_code=404, detail="Submission not found")

            submission = submission_response.data

            # Check permissions
            if user["role"] == "teacher":
                # Teacher can download submissions for their assignments
                assignment_response = supabase.table("assignments").select("teacher_id").eq("id", submission["assignment_id"]).single().execute()
                if not assignment_response.data or assignment_response.data["teacher_id"] != user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            elif user["role"] == "student":
                # Student can only download their own submissions
                if submission["student_id"] != user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            else:
                raise HTTPException(status_code=403, detail="Permission denied")

            # Generate download URL (Supabase URLs are already public)
            download_url = storage_manager.get_file_download_url(submission["file_url"], "assignments")
            return {"download_url": download_url}

        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate download URL")
