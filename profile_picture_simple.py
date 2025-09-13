"""
Simple Profile Picture Upload API
Working version based on course thumbnail upload pattern
"""

import os
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/profile-pictures", tags=["profile-pictures"])

class ProfilePictureResponse(BaseModel):
    message: str
    profile_picture_url: str

@router.post("/upload", response_model=ProfilePictureResponse)
async def upload_profile_picture_simple(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a profile picture using the exact same pattern as course thumbnails"""
    try:
        print(f"Uploading profile picture for user: {user_id}")

        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Profile picture must be an image file")

        # Validate file size (max 5MB)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")

        # Generate unique filename (same pattern as course thumbnails)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        filename = f"{timestamp}_{unique_id}_profile{file_extension}"

        # Upload to Supabase Storage (exact same pattern as course thumbnails)
        response = supabase.storage.from_("profile-pictures").upload(
            path=filename,
            file=file_content,
            file_options={
                'content-type': file.content_type,
                'upsert': False
            }
        )

        # Check if upload was successful (same pattern as course thumbnails)
        if not response or (hasattr(response, 'error') and response.error):
            error_msg = response.error if hasattr(response, 'error') else "Unknown upload error"
            raise HTTPException(status_code=500, detail=f"Storage upload failed: {error_msg}")

        # Generate public URL
        public_url = supabase.storage.from_("profile-pictures").get_public_url(filename)

        print(f"Profile picture uploaded successfully: {filename}")

        # Update user profile with picture URL
        update_response = supabase.table('profiles').update({
            'profile_picture': public_url
        }).eq('id', user_id).execute()

        if not update_response.data:
            raise HTTPException(status_code=404, detail="User profile not found")

        return ProfilePictureResponse(
            message="Profile picture uploaded successfully",
            profile_picture_url=public_url
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading profile picture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_profile_picture_simple(user_id: str):
    """Get a user's profile picture URL"""
    try:
        response = supabase.table('profiles').select('profile_picture, full_name').eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        profile = response.data[0]
        return {
            "profile_picture_url": profile.get('profile_picture'),
            "full_name": profile.get('full_name')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting profile picture URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
