"""
Enhanced Notifications API for LearnSphere
Provides comprehensive notification management for students and teachers
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
from supabase import create_client, Client
from auth_middleware import get_current_user

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Pydantic models
class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str
    is_read: bool
    read_at: Optional[str] = None
    action_url: Optional[str] = None
    created_at: str
    expires_at: Optional[str] = None

class NotificationPreferences(BaseModel):
    email_notifications: bool = True
    in_app_notifications: bool = True
    assignment_reminders: bool = True
    quiz_reminders: bool = True
    forum_notifications: bool = True
    course_updates: bool = True
    system_notifications: bool = True
    quiet_hours_start: Optional[str] = None  # Format: "HH:MM"
    quiet_hours_end: Optional[str] = None    # Format: "HH:MM"

class CreateNotificationRequest(BaseModel):
    user_id: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    action_url: Optional[str] = None
    expires_at: Optional[str] = None

class MarkReadRequest(BaseModel):
    notification_ids: List[str]

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    type_filter: Optional[str] = Query(None),
    priority_filter: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications with filtering options"""
    try:
        query = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", current_user["id"])\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)
        
        # Apply filters
        if unread_only:
            query = query.eq("is_read", False)
        
        if type_filter:
            query = query.eq("type", type_filter)
        
        if priority_filter:
            query = query.eq("priority", priority_filter)
        
        # Filter out expired notifications
        query = query.or_("expires_at.is.null,expires_at.gt." + datetime.utcnow().isoformat())
        
        result = query.execute()
        
        if not result.data:
            return []
        
        return [NotificationResponse(**notification) for notification in result.data]
        
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notifications")

