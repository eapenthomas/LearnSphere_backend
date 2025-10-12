"""
Admin Dashboard API
Provides real-time statistics and data for admin dashboard
"""

import os
import json
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/admin/dashboard", tags=["admin-dashboard"])

class DashboardStats(BaseModel):
    active_students: int
    active_teachers: int
    pending_approvals: int
    active_courses: int
    total_enrollments: int
    total_assignments: int
    total_quizzes: int
    total_submissions: int
    ai_tokens_used: int
    ai_cost_usd: float
    system_health: int

class ActivityLog(BaseModel):
    id: str
    user_name: str
    action: str
    timestamp: datetime
    details: str

class UserGrowthData(BaseModel):
    month: str
    students: int
    teachers: int

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get real-time dashboard statistics with optimized queries"""
    try:
        print("Fetching optimized dashboard stats...")

        # Use concurrent queries with specific field selection for better performance
        import asyncio

        async def get_profile_counts():
            """Get all profile-related counts in one optimized query"""
            try:
                # Use more efficient queries with specific filters
                students_response = supabase.table('profiles').select('id', count='exact').eq('role', 'student').eq('is_active', True).execute()
                
                # Active teachers: either OCR passed (auto-approved) or manually approved
                teachers_response = supabase.table('profiles').select('id', count='exact').eq('role', 'teacher').eq('is_active', True).eq('approval_status', 'approved').execute()
                
                # Pending teachers: OCR failed or manual verification waiting for admin approval
                pending_response = supabase.table('profiles').select('id', count='exact').eq('role', 'teacher').eq('approval_status', 'pending').execute()
                total_response = supabase.table('profiles').select('id', count='exact').execute()

                active_students = students_response.count or 0
                active_teachers = teachers_response.count or 0
                pending_approvals = pending_response.count or 0
                total_users = total_response.count or 0

                return active_students, active_teachers, pending_approvals, total_users
            except Exception as e:
                print(f"Error getting profile counts: {e}")
                return 0, 0, 0, 0

        async def get_content_counts():
            """Get content counts with minimal data transfer"""
            # Use count queries where possible, otherwise select only IDs
            courses_response = supabase.table('courses').select('id', count='exact').execute()
            enrollments_response = supabase.table('enrollments').select('id', count='exact').execute()
            assignments_response = supabase.table('assignments').select('id', count='exact').execute()
            quizzes_response = supabase.table('quizzes').select('id', count='exact').execute()

            active_courses = courses_response.count or 0
            total_enrollments = enrollments_response.count or 0
            total_assignments = assignments_response.count or 0
            total_quizzes = quizzes_response.count or 0

            return active_courses, total_enrollments, total_assignments, total_quizzes

        async def get_submission_counts():
            """Get submission counts efficiently"""
            try:
                assignment_subs_response = supabase.table('assignment_submissions').select('id', count='exact').execute()
                assignment_subs = assignment_subs_response.count if hasattr(assignment_subs_response, 'count') else len(assignment_subs_response.data or [])
            except Exception as e:
                print(f"Error getting assignment submissions: {e}")
                assignment_subs = 0
            
            try:
                quiz_subs_response = supabase.table('quiz_submissions').select('id', count='exact').execute()
                quiz_subs = quiz_subs_response.count if hasattr(quiz_subs_response, 'count') else len(quiz_subs_response.data or [])
            except Exception as e:
                print(f"Error getting quiz submissions: {e}")
                quiz_subs = 0

            return assignment_subs + quiz_subs

        async def get_ai_usage():
            """Get AI usage statistics efficiently"""
            try:
                ai_usage_response = supabase.table('ai_usage_logs').select('tokens_used, cost_usd').execute()
                ai_data = ai_usage_response.data or []
                ai_tokens_used = sum(record.get('tokens_used', 0) for record in ai_data)
                ai_cost_usd = sum(record.get('cost_usd', 0.0) for record in ai_data)
                return ai_tokens_used, ai_cost_usd
            except:
                return 0, 0.0

        # Execute all queries concurrently for better performance
        (active_students, active_teachers, pending_approvals, total_users), \
        (active_courses, total_enrollments, total_assignments, total_quizzes), \
        total_submissions, \
        (ai_tokens_used, ai_cost_usd) = await asyncio.gather(
            get_profile_counts(),
            get_content_counts(),
            get_submission_counts(),
            get_ai_usage()
        )

        # Calculate system health
        active_users = active_students + active_teachers
        system_health = min(98, max(50, int((active_users / total_users) * 100))) if total_users > 0 else 98

        print(f"Optimized stats - Students: {active_students}, Teachers: {active_teachers}, Courses: {active_courses}")
        
        stats = DashboardStats(
            active_students=active_students,
            active_teachers=active_teachers,
            pending_approvals=pending_approvals,
            active_courses=active_courses,
            total_enrollments=total_enrollments,
            total_assignments=total_assignments,
            total_quizzes=total_quizzes,
            total_submissions=total_submissions,
            ai_tokens_used=ai_tokens_used,
            ai_cost_usd=round(ai_cost_usd, 4),
            system_health=system_health
        )

        print(f"Final stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity", response_model=List[ActivityLog])
async def get_recent_activity(limit: int = Query(10, ge=1, le=50)):
    """Get recent user activity logs"""
    try:
        # Get recent user registrations
        recent_users = supabase.table('profiles').select('id, full_name, role, created_at').order('created_at', desc=True).limit(limit).execute()
        
        activity_logs = []
        for user in recent_users.data:
            # Handle null names better
            user_name = user.get('full_name', '').strip()
            if not user_name:
                user_name = f"User {user['id'][:8]}"
            
            activity_logs.append(ActivityLog(
                id=user['id'],
                user_name=user_name,
                action=f"New {user['role']} registered",
                timestamp=datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')),
                details=f"{user['role'].title()} account created"
            ))
        
        # Get recent course creations
        recent_courses = supabase.table('courses').select('''
            id, title, created_at,
            profiles!courses_teacher_id_fkey(full_name)
        ''').order('created_at', desc=True).limit(5).execute()
        
        for course in recent_courses.data:
            # Handle teacher names better
            teacher_name = 'Unknown Teacher'
            if course.get('profiles') and course['profiles'].get('full_name'):
                teacher_name = course['profiles']['full_name'].strip()
            elif course.get('profiles'):
                teacher_name = f"Teacher {course['profiles'].get('id', course['id'])[:8]}"
            
            activity_logs.append(ActivityLog(
                id=course['id'],
                user_name=teacher_name,
                action="Course created",
                timestamp=datetime.fromisoformat(course['created_at'].replace('Z', '+00:00')),
                details=f"Created course: {course['title']}"
            ))
        
        # Sort by timestamp and limit
        activity_logs.sort(key=lambda x: x.timestamp, reverse=True)
        return activity_logs[:limit]
        
    except Exception as e:
        print(f"Error fetching activity logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-growth", response_model=List[UserGrowthData])
async def get_user_growth_data():
    """Get user growth data for the last 6 months"""
    try:
        growth_data = []
        now = datetime.now(timezone.utc)
        
        for i in range(6):
            # Calculate month start and end
            month_start = now.replace(day=1) - timedelta(days=i*30)
            month_end = month_start + timedelta(days=30)
            month_name = month_start.strftime('%b %Y')
            
            # Get students registered in this month
            students_response = supabase.table('profiles').select('id').eq('role', 'student').gte('created_at', month_start.isoformat()).lt('created_at', month_end.isoformat()).execute()
            students_count = len(students_response.data)
            
            # Get teachers registered in this month
            teachers_response = supabase.table('profiles').select('id').eq('role', 'teacher').gte('created_at', month_start.isoformat()).lt('created_at', month_end.isoformat()).execute()
            teachers_count = len(teachers_response.data)
            
            growth_data.append(UserGrowthData(
                month=month_name,
                students=students_count,
                teachers=teachers_count
            ))
        
        # Reverse to show oldest to newest
        growth_data.reverse()
        return growth_data
        
    except Exception as e:
        print(f"Error fetching user growth data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-health")
async def get_system_health():
    """Get system health metrics"""
    try:
        # Check database connectivity
        db_health = True
        try:
            supabase.table('profiles').select('id').limit(1).execute()
        except:
            db_health = False
        
        # Get storage usage (simplified)
        storage_usage = {
            "total_files": 0,
            "total_size_mb": 0
        }
        
        # Get recent error logs (if any)
        error_count = 0
        
        return {
            "database_status": "healthy" if db_health else "error",
            "storage_usage": storage_usage,
            "recent_errors": error_count,
            "uptime": "99.9%",  # This would be calculated from actual uptime monitoring
            "last_backup": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-growth")
async def get_user_growth_data():
    """Get user growth data for the last 6 months"""
    try:
        # Calculate date range for last 6 months
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=180)  # 6 months
        
        # Get user registrations grouped by month
        response = supabase.table("profiles").select("created_at, role").gte("created_at", start_date.isoformat()).execute()
        
        if not response.data:
            return {"success": True, "data": []}
        
        # Group by month and role
        monthly_data = {}
        
        for user in response.data:
            created_at = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
            month_key = created_at.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {'students': 0, 'teachers': 0}
            
            if user['role'] == 'student':
                monthly_data[month_key]['students'] += 1
            elif user['role'] == 'teacher':
                monthly_data[month_key]['teachers'] += 1
        
        # Convert to array format with month names
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        growth_data = []
        
        # Get last 6 months
        for i in range(6):
            date = end_date - timedelta(days=30*i)
            month_key = date.strftime('%Y-%m')
            month_name = month_names[date.month - 1]
            
            data_point = {
                'name': month_name,
                'students': monthly_data.get(month_key, {}).get('students', 0),
                'teachers': monthly_data.get(month_key, {}).get('teachers', 0)
            }
            growth_data.insert(0, data_point)  # Insert at beginning to maintain chronological order
        
        return {"success": True, "data": growth_data}
        
    except Exception as e:
        print(f"Error fetching user growth data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity-logs")
async def get_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    start_date: str = Query(None),
    end_date: str = Query(None),
    action_type: str = Query(None),
    user_role: str = Query(None)
):
    """Get comprehensive activity logs with filtering and pagination"""
    try:
        # Build query
        query = supabase.table("email_notifications").select("""
            id,
            notification_type,
            recipient_email,
            created_at,
            status
        """).order("created_at", desc=True)
        
        # Apply filters
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)
        if action_type:
            query = query.eq("notification_type", action_type)
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Get total count for pagination
        count_query = supabase.table("email_notifications").select("id", count="exact")
        if start_date:
            count_query = count_query.gte("created_at", start_date)
        if end_date:
            count_query = count_query.lte("created_at", end_date)
        if action_type:
            count_query = count_query.eq("notification_type", action_type)
            
        count_response = count_query.execute()
        total_count = count_response.count or 0
        
        # Format the data
        logs = []
        for log in response.data or []:
            formatted_log = {
                'id': log['id'],
                'timestamp': log['created_at'],
                'event_type': log['notification_type'],
                'recipient_email': log['recipient_email'],
                'status': log['status'],
                'description': _format_activity_description(log['notification_type'], {}),
                'metadata': {}
            }
            logs.append(formatted_log)
        
        return {
            "success": True,
            "data": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"Error fetching activity logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _format_activity_description(event_type: str, metadata: dict) -> str:
    """Format activity description based on event type and metadata"""
    descriptions = {
        'user_registration': 'New user registered',
        'teacher_verification_success_teacher': 'Teacher verification approved',
        'teacher_verification_success': 'Teacher verification approved (admin notification)',
        'teacher_verification_failed': 'Teacher verification failed',
        'teacher_manual_review_teacher': 'Teacher verification submitted for manual review',
        'teacher_manual_review': 'Teacher manual review notification (admin)',
        'teacher_approved': 'Teacher account approved',
        'teacher_rejected': 'Teacher account rejected',
        'course_created': 'New course created',
        'assignment_created': 'New assignment created',
        'quiz_submitted': 'Quiz submitted',
        'enrollment_created': 'Student enrolled in course',
        'password_reset': 'Password reset requested',
        'email_verification': 'Email verification sent'
    }
    
    base_description = descriptions.get(event_type, event_type.replace('_', ' ').title())
    
    # Add specific details from metadata
    if metadata:
        if 'teacher_name' in metadata:
            base_description += f" - {metadata['teacher_name']}"
        elif 'course_name' in metadata:
            base_description += f" - {metadata['course_name']}"
        elif 'student_name' in metadata:
            base_description += f" - {metadata['student_name']}"
    
    return base_description

@router.get("/activity-logs/export")
async def export_activity_logs(
    format: str = Query("csv", regex="^(csv|json)$"),
    start_date: str = Query(None),
    end_date: str = Query(None),
    action_type: str = Query(None)
):
    """Export activity logs in CSV or JSON format"""
    try:
        # Build query (no pagination for export)
        query = supabase.table("email_notifications").select("""
            id,
            notification_type,
            recipient_email,
            created_at,
            status
        """).order("created_at", desc=True)
        
        # Apply filters
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)
        if action_type:
            query = query.eq("notification_type", action_type)
        
        response = query.execute()
        
        # Format the data
        logs = []
        for log in response.data or []:
            formatted_log = {
                'id': log['id'],
                'timestamp': log['created_at'],
                'event_type': log['notification_type'],
                'recipient_email': log['recipient_email'],
                'status': log['status'],
                'description': _format_activity_description(log['notification_type'], {}),
                'teacher_name': '',
                'course_name': '',
                'student_name': '',
                'confidence': '',
                'reason': ''
            }
            logs.append(formatted_log)
        
        if format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if logs:
                writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                writer.writeheader()
                writer.writerows(logs)
            
            return {
                "success": True,
                "data": output.getvalue(),
                "filename": f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "content_type": "text/csv"
            }
        else:  # JSON
            return {
                "success": True,
                "data": logs,
                "filename": f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "content_type": "application/json"
            }
        
    except Exception as e:
        print(f"Error exporting activity logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
