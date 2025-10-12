"""
API endpoints for email notifications
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import asyncio
import threading
from notification_service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class TeacherApprovalNotification(BaseModel):
    teacher_email: EmailStr
    teacher_name: str
    admin_name: str = "Administrator"

class TeacherRejectionNotification(BaseModel):
    teacher_email: EmailStr
    teacher_name: str
    reason: str
    admin_name: str = "Administrator"

class UserStatusChangeNotification(BaseModel):
    user_email: EmailStr
    user_name: str
    is_enabled: bool
    admin_name: str = "Administrator"

def send_email_async(func, *args, **kwargs):
    """Send email in a separate thread to avoid blocking"""
    def run_in_thread():
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in email thread: {e}")
            return False
    
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()
    return True

@router.post("/teacher-approval")
async def send_teacher_approval_notification(notification: TeacherApprovalNotification):
    """Send teacher approval notification email"""
    try:
        # Send email asynchronously to avoid blocking
        success = send_email_async(
            notification_service.send_teacher_approval_notification,
            notification.teacher_email,
            notification.teacher_name,
            notification.admin_name
        )
        
        if success:
            return {"message": "Teacher approval notification sent successfully", "status": "success"}
        else:
            return {"message": "Failed to send teacher approval notification", "status": "error"}
            
    except Exception as e:
        print(f"Error sending teacher approval notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.post("/teacher-rejection")
async def send_teacher_rejection_notification(notification: TeacherRejectionNotification):
    """Send teacher rejection notification email"""
    try:
        # Send email asynchronously to avoid blocking
        success = send_email_async(
            notification_service.send_teacher_rejection_notification,
            notification.teacher_email,
            notification.teacher_name,
            notification.reason,
            notification.admin_name
        )
        
        if success:
            return {"message": "Teacher rejection notification sent successfully", "status": "success"}
        else:
            return {"message": "Failed to send teacher rejection notification", "status": "error"}
            
    except Exception as e:
        print(f"Error sending teacher rejection notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.post("/user-status-change")
async def send_user_status_change_notification(notification: UserStatusChangeNotification):
    """Send user status change notification email"""
    try:
        # Send email asynchronously to avoid blocking
        success = send_email_async(
            notification_service.send_user_status_change_notification,
            notification.user_email,
            notification.user_name,
            notification.is_enabled,
            notification.admin_name
        )
        
        if success:
            return {"message": "User status change notification sent successfully", "status": "success"}
        else:
            return {"message": "Failed to send user status change notification", "status": "error"}
            
    except Exception as e:
        print(f"Error sending user status change notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

@router.get("/test")
async def test_email_configuration():
    """Test email configuration"""
    try:
        # Test with a simple email
        test_email_data = notification_service.create_teacher_approval_email("Test User", "Test Admin")
        
        return {
            "message": "Email configuration test completed",
            "smtp_configured": bool(notification_service.smtp_username and notification_service.smtp_password),
            "smtp_server": notification_service.smtp_server,
            "smtp_port": notification_service.smtp_port,
            "from_email": notification_service.from_email,
            "sample_subject": test_email_data["subject"]
        }
        
    except Exception as e:
        print(f"Error testing email configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to test email configuration")
