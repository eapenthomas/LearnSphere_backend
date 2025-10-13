"""
Enhanced Course Materials API with Multiple File Upload Support
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import logging
from supabase import create_client, Client
from auth_middleware import get_current_user, get_current_teacher, TokenData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

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

class MultipleUploadResponse(BaseModel):
    success: bool
    message: str
    uploaded_files: List[CourseMaterialResponse]
    failed_files: List[Dict[str, str]]
    total_uploaded: int
    total_failed: int

class MaterialUpdateRequest(BaseModel):
    description: Optional[str] = None

# Helper functions
def get_file_size(file: UploadFile) -> int:
    """Get file size in bytes"""
    if hasattr(file, 'size'):
        return file.size
    return 0

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file_type(filename: str) -> bool:
    """Check if file type is allowed"""
    allowed_extensions = {
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.txt', '.md', '.jpg', '.jpeg', '.png', '.gif', '.mp4',
        '.mp3', '.wav', '.zip', '.rar', '.7z'
    }
    extension = get_file_extension(filename)
    return extension in allowed_extensions

def upload_file_to_supabase(file: UploadFile, course_id: str, folder: str = "materials") -> Dict[str, Any]:
    """Upload file to Supabase storage"""
    try:
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = f"{folder}/{course_id}/{filename}"
        
        # Read file content
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Upload to Supabase storage
        result = supabase.storage.from_("course-materials").upload(
            file_path,
            file_content,
            file_options={"content-type": file.content_type or "application/octet-stream"}
        )
        
        if result.get('error'):
            raise Exception(f"Upload failed: {result['error']}")
        
        # Get public URL
        public_url = supabase.storage.from_("course-materials").get_public_url(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "public_url": public_url,
            "filename": filename
        }
        
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {e}")
        return {
            "success": False,
            "error": str(e),
            "filename": file.filename
        }

@router.post("/upload", response_model=CourseMaterialResponse)
async def upload_single_file(
    course_id: str = Form(...),
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_teacher)
):
    """Upload a single file to a course"""
    try:
        # Validate course ownership
        course_response = supabase.table("courses").select("*").eq("id", course_id).eq("teacher_id", current_user.user_id).single().execute()

        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found or you don't have permission to upload to this course")

        # Upload file to Supabase storage
        upload_result = upload_file_to_supabase(file, course_id)
        
        if not upload_result["success"]:
            raise HTTPException(status_code=500, detail=f"File upload failed: {upload_result['error']}")

        # Prepare material data
        material_data = {
            "course_id": course_id,
            "file_name": file.filename,
            "file_url": upload_result["public_url"],
            "file_size": upload_result["file_size"],
            "file_type": file.content_type,
            "uploaded_by": current_user.user_id,
            "description": description,
            "uploaded_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True
        }

        # Insert into database
        db_response = supabase.table("course_materials").insert(material_data).select().single().execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Failed to save file metadata to database")

        return CourseMaterialResponse(**db_response.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-multiple", response_model=MultipleUploadResponse)
async def upload_multiple_files(
    course_id: str = Form(...),
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_teacher)
):
    """Upload multiple files to a course"""
    try:
        # Validate course ownership
        course_response = supabase.table("courses").select("*").eq("id", course_id).eq("teacher_id", current_user.user_id).single().execute()
        
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found or you don't have permission")
        
        if len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Limit to 10 files at once
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed per upload")
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            try:
                # Validate file
                if not file.filename:
                    failed_files.append({"filename": "unknown", "error": "No filename provided"})
                    continue
                
                if not is_allowed_file_type(file.filename):
                    failed_files.append({"filename": file.filename, "error": "File type not allowed"})
                    continue
                
                # Check file size (limit to 50MB)
                file_size = get_file_size(file)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    failed_files.append({"filename": file.filename, "error": "File too large (max 50MB)"})
                    continue
                
                # Upload file
                upload_result = upload_file_to_supabase(file, course_id)
                
                if not upload_result["success"]:
                    failed_files.append({"filename": file.filename, "error": upload_result["error"]})
                    continue
                
                # Save to database
                material_data = {
                    "course_id": course_id,
                    "file_name": file.filename,
                    "file_url": upload_result["public_url"],
                    "file_size": file_size,
                    "file_type": get_file_extension(file.filename),
                    "uploaded_by": current_user.user_id,
                    "description": description or f"Uploaded file: {file.filename}",
                    "uploaded_at": "now()",
                    "updated_at": "now()"
                }
                
                db_response = supabase.table("course_materials").insert(material_data).execute()
                
                if db_response.data:
                    material = db_response.data[0]
                    
                    # Get uploader name
                    user_response = supabase.table("profiles").select("full_name").eq("id", current_user.user_id).single().execute()
                    uploader_name = user_response.data.get("full_name", "Unknown") if user_response.data else "Unknown"
                    
                    uploaded_files.append(CourseMaterialResponse(
                        id=material["id"],
                        course_id=material["course_id"],
                        file_name=material["file_name"],
                        file_url=material["file_url"],
                        file_size=material["file_size"],
                        file_type=material["file_type"],
                        uploaded_by=material["uploaded_by"],
                        uploaded_at=material["uploaded_at"],
                        updated_at=material["updated_at"],
                        description=material["description"],
                        uploader_name=uploader_name
                    ))
                else:
                    failed_files.append({"filename": file.filename, "error": "Failed to save to database"})
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                failed_files.append({"filename": file.filename, "error": str(e)})
        
        return MultipleUploadResponse(
            success=len(uploaded_files) > 0,
            message=f"Uploaded {len(uploaded_files)} files successfully, {len(failed_files)} failed",
            uploaded_files=uploaded_files,
            failed_files=failed_files,
            total_uploaded=len(uploaded_files),
            total_failed=len(failed_files)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/course/{course_id}", response_model=List[CourseMaterialResponse])
async def get_course_materials(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all materials for a course"""
    try:
        # Check if user is enrolled or is the teacher
        course_response = supabase.table("courses").select("teacher_id").eq("id", course_id).single().execute()
        
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Check permissions
        is_teacher = course_response.data["teacher_id"] == current_user.user_id
        is_enrolled = False
        
        if not is_teacher:
            enrollment_response = supabase.table("enrollments").select("id").eq("course_id", course_id).eq("student_id", current_user.user_id).execute()
            is_enrolled = len(enrollment_response.data) > 0
        
        if not is_teacher and not is_enrolled:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get materials
        materials_response = supabase.table("course_materials").select("""
            *,
            profiles!course_materials_uploaded_by_fkey(full_name)
        """).eq("course_id", course_id).order("uploaded_at", desc=True).execute()
        
        materials = []
        for material in materials_response.data or []:
            materials.append(CourseMaterialResponse(
                id=material["id"],
                course_id=material["course_id"],
                file_name=material["file_name"],
                file_url=material["file_url"],
                file_size=material["file_size"],
                file_type=material["file_type"],
                uploaded_by=material["uploaded_by"],
                uploaded_at=material["uploaded_at"],
                updated_at=material["updated_at"],
                description=material["description"],
                uploader_name=material["profiles"]["full_name"] if material.get("profiles") else "Unknown"
            ))
        
        return materials
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting materials: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get materials: {str(e)}")

