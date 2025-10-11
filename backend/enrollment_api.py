"""
FastAPI routes for enrollment management.
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from supabase import create_client, Client

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
router = APIRouter(prefix="/api/enrollments", tags=["enrollments"])

# Pydantic models
class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    course_title: Optional[str]
    teacher_name: Optional[str]
    status: str
    progress: Optional[int] = 0
    enrolled_at: datetime
    updated_at: datetime

class EnrollmentCreate(BaseModel):
    student_id: str
    course_id: str

# Helper functions
async def get_current_user(user_id: str) -> Dict[str, Any]:
    """Get current user from user_id parameter."""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

# Enrollment routes
@router.get("/student/{student_id}", response_model=List[EnrollmentResponse])
async def get_student_enrollments(student_id: str):
    """Get all enrollments for a student."""
    try:
        # Verify student exists
        await get_current_user(student_id)
        
        # Get enrollments with course and teacher details
        response = supabase.table("enrollments").select("""
            *,
            courses!enrollments_course_id_fkey (
                title,
                teacher_id,
                profiles!courses_teacher_id_fkey (
                    full_name
                )
            )
        """).eq("student_id", student_id).eq("status", "active").execute()
        
        enrollments = []
        for enrollment in response.data:
            course = enrollment.get("courses", {})
            teacher = course.get("profiles", {}) if course else {}
            
            enrollments.append(EnrollmentResponse(
                id=enrollment["id"],
                student_id=enrollment["student_id"],
                course_id=enrollment["course_id"],
                course_title=course.get("title", "Unknown Course"),
                teacher_name=teacher.get("full_name", "Unknown Teacher"),
                status=enrollment["status"],
                progress=enrollment.get("progress", 0),
                enrolled_at=enrollment.get("enrolled_at", enrollment.get("created_at")),
                updated_at=enrollment.get("updated_at", enrollment.get("enrolled_at", enrollment.get("created_at")))
            ))
        
        return enrollments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student enrollments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch enrollments")

@router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
async def get_course_enrollments(course_id: str, teacher_id: str = Query(...)):
    """Get all enrollments for a course (teacher only)."""
    try:
        # Verify teacher owns the course
        course_response = supabase.table("courses").select("teacher_id").eq("id", course_id).single().execute()
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        if course_response.data["teacher_id"] != teacher_id:
            raise HTTPException(status_code=403, detail="You don't have permission to view these enrollments")
        
        # Get enrollments with student details
        response = supabase.table("enrollments").select("""
            *,
            profiles:student_id (
                full_name,
                email
            ),
            courses:course_id (
                title
            )
        """).eq("course_id", course_id).eq("status", "active").execute()
        
        enrollments = []
        for enrollment in response.data:
            student = enrollment.get("profiles", {})
            course = enrollment.get("courses", {})
            
            enrollments.append(EnrollmentResponse(
                id=enrollment["id"],
                student_id=enrollment["student_id"],
                course_id=enrollment["course_id"],
                course_title=course.get("title", "Unknown Course"),
                teacher_name=student.get("full_name", "Unknown Student"),
                status=enrollment["status"],
                progress=enrollment.get("progress", 0),
                enrolled_at=enrollment.get("enrolled_at", enrollment.get("created_at")),
                updated_at=enrollment.get("updated_at", enrollment.get("enrolled_at", enrollment.get("created_at")))
            ))
        
        return enrollments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching course enrollments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch enrollments")

@router.post("/enroll", response_model=EnrollmentResponse)
async def enroll_student(enrollment: EnrollmentCreate):
    """Enroll a student in a course."""
    try:
        # Verify student exists
        await get_current_user(enrollment.student_id)
        
        # Verify course exists
        course_response = supabase.table("courses").select("*").eq("id", enrollment.course_id).single().execute()
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check if already enrolled (check for any existing enrollment, not just active)
        existing_response = supabase.table("enrollments").select("*").eq("student_id", enrollment.student_id).eq("course_id", enrollment.course_id).execute()
        if existing_response.data:
            existing_enrollment = existing_response.data[0]
            if existing_enrollment["status"] == "active":
                raise HTTPException(status_code=400, detail="Student is already enrolled in this course")
            elif existing_enrollment["status"] == "dropped":
                # Reactivate the dropped enrollment instead of creating a new one
                reactivated_response = supabase.table("enrollments").update({
                    "status": "active",
                    "enrolled_at": datetime.utcnow().isoformat(),
                    "progress": 0
                }).eq("id", existing_enrollment["id"]).execute()
                
                if not reactivated_response.data:
                    raise HTTPException(status_code=500, detail="Failed to reactivate enrollment")
                
                # Get the reactivated enrollment with details
                enrollment_id = existing_enrollment["id"]
                detailed_response = supabase.table("enrollments").select("""
                    *,
                    courses:course_id (
                        title,
                        teacher_id,
                        profiles:teacher_id (
                            full_name
                        )
                    )
                """).eq("id", enrollment_id).single().execute()
                
                enrollment_data = detailed_response.data
                course = enrollment_data.get("courses", {})
                teacher = course.get("profiles", {}) if course else {}
                
                return EnrollmentResponse(
                    id=enrollment_data["id"],
                    student_id=enrollment_data["student_id"],
                    course_id=enrollment_data["course_id"],
                    course_title=course.get("title", "Unknown Course"),
                    teacher_name=teacher.get("full_name", "Unknown Teacher"),
                    status=enrollment_data["status"],
                    progress=enrollment_data.get("progress", 0),
                    enrolled_at=enrollment_data.get("enrolled_at", enrollment_data.get("created_at")),
                    updated_at=enrollment_data.get("updated_at", enrollment_data.get("enrolled_at", enrollment_data.get("created_at")))
                )
        
        # Create enrollment
        enrollment_data = {
            "student_id": enrollment.student_id,
            "course_id": enrollment.course_id,
            "status": "active",
            "progress": 0
        }
        
        response = supabase.table("enrollments").insert(enrollment_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create enrollment")
        
        # Get enrollment with details
        enrollment_id = response.data[0]["id"]
        detailed_response = supabase.table("enrollments").select("""
            *,
            courses:course_id (
                title,
                teacher_id,
                profiles:teacher_id (
                    full_name
                )
            )
        """).eq("id", enrollment_id).single().execute()
        
        enrollment_data = detailed_response.data
        course = enrollment_data.get("courses", {})
        teacher = course.get("profiles", {}) if course else {}
        
        return EnrollmentResponse(
            id=enrollment_data["id"],
            student_id=enrollment_data["student_id"],
            course_id=enrollment_data["course_id"],
            course_title=course.get("title", "Unknown Course"),
            teacher_name=teacher.get("full_name", "Unknown Teacher"),
            status=enrollment_data["status"],
            progress=enrollment_data.get("progress", 0),
            enrolled_at=enrollment_data.get("enrolled_at", enrollment_data.get("created_at")),
            updated_at=enrollment_data.get("updated_at", enrollment_data.get("enrolled_at", enrollment_data.get("created_at")))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating enrollment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create enrollment")

@router.delete("/{enrollment_id}")
async def unenroll_student(enrollment_id: str, student_id: str = Query(...)):
    """Unenroll a student from a course."""
    try:
        # Verify student owns the enrollment
        enrollment_response = supabase.table("enrollments").select("*").eq("id", enrollment_id).single().execute()
        if not enrollment_response.data:
            raise HTTPException(status_code=404, detail="Enrollment not found")

        if enrollment_response.data["student_id"] != student_id:
            raise HTTPException(status_code=403, detail="You don't have permission to modify this enrollment")

        # Update enrollment status to dropped instead of deleting
        response = supabase.table("enrollments").update({"status": "dropped"}).eq("id", enrollment_id).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to unenroll student")

        return {"message": "Successfully unenrolled from course"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling student: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unenroll student")

@router.delete("/student/{student_id}/course/{course_id}")
async def unenroll_student_from_course(student_id: str, course_id: str):
    """Unenroll a student from a course using student_id and course_id."""
    try:
        # Find the enrollment
        enrollment_response = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).eq("status", "active").execute()
        if not enrollment_response.data:
            # Check if student was ever enrolled (but already dropped)
            any_enrollment = supabase.table("enrollments").select("*").eq("student_id", student_id).eq("course_id", course_id).execute()
            if any_enrollment.data:
                return {"message": "Student is already unenrolled from this course"}
            else:
                raise HTTPException(status_code=404, detail="No enrollment found for this student and course")

        enrollment_id = enrollment_response.data[0]["id"]

        # Update enrollment status to dropped instead of deleting
        response = supabase.table("enrollments").update({"status": "dropped"}).eq("id", enrollment_id).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to unenroll student")

        return {"message": "Successfully unenrolled from course"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unenrolling student: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unenroll student")

@router.put("/{enrollment_id}/progress")
async def update_progress(enrollment_id: str, progress: int = Query(..., ge=0, le=100), student_id: str = Query(...)):
    """Update student progress in a course."""
    try:
        # Verify student owns the enrollment
        enrollment_response = supabase.table("enrollments").select("*").eq("id", enrollment_id).single().execute()
        if not enrollment_response.data:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        
        if enrollment_response.data["student_id"] != student_id:
            raise HTTPException(status_code=403, detail="You don't have permission to modify this enrollment")
        
        # Update progress
        response = supabase.table("enrollments").update({"progress": progress}).eq("id", enrollment_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update progress")
        
        return {"message": "Progress updated successfully", "progress": progress}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")
