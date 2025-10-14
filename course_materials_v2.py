"""
Course Materials API v2 - Complete Rewrite
Handles file upload, fetching, and progress tracking for course materials.
"""

import os
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from supabase import create_client
from auth_middleware import get_current_user, get_current_teacher, TokenData

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(supabase_url, supabase_key)

router = APIRouter(prefix="/api/course-materials", tags=["course-materials"])

# Pydantic models
class CourseMaterialResponse(BaseModel):
    id: str
    course_id: str
    title: str
    description: Optional[str]
    file_name: str
    file_url: str
    file_size: int
    file_type: str
    uploaded_by: str
    uploaded_at: str
    updated_at: str
    is_active: bool
    uploader_name: str
    download_count: int = 0
    view_count: int = 0
    
    class Config:
        from_attributes = True

class MaterialProgressResponse(BaseModel):
    material_id: str
    course_id: str
    total_materials: int
    completed_materials: int
    progress_percentage: float
    
    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    success: bool
    message: str
    material: Optional[CourseMaterialResponse] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True

class MaterialsListResponse(BaseModel):
    success: bool
    materials: List[CourseMaterialResponse]
    total_count: int
    progress: Optional[MaterialProgressResponse] = None
    
    class Config:
        from_attributes = True

# Utility functions
def get_file_size(file: UploadFile) -> int:
    """Get file size in bytes"""
    try:
        current_position = file.file.tell()
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(current_position)  # Reset position
        return file_size
    except Exception:
        try:
            file.file.seek(0)
            content = file.file.read()
            file.file.seek(0)
            return len(content)
        except Exception:
            return 0

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()

def upload_file_to_supabase(file: UploadFile, course_id: str) -> Dict[str, Any]:
    """Upload file to Supabase Storage"""
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = get_file_extension(file.filename)
        unique_filename = f"{timestamp}_{file.filename}"
        
        # Upload to Supabase Storage
        result = supabase.storage.from_("course-materials").upload(
            f"materials/{course_id}/{unique_filename}",
            file.file.read(),
            {"content-type": file.content_type}
        )
        
        if hasattr(result, 'error') and result.error:
            return {"success": False, "error": str(result.error)}
        
        # Get public URL
        public_url = supabase.storage.from_("course-materials").get_public_url(
            f"materials/{course_id}/{unique_filename}"
        )
        
        return {
            "success": True,
            "public_url": public_url,
            "file_path": f"materials/{course_id}/{unique_filename}"
        }
        
    except Exception as e:
        logger.error(f"Error uploading file to Supabase: {e}")
        return {"success": False, "error": str(e)}

def validate_course_ownership(course_id: str, teacher_id: str) -> bool:
    """Validate that teacher owns the course"""
    try:
        result = supabase.table("courses").select("id").eq("id", course_id).eq("teacher_id", teacher_id).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error validating course ownership: {e}")
        return False

def validate_student_enrollment(course_id: str, student_id: str) -> bool:
    """Validate that student is enrolled in the course"""
    try:
        result = supabase.table("enrollments").select("id").eq("course_id", course_id).eq("student_id", student_id).eq("status", "active").execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Error validating student enrollment: {e}")
        return False

def get_material_stats(material_id: str) -> Dict[str, int]:
    """Get download and view counts for a material"""
    try:
        view_result = supabase.table("material_progress").select("id").eq("material_id", material_id).eq("action_type", "view").execute()
        download_result = supabase.table("material_progress").select("id").eq("material_id", material_id).eq("action_type", "download").execute()
        
        return {
            "view_count": len(view_result.data),
            "download_count": len(download_result.data)
        }
    except Exception as e:
        logger.error(f"Error getting material stats: {e}")
        return {"view_count": 0, "download_count": 0}

def track_material_action(student_id: str, material_id: str, course_id: str, action_type: str):
    """Track material view/download for progress"""
    try:
        # Check if already tracked (to avoid duplicates)
        existing = supabase.table("material_progress").select("id").eq("student_id", student_id).eq("material_id", material_id).eq("action_type", action_type).execute()
        
        if len(existing.data) == 0:
            supabase.table("material_progress").insert({
                "student_id": student_id,
                "material_id": material_id,
                "course_id": course_id,
                "action_type": action_type
            }).execute()
            
            # Update course progress
            update_course_progress(student_id, course_id)
            
    except Exception as e:
        logger.error(f"Error tracking material action: {e}")

