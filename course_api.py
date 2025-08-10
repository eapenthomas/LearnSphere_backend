from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/courses", tags=["courses"])

# Pydantic models
class CourseCreate(BaseModel):
    teacher_id: str
    title: str
    description: Optional[str] = ""
    code: str
    status: Optional[str] = "active"

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class CourseResponse(BaseModel):
    id: str
    teacher_id: str
    title: str
    description: Optional[str]
    code: str
    status: str
    created_at: str
    updated_at: str

@router.post("", response_model=Dict[str, Any])
async def create_course(course: CourseCreate):
    """Create a new course"""
    try:
        print(f"Creating course: {course.dict()}")
        
        # Insert course into database
        response = supabase.table('courses').insert({
            'teacher_id': course.teacher_id,
            'title': course.title,
            'description': course.description,
            'code': course.code,
            'status': course.status,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Course created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create course")

    except Exception as e:
        print(f"Error creating course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{course_id}", response_model=Dict[str, Any])
async def get_course(course_id: str):
    """Get a specific course by ID"""
    try:
        response = supabase.table('courses').select('*').eq('id', course_id).execute()
        
        if response.data:
            return {
                "success": True,
                "data": response.data[0]
            }
        else:
            raise HTTPException(status_code=404, detail="Course not found")

    except Exception as e:
        print(f"Error fetching course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{course_id}", response_model=Dict[str, Any])
async def update_course(course_id: str, course_update: CourseUpdate):
    """Update a course"""
    try:
        print(f"Updating course {course_id} with: {course_update.dict()}")
        
        # Prepare update data (only include non-None values)
        update_data = {k: v for k, v in course_update.dict().items() if v is not None}
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        response = supabase.table('courses').update(update_data).eq('id', course_id).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Course updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Course not found")

    except Exception as e:
        print(f"Error updating course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{course_id}", response_model=Dict[str, Any])
async def delete_course(course_id: str):
    """Delete a course"""
    try:
        print(f"Deleting course: {course_id}")
        
        # First check if course exists
        check_response = supabase.table('courses').select('id').eq('id', course_id).execute()
        if not check_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Delete the course
        response = supabase.table('courses').delete().eq('id', course_id).execute()
        
        return {
            "success": True,
            "message": "Course deleted successfully"
        }

    except Exception as e:
        print(f"Error deleting course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/{teacher_id}", response_model=Dict[str, Any])
async def get_teacher_courses(teacher_id: str):
    """Get all courses for a specific teacher"""
    try:
        response = supabase.table('courses').select('*').eq('teacher_id', teacher_id).order('created_at', desc=True).execute()

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:
        print(f"Error fetching teacher courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Course Materials API (simplified)
course_materials_router = APIRouter(prefix="/api/course-materials", tags=["course-materials"])

class MaterialCreate(BaseModel):
    course_id: str
    title: str
    description: Optional[str] = ""
    file_url: str
    file_size: Optional[int] = 0

@course_materials_router.get("/course/{course_id}", response_model=Dict[str, Any])
async def get_course_materials(course_id: str):
    """Get all materials for a course"""
    try:
        response = supabase.table('course_materials').select('*').eq('course_id', course_id).order('created_at', desc=True).execute()

        return {
            "success": True,
            "data": response.data or []
        }

    except Exception as e:
        print(f"Error fetching course materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@course_materials_router.post("/upload", response_model=Dict[str, Any])
async def upload_material(
    course_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):
    """Upload a course material (simplified - stores file info only)"""
    try:
        # For now, just store the file info without actual S3 upload
        # In production, you would upload to S3 here

        material_data = {
            'course_id': course_id,
            'title': title,
            'description': description,
            'file_name': file.filename,
            'file_url': f"https://example.com/files/{file.filename}",  # Placeholder URL
            'file_size': 0,  # Would get actual size from uploaded file
            'file_type': file.content_type,
            'created_at': datetime.utcnow().isoformat()
        }

        response = supabase.table('course_materials').insert(material_data).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Material uploaded successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to upload material")

    except Exception as e:
        print(f"Error uploading material: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@course_materials_router.delete("/{material_id}", response_model=Dict[str, Any])
async def delete_material(material_id: str):
    """Delete a course material"""
    try:
        response = supabase.table('course_materials').delete().eq('id', material_id).execute()

        return {
            "success": True,
            "message": "Material deleted successfully"
        }

    except Exception as e:
        print(f"Error deleting material: {e}")
        raise HTTPException(status_code=500, detail=str(e))
