"""
Profile Picture Upload API
Handles profile picture upload and management using Supabase Storage
"""

import os
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/profile-pictures", tags=["profile-pictures"])

BUCKET_NAME = "profile-pictures"

def ensure_bucket_exists():
    """Ensure the profile pictures bucket exists"""
    try:
        # Try to list buckets to check if our bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = [bucket['name'] for bucket in buckets]

        if BUCKET_NAME not in bucket_names:
            # Create the bucket if it doesn't exist
            result = supabase.storage.create_bucket(BUCKET_NAME, {"public": True})
            if result.get('error'):
                print(f"Warning: Could not create bucket: {result['error']}")
            else:
                print(f"Created bucket '{BUCKET_NAME}' successfully")
    except Exception as e:
        print(f"Warning: Could not ensure bucket exists: {e}")

class ProfilePictureResponse(BaseModel):
    message: str
    profile_picture_url: Optional[str] = None

@router.post("/upload", response_model=ProfilePictureResponse)
async def upload_profile_picture(
    user_id: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload a profile picture for a user using Supabase Storage"""
    try:
        # Ensure bucket exists
        ensure_bucket_exists()
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only JPEG, PNG, GIF, and WebP images are allowed."
            )

        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum size is 5MB."
            )

        # Generate unique filename with user folder structure
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{user_id}/profile.{file_extension}"

        # Delete existing profile picture if it exists
        try:
            existing_files = supabase.storage.from_(BUCKET_NAME).list(user_id)
            if existing_files.get('data'):
                for existing_file in existing_files['data']:
                    supabase.storage.from_(BUCKET_NAME).remove([f"{user_id}/{existing_file['name']}"])
        except:
            pass  # Ignore errors when deleting existing files

        # Upload to Supabase Storage
        upload_response = supabase.storage.from_(BUCKET_NAME).upload(
            unique_filename,
            file_content,
            file_options={
                "content-type": file.content_type,
                "upsert": True
            }
        )

        if upload_response.get('error'):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {upload_response['error']}"
            )

        # Get public URL
        public_url_response = supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)
        profile_picture_url = public_url_response

        # Update user profile with picture URL
        response = supabase.table('profiles').update({
            'profile_picture': profile_picture_url
        }).eq('id', user_id).execute()

        if not response.data:
            # Clean up uploaded file if database update fails
            try:
                supabase.storage.from_(BUCKET_NAME).remove([unique_filename])
            except:
                pass
            raise HTTPException(status_code=404, detail="User profile not found")

        return ProfilePictureResponse(
            message="Profile picture uploaded successfully",
            profile_picture_url=profile_picture_url
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading profile picture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/view/{user_id}/{filename}")
async def view_profile_picture(user_id: str, filename: str):
    """Redirect to Supabase Storage public URL"""
    try:
        file_path = f"{user_id}/{filename}"

        # Get public URL from Supabase Storage
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

        # Redirect to the public URL
        return RedirectResponse(url=public_url)

    except Exception as e:
        print(f"Error viewing profile picture: {e}")
        raise HTTPException(status_code=404, detail="Profile picture not found")

@router.delete("/{user_id}")
async def delete_profile_picture(user_id: str):
    """Delete a user's profile picture from Supabase Storage"""
    try:
        # Update profile to remove picture URL
        response = supabase.table('profiles').update({
            'profile_picture': None
        }).eq('id', user_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Delete files from Supabase Storage
        try:
            # List all files in user's folder
            files_response = supabase.storage.from_(BUCKET_NAME).list(user_id)
            if files_response.get('data'):
                # Delete all files in the user's folder
                file_paths = [f"{user_id}/{file['name']}" for file in files_response['data']]
                if file_paths:
                    supabase.storage.from_(BUCKET_NAME).remove(file_paths)
        except Exception as storage_error:
            print(f"Warning: Could not delete files from storage: {storage_error}")
            # Don't fail the request if storage deletion fails

        return {"message": "Profile picture deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile picture: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_profile_picture_url(user_id: str):
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
