"""
Admin Notifications API
Handles notifications for admin panel like pending teacher approvals
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
from supabase import create_client, Client

# Initialize Supabase admin client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/admin/notifications", tags=["admin-notifications"])

class AdminNotification(BaseModel):
    id: str
    type: str  # 'teacher_approval', 'user_report', 'system_alert'
    title: str
    message: str
    priority: str  # 'low', 'medium', 'high', 'urgent'
    is_read: bool
    created_at: str
    data: Optional[dict] = None

@router.get("/", response_model=List[AdminNotification])
async def get_admin_notifications(limit: int = 20, unread_only: bool = False):
    """Get admin notifications"""
    try:
        notifications = []
        
        # Get pending teacher approvals
        pending_teachers_response = supabase_admin.table('profiles').select(
            'id, full_name, email, created_at'
        ).eq('role', 'teacher').eq('approval_status', 'pending').execute()
        
        for teacher in pending_teachers_response.data or []:
            notifications.append({
                'id': f"teacher_approval_{teacher['id']}",
                'type': 'teacher_approval',
                'title': 'New Teacher Approval Required',
                'message': f"{teacher['full_name']} ({teacher['email']}) is waiting for approval",
                'priority': 'high',
                'is_read': False,
                'created_at': teacher['created_at'],
                'data': {
                    'teacher_id': teacher['id'],
                    'teacher_name': teacher['full_name'],
                    'teacher_email': teacher['email']
                }
            })
        
        # Get recent disabled users (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        disabled_users_response = supabase_admin.table('profiles').select(
            'id, full_name, email, updated_at'
        ).eq('is_active', False).gte('updated_at', yesterday).execute()
        
        for user in disabled_users_response.data or []:
            notifications.append({
                'id': f"user_disabled_{user['id']}",
                'type': 'user_report',
                'title': 'User Account Disabled',
                'message': f"User {user['full_name']} ({user['email']}) was recently disabled",
                'priority': 'medium',
                'is_read': False,
                'created_at': user['updated_at'],
                'data': {
                    'user_id': user['id'],
                    'user_name': user['full_name'],
                    'user_email': user['email']
                }
            })
        
        # Get system alerts (courses without teachers, etc.)
        orphaned_courses_response = supabase_admin.table('courses').select(
            'id, title, created_at'
        ).is_('teacher_id', 'null').execute()
        
        for course in orphaned_courses_response.data or []:
            notifications.append({
                'id': f"orphaned_course_{course['id']}",
                'type': 'system_alert',
                'title': 'Course Without Teacher',
                'message': f"Course '{course['title']}' has no assigned teacher",
                'priority': 'low',
                'is_read': False,
                'created_at': course['created_at'],
                'data': {
                    'course_id': course['id'],
                    'course_title': course['title']
                }
            })
        
        # Sort by priority and date
        priority_order = {'urgent': 4, 'high': 3, 'medium': 2, 'low': 1}
        notifications.sort(
            key=lambda x: (priority_order.get(x['priority'], 0), x['created_at']), 
            reverse=True
        )
        
        # Apply filters
        if unread_only:
            notifications = [n for n in notifications if not n['is_read']]
        
        return notifications[:limit]
        
    except Exception as e:
        print(f"Error fetching admin notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/count")
async def get_notification_count():
    """Get count of unread notifications"""
    try:
        # Count pending teacher approvals
        pending_teachers_response = supabase_admin.table('profiles').select(
            'id', count='exact'
        ).eq('role', 'teacher').eq('approval_status', 'pending').execute()
        
        pending_teachers = pending_teachers_response.count or 0
        
        # Count recent system issues (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        
        # Count recently disabled users
        disabled_users_response = supabase_admin.table('profiles').select(
            'id', count='exact'
        ).eq('is_active', False).gte('updated_at', yesterday).execute()
        
        disabled_users = disabled_users_response.count or 0
        
        # Count orphaned courses
        orphaned_courses_response = supabase_admin.table('courses').select(
            'id', count='exact'
        ).is_('teacher_id', 'null').execute()
        
        orphaned_courses = orphaned_courses_response.count or 0
        
        total_count = pending_teachers + disabled_users + orphaned_courses
        
        return {
            'total': total_count,
            'pending_teachers': pending_teachers,
            'disabled_users': disabled_users,
            'orphaned_courses': orphaned_courses,
            'breakdown': {
                'teacher_approvals': pending_teachers,
                'user_reports': disabled_users,
                'system_alerts': orphaned_courses
            }
        }
        
    except Exception as e:
        print(f"Error getting notification count: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    try:
        # For now, we'll just return success since we're generating notifications dynamically
        # In a real implementation, you'd store read status in a database
        return {"success": True, "message": "Notification marked as read"}
        
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-all-read")
async def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        # For now, we'll just return success since we're generating notifications dynamically
        # In a real implementation, you'd update all unread notifications in the database
        return {"success": True, "message": "All notifications marked as read"}
        
    except Exception as e:
        print(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def dismiss_notification(notification_id: str):
    """Dismiss a notification"""
    try:
        # For now, we'll just return success since we're generating notifications dynamically
        # In a real implementation, you'd delete or hide the notification
        return {"success": True, "message": "Notification dismissed"}
        
    except Exception as e:
        print(f"Error dismissing notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_notifications_summary():
    """Get a summary of notifications for dashboard"""
    try:
        count_data = await get_notification_count()
        notifications = await get_admin_notifications(limit=5, unread_only=True)
        
        return {
            'total_unread': count_data['total'],
            'recent_notifications': notifications,
            'breakdown': count_data['breakdown'],
            'has_urgent': any(n['priority'] == 'urgent' for n in notifications),
            'has_high_priority': any(n['priority'] == 'high' for n in notifications)
        }
        
    except Exception as e:
        print(f"Error getting notifications summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
