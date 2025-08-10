"""
FastAPI routes for course materials management.
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging
from supabase import create_client, Client

from s3_utils import get_s3_manager, S3Manager
from course_permissions import CoursePermissions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/courses", tags=["Course Materials"])

# Pydantic models
class CourseMaterialResponse(BaseModel):
    id: str
    course_id: str
    file_name: str
    file_url: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    uploader_name: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    materials: List[CourseMaterialResponse]

class MaterialListResponse(BaseModel):
    success: bool
    materials: List[CourseMaterialResponse]
    total_count: int

class DeleteResponse(BaseModel):
    success: bool
    message: str

# Dependency to get current user
async def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    """
    Get current authenticated user from authorization header.
    Integrate this with your existing authentication system.
    """
    # TODO: Replace this with your actual authentication logic
    # Example integration with existing auth system:

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )

    try:
        # Extract token from "Bearer <token>" format
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization format"
            )

        token = authorization.split(" ")[1]

        # TODO: Validate token and get user info
        # This should integrate with your existing AuthService
        # Example:
        # user_data = await AuthService.verify_token(token)
        # return user_data

        # For now, return a mock user for testing
        # Remove this when implementing real authentication
        return {
            "id": "mock-user-id",
            "role": "teacher",
            "full_name": "Mock Teacher"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@router.post("/{course_id}/materials", response_model=UploadResponse)
async def upload_course_materials(
    course_id: str,
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    s3_manager: S3Manager = Depends(get_s3_manager)
):
    """
    Upload one or more files as course materials.
    Only accessible to the teacher who owns the course.
    """
    try:
        # Verify user is a teacher
        await CoursePermissions.verify_teacher_role(current_user["id"])
        
        # Verify course ownership
        await CoursePermissions.verify_course_ownership(course_id, current_user["id"])
        
        # Validate files
        if not files or len(files) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        # Limit number of files per upload
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per upload"
            )
        
        uploaded_materials = []
        
        for file in files:
            # Validate file
            if not file.filename:
                continue
            
            # Upload to S3
            s3_result = await s3_manager.upload_file(file, course_id)
            
            # Store metadata in Supabase
            material_data = {
                "course_id": course_id,
                "file_name": s3_result["file_name"],
                "file_url": s3_result["file_url"],
                "file_size": s3_result["file_size"],
                "file_type": s3_result["file_type"],
                "uploaded_by": current_user["id"],
                "description": description
            }
            
            response = supabase.table("course_materials").insert(material_data).execute()
            
            if response.data:
                material = response.data[0]
                material["uploader_name"] = current_user["full_name"]
                uploaded_materials.append(CourseMaterialResponse(**material))
        
        if not uploaded_materials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid files were uploaded"
            )
        
        logger.info(f"Successfully uploaded {len(uploaded_materials)} materials for course {course_id}")
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {len(uploaded_materials)} file(s)",
            materials=uploaded_materials
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading course materials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload course materials: {str(e)}"
        )

@router.get("/{course_id}/materials", response_model=MaterialListResponse)
async def get_course_materials(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of course materials.
    Accessible to course teacher and enrolled students.
    """
    try:
        # Verify course exists
        await CoursePermissions.verify_course_exists(course_id)
        
        # Check permissions based on user role
        if current_user["role"] == "teacher":
            # Verify course ownership for teachers
            await CoursePermissions.verify_course_ownership(course_id, current_user["id"])
        elif current_user["role"] == "student":
            # Verify enrollment for students
            await CoursePermissions.verify_student_enrollment(course_id, current_user["id"])
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get materials from database with uploader info
        response = supabase.table("course_materials_with_metadata").select("*").eq("course_id", course_id).eq("is_active", True).order("uploaded_at", desc=True).execute()
        
        materials = []
        if response.data:
            for material in response.data:
                materials.append(CourseMaterialResponse(**material))
        
        logger.info(f"Retrieved {len(materials)} materials for course {course_id}")
        
        return MaterialListResponse(
            success=True,
            materials=materials,
            total_count=len(materials)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving course materials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve course materials: {str(e)}"
        )

@router.delete("/{course_id}/materials/{material_id}", response_model=DeleteResponse)
async def delete_course_material(
    course_id: str,
    material_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    s3_manager: S3Manager = Depends(get_s3_manager)
):
    """
    Delete a course material.
    Only accessible to the teacher who owns the course.
    """
    try:
        # Verify user is a teacher
        await CoursePermissions.verify_teacher_role(current_user["id"])
        
        # Verify material ownership (this also verifies course ownership)
        material = await CoursePermissions.verify_material_ownership(material_id, current_user["id"])
        
        # Verify course_id matches
        if material["course_id"] != course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Material does not belong to the specified course"
            )
        
        # Delete from S3
        s3_manager.delete_file(material["file_url"])
        
        # Soft delete from database (set is_active to false)
        supabase.table("course_materials").update({"is_active": False}).eq("id", material_id).execute()
        
        logger.info(f"Successfully deleted material {material_id} from course {course_id}")
        
        return DeleteResponse(
            success=True,
            message="Course material deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting course material: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete course material: {str(e)}"
        )

@router.get("/{course_id}/materials/{material_id}/download")
async def get_material_download_url(
    course_id: str,
    material_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    s3_manager: S3Manager = Depends(get_s3_manager)
):
    """
    Get a presigned download URL for a course material.
    Accessible to course teacher and enrolled students.
    """
    try:
        # Verify material exists
        material = await CoursePermissions.verify_material_exists(material_id)
        
        # Verify course_id matches
        if material["course_id"] != course_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Material does not belong to the specified course"
            )
        
        # Check permissions based on user role
        if current_user["role"] == "teacher":
            # Verify course ownership for teachers
            await CoursePermissions.verify_course_ownership(course_id, current_user["id"])
        elif current_user["role"] == "student":
            # Verify enrollment for students
            await CoursePermissions.verify_student_enrollment(course_id, current_user["id"])
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Generate presigned URL (valid for 1 hour)
        download_url = s3_manager.generate_presigned_url(material["file_url"], expiration=3600)
        
        return {
            "success": True,
            "download_url": download_url,
            "file_name": material["file_name"],
            "expires_in": 3600
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate download URL: {str(e)}"
        )
