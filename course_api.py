from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from datetime import datetime
from supabase_storage import get_storage_manager
import uuid

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
    thumbnail_url: Optional[str] = None
    created_at: str
    updated_at: str

@router.post("", response_model=Dict[str, Any])
async def create_course(course: CourseCreate):
    """Create a new course (without thumbnail)"""
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

@router.post("/with-thumbnail", response_model=Dict[str, Any])
async def create_course_with_thumbnail(
    teacher_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    code: str = Form(...),
    status: str = Form("active"),
    thumbnail: Optional[UploadFile] = File(None)
):
    """Create a new course with optional thumbnail"""
    try:
        print(f"Creating course with thumbnail: {title}")

        thumbnail_url = None

        # Upload thumbnail to S3 if provided
        if thumbnail:
            try:
                # Validate file type
                if not thumbnail.content_type.startswith('image/'):
                    raise HTTPException(status_code=400, detail="Thumbnail must be an image file")

                # Validate file size (max 5MB)
                content = await thumbnail.read()
                if len(content) > 5 * 1024 * 1024:
                    raise HTTPException(status_code=400, detail="Thumbnail file size must be less than 5MB")

                # Reset file pointer
                await thumbnail.seek(0)

                # Generate unique filename
                file_extension = thumbnail.filename.split('.')[-1] if '.' in thumbnail.filename else 'jpg'
                unique_filename = f"course-thumbnails/{uuid.uuid4()}.{file_extension}"

                # Upload to Supabase Storage
                storage_manager = get_storage_manager()
                thumbnail_result = await storage_manager.upload_course_thumbnail(thumbnail)

                # Extract the URL from the result
                thumbnail_url = thumbnail_result['file_url']
                print(f"Thumbnail uploaded successfully: {thumbnail_url}")

            except Exception as upload_error:
                print(f"Error uploading thumbnail: {upload_error}")
                # Continue without thumbnail if upload fails
                thumbnail_url = None

        # Insert course into database
        course_data = {
            'teacher_id': teacher_id,
            'title': title,
            'description': description,
            'code': code,
            'status': status,
            'thumbnail_url': thumbnail_url,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }

        response = supabase.table('courses').insert(course_data).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data[0],
                "message": "Course created successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create course")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating course with thumbnail: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Student course endpoints (put specific routes before parameterized ones)
@router.get("/all", response_model=Dict[str, Any])
async def get_all_courses():
    """Get all active courses for course discovery (student view)"""
    try:
        # Get all active courses with teacher information
        response = supabase.table('courses').select("""
            *,
            profiles!courses_teacher_id_fkey(full_name)
        """).eq('status', 'active').order('created_at', desc=True).execute()

        # Add enrollment count for each course using optimized query
        courses_with_stats = []
        for course in response.data:
            # Get enrollment count with proper count query
            enrollment_response = supabase.table('enrollments').select('*', count='exact').eq('course_id', course['id']).eq('status', 'active').execute()
            enrollment_count = len(enrollment_response.data) if enrollment_response.data else 0

            course_data = {
                **course,
                'teacher_name': course.get('profiles', {}).get('full_name', 'Unknown Teacher'),
                'enrollment_count': enrollment_count
            }
            courses_with_stats.append(course_data)

        return {
            "success": True,
            "data": courses_with_stats,
            "message": f"Found {len(courses_with_stats)} active courses"
        }

    except Exception as e:
        print(f"Error fetching all courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/enrolled", response_model=Dict[str, Any])
async def get_student_enrolled_courses(student_id: str):
    """Get all courses a student is enrolled in"""
    try:
        # Get enrollments with course and teacher information
        response = supabase.table('enrollments').select("""
            *,
            courses(
                *,
                profiles!courses_teacher_id_fkey(full_name)
            )
        """).eq('student_id', student_id).eq('status', 'active').order('enrolled_at', desc=True).execute()

        # Format the response
        enrolled_courses = []
        for enrollment in response.data:
            course = enrollment.get('courses', {})
            if course:
                # Get progress data for this course
                progress_response = supabase.table('course_progress').select('*').eq('student_id', student_id).eq('course_id', enrollment['course_id']).execute()
                progress_data = progress_response.data[0] if progress_response.data else None

                course_data = {
                    'enrollment_id': enrollment['id'],
                    'student_id': enrollment['student_id'],
                    'course_id': enrollment['course_id'],
                    'enrolled_at': enrollment['enrolled_at'],
                    'progress': progress_data['overall_progress_percentage'] if progress_data else 0,
                    'is_completed': progress_data['is_completed'] if progress_data else False,
                    'materials_completed': progress_data['materials_completed'] if progress_data else 0,
                    'total_materials': progress_data['total_materials'] if progress_data else 0,
                    'status': enrollment['status'],
                    'course': {
                        **course,
                        'teacher_name': course.get('profiles', {}).get('full_name', 'Unknown Teacher')
                    }
                }
                enrolled_courses.append(course_data)

        return {
            "success": True,
            "data": enrolled_courses,
            "message": f"Found {len(enrolled_courses)} enrolled courses"
        }

    except Exception as e:
        print(f"Error fetching student enrolled courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/enrollment-status/{course_id}", response_model=Dict[str, Any])
async def check_enrollment_status(student_id: str, course_id: str):
    """Check if a student is enrolled in a specific course"""
    try:
        response = supabase.table('enrollments').select('*').eq('student_id', student_id).eq('course_id', course_id).execute()

        is_enrolled = len(response.data) > 0
        enrollment_data = response.data[0] if is_enrolled else None

        return {
            "success": True,
            "data": {
                "is_enrolled": is_enrolled,
                "enrollment": enrollment_data
            }
        }

    except Exception as e:
        print(f"Error checking enrollment status: {e}")
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

        # Debug: Print the first course to see what fields are available
        if response.data:
            print(f"Sample course data: {response.data[0]}")
            print(f"Available fields: {list(response.data[0].keys())}")

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:
        print(f"Error fetching teacher courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{course_id}/thumbnail", response_model=Dict[str, Any])
async def update_course_thumbnail(
    course_id: str,
    thumbnail: UploadFile = File(...)
):
    """Update course thumbnail"""
    try:
        print(f"Updating thumbnail for course: {course_id}")

        # Check if course exists
        course_response = supabase.table('courses').select('*').eq('id', course_id).execute()
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")

        # Validate file type
        if not thumbnail.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Thumbnail must be an image file")

        # Validate file size (max 5MB)
        content = await thumbnail.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Thumbnail file size must be less than 5MB")

        # Generate unique filename
        file_extension = thumbnail.filename.split('.')[-1] if '.' in thumbnail.filename else 'jpg'
        unique_filename = f"course-thumbnails/{uuid.uuid4()}.{file_extension}"

        # Upload to Supabase Storage
        storage_manager = get_storage_manager()
        thumbnail_result = await storage_manager.upload_course_thumbnail(thumbnail)

        # Extract the URL from the result
        thumbnail_url = thumbnail_result['file_url']

        # Update course in database
        update_response = supabase.table('courses').update({
            'thumbnail_url': thumbnail_url,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', course_id).execute()

        if update_response.data:
            return {
                "success": True,
                "data": update_response.data[0],
                "message": "Course thumbnail updated successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update course thumbnail")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating course thumbnail: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# Course Materials API is now handled by course_materials_routes.py
# This router has been removed to avoid conflicts
