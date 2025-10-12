"""
Enhanced File Download API
Provides robust file download functionality with proper headers and error handling
"""

import os
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
import requests
from supabase import create_client, Client
from auth_middleware import get_current_user, TokenData

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/api/files", tags=["file-downloads"])

@router.get("/download/assignment/{assignment_id}")
async def download_assignment_file(
    assignment_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Download assignment file with proper authentication and headers."""
    try:
        # Get assignment details
        assignment_response = supabase.table("assignments").select("*").eq("id", assignment_id).single().execute()
        if not assignment_response.data:
            raise HTTPException(status_code=404, detail="Assignment not found")

        assignment = assignment_response.data

        # Check permissions
        if current_user.role == "teacher":
            # Teacher can download their own assignment files
            if assignment["teacher_id"] != current_user.user_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        elif current_user.role == "student":
            # Student can download if enrolled in course
            enrollment_response = supabase.table("enrollments").select("*").eq("student_id", current_user.user_id).eq("course_id", assignment["course_id"]).eq("status", "active").execute()
            if not enrollment_response.data:
                raise HTTPException(status_code=403, detail="Not enrolled in this course")
        else:
            raise HTTPException(status_code=403, detail="Permission denied")

        if not assignment["file_url"]:
            raise HTTPException(status_code=404, detail="No file attached to this assignment")

        # Get file URL from database
        file_url = assignment["file_url"]
        
        # Extract storage path from URL
        # Example: https://.../storage/v1/object/public/assignments/courses/...
        if '/storage/v1/object/public/' in file_url:
            parts = file_url.split('/storage/v1/object/public/')
            if len(parts) == 2:
                bucket_and_path = parts[1]
                # Split bucket name from path
                path_parts = bucket_and_path.split('/', 1)
                if len(path_parts) == 2:
                    bucket_name, file_path = path_parts
                    
                    # Create a signed URL with download parameter for direct download
                    try:
                        # Get signed URL with 1 hour expiration and download=true
                        signed_url = supabase.storage.from_(bucket_name).create_signed_url(
                            file_path,
                            expires_in=3600,
                            options={'download': True}
                        )
                        
                        if signed_url and 'signedURL' in signed_url:
                            return RedirectResponse(url=signed_url['signedURL'], status_code=302)
                    except Exception as sign_error:
                        logger.error(f"Error creating signed URL: {sign_error}")
                        # Fall back to public URL
        
        # Clean the file URL and return as fallback
        if '?' in file_url:
            file_url = file_url.split('?')[0]
        
        # Instead of redirecting, stream the file directly with download headers
        try:
            # Download the file content from Supabase
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL
            filename = file_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Create streaming response with download headers
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Determine content type from filename
            content_type = response.headers.get('content-type', 'application/octet-stream')
            if filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif filename.lower().endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.doc'):
                content_type = 'application/msword'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif filename.lower().endswith(('.xls', '.xlsx')):
                content_type = 'application/vnd.ms-excel' if filename.lower().endswith('.xls') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.lower().endswith(('.ppt', '.pptx')):
                content_type = 'application/vnd.ms-powerpoint' if filename.lower().endswith('.ppt') else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif filename.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif filename.lower().endswith('.zip'):
                content_type = 'application/zip'
            elif filename.lower().endswith('.mp4'):
                content_type = 'video/mp4'
            elif filename.lower().endswith('.mp3'):
                content_type = 'audio/mpeg'
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Type": content_type,
                    "Cache-Control": "no-cache"
                }
            )
        except Exception as stream_error:
            logger.error(f"Error streaming file: {stream_error}")
            # Fallback to redirect with download parameter
            download_url = f"{file_url}?download=true"
            return RedirectResponse(url=download_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.get("/download/submission/{submission_id}")
async def download_submission_file(
    submission_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Download assignment submission file."""
    try:
        # Get submission details
        submission_response = supabase.table("assignment_submissions").select("*").eq("id", submission_id).single().execute()
        if not submission_response.data:
            raise HTTPException(status_code=404, detail="Submission not found")

        submission = submission_response.data

        # Check permissions
        if current_user.role == "teacher":
            # Teacher can download submissions for their assignments
            assignment_response = supabase.table("assignments").select("teacher_id").eq("id", submission["assignment_id"]).single().execute()
            if not assignment_response.data or assignment_response.data["teacher_id"] != current_user.user_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        elif current_user.role == "student":
            # Student can only download their own submissions
            if submission["student_id"] != current_user.user_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        else:
            raise HTTPException(status_code=403, detail="Permission denied")

        if not submission["file_url"]:
            raise HTTPException(status_code=404, detail="No file attached to this submission")

        # Get file URL from database
        file_url = submission["file_url"]
        
        # Extract storage path from URL and create signed URL
        if '/storage/v1/object/public/' in file_url:
            parts = file_url.split('/storage/v1/object/public/')
            if len(parts) == 2:
                bucket_and_path = parts[1]
                path_parts = bucket_and_path.split('/', 1)
                if len(path_parts) == 2:
                    bucket_name, file_path = path_parts
                    
                    try:
                        signed_url = supabase.storage.from_(bucket_name).create_signed_url(
                            file_path,
                            expires_in=3600,
                            options={'download': True}
                        )
                        
                        if signed_url and 'signedURL' in signed_url:
                            return RedirectResponse(url=signed_url['signedURL'], status_code=302)
                    except Exception as sign_error:
                        logger.error(f"Error creating signed URL: {sign_error}")
        
        # Instead of redirecting, stream the file directly with download headers
        try:
            # Download the file content from Supabase
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL
            filename = file_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Create streaming response with download headers
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Determine content type from filename
            content_type = response.headers.get('content-type', 'application/octet-stream')
            if filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif filename.lower().endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.doc'):
                content_type = 'application/msword'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif filename.lower().endswith(('.xls', '.xlsx')):
                content_type = 'application/vnd.ms-excel' if filename.lower().endswith('.xls') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.lower().endswith(('.ppt', '.pptx')):
                content_type = 'application/vnd.ms-powerpoint' if filename.lower().endswith('.ppt') else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif filename.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif filename.lower().endswith('.zip'):
                content_type = 'application/zip'
            elif filename.lower().endswith('.mp4'):
                content_type = 'video/mp4'
            elif filename.lower().endswith('.mp3'):
                content_type = 'audio/mpeg'
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Type": content_type,
                    "Cache-Control": "no-cache"
                }
            )
        except Exception as stream_error:
            logger.error(f"Error streaming file: {stream_error}")
            # Fallback to redirect with download parameter
            download_url = f"{file_url}?download=true"
            return RedirectResponse(url=download_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.get("/download/course-material/{material_id}")
async def download_course_material(
    material_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Download course material file."""
    try:
        # Get material details
        material_response = supabase.table("course_materials").select("*").eq("id", material_id).single().execute()
        if not material_response.data:
            raise HTTPException(status_code=404, detail="Course material not found")

        material = material_response.data

        # Check permissions
        if current_user.role == "teacher":
            # Teacher can download materials for their courses
            course_response = supabase.table("courses").select("teacher_id").eq("id", material["course_id"]).single().execute()
            if not course_response.data or course_response.data["teacher_id"] != current_user.user_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        elif current_user.role == "student":
            # Student can download if enrolled in course
            enrollment_response = supabase.table("enrollments").select("*").eq("student_id", current_user.user_id).eq("course_id", material["course_id"]).eq("status", "active").execute()
            if not enrollment_response.data:
                raise HTTPException(status_code=403, detail="Not enrolled in this course")
        else:
            raise HTTPException(status_code=403, detail="Permission denied")

        if not material["file_url"]:
            raise HTTPException(status_code=404, detail="No file attached to this material")

        # Get file URL from database
        file_url = material["file_url"]
        
        # Extract storage path from URL and create signed URL
        if '/storage/v1/object/public/' in file_url:
            parts = file_url.split('/storage/v1/object/public/')
            if len(parts) == 2:
                bucket_and_path = parts[1]
                path_parts = bucket_and_path.split('/', 1)
                if len(path_parts) == 2:
                    bucket_name, file_path = path_parts
                    
                    try:
                        signed_url = supabase.storage.from_(bucket_name).create_signed_url(
                            file_path,
                            expires_in=3600,
                            options={'download': True}
                        )
                        
                        if signed_url and 'signedURL' in signed_url:
                            return RedirectResponse(url=signed_url['signedURL'], status_code=302)
                    except Exception as sign_error:
                        logger.error(f"Error creating signed URL: {sign_error}")
        
        # Instead of redirecting, stream the file directly with download headers
        try:
            # Download the file content from Supabase
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL
            filename = file_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Create streaming response with download headers
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            # Determine content type from filename
            content_type = response.headers.get('content-type', 'application/octet-stream')
            if filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif filename.lower().endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.doc'):
                content_type = 'application/msword'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif filename.lower().endswith(('.xls', '.xlsx')):
                content_type = 'application/vnd.ms-excel' if filename.lower().endswith('.xls') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.lower().endswith(('.ppt', '.pptx')):
                content_type = 'application/vnd.ms-powerpoint' if filename.lower().endswith('.ppt') else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif filename.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif filename.lower().endswith('.zip'):
                content_type = 'application/zip'
            elif filename.lower().endswith('.mp4'):
                content_type = 'video/mp4'
            elif filename.lower().endswith('.mp3'):
                content_type = 'audio/mpeg'
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Type": content_type,
                    "Cache-Control": "no-cache"
                }
            )
        except Exception as stream_error:
            logger.error(f"Error streaming file: {stream_error}")
            # Fallback to redirect with download parameter
            download_url = f"{file_url}?download=true"
            return RedirectResponse(url=download_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.get("/view/{file_type}/{file_id}")
async def view_file(
    file_type: str,
    file_id: str
):
    """View file inline in browser (for preview/viewing) - public endpoint."""
    try:
        # Get file URL based on type
        if file_type == "assignment":
            assignment_response = supabase.table("assignments").select("file_url").eq("id", file_id).single().execute()
            if not assignment_response.data:
                raise HTTPException(status_code=404, detail="Assignment not found")
            file_url = assignment_response.data["file_url"]
        elif file_type == "submission":
            submission_response = supabase.table("assignment_submissions").select("file_url").eq("id", file_id).single().execute()
            if not submission_response.data:
                raise HTTPException(status_code=404, detail="Submission not found")
            file_url = submission_response.data["file_url"]
        elif file_type == "material":
            material_response = supabase.table("course_materials").select("file_url").eq("id", file_id).single().execute()
            if not material_response.data:
                raise HTTPException(status_code=404, detail="Material not found")
            file_url = material_response.data["file_url"]
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

        if not file_url:
            raise HTTPException(status_code=404, detail="File not found")

        # For viewing, stream the content directly with proper headers
        # This avoids redirect issues and ensures proper content type handling
        
        # Stream the file content for inline viewing
        try:
            response = requests.get(file_url, stream=True)
            response.raise_for_status()
            
            # Get filename and determine content type
            filename = file_url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # Determine content type from filename
            content_type = response.headers.get('content-type', 'application/octet-stream')
            if filename.lower().endswith('.pdf'):
                content_type = 'application/pdf'
            elif filename.lower().endswith('.docx'):
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            elif filename.lower().endswith('.doc'):
                content_type = 'application/msword'
            elif filename.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            elif filename.lower().endswith('.png'):
                content_type = 'image/png'
            elif filename.lower().endswith('.gif'):
                content_type = 'image/gif'
            elif filename.lower().endswith(('.xls', '.xlsx')):
                content_type = 'application/vnd.ms-excel' if filename.lower().endswith('.xls') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif filename.lower().endswith(('.ppt', '.pptx')):
                content_type = 'application/vnd.ms-powerpoint' if filename.lower().endswith('.ppt') else 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            elif filename.lower().endswith('.txt'):
                content_type = 'text/plain'
            elif filename.lower().endswith('.zip'):
                content_type = 'application/zip'
            elif filename.lower().endswith('.mp4'):
                content_type = 'video/mp4'
            elif filename.lower().endswith('.mp3'):
                content_type = 'audio/mpeg'
            
            # Create streaming response for inline viewing
            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
            
            return StreamingResponse(
                generate(),
                media_type=content_type,
                headers={
                    "Content-Disposition": f"inline; filename=\"{filename}\"",  # inline for viewing
                    "Cache-Control": "public, max-age=3600",
                    "Content-Type": content_type
                }
            )
        except Exception as stream_error:
            logger.error(f"Error streaming file for view: {stream_error}")
            # Final fallback: redirect to the original URL
            return RedirectResponse(url=file_url, status_code=302)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to view file: {str(e)}")

@router.get("/direct/{file_type}/{file_id}")
async def direct_file_download(
    file_type: str,
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Direct file download with proper authentication - universal endpoint."""
    try:
        if file_type == "assignment":
            return await download_assignment_file(file_id, current_user)
        elif file_type == "submission":
            return await download_submission_file(file_id, current_user)
        elif file_type == "material":
            return await download_course_material(file_id, current_user)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.get("/url/{file_type}/{file_id}")
async def get_file_download_url(
    file_type: str,
    file_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get file download URL (for cases where redirect doesn't work)."""
    try:
        if file_type == "assignment":
            # Get assignment details
            assignment_response = supabase.table("assignments").select("*").eq("id", file_id).single().execute()
            if not assignment_response.data:
                raise HTTPException(status_code=404, detail="Assignment not found")

            assignment = assignment_response.data

            # Check permissions
            if current_user.role == "teacher":
                if assignment["teacher_id"] != current_user.user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            elif current_user.role == "student":
                enrollment_response = supabase.table("enrollments").select("*").eq("student_id", current_user.user_id).eq("course_id", assignment["course_id"]).eq("status", "active").execute()
                if not enrollment_response.data:
                    raise HTTPException(status_code=403, detail="Not enrolled in this course")
            else:
                raise HTTPException(status_code=403, detail="Permission denied")

            if not assignment["file_url"]:
                raise HTTPException(status_code=404, detail="No file attached to this assignment")

            # Clean the file URL
            file_url = assignment["file_url"]
            if '?' in file_url:
                file_url = file_url.split('?')[0]

            return {
                "success": True,
                "download_url": file_url,
                "file_name": f"assignment_{file_id}.pdf",
                "file_type": "assignment"
            }

        elif file_type == "submission":
            # Get submission details
            submission_response = supabase.table("assignment_submissions").select("*").eq("id", file_id).single().execute()
            if not submission_response.data:
                raise HTTPException(status_code=404, detail="Submission not found")

            submission = submission_response.data

            # Check permissions
            if current_user.role == "teacher":
                assignment_response = supabase.table("assignments").select("teacher_id").eq("id", submission["assignment_id"]).single().execute()
                if not assignment_response.data or assignment_response.data["teacher_id"] != current_user.user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            elif current_user.role == "student":
                if submission["student_id"] != current_user.user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            else:
                raise HTTPException(status_code=403, detail="Permission denied")

            if not submission["file_url"]:
                raise HTTPException(status_code=404, detail="No file attached to this submission")

            # Clean the file URL
            file_url = submission["file_url"]
            if '?' in file_url:
                file_url = file_url.split('?')[0]

            return {
                "success": True,
                "download_url": file_url,
                "file_name": f"submission_{file_id}.pdf",
                "file_type": "submission"
            }

        elif file_type == "material":
            # Get material details
            material_response = supabase.table("course_materials").select("*").eq("id", file_id).single().execute()
            if not material_response.data:
                raise HTTPException(status_code=404, detail="Course material not found")

            material = material_response.data

            # Check permissions
            if current_user.role == "teacher":
                course_response = supabase.table("courses").select("teacher_id").eq("id", material["course_id"]).single().execute()
                if not course_response.data or course_response.data["teacher_id"] != current_user.user_id:
                    raise HTTPException(status_code=403, detail="Permission denied")
            elif current_user.role == "student":
                enrollment_response = supabase.table("enrollments").select("*").eq("student_id", current_user.user_id).eq("course_id", material["course_id"]).eq("status", "active").execute()
                if not enrollment_response.data:
                    raise HTTPException(status_code=403, detail="Not enrolled in this course")
            else:
                raise HTTPException(status_code=403, detail="Permission denied")

            if not material["file_url"]:
                raise HTTPException(status_code=404, detail="No file attached to this material")

            # Clean the file URL
            file_url = material["file_url"]
            if '?' in file_url:
                file_url = file_url.split('?')[0]

            return {
                "success": True,
                "download_url": file_url,
                "file_name": material["file_name"],
                "file_type": "material"
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid file type")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get download URL: {str(e)}")
