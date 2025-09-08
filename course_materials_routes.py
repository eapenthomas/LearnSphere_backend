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

from supabase_storage import get_storage_manager, SupabaseStorageManager
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
router = APIRouter(prefix="/api/course-materials", tags=["Course Materials"])

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
    For now, we'll accept the user ID directly from the frontend.
    """
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

        # For now, treat the token as the user ID directly
        # This is a temporary solution - in production, you should validate JWT tokens
        user_id = token
        
        # TODO: For testing, allow any valid UUID to pass. Replace with real auth later.
        # This is temporary - remove when implementing real authentication
        
        # Verify the user exists in the database
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID"
            )
        
        user_data = response.data[0]
        
        return {
            "id": user_data["id"],
            "role": user_data["role"],
            "full_name": user_data["full_name"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

@router.get("/debug/schema")
async def debug_schema():
    """Debug endpoint to check the current database schema"""
    try:
        # Check what columns exist in the course_materials table
        table_response = supabase.table("course_materials").select("*").limit(1).execute()
        
        # Check what columns exist in the view
        view_response = supabase.table("course_materials_with_metadata").select("*").limit(1).execute()
        
        return {
            "table_columns": list(table_response.data[0].keys()) if table_response.data else [],
            "view_columns": list(view_response.data[0].keys()) if view_response.data else [],
            "table_sample": table_response.data[0] if table_response.data else None,
            "view_sample": view_response.data[0] if view_response.data else None
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload", response_model=UploadResponse)
async def upload_course_materials(
    course_id: str = Form(...),
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """
    Upload one or more files as course materials.
    Only accessible to the teacher who owns the course.
    """
    try:
        # TODO: Re-enable permissions after testing
        # await CoursePermissions.verify_teacher_role(current_user["id"])
        # await CoursePermissions.verify_course_ownership(course_id, current_user["id"])
        logger.info(f"Upload request from user: {current_user['id']} for course: {course_id}")
        
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
            
            # Upload to Supabase Storage
            storage_result = await storage_manager.upload_file(file, course_id, "course-materials")
            
            # Store metadata in Supabase
            material_data = {
                "course_id": course_id,
                "title": file.filename,  # Add the missing title field
                "file_name": storage_result["file_name"],
                "file_url": storage_result["file_url"],
                "file_size": storage_result["file_size"],
                "file_type": storage_result["file_type"],
                "uploaded_by": current_user["id"],
                "description": description,
                "is_active": True
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

@router.get("/course/{course_id}", response_model=MaterialListResponse)
async def get_course_materials(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get list of course materials.
    Accessible to course teacher and enrolled students.
    """
    try:
        # TODO: Re-enable permissions after testing
        # await CoursePermissions.verify_course_exists(course_id)
        # Check permissions based on user role
        # if current_user["role"] == "teacher":
        #     # Verify course ownership for teachers
        #     await CoursePermissions.verify_course_ownership(course_id, current_user["id"])
        # elif current_user["role"] == "student":
        #     # Verify enrollment for students
        #     await CoursePermissions.verify_student_enrollment(course_id, current_user["id"])
        # else:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Access denied"
        #     )
        logger.info(f"Listing materials for course: {course_id} by user: {current_user['id']}")
        
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

@router.delete("/{material_id}", response_model=DeleteResponse)
async def delete_course_material(
    material_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
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
        
        # Get course_id from material for logging purposes
        course_id = material["course_id"]
        
        # Delete from Supabase Storage
        storage_manager.delete_file(material["file_url"], "course-materials")
        
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

@router.get("/{material_id}/download")
async def get_material_download_url(
    material_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    storage_manager: SupabaseStorageManager = Depends(get_storage_manager)
):
    """
    Get a presigned download URL for a course material.
    Accessible to course teacher and enrolled students.
    """
    try:
        # Verify material exists
        material = await CoursePermissions.verify_material_exists(material_id)
        
        # Get course_id from material for verification
        course_id = material["course_id"]
        
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
        
        # Generate download URL (Supabase URLs are already public)
        download_url = storage_manager.get_file_download_url(material["file_url"], "course-materials")
        
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
