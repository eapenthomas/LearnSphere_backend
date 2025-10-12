from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from supabase import create_client, Client
from datetime import datetime
from admin_email_service import send_user_status_email, send_teacher_approval_email

# Initialize Supabase admin client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/admin", tags=["admin"])

class ToggleUserStatusRequest(BaseModel):
    user_id: str
    is_active: bool
    admin_id: str

class ApproveTeacherRequest(BaseModel):
    request_id: str
    teacher_id: str
    admin_id: str
    notes: Optional[str] = ""

class RejectTeacherRequest(BaseModel):
    request_id: str
    teacher_id: str
    admin_id: str
    reason: str

@router.post("/toggle-user-status")
async def toggle_user_status(request: ToggleUserStatusRequest):
    """Toggle user active status using admin privileges"""
    try:
        print(f"Admin API: Toggling user status for {request.user_id} to {request.is_active}")
        
        # First, get the current user status for logging
        current_user_response = supabase_admin.table('profiles').select('is_active, email, full_name').eq('id', request.user_id).single().execute()

        if not current_user_response.data:
            raise HTTPException(status_code=404, detail="User not found")

        current_user = current_user_response.data
        print(f"Current user status: {current_user}")

        # Update the user status using admin client
        update_response = supabase_admin.table('profiles').update({
            'is_active': request.is_active,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', request.user_id).execute()

        print(f"User status updated successfully: {update_response.data}")

        # Get admin name for email
        admin_response = supabase_admin.table('profiles').select('full_name').eq('id', request.admin_id).single().execute()
        admin_name = admin_response.data['full_name'] if admin_response.data else "Administrator"

        # Send email notification
        try:
            await send_user_status_email(request.user_id, request.is_active, admin_name)
        except Exception as email_error:
            print(f"Failed to send status email: {email_error}")

        # Try to log the action (don't fail if this fails)
        try:
            log_response = supabase_admin.table('user_activity_logs').insert({
                'user_id': request.user_id,
                'action': 'user_enabled' if request.is_active else 'user_disabled',
                'admin_id': request.admin_id,
                'details': {
                    'previous_status': current_user['is_active'],
                    'new_status': request.is_active,
                    'user_email': current_user['email'],
                    'user_name': current_user['full_name']
                }
            }).execute()

            if log_response.error:
                print(f"Warning: Failed to log user action: {log_response.error}")
        except Exception as log_exception:
            print(f"Warning: Exception while logging user action: {log_exception}")
        
        return {
            "success": True,
            "message": f"User {'enabled' if request.is_active else 'disabled'} successfully",
            "data": update_response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in toggle_user_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-teacher")
async def approve_teacher(request: ApproveTeacherRequest):
    """Approve teacher request using admin privileges"""
    try:
        print(f"Admin API: Approving teacher {request.teacher_id}")
        
        # Update approval request
        request_response = supabase_admin.table('teacher_approval_requests').update({
            'status': 'approved',
            'admin_id': request.admin_id,
            'admin_notes': request.notes,
            'processed_at': datetime.utcnow().isoformat()
        }).eq('id', request.request_id).execute()

        # Update teacher profile - IMPORTANT: Set is_active to true and approval_status to approved
        profile_response = supabase_admin.table('profiles').update({
            'approval_status': 'approved',
            'is_active': True,  # Enable the teacher account
            'approved_by': request.admin_id,
            'approved_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', request.teacher_id).execute()

        print(f"Teacher approved successfully: {profile_response.data}")

        # Get admin name for email
        admin_response = supabase_admin.table('profiles').select('full_name').eq('id', request.admin_id).single().execute()
        admin_name = admin_response.data['full_name'] if admin_response.data else "Administrator"

        # Send approval email notification
        try:
            await send_teacher_approval_email(request.teacher_id, True, admin_name)
        except Exception as email_error:
            print(f"Failed to send approval email: {email_error}")

        return {
            "success": True,
            "message": "Teacher approved successfully",
            "data": profile_response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in approve_teacher: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reject-teacher")
async def reject_teacher(request: RejectTeacherRequest):
    """Reject teacher request using admin privileges"""
    try:
        print(f"Admin API: Rejecting teacher {request.teacher_id}")
        
        # Update approval request
        request_response = supabase_admin.table('teacher_approval_requests').update({
            'status': 'rejected',
            'admin_id': request.admin_id,
            'admin_notes': request.reason,
            'processed_at': datetime.utcnow().isoformat()
        }).eq('id', request.request_id).execute()

        # Update teacher profile - Set approval_status to rejected and ensure is_active is false
        profile_response = supabase_admin.table('profiles').update({
            'approval_status': 'rejected',
            'is_active': False,  # Disable the teacher account
            'rejection_reason': request.reason,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', request.teacher_id).execute()

        print(f"Teacher rejected successfully: {profile_response.data}")
        
        return {
            "success": True,
            "message": "Teacher rejected successfully",
            "data": profile_response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in reject_teacher: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users():
    """Get all users for admin management"""
    try:
        response = supabase_admin.table('profiles').select('*').order('created_at', desc=True).execute()

        return {
            "success": True,
            "data": response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_all_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-approvals")
async def get_pending_approvals():
    """Get pending teacher approval requests"""
    try:
        response = supabase_admin.table('teacher_approval_requests').select('''
            *,
            profiles!teacher_approval_requests_teacher_id_fkey (
                id,
                email,
                full_name,
                created_at
            )
        ''').eq('status', 'pending').order('created_at', desc=True).execute()

        return {
            "success": True,
            "data": response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_pending_approvals: {e}")
        raise HTTPException(status_code=500, detail=str(e))
