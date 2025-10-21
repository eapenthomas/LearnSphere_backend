"""
Teacher Activity-Based Notifications API for LearnSphere
Provides notifications based on teacher activities since last login
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import os
from supabase import create_client, Client
from auth_middleware import get_current_user, TokenData

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

router = APIRouter(prefix="/api/teacher-activity-notifications", tags=["teacher-activity-notifications"])

class TeacherActivityNotification(BaseModel):
    id: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    is_read: bool = False
    read_at: Optional[str] = None
    action_url: Optional[str] = None
    created_at: str
    activity_timestamp: str

class TeacherActivitySummary(BaseModel):
    total_activities: int
    new_enrollments: int
    assignment_submissions: int
    quiz_submissions: int
    forum_questions: int
    course_ratings: int
    last_login: Optional[str] = None
    current_login: str

@router.get("/summary", response_model=TeacherActivitySummary)
async def get_teacher_activity_summary(
    current_user: TokenData = Depends(get_current_user)
):
    """Get summary of teacher activities since last login"""
    try:
        # Verify user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
        
        # Get teacher's last login time
        user_response = supabase.table("profiles").select("last_login").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        last_login = user_response.data[0].get("last_login")
        current_time = datetime.now(timezone.utc)
        
        # If no last login, use 7 days ago as default
        if not last_login:
            last_login = (current_time - timedelta(days=7)).isoformat()
        else:
            # Convert string to datetime if needed
            if isinstance(last_login, str):
                last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            last_login = last_login.isoformat()
        
        # Get activities since last login
        activities = await get_teacher_activities_since_login(current_user.user_id, last_login)
        
        # Count different types of activities
        summary = TeacherActivitySummary(
            total_activities=len(activities),
            new_enrollments=len([a for a in activities if a['type'] == 'student_enrolled']),
            assignment_submissions=len([a for a in activities if a['type'] == 'assignment_submission_received']),
            quiz_submissions=len([a for a in activities if a['type'] == 'quiz_submission_received']),
            forum_questions=len([a for a in activities if a['type'] == 'student_question_asked']),
            course_ratings=len([a for a in activities if a['type'] == 'course_rating_received']),
            last_login=last_login,
            current_login=current_time.isoformat()
        )
        
        return summary
        
    except Exception as e:
        print(f"Error getting teacher activity summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get teacher activity summary")

@router.get("/", response_model=List[TeacherActivityNotification])
async def get_teacher_activity_notifications(
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user)
):
    """Get teacher activity-based notifications since last login"""
    try:
        # Verify user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
        
        # Get teacher's last login time
        user_response = supabase.table("profiles").select("last_login").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        last_login = user_response.data[0].get("last_login")
        
        # If no last login, use 7 days ago as default
        if not last_login:
            last_login = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        else:
            # Convert string to datetime if needed
            if isinstance(last_login, str):
                last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            last_login = last_login.isoformat()
        
        # Get activities since last login
        activities = await get_teacher_activities_since_login(current_user.user_id, last_login)
        
        # Convert to notifications and apply pagination
        notifications = []
        for activity in activities[offset:offset + limit]:
            notification = TeacherActivityNotification(
                id=f"teacher_activity_{activity['id']}",
                type=activity['type'],
                title=activity['title'],
                message=activity['message'],
                data=activity.get('data'),
                priority=activity.get('priority', 'medium'),
                is_read=False,
                action_url=activity.get('action_url'),
                created_at=activity['created_at'],
                activity_timestamp=activity['activity_timestamp']
            )
            notifications.append(notification)
        
        return notifications
        
    except Exception as e:
        print(f"Error getting teacher activity notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get teacher activity notifications")

async def get_teacher_activities_since_login(teacher_id: str, last_login: str) -> List[Dict[str, Any]]:
    """Get all teacher activities since last login"""
    activities = []
    
    try:
        # Get teacher's courses
        courses_response = supabase.table("courses").select("id").eq("teacher_id", teacher_id).execute()
        course_ids = [course['id'] for course in courses_response.data or []]
        
        if not course_ids:
            return activities
        
        # 1. New student enrollments since last login
        enrollments_response = supabase.table("enrollments").select("""
            id, enrolled_at, student_id, course_id,
            courses!inner(title),
            profiles!enrollments_student_id_fkey(full_name, email)
        """).in_("course_id", course_ids).gte("enrolled_at", last_login).execute()
        
        for enrollment in enrollments_response.data or []:
            student_name = enrollment.get('profiles', {}).get('full_name', 'Unknown Student')
            course_title = enrollment.get('courses', {}).get('title', 'Unknown Course')
            
            activities.append({
                'id': enrollment['id'],
                'type': 'student_enrolled',
                'title': f"New Student Enrolled: {student_name}",
                'message': f"{student_name} has enrolled in your course '{course_title}'",
                'priority': 'medium',
                'created_at': enrollment['enrolled_at'],
                'activity_timestamp': enrollment['enrolled_at'],
                'action_url': f"/teacher/courses/{enrollment['course_id']}/students",
                'data': {
                    'enrollment_id': enrollment['id'],
                    'student_id': enrollment['student_id'],
                    'course_id': enrollment['course_id'],
                    'student_name': student_name,
                    'course_title': course_title
                }
            })
        
        # 2. Assignment submissions received since last login
        submissions_response = supabase.table("assignment_submissions").select("""
            id, submitted_at, student_id, assignment_id, score,
            assignments!inner(title, course_id),
            courses!inner(title),
            profiles!assignment_submissions_student_id_fkey(full_name)
        """).in_("assignments.course_id", course_ids).gte("submitted_at", last_login).execute()
        
        for submission in submissions_response.data or []:
            student_name = submission.get('profiles', {}).get('full_name', 'Unknown Student')
            assignment_title = submission.get('assignments', {}).get('title', 'Unknown Assignment')
            course_title = submission.get('courses', {}).get('title', 'Unknown Course')
            
            activities.append({
                'id': submission['id'],
                'type': 'assignment_submission_received',
                'title': f"Assignment Submitted: {assignment_title}",
                'message': f"{student_name} submitted '{assignment_title}' in {course_title}",
                'priority': 'high',
                'created_at': submission['submitted_at'],
                'activity_timestamp': submission['submitted_at'],
                'action_url': f"/teacher/assignments/{submission['assignment_id']}/submissions",
                'data': {
                    'submission_id': submission['id'],
                    'assignment_id': submission['assignment_id'],
                    'student_id': submission['student_id'],
                    'course_id': submission.get('assignments', {}).get('course_id'),
                    'student_name': student_name,
                    'assignment_title': assignment_title,
                    'course_title': course_title
                }
            })
        
        # 3. Quiz submissions received since last login
        quiz_submissions_response = supabase.table("quiz_submissions").select("""
            id, submitted_at, student_id, quiz_id, score,
            quizzes!inner(title, course_id),
            courses!inner(title),
            profiles!quiz_submissions_student_id_fkey(full_name)
        """).in_("quizzes.course_id", course_ids).gte("submitted_at", last_login).execute()
        
        for submission in quiz_submissions_response.data or []:
            student_name = submission.get('profiles', {}).get('full_name', 'Unknown Student')
            quiz_title = submission.get('quizzes', {}).get('title', 'Unknown Quiz')
            course_title = submission.get('courses', {}).get('title', 'Unknown Course')
            
            activities.append({
                'id': submission['id'],
                'type': 'quiz_submission_received',
                'title': f"Quiz Completed: {quiz_title}",
                'message': f"{student_name} completed '{quiz_title}' in {course_title} with score {submission.get('score', 'N/A')}",
                'priority': 'medium',
                'created_at': submission['submitted_at'],
                'activity_timestamp': submission['submitted_at'],
                'action_url': f"/teacher/quizzes/{submission['quiz_id']}/results",
                'data': {
                    'submission_id': submission['id'],
                    'quiz_id': submission['quiz_id'],
                    'student_id': submission['student_id'],
                    'course_id': submission.get('quizzes', {}).get('course_id'),
                    'student_name': student_name,
                    'quiz_title': quiz_title,
                    'course_title': course_title,
                    'score': submission.get('score')
                }
            })
        
        # 4. Forum questions asked since last login
        forum_questions_response = supabase.table("forum_posts").select("""
            id, title, content, created_at, course_id, post_type,
            courses!inner(title),
            profiles!forum_posts_student_id_fkey(full_name)
        """).in_("course_id", course_ids).eq("post_type", "question").gte("created_at", last_login).execute()
        
        for question in forum_questions_response.data or []:
            student_name = question.get('profiles', {}).get('full_name', 'Unknown Student')
            question_title = question.get('title', 'Untitled Question')
            course_title = question.get('courses', {}).get('title', 'Unknown Course')
            
            activities.append({
                'id': question['id'],
                'type': 'student_question_asked',
                'title': f"New Question: {question_title}",
                'message': f"{student_name} asked a question in {course_title}: '{question_title}'",
                'priority': 'medium',
                'created_at': question['created_at'],
                'activity_timestamp': question['created_at'],
                'action_url': f"/teacher/courses/{question['course_id']}/forum",
                'data': {
                    'post_id': question['id'],
                    'course_id': question['course_id'],
                    'student_id': question.get('student_id'),
                    'student_name': student_name,
                    'question_title': question_title,
                    'course_title': course_title
                }
            })
        
        # 5. Course ratings received since last login
        ratings_response = supabase.table("course_ratings").select("""
            id, rating, review, created_at, course_id, student_id,
            courses!inner(title),
            profiles!course_ratings_student_id_fkey(full_name)
        """).in_("course_id", course_ids).gte("created_at", last_login).execute()
        
        for rating in ratings_response.data or []:
            student_name = rating.get('profiles', {}).get('full_name', 'Unknown Student')
            course_title = rating.get('courses', {}).get('title', 'Unknown Course')
            rating_value = rating.get('rating', 0)
            
            activities.append({
                'id': rating['id'],
                'type': 'course_rating_received',
                'title': f"Course Rated: {course_title}",
                'message': f"{student_name} rated '{course_title}' with {rating_value} stars",
                'priority': 'low',
                'created_at': rating['created_at'],
                'activity_timestamp': rating['created_at'],
                'action_url': f"/teacher/courses/{rating['course_id']}/ratings",
                'data': {
                    'rating_id': rating['id'],
                    'course_id': rating['course_id'],
                    'student_id': rating['student_id'],
                    'student_name': student_name,
                    'course_title': course_title,
                    'rating': rating_value,
                    'review': rating.get('review')
                }
            })
        
        # 6. Course progress updates (students completing materials)
        progress_response = supabase.table("course_material_progress").select("""
            id, completed_at, student_id, course_id, material_id,
            courses!inner(title),
            course_materials!inner(title, material_type),
            profiles!course_material_progress_student_id_fkey(full_name)
        """).in_("course_id", course_ids).not_.is_("completed_at", "null").gte("completed_at", last_login).execute()
        
        for progress in progress_response.data or []:
            student_name = progress.get('profiles', {}).get('full_name', 'Unknown Student')
            material_title = progress.get('course_materials', {}).get('title', 'Unknown Material')
            material_type = progress.get('course_materials', {}).get('material_type', 'material')
            course_title = progress.get('courses', {}).get('title', 'Unknown Course')
            
            activities.append({
                'id': progress['id'],
                'type': 'material_completed',
                'title': f"Material Completed: {material_title}",
                'message': f"{student_name} completed {material_type} '{material_title}' in {course_title}",
                'priority': 'low',
                'created_at': progress['completed_at'],
                'activity_timestamp': progress['completed_at'],
                'action_url': f"/teacher/courses/{progress['course_id']}/progress",
                'data': {
                    'progress_id': progress['id'],
                    'course_id': progress['course_id'],
                    'student_id': progress['student_id'],
                    'material_id': progress['material_id'],
                    'student_name': student_name,
                    'material_title': material_title,
                    'material_type': material_type,
                    'course_title': course_title
                }
            })
        
        # Sort activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['activity_timestamp'], reverse=True)
        
        return activities
        
    except Exception as e:
        print(f"Error getting teacher activities: {e}")
        return []

@router.post("/mark-read/{activity_id}")
async def mark_teacher_activity_read(
    activity_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Mark a teacher activity notification as read"""
    try:
        # Verify user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
        
        # For now, we'll just return success since we're not persisting read status
        # In a full implementation, you'd store this in a separate table
        return {"message": "Teacher activity marked as read", "activity_id": activity_id}
        
    except Exception as e:
        print(f"Error marking teacher activity as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark teacher activity as read")

@router.get("/count")
async def get_teacher_activity_notification_count(
    current_user: TokenData = Depends(get_current_user)
):
    """Get count of unread teacher activity notifications"""
    try:
        # Verify user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
        
        # Get teacher's last login time
        user_response = supabase.table("profiles").select("last_login").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            return {"count": 0}
        
        last_login = user_response.data[0].get("last_login")
        
        # If no last login, use 7 days ago as default
        if not last_login:
            last_login = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        else:
            # Convert string to datetime if needed
            if isinstance(last_login, str):
                last_login = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
            last_login = last_login.isoformat()
        
        # Get activities count since last login
        activities = await get_teacher_activities_since_login(current_user.user_id, last_login)
        
        return {"count": len(activities)}
        
    except Exception as e:
        print(f"Error getting teacher activity notification count: {e}")
        return {"count": 0}
