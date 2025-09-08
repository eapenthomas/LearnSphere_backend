"""
FastAPI routes for student deadlines and calendar events.
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timezone, timedelta
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
router = APIRouter(prefix="/api/student", tags=["student-deadlines"])

# Pydantic models
class DeadlineEvent(BaseModel):
    id: str
    title: str
    course_name: str
    course_id: str
    due_date: datetime
    category: str  # assignment, quiz, exam, project, event
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = "normal"  # high, normal, low
    teacher_name: Optional[str] = None
    submission_status: Optional[str] = None  # for assignments
    score: Optional[int] = None  # for completed items

class CalendarResponse(BaseModel):
    events: List[DeadlineEvent]
    upcoming_count: int
    overdue_count: int
    total_count: int

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

async def get_student_enrollments(student_id: str) -> List[str]:
    """Get list of course IDs the student is enrolled in."""
    try:
        response = supabase.table("enrollments").select("course_id").eq("student_id", student_id).eq("status", "active").execute()
        return [enrollment["course_id"] for enrollment in response.data]
    except Exception as e:
        logger.error(f"Error fetching enrollments for student {student_id}: {str(e)}")
        return []

async def fetch_assignment_deadlines(student_id: str, enrolled_courses: List[str]) -> List[DeadlineEvent]:
    """Fetch assignment deadlines for enrolled courses."""
    if not enrolled_courses:
        return []
    
    try:
        # Get assignments for enrolled courses
        response = supabase.table("assignments_with_details").select("*").in_("course_id", enrolled_courses).eq("status", "active").execute()
        
        deadlines = []
        for assignment in response.data:
            # Check submission status
            submission_response = supabase.table("assignment_submissions").select("*").eq("assignment_id", assignment["id"]).eq("student_id", student_id).execute()
            
            submission_status = "not_submitted"
            score = None
            if submission_response.data:
                submission = submission_response.data[0]
                submission_status = submission["status"]
                score = submission.get("score")
            
            # Determine priority based on due date
            due_date = datetime.fromisoformat(assignment["due_date"].replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_until_due = (due_date - now).days
            
            priority = "normal"
            if days_until_due < 0:
                priority = "high"  # Overdue
            elif days_until_due <= 1:
                priority = "high"  # Due within 24 hours
            elif days_until_due <= 3:
                priority = "normal"  # Due within 3 days
            
            deadlines.append(DeadlineEvent(
                id=assignment["id"],
                title=assignment["title"],
                course_name=assignment["course_title"],
                course_id=assignment["course_id"],
                due_date=due_date,
                category="assignment",
                description=assignment.get("description"),
                status="active",
                priority=priority,
                teacher_name=assignment.get("teacher_name"),
                submission_status=submission_status,
                score=score
            ))
        
        return deadlines
    except Exception as e:
        logger.error(f"Error fetching assignment deadlines: {str(e)}")
        return []

async def fetch_quiz_deadlines(student_id: str, enrolled_courses: List[str]) -> List[DeadlineEvent]:
    """Fetch quiz deadlines for enrolled courses."""
    if not enrolled_courses:
        return []
    
    try:
        # Get quizzes for enrolled courses
        response = supabase.table("quizzes").select("""
            *,
            courses:course_id (
                title,
                teacher_id,
                profiles:teacher_id (
                    full_name
                )
            )
        """).in_("course_id", enrolled_courses).in_("status", ["active", "published"]).execute()
        
        deadlines = []
        for quiz in response.data:
            course = quiz.get("courses", {})
            teacher = course.get("profiles", {}) if course else {}
            
            # Check if quiz has a due date (use end_time if due_date not available)
            due_date_field = quiz.get("due_date") or quiz.get("end_time")
            if not due_date_field:
                continue
            
            # Check submission status
            submission_response = supabase.table("quiz_submissions").select("*").eq("quiz_id", quiz["id"]).eq("student_id", student_id).execute()
            
            submission_status = "not_submitted"
            score = None
            if submission_response.data:
                submission = submission_response.data[0]
                submission_status = "submitted" if submission.get("submitted_at") else "in_progress"
                score = submission.get("score")
            
            # Determine priority based on due date
            due_date = datetime.fromisoformat(due_date_field.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            days_until_due = (due_date - now).days
            
            priority = "normal"
            if days_until_due < 0:
                priority = "high"  # Overdue
            elif days_until_due <= 1:
                priority = "high"  # Due within 24 hours
            elif days_until_due <= 3:
                priority = "normal"  # Due within 3 days
            
            deadlines.append(DeadlineEvent(
                id=quiz["id"],
                title=quiz["title"],
                course_name=course.get("title", "Unknown Course"),
                course_id=quiz["course_id"],
                due_date=due_date,
                category="quiz",
                description=quiz.get("description"),
                status="active",
                priority=priority,
                teacher_name=teacher.get("full_name", "Unknown Teacher"),
                submission_status=submission_status,
                score=score
            ))
        
        return deadlines
    except Exception as e:
        logger.error(f"Error fetching quiz deadlines: {str(e)}")
        return []

async def fetch_other_events(student_id: str, enrolled_courses: List[str]) -> List[DeadlineEvent]:
    """Fetch other academic events (exams, projects, etc.)."""
    # This is a placeholder for future implementation
    # You can add more event types here as needed
    return []

# API Routes
@router.get("/deadlines", response_model=CalendarResponse)
async def get_student_deadlines(
    student_id: str = Query(...),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    category: Optional[str] = Query(None, description="Filter by category: assignment, quiz, exam, project, event"),
    include_completed: bool = Query(True, description="Include completed/submitted items")
):
    """Get all deadlines and events for a student."""
    try:
        # Verify student exists
        await get_current_user(student_id)
        
        # Get enrolled courses
        enrolled_courses = await get_student_enrollments(student_id)
        
        if not enrolled_courses:
            return CalendarResponse(
                events=[],
                upcoming_count=0,
                overdue_count=0,
                total_count=0
            )
        
        # Fetch all types of deadlines
        all_deadlines = []
        
        if not category or category == "assignment":
            assignment_deadlines = await fetch_assignment_deadlines(student_id, enrolled_courses)
            all_deadlines.extend(assignment_deadlines)
        
        if not category or category == "quiz":
            quiz_deadlines = await fetch_quiz_deadlines(student_id, enrolled_courses)
            all_deadlines.extend(quiz_deadlines)
        
        if not category or category in ["exam", "project", "event"]:
            other_events = await fetch_other_events(student_id, enrolled_courses)
            all_deadlines.extend(other_events)
        
        # Apply date filters
        if start_date:
            start_dt = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            all_deadlines = [d for d in all_deadlines if d.due_date >= start_dt]
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            all_deadlines = [d for d in all_deadlines if d.due_date <= end_dt]
        
        # Filter completed items if requested
        if not include_completed:
            all_deadlines = [d for d in all_deadlines if d.submission_status not in ["reviewed", "submitted"]]
        
        # Sort by due date
        all_deadlines.sort(key=lambda x: x.due_date)
        
        # Calculate statistics
        now = datetime.now(timezone.utc)
        upcoming_count = len([d for d in all_deadlines if d.due_date > now])
        overdue_count = len([d for d in all_deadlines if d.due_date < now and d.submission_status == "not_submitted"])
        
        return CalendarResponse(
            events=all_deadlines,
            upcoming_count=upcoming_count,
            overdue_count=overdue_count,
            total_count=len(all_deadlines)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student deadlines: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch deadlines")

@router.get("/deadlines/upcoming", response_model=List[DeadlineEvent])
async def get_upcoming_deadlines(
    student_id: str = Query(...),
    limit: int = Query(7, description="Number of upcoming deadlines to return"),
    days_ahead: int = Query(2, description="Look ahead this many days (default 2 for urgent deadlines)")
):
    """Get upcoming deadlines for the next N days."""
    try:
        # Calculate date range
        now = datetime.now(timezone.utc)
        end_date = now + timedelta(days=days_ahead)

        # Get all deadlines in the range
        response = await get_student_deadlines(
            student_id=student_id,
            start_date=now.isoformat(),
            end_date=end_date.isoformat(),
            include_completed=False
        )

        # Return only the requested number of upcoming items
        upcoming = [event for event in response.events if event.due_date > now]
        return upcoming[:limit]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upcoming deadlines: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch upcoming deadlines")

@router.get("/deadlines/urgent", response_model=List[DeadlineEvent])
async def get_urgent_deadlines(
    student_id: str = Query(...),
    limit: int = Query(10, description="Number of urgent deadlines to return")
):
    """Get urgent deadlines (2 days or less) for student dashboard."""
    try:
        # Calculate date range for urgent deadlines (2 days)
        now = datetime.now(timezone.utc)
        urgent_date = now + timedelta(days=2)

        # Get enrolled courses
        enrolled_courses = await get_student_enrollments(student_id)

        if not enrolled_courses:
            return []

        # Fetch urgent deadlines
        all_deadlines = []

        # Get urgent assignments
        assignment_deadlines = await fetch_assignment_deadlines(student_id, enrolled_courses)
        urgent_assignments = [d for d in assignment_deadlines if now < d.due_date <= urgent_date and d.submission_status == "not_submitted"]
        all_deadlines.extend(urgent_assignments)

        # Get urgent quizzes
        quiz_deadlines = await fetch_quiz_deadlines(student_id, enrolled_courses)
        urgent_quizzes = [d for d in quiz_deadlines if now < d.due_date <= urgent_date and d.submission_status == "not_submitted"]
        all_deadlines.extend(urgent_quizzes)

        # Sort by due date
        all_deadlines.sort(key=lambda x: x.due_date)

        return all_deadlines[:limit]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching urgent deadlines: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch urgent deadlines")