def update_course_progress(student_id: str, course_id: str):
    """Update student's course progress based on completed materials"""
    try:
        # Get total materials for the course
        total_materials_result = supabase.table("course_materials").select("id").eq("course_id", course_id).eq("is_active", True).execute()
        total_materials = len(total_materials_result.data)
        
        if total_materials == 0:
            return
        
        # Get completed materials (viewed or downloaded)
        completed_materials_result = supabase.table("material_progress").select("material_id").eq("student_id", student_id).eq("course_id", course_id).execute()
        completed_materials = len(set([item["material_id"] for item in completed_materials_result.data]))
        
        # Calculate progress percentage
        progress_percentage = int((completed_materials / total_materials) * 100)
        
        # Update enrollment progress
        supabase.table("enrollments").update({
            "progress": progress_percentage,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("student_id", student_id).eq("course_id", course_id).execute()
        
    except Exception as e:
        logger.error(f"Error updating course progress: {e}")

# API Endpoints

@router.post("/upload", response_model=UploadResponse)
async def upload_course_material(
    course_id: str = Form(...),
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_teacher)
):
    """Upload a single file to a course (Teachers only)"""
    try:
        logger.info(f"Upload request from teacher {current_user.user_id} for course {course_id}")
        
        # Validate course ownership
        if not validate_course_ownership(course_id, current_user.user_id):
            raise HTTPException(status_code=403, detail="You don't have permission to upload to this course")
        
        # Validate file
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (50MB limit)
        file_size = get_file_size(file)
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=413, detail="File too large (max 50MB)")
        
        # Upload file to Supabase Storage
        upload_result = upload_file_to_supabase(file, course_id)
        if not upload_result["success"]:
            raise HTTPException(status_code=500, detail=f"File upload failed: {upload_result['error']}")
        
        # Prepare material data
        material_data = {
            "course_id": course_id,
            "title": title or file.filename,
            "description": description or f"Uploaded file: {file.filename}",
            "file_name": file.filename,
            "file_url": upload_result["public_url"],
            "file_size": file_size,
            "file_type": file.content_type,
            "uploaded_by": current_user.user_id,
            "uploaded_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Save to database
        db_result = supabase.table("course_materials").insert(material_data).execute()
        if not db_result.data:
            raise HTTPException(status_code=500, detail="Failed to save material to database")
        
        # Get uploader name
        try:
            user_result = supabase.table("profiles").select("full_name").eq("id", current_user.user_id).execute()
            uploader_name = user_result.data[0]["full_name"] if user_result.data else "Unknown"
        except Exception:
            uploader_name = "Unknown"
        
        # Create response
        material = CourseMaterialResponse(
            id=db_result.data[0]["id"],
            course_id=course_id,
            title=material_data["title"],
            description=material_data["description"],
            file_name=file.filename,
            file_url=upload_result["public_url"],
            file_size=file_size,
            file_type=file.content_type,
            uploaded_by=current_user.user_id,
            uploaded_at=material_data["uploaded_at"],
            updated_at=material_data["updated_at"],
            is_active=True,
            uploader_name=uploader_name
        )
        
        logger.info(f"Successfully uploaded material {material.id} for course {course_id}")
        
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            material=material
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading material: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/course/{course_id}", response_model=MaterialsListResponse)
async def get_course_materials(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all materials for a course (Teachers and enrolled students)"""
    try:
        logger.info(f"Fetching materials for course {course_id} by user {current_user.user_id}")
        
        # Check if user is teacher or enrolled student
        is_teacher = False
        is_student = False
        
        # Check if user is the teacher
        try:
            course_result = supabase.table("courses").select("teacher_id").eq("id", course_id).execute()
            if course_result.data and course_result.data[0]["teacher_id"] == current_user.user_id:
                is_teacher = True
        except Exception as e:
            logger.error(f"Error checking teacher status: {e}")
        
        # Check if user is enrolled student
        if not is_teacher:
            is_student = validate_student_enrollment(course_id, current_user.user_id)
        
        if not is_teacher and not is_student:
            raise HTTPException(status_code=403, detail="Access denied. You must be the teacher or an enrolled student.")
        
        # Get materials
        materials_result = supabase.table("course_materials").select("""
            *,
            profiles!uploaded_by(full_name)
        """).eq("course_id", course_id).eq("is_active", True).order("uploaded_at", desc=True).execute()
        
        materials = []
        for material in materials_result.data or []:
            # Get stats
            stats = get_material_stats(material["id"])
            
            materials.append(CourseMaterialResponse(
                id=material["id"],
                course_id=material["course_id"],
                title=material["title"],
                description=material["description"],
                file_name=material["file_name"],
                file_url=material["file_url"],
                file_size=material["file_size"],
                file_type=material["file_type"],
                uploaded_by=material["uploaded_by"],
                uploaded_at=material["uploaded_at"],
                updated_at=material["updated_at"],
                is_active=material["is_active"],
                uploader_name=material["profiles"]["full_name"] if material.get("profiles") else "Unknown",
                download_count=stats["download_count"],
                view_count=stats["view_count"]
            ))
        
        # Get progress for students
        progress = None
        if is_student:
            try:
                total_materials = len(materials)
                completed_materials_result = supabase.table("material_progress").select("material_id").eq("student_id", current_user.user_id).eq("course_id", course_id).execute()
                completed_materials = len(set([item["material_id"] for item in completed_materials_result.data]))
                progress_percentage = int((completed_materials / total_materials) * 100) if total_materials > 0 else 0
                
                progress = MaterialProgressResponse(
                    material_id="",
                    course_id=course_id,
                    total_materials=total_materials,
                    completed_materials=completed_materials,
                    progress_percentage=progress_percentage
                )
            except Exception as e:
                logger.error(f"Error getting progress: {e}")
        
        logger.info(f"Successfully fetched {len(materials)} materials for course {course_id}")
        
        return MaterialsListResponse(
            success=True,
            materials=materials,
            total_count=len(materials),
            progress=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching materials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch materials: {str(e)}")

@router.post("/track-view/{material_id}")
async def track_material_view(
    material_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Track material view for progress (Students only)"""
    try:
        # Get material and course info
        material_result = supabase.table("course_materials").select("course_id").eq("id", material_id).execute()
        if not material_result.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        course_id = material_result.data[0]["course_id"]
        
        # Validate student enrollment
        if not validate_student_enrollment(course_id, current_user.user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Track view
        track_material_action(current_user.user_id, material_id, course_id, "view")
        
        return {"success": True, "message": "View tracked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking view: {e}")
        raise HTTPException(status_code=500, detail="Failed to track view")

@router.post("/track-download/{material_id}")
async def track_material_download(
    material_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Track material download for progress (Students only)"""
    try:
        # Get material and course info
        material_result = supabase.table("course_materials").select("course_id").eq("id", material_id).execute()
        if not material_result.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        course_id = material_result.data[0]["course_id"]
        
        # Validate student enrollment
        if not validate_student_enrollment(course_id, current_user.user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Track download
        track_material_action(current_user.user_id, material_id, course_id, "download")
        
        return {"success": True, "message": "Download tracked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking download: {e}")
        raise HTTPException(status_code=500, detail="Failed to track download")

@router.get("/download/{material_id}")
async def download_material(
    material_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Download course material (Teachers and enrolled students)"""
    try:
        # Get material info
        material_result = supabase.table("course_materials").select("""
            *,
            courses!inner(teacher_id)
        """).eq("id", material_id).execute()
        
        if not material_result.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material = material_result.data[0]
        course_id = material["course_id"]
        teacher_id = material["courses"]["teacher_id"]
        
        # Check permissions
        is_teacher = teacher_id == current_user.user_id
        is_student = validate_student_enrollment(course_id, current_user.user_id)
        
        if not is_teacher and not is_student:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Track download for students
        if is_student:
            track_material_action(current_user.user_id, material_id, course_id, "download")
        
        # Extract file path from URL
        file_url = material["file_url"]
        file_path = file_url.split("/storage/v1/object/public/course-materials/")[-1]
        
        # Download file from Supabase Storage
        file_data = supabase.storage.from_("course-materials").download(file_path)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        # Return file as streaming response
        return StreamingResponse(
            iter([file_data]),
            media_type=material["file_type"],
            headers={
                "Content-Disposition": f'attachment; filename="{material["file_name"]}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading material: {e}")
        raise HTTPException(status_code=500, detail="Download failed")

@router.delete("/{material_id}")
async def delete_material(
    material_id: str,
    current_user: TokenData = Depends(get_current_teacher)
):
    """Delete a course material (Teachers only)"""
    try:
        # Get material info
        material_result = supabase.table("course_materials").select("""
            *,
            courses!inner(teacher_id)
        """).eq("id", material_id).execute()
        
        if not material_result.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material = material_result.data[0]
        if material["courses"]["teacher_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete from storage
        try:
            file_url = material["file_url"]
            file_path = file_url.split("/storage/v1/object/public/course-materials/")[-1]
            supabase.storage.from_("course-materials").remove([file_path])
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {e}")
        
        # Delete from database
        supabase.table("course_materials").delete().eq("id", material_id).execute()
        
        # Delete related progress records
        supabase.table("material_progress").delete().eq("material_id", material_id).execute()
        
        return {"success": True, "message": "Material deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting material: {e}")
        raise HTTPException(status_code=500, detail="Delete failed")

# CORS handling
@router.options("/{path:path}")
async def options_handler(path: str):
    """Handle CORS preflight requests"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true"
        }
    )
