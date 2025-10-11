"""
Profile Picture API
Handles profile picture upload, retrieval, and management
"""

import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from supabase import create_client, Client
from auth_middleware import get_current_user, TokenData
from supabase_storage import get_storage_manager, SupabaseStorageManager

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/api/profile-pictures", tags=["profile-pictures"])

@router.get("/{user_id}")
async def get_profile_picture(user_id: str):
    """Get user's profile picture URL."""
    try:
        # Get user profile from database
        response = supabase.table("profiles").select("profile_picture").eq("id", user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile_picture_url = response.data.get("profile_picture")
        
        if not profile_picture_url:
            return JSONResponse(
                status_code=404,
                content={"message": "No profile picture found", "profile_picture": None}
            )
        
        return {
            "user_id": user_id,
            "profile_picture": profile_picture_url,
            "profile_picture_url": profile_picture_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile picture: {str(e)}")

@router.post("/upload")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """Upload a new profile picture."""
    try:
        # Upload file to storage
        upload_result = await storage_manager.upload_profile_picture(file, current_user.user_id)
        
        # Update user profile in database
        update_response = supabase.table("profiles").update({
            "profile_picture": upload_result["file_url"],
            "updated_at": "now()"
        }).eq("id", current_user.user_id).execute()
        
        if not update_response.data:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return {
            "message": "Profile picture uploaded successfully",
            "file_url": upload_result["file_url"],
            "file_name": upload_result["file_name"],
            "file_size": upload_result["file_size"],
            "file_type": upload_result["file_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload profile picture: {str(e)}")

@router.delete("/{user_id}")
async def delete_profile_picture(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete user's profile picture."""
    try:
        # Verify user can only delete their own profile picture
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update user profile to remove profile picture
        update_response = supabase.table("profiles").update({
            "profile_picture": None,
            "updated_at": "now()"
        }).eq("id", user_id).execute()
        
        if not update_response.data:
            raise HTTPException(status_code=500, detail="Failed to delete profile picture")
        
        return {
            "message": "Profile picture deleted successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete profile picture: {str(e)}")

@router.post("/{user_id}")
async def upload_profile_picture_for_user(
    user_id: str,
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """Upload profile picture for a specific user (admin or self)."""
    try:
        # Verify user can upload for this user
        if current_user.user_id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Upload file to storage
        upload_result = await storage_manager.upload_profile_picture(file, user_id)
        
        # Update user profile in database
        update_response = supabase.table("profiles").update({
            "profile_picture": upload_result["file_url"],
            "updated_at": "now()"
        }).eq("id", user_id).execute()
        
        if not update_response.data:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return {
            "message": "Profile picture uploaded successfully",
            "user_id": user_id,
            "file_url": upload_result["file_url"],
            "file_name": upload_result["file_name"],
            "file_size": upload_result["file_size"],
            "file_type": upload_result["file_type"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload profile picture: {str(e)}")
