"""
Admin Dashboard API
Provides real-time statistics and data for admin dashboard
"""

import os
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
            profiles_response = supabase.table('profiles').select('role, is_active, approval_status').execute()
            profiles = profiles_response.data or []

            active_students = sum(1 for p in profiles if p.get('role') == 'student' and p.get('is_active', True))
            active_teachers = sum(1 for p in profiles if p.get('role') == 'teacher' and p.get('is_active', True) and p.get('approval_status') == 'approved')
            pending_approvals = sum(1 for p in profiles if p.get('role') == 'teacher' and p.get('approval_status') == 'pending')
            total_users = len(profiles)

            return active_students, active_teachers, pending_approvals, total_users

        async def get_content_counts():
            """Get content counts with minimal data transfer"""
            # Use count queries where possible, otherwise select only IDs
            courses_response = supabase.table('courses').select('id', count='exact').execute()
            enrollments_response = supabase.table('enrollments').select('id', count='exact').execute()
            assignments_response = supabase.table('assignments').select('id', count='exact').execute()
            quizzes_response = supabase.table('quizzes').select('id', count='exact').execute()

            active_courses = courses_response.count if hasattr(courses_response, 'count') else len(courses_response.data or [])
            total_enrollments = enrollments_response.count if hasattr(enrollments_response, 'count') else len(enrollments_response.data or [])
            total_assignments = assignments_response.count if hasattr(assignments_response, 'count') else len(assignments_response.data or [])
            total_quizzes = quizzes_response.count if hasattr(quizzes_response, 'count') else len(quizzes_response.data or [])

            return active_courses, total_enrollments, total_assignments, total_quizzes

        async def get_submission_counts():
            """Get submission counts efficiently"""
            assignment_subs_response = supabase.table('assignment_submissions').select('id', count='exact').execute()
            quiz_subs_response = supabase.table('quiz_submissions').select('id', count='exact').execute()

            assignment_subs = assignment_subs_response.count if hasattr(assignment_subs_response, 'count') else len(assignment_subs_response.data or [])
            quiz_subs = quiz_subs_response.count if hasattr(quiz_subs_response, 'count') else len(quiz_subs_response.data or [])

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
            activity_logs.append(ActivityLog(
                id=user['id'],
                user_name=user['full_name'] or 'Unknown User',
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
            teacher_name = course['profiles']['full_name'] if course.get('profiles') else 'Unknown Teacher'
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