@router.get("/count", response_model=Dict[str, int])
async def get_notification_count(
    current_user: dict = Depends(get_current_user)
):
    """Get unread notification count for user"""
    try:
        # Get total unread count directly from table
        result = supabase.table("notifications")\
            .select("id", count="exact")\
            .eq("user_id", current_user["id"])\
            .eq("is_read", False)\
            .execute()
        
        total_unread = result.count or 0
        
        # Also get count by type for more detailed stats
        type_counts = {}
        notification_types = [
            "assignment_created", "assignment_due_soon", "assignment_overdue",
            "quiz_available", "quiz_due_soon", "course_enrolled",
            "forum_question_answered", "student_enrolled", "assignment_submission_received"
        ]
        
        for notif_type in notification_types:
            type_result = supabase.table("notifications")\
                .select("id", count="exact")\
                .eq("user_id", current_user["id"])\
                .eq("type", notif_type)\
                .eq("is_read", False)\
                .execute()
            
            type_counts[notif_type] = type_result.count or 0
        
        return {
            "total_unread": total_unread,
            "by_type": type_counts
        }
        
    except Exception as e:
        print(f"Error fetching notification count: {e}")
        # Return a safe fallback instead of throwing 500
        return {
            "total_unread": 0,
            "by_type": {}
        }

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a specific notification as read"""
    try:
        # Update notification directly
        result = supabase.table("notifications")\
            .update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            })\
            .eq("id", notification_id)\
            .eq("user_id", current_user["id"])\
            .select()\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Notification not found or already read")
        
        return NotificationResponse(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")

@router.put("/mark-all-read", response_model=Dict[str, int])
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user)
):
    """Mark all user notifications as read"""
    try:
        # Update all unread notifications directly
        result = supabase.table("notifications")\
            .update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            })\
            .eq("user_id", current_user["id"])\
            .eq("is_read", False)\
            .execute()
        
        updated_count = len(result.data) if result.data else 0
        
        return {
            "message": "All notifications marked as read",
            "updated_count": updated_count
        }
        
    except Exception as e:
        print(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark all notifications as read")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a specific notification"""
    try:
        result = supabase.table("notifications")\
            .delete()\
            .eq("id", notification_id)\
            .eq("user_id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@router.delete("/cleanup-expired")
async def cleanup_expired_notifications(
    current_user: dict = Depends(get_current_user)
):
    """Clean up expired notifications for the user"""
    try:
        # Only clean up for the current user
        result = supabase.table("notifications")\
            .delete()\
            .eq("user_id", current_user["id"])\
            .not_.is_("expires_at", "null")\
            .lt("expires_at", datetime.utcnow().isoformat())\
            .execute()
        
        deleted_count = len(result.data) if result.data else 0
        
        return {
            "message": "Expired notifications cleaned up",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        print(f"Error cleaning up expired notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to clean up expired notifications")

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user notification preferences"""
    try:
        result = supabase.table("profiles")\
            .select("notification_preferences")\
            .eq("id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        preferences = result.data[0].get("notification_preferences", {})
        
        # Return default preferences if none exist
        return NotificationPreferences(**preferences) if preferences else NotificationPreferences()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notification preferences")

@router.put("/preferences", response_model=Dict[str, str])
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update user notification preferences"""
    try:
        result = supabase.table("profiles")\
            .update({"notification_preferences": preferences.dict()})\
            .eq("id", current_user["id"])\
            .execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Notification preferences updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

@router.post("/create", response_model=NotificationResponse)
async def create_notification(
    notification: CreateNotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new notification (admin/teacher only)"""
    try:
        # Check if user has permission to create notifications
        user_role = current_user.get("role", "student")
        if user_role not in ["admin", "teacher"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Use the database function to create notification
        result = supabase.rpc("create_notification", {
            "p_user_id": notification.user_id,
            "p_type": notification.type,
            "p_title": notification.title,
            "p_message": notification.message,
            "p_data": notification.data,
            "p_priority": notification.priority,
            "p_action_url": notification.action_url,
            "p_expires_at": notification.expires_at
        }).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create notification")
        
        # Fetch the created notification
        notification_result = supabase.table("notifications")\
            .select("*")\
            .eq("id", result.data)\
            .execute()
        
        if not notification_result.data:
            raise HTTPException(status_code=500, detail="Failed to fetch created notification")
        
        return NotificationResponse(**notification_result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.get("/types", response_model=List[Dict[str, str]])
async def get_notification_types():
    """Get available notification types with descriptions"""
    notification_types = [
        {
            "type": "assignment_created",
            "description": "New assignment posted",
            "category": "assignments",
            "icon": "📝"
        },
        {
            "type": "assignment_due_soon",
            "description": "Assignment due within 24 hours",
            "category": "assignments",
            "icon": "⏰"
        },
        {
            "type": "assignment_due_today",
            "description": "Assignment due today",
            "category": "assignments",
            "icon": "🚨"
        },
        {
            "type": "assignment_overdue",
            "description": "Assignment is overdue",
            "category": "assignments",
            "icon": "⚠️"
        },
        {
            "type": "assignment_submitted",
            "description": "Assignment submitted successfully",
            "category": "assignments",
            "icon": "✅"
        },
        {
            "type": "assignment_graded",
            "description": "Assignment has been graded",
            "category": "assignments",
            "icon": "📊"
        },
        {
            "type": "quiz_available",
            "description": "New quiz is available",
            "category": "quizzes",
            "icon": "🧠"
        },
        {
            "type": "quiz_due_soon",
            "description": "Quiz due within 24 hours",
            "category": "quizzes",
            "icon": "⏰"
        },
        {
            "type": "quiz_due_today",
            "description": "Quiz due today",
            "category": "quizzes",
            "icon": "🚨"
        },
        {
            "type": "quiz_overdue",
            "description": "Quiz is overdue",
            "category": "quizzes",
            "icon": "⚠️"
        },
        {
            "type": "quiz_completed",
            "description": "Quiz has been completed",
            "category": "quizzes",
            "icon": "✅"
        },
        {
            "type": "quiz_graded",
            "description": "Quiz results available",
            "category": "quizzes",
            "icon": "📊"
        },
        {
            "type": "course_enrolled",
            "description": "Successfully enrolled in course",
            "category": "courses",
            "icon": "🎓"
        },
        {
            "type": "course_updated",
            "description": "Course information updated",
            "category": "courses",
            "icon": "📚"
        },
        {
            "type": "new_material",
            "description": "New course material uploaded",
            "category": "courses",
            "icon": "📄"
        },
        {
            "type": "course_completed",
            "description": "Course completed successfully",
            "category": "courses",
            "icon": "🏆"
        },
        {
            "type": "forum_question_answered",
            "description": "Your question has been answered",
            "category": "forum",
            "icon": "💬"
        },
        {
            "type": "forum_new_question",
            "description": "New question in course forum",
            "category": "forum",
            "icon": "❓"
        },
        {
            "type": "forum_question_resolved",
            "description": "Question marked as resolved",
            "category": "forum",
            "icon": "✅"
        },
        {
            "type": "student_enrolled",
            "description": "New student enrolled in your course",
            "category": "teacher",
            "icon": "👨‍🎓"
        },
        {
            "type": "assignment_submission_received",
            "description": "Student submitted assignment",
            "category": "teacher",
            "icon": "📥"
        },
        {
            "type": "quiz_submission_received",
            "description": "Student completed quiz",
            "category": "teacher",
            "icon": "📥"
        },
        {
            "type": "student_question_asked",
            "description": "Student asked a question",
            "category": "teacher",
            "icon": "❓"
        },
        {
            "type": "course_rating_received",
            "description": "Course received a new rating",
            "category": "teacher",
            "icon": "⭐"
        },
        {
            "type": "account_approved",
            "description": "Account approved by admin",
            "category": "system",
            "icon": "✅"
        },
        {
            "type": "account_rejected",
            "description": "Account application rejected",
            "category": "system",
            "icon": "❌"
        },
        {
            "type": "password_changed",
            "description": "Password successfully changed",
            "category": "system",
            "icon": "🔐"
        },
        {
            "type": "login_alert",
            "description": "New login detected",
            "category": "system",
            "icon": "🔔"
        },
        {
            "type": "payment_successful",
            "description": "Payment processed successfully",
            "category": "system",
            "icon": "💳"
        },
        {
            "type": "payment_failed",
            "description": "Payment processing failed",
            "category": "system",
            "icon": "❌"
        },
        {
            "type": "subscription_expired",
            "description": "Subscription has expired",
            "category": "system",
            "icon": "⏰"
        }
    ]
    
    return notification_types

@router.get("/stats", response_model=Dict[str, Any])
async def get_notification_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get notification statistics for the user"""
    try:
        # Get total notifications
        total_result = supabase.table("notifications")\
            .select("id", count="exact")\
            .eq("user_id", current_user["id"])\
            .execute()
        
        # Get unread notifications
        unread_result = supabase.table("notifications")\
            .select("id", count="exact")\
            .eq("user_id", current_user["id"])\
            .eq("is_read", False)\
            .execute()
        
        # Get notifications by priority
        priority_stats = {}
        priorities = ["low", "medium", "high", "urgent"]
        
        for priority in priorities:
            priority_result = supabase.table("notifications")\
                .select("id", count="exact")\
                .eq("user_id", current_user["id"])\
                .eq("priority", priority)\
                .eq("is_read", False)\
                .execute()
            
            priority_stats[priority] = priority_result.count or 0
        
        # Get notifications by type (top 5)
        type_result = supabase.table("notifications")\
            .select("type", count="exact")\
            .eq("user_id", current_user["id"])\
            .eq("is_read", False)\
            .order("count", desc=True)\
            .limit(5)\
            .execute()
        
        return {
            "total_notifications": total_result.count or 0,
            "unread_notifications": unread_result.count or 0,
            "read_notifications": (total_result.count or 0) - (unread_result.count or 0),
            "by_priority": priority_stats,
            "top_types": type_result.data or []
        }
        
    except Exception as e:
        print(f"Error fetching notification stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notification statistics")
