"""
Activity-Based Notifications API for LearnSphere
Provides notifications based on user activities since last login
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

router = APIRouter(prefix="/api/activity-notifications", tags=["activity-notifications"])

class ActivityNotification(BaseModel):
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

class ActivitySummary(BaseModel):
    total_activities: int
    new_assignments: int
    new_quizzes: int
    course_updates: int
    forum_activities: int
    grades_received: int
    last_login: Optional[str] = None
    current_login: str

@router.get("/summary", response_model=ActivitySummary)
async def get_activity_summary(
    current_user: TokenData = Depends(get_current_user)
):
    """Get summary of activities since last login"""
    try:
        # Get user's last login time
        user_response = supabase.table("profiles").select("last_login").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        activities = await get_user_activities_since_login(current_user.user_id, last_login)
        
        # Count different types of activities
        summary = ActivitySummary(
            total_activities=len(activities),
            new_assignments=len([a for a in activities if a['type'] == 'assignment_created']),
            new_quizzes=len([a for a in activities if a['type'] == 'quiz_available']),
            course_updates=len([a for a in activities if a['type'] == 'course_updated']),
            forum_activities=len([a for a in activities if 'forum' in a['type']]),
            grades_received=len([a for a in activities if 'graded' in a['type']]),
            last_login=last_login,
            current_login=current_time.isoformat()
        )
        
        return summary
        
    except Exception as e:
        print(f"Error getting activity summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity summary")

@router.get("/", response_model=List[ActivityNotification])
async def get_activity_notifications(
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(get_current_user)
):
    """Get activity-based notifications since last login"""
    try:
        # Get user's last login time
        user_response = supabase.table("profiles").select("last_login").eq("id", current_user.user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        activities = await get_user_activities_since_login(current_user.user_id, last_login)
        
        # Convert to notifications and apply pagination
        notifications = []
        for activity in activities[offset:offset + limit]:
            notification = ActivityNotification(
                id=f"activity_{activity['id']}",
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
        print(f"Error getting activity notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity notifications")

async def get_user_activities_since_login(user_id: str, last_login: str) -> List[Dict[str, Any]]:
    """Get all user activities since last login"""
    activities = []
    
    try:
        # Get user's enrolled courses
        enrollments_response = supabase.table("enrollments").select("course_id").eq("student_id", user_id).execute()
        course_ids = [enrollment['course_id'] for enrollment in enrollments_response.data or []]
        
        if not course_ids:
            return activities
        
        # 1. New assignments created since last login
        assignments_response = supabase.table("assignments").select("""
            id, title, description, due_date, course_id, created_at,
            courses!inner(title)
        """).in_("course_id", course_ids).gte("created_at", last_login).execute()
        
        for assignment in assignments_response.data or []:
            activities.append({
                'id': assignment['id'],
                'type': 'assignment_created',
                'title': f"New Assignment: {assignment['title']}",
                'message': f"A new assignment '{assignment['title']}' has been posted in {assignment['courses']['title']}",
                'priority': 'high',
                'created_at': assignment['created_at'],
                'activity_timestamp': assignment['created_at'],
                'action_url': f"/student/assignments",
                'data': {
                    'assignment_id': assignment['id'],
                    'course_id': assignment['course_id'],
                    'course_title': assignment['courses']['title'],
                    'due_date': assignment['due_date']
                }
            })
        
        # 2. New quizzes created since last login
        quizzes_response = supabase.table("quizzes").select("""
            id, title, description, course_id, created_at,
            courses!inner(title)
        """).in_("course_id", course_ids).gte("created_at", last_login).execute()
        
        for quiz in quizzes_response.data or []:
            activities.append({
                'id': quiz['id'],
                'type': 'quiz_available',
                'title': f"New Quiz: {quiz['title']}",
                'message': f"A new quiz '{quiz['title']}' is now available in {quiz['courses']['title']}",
                'priority': 'high',
                'created_at': quiz['created_at'],
                'activity_timestamp': quiz['created_at'],
                'action_url': f"/student/quizzes",
                'data': {
                    'quiz_id': quiz['id'],
                    'course_id': quiz['course_id'],
                    'course_title': quiz['courses']['title']
                }
            })
        
        # 3. Assignment grades received since last login
        # First get assignments for enrolled courses
        assignments_response = supabase.table("assignments").select("id, title, course_id").in_("course_id", course_ids).execute()
        assignment_ids = [a['id'] for a in assignments_response.data or []]
        
        if assignment_ids:
            grades_response = supabase.table("assignment_submissions").select("""
                id, score, graded_at, assignment_id
            """).eq("student_id", user_id).in_("assignment_id", assignment_ids).not_.is_("graded_at", "null").gte("graded_at", last_login).execute()
            
            # Create lookup for assignment details
            assignment_lookup = {a['id']: a for a in assignments_response.data or []}
            
            for grade in grades_response.data or []:
                assignment = assignment_lookup.get(grade['assignment_id'], {})
                activities.append({
                    'id': grade['id'],
                    'type': 'assignment_graded',
                    'title': f"Assignment Graded: {assignment.get('title', 'Unknown')}",
                    'message': f"Your assignment '{assignment.get('title', 'Unknown')}' has been graded. Score: {grade['score']}",
                    'priority': 'medium',
                    'created_at': grade['graded_at'],
                    'activity_timestamp': grade['graded_at'],
                    'action_url': f"/student/assignments",
                    'data': {
                        'assignment_id': grade['assignment_id'],
                        'course_id': assignment.get('course_id'),
                        'score': grade['score'],
                        'course_title': 'Course'
                    }
                })
        
        # 4. Quiz results received since last login
        # First get quizzes for enrolled courses
        quizzes_response = supabase.table("quizzes").select("id, title, course_id").in_("course_id", course_ids).execute()
        quiz_ids = [q['id'] for q in quizzes_response.data or []]
        
        if quiz_ids:
            quiz_results_response = supabase.table("quiz_submissions").select("""
                id, score, submitted_at, quiz_id
            """).eq("student_id", user_id).in_("quiz_id", quiz_ids).gte("submitted_at", last_login).execute()
            
            # Create lookup for quiz details
            quiz_lookup = {q['id']: q for q in quizzes_response.data or []}
            
            for result in quiz_results_response.data or []:
                quiz = quiz_lookup.get(result['quiz_id'], {})
                activities.append({
                    'id': result['id'],
                    'type': 'quiz_graded',
                    'title': f"Quiz Completed: {quiz.get('title', 'Unknown')}",
                    'message': f"You completed the quiz '{quiz.get('title', 'Unknown')}' with a score of {result['score']}",
                    'priority': 'medium',
                    'created_at': result['submitted_at'],
                    'activity_timestamp': result['submitted_at'],
                    'action_url': f"/student/quizzes",
                    'data': {
                        'quiz_id': result['quiz_id'],
                        'course_id': quiz.get('course_id'),
                        'score': result['score'],
                        'course_title': 'Course'
                    }
                })
        
        # 5. Course material updates since last login
        materials_response = supabase.table("course_materials").select("""
            id, title, material_type, course_id, created_at
        """).in_("course_id", course_ids).gte("created_at", last_login).execute()
        
        # Create lookup for course details
        course_lookup = {c['id']: c for c in courses_response.data or []}
        
        for material in materials_response.data or []:
            course = course_lookup.get(material['course_id'], {})
            activities.append({
                'id': material['id'],
                'type': 'new_material',
                'title': f"New Material: {material['title']}",
                'message': f"New {material['material_type']} '{material['title']}' has been added to {course.get('title', 'Course')}",
                'priority': 'medium',
                'created_at': material['created_at'],
                'activity_timestamp': material['created_at'],
                'action_url': f"/student/courses",
                'data': {
                    'material_id': material['id'],
                    'course_id': material['course_id'],
                    'material_type': material['material_type'],
                    'course_title': course.get('title', 'Course')
                }
            })
        
        # 6. Forum activities since last login
        forum_response = supabase.table("forum_posts").select("""
            id, title, content, course_id, created_at, post_type, student_id
        """).in_("course_id", course_ids).gte("created_at", last_login).execute()
        
        for post in forum_response.data or []:
            course = course_lookup.get(post['course_id'], {})
            if post['post_type'] == 'question':
                activities.append({
                    'id': post['id'],
                    'type': 'forum_new_question',
                    'title': f"New Question: {post['title']}",
                    'message': f"A new question '{post['title']}' has been posted in {course.get('title', 'Course')} forum",
                    'priority': 'low',
                    'created_at': post['created_at'],
                    'activity_timestamp': post['created_at'],
                    'action_url': f"/student/forum",
                    'data': {
                        'post_id': post['id'],
                        'course_id': post['course_id'],
                        'course_title': course.get('title', 'Course'),
                        'author': 'Student'
                    }
                })
        
        # Sort activities by timestamp (most recent first)
        activities.sort(key=lambda x: x['activity_timestamp'], reverse=True)
        
        return activities
        
    except Exception as e:
        print(f"Error getting user activities: {e}")
        return []

@router.post("/mark-read/{activity_id}")
async def mark_activity_read(
    activity_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Mark an activity notification as read"""
    try:
        # For now, we'll just return success since we're not persisting read status
        # In a full implementation, you'd store this in a separate table
        return {"message": "Activity marked as read", "activity_id": activity_id}
        
    except Exception as e:
        print(f"Error marking activity as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark activity as read")

@router.get("/count")
async def get_activity_notification_count(
    current_user: TokenData = Depends(get_current_user)
):
    """Get count of unread activity notifications"""
    try:
        # Get user's last login time
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
        activities = await get_user_activities_since_login(current_user.user_id, last_login)
        
        return {"count": len(activities)}
        
    except Exception as e:
        print(f"Error getting activity notification count: {e}")
        return {"count": 0}