@router.delete("/{material_id}")
async def delete_material(
    material_id: str,
    current_user: TokenData = Depends(get_current_teacher)
):
    """Delete a course material"""
    try:
        # Check if material exists and user has permission
        material_response = supabase.table("course_materials").select("""
            *,
            courses!inner(teacher_id)
        """).eq("id", material_id).single().execute()
        
        if not material_response.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material = material_response.data
        if material["courses"]["teacher_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Delete from storage
        try:
            file_path = material["file_url"].split("/")[-2] + "/" + material["file_url"].split("/")[-1]
            supabase.storage.from_("course-materials").remove([file_path])
        except Exception as e:
            logger.warning(f"Failed to delete file from storage: {e}")
        
        # Delete from database
        supabase.table("course_materials").delete().eq("id", material_id).execute()
        
        return {"success": True, "message": "Material deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting material: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete material: {str(e)}")

@router.put("/{material_id}")
async def update_material(
    material_id: str,
    request: MaterialUpdateRequest,
    current_user: TokenData = Depends(get_current_teacher)
):
    """Update material description"""
    try:
        # Check if material exists and user has permission
        material_response = supabase.table("course_materials").select("""
            *,
            courses!inner(teacher_id)
        """).eq("id", material_id).single().execute()
        
        if not material_response.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material = material_response.data
        if material["courses"]["teacher_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Update material
        update_data = {"updated_at": "now()"}
        if request.description is not None:
            update_data["description"] = request.description
        
        supabase.table("course_materials").update(update_data).eq("id", material_id).execute()
        
        return {"success": True, "message": "Material updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating material: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update material: {str(e)}")
