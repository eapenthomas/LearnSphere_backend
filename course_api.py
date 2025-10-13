from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from datetime import datetime
from supabase_storage import get_storage_manager
import uuid
from auth_middleware import get_current_teacher, TokenData

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
        # Get all active courses first
        courses_response = supabase.table('courses').select('*').eq('status', 'active').order('created_at', desc=True).execute()
        
        if not courses_response.data:
            return {
                "success": True,
                "data": [],
                "message": "No active courses found"
            }
        
        # Batch fetch teacher names for all courses
        teacher_ids = list(set(course['teacher_id'] for course in courses_response.data if course.get('teacher_id')))
        teacher_names = {}
        if teacher_ids:
            teachers_response = supabase.table('profiles').select('id, full_name').in_('id', teacher_ids).execute()
            teacher_names = {teacher['id']: teacher['full_name'] for teacher in teachers_response.data or []}
        
        # Batch fetch enrollment counts for all courses using optimized query
        course_ids = [course['id'] for course in courses_response.data]
        enrollment_counts = {}
        if course_ids:
            # Use optimized query with proper indexing
            try:
                # Get enrollment counts grouped by course_id
                enrollments_response = supabase.table('enrollments').select('course_id').eq('status', 'active').in_('course_id', course_ids).execute()
                
                # Count enrollments per course efficiently
                for enrollment in enrollments_response.data or []:
                    course_id = enrollment['course_id']
                    enrollment_counts[course_id] = enrollment_counts.get(course_id, 0) + 1
                    
            except Exception as e:
                print(f"Error fetching enrollment counts: {e}")
                # Initialize all courses with 0 enrollments
                for course_id in course_ids:
                    enrollment_counts[course_id] = 0

        # Process each course with optimized data
        courses_with_stats = []
        for course in courses_response.data:
            course_data = {
                **course,
                'teacher_name': teacher_names.get(course.get('teacher_id'), 'Unknown Teacher'),
                'enrollment_count': enrollment_counts.get(course['id'], 0)
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
        print(f"Fetching enrolled courses for student: {student_id}")
        
        # Get enrollments first
        enrollments_response = supabase.table('enrollments').select('*').eq('student_id', student_id).eq('status', 'active').order('enrolled_at', desc=True).execute()

        print(f"Found {len(enrollments_response.data)} enrollments")

        if not enrollments_response.data:
            return {
                "success": True,
                "data": [],
                "message": "No enrolled courses found"
            }

        # Batch fetch course details
        course_ids = [enrollment['course_id'] for enrollment in enrollments_response.data]
        courses_response = supabase.table('courses').select('*').in_('id', course_ids).execute()
        courses_data = {course['id']: course for course in courses_response.data or []}
        
        # Batch fetch teacher names
        teacher_ids = list(set(course['teacher_id'] for course in courses_data.values() if course.get('teacher_id')))
        teacher_names = {}
        if teacher_ids:
            teachers_response = supabase.table('profiles').select('id, full_name').in_('id', teacher_ids).execute()
            teacher_names = {teacher['id']: teacher['full_name'] for teacher in teachers_response.data or []}

        # Get enrollment counts for each course
        enrollment_counts = {}
        if course_ids:
            try:
                # Get enrollment counts grouped by course_id
                enrollments_count_response = supabase.table('enrollments').select('course_id').eq('status', 'active').in_('course_id', course_ids).execute()
                
                # Count enrollments per course efficiently
                for enrollment in enrollments_count_response.data or []:
                    course_id = enrollment['course_id']
                    enrollment_counts[course_id] = enrollment_counts.get(course_id, 0) + 1
                    
                print(f"DEBUG: Enrollment counts calculated: {enrollment_counts}")
                    
            except Exception as e:
                print(f"Error fetching enrollment counts: {e}")
                # Initialize all courses with 0 enrollments
                for course_id in course_ids:
                    enrollment_counts[course_id] = 0

        # Format the response
        enrolled_courses = []
        for enrollment in enrollments_response.data:
            course = courses_data.get(enrollment['course_id'])
            if not course:
                continue
                
            # Get progress data for this course
            progress_response = supabase.table('course_progress').select('*').eq('student_id', student_id).eq('course_id', enrollment['course_id']).execute()
            progress_data = progress_response.data[0] if progress_response.data else None

            # Get payment info if exists
            payment = None
            if enrollment.get('payment_id'):
                payment_response = supabase.table('payments').select('status, amount').eq('id', enrollment['payment_id']).execute()
                payment = payment_response.data[0] if payment_response.data else None
                
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
                'enrollment_type': enrollment.get('enrollment_type', 'free'),
                'payment_status': payment.get('status') if payment else None,
                'course': {
                    **course,
                    'teacher_name': teacher_names.get(course.get('teacher_id'), 'Unknown Teacher'),
                    'enrollment_count': enrollment_counts.get(course['id'], 0)
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
        response = supabase.table('enrollments').select("""
            *,
            payments!enrollments_payment_id_fkey(
                status,
                amount
            )
        """).eq('student_id', student_id).eq('course_id', course_id).eq('status', 'active').execute()

        is_enrolled = len(response.data) > 0
        enrollment_data = response.data[0] if is_enrolled else None

        # Add payment info to enrollment if exists
        if enrollment_data and enrollment_data.get('payments'):
            enrollment_data['payment_status'] = enrollment_data['payments']['status']
            enrollment_data['payment_amount'] = enrollment_data['payments']['amount']

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

@router.get("/teacher", response_model=Dict[str, Any])
async def get_current_teacher_courses(current_user: TokenData = Depends(get_current_teacher)):
    """Get all courses for the current teacher with enrollment counts"""
    try:
        # Get teacher's courses
        courses_response = supabase.table('courses').select('*').eq('teacher_id', current_user.user_id).order('created_at', desc=True).execute()
        
        if not courses_response.data:
            return {
                "success": True,
                "data": [],
                "message": "No courses found for this teacher"
            }

        # Get enrollment counts for each course
        course_ids = [course['id'] for course in courses_response.data]
        enrollment_counts = {}
        
        for course_id in course_ids:
            enrollments = supabase.table('enrollments').select('id').eq('course_id', course_id).eq('status', 'active').execute()
            enrollment_counts[course_id] = len(enrollments.data) if enrollments.data else 0

        # Add enrollment counts to courses
        for course in courses_response.data:
            course['enrollment_count'] = enrollment_counts.get(course['id'], 0)

        return {
            "success": True,
            "data": courses_response.data,
            "message": f"Found {len(courses_response.data)} courses"
        }

    except Exception as e:
        print(f"Error fetching teacher courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/{teacher_id}", response_model=Dict[str, Any])
async def get_teacher_courses(teacher_id: str):
    """Get all courses for a specific teacher with enrollment counts"""
    try:
        # Get teacher's courses
        courses_response = supabase.table('courses').select('*').eq('teacher_id', teacher_id).order('created_at', desc=True).execute()
        
        if not courses_response.data:
            return {
                "success": True,
                "data": [],
                "message": "No courses found for this teacher"
            }

        # Get enrollment counts for each course
        course_ids = [course['id'] for course in courses_response.data]
        enrollment_counts = {}
        
        if course_ids:
            try:
                # Get enrollment counts grouped by course_id
                enrollments_response = supabase.table('enrollments').select('course_id').eq('status', 'active').in_('course_id', course_ids).execute()
                
                # Count enrollments per course efficiently
                for enrollment in enrollments_response.data or []:
                    course_id = enrollment['course_id']
                    enrollment_counts[course_id] = enrollment_counts.get(course_id, 0) + 1
                    
            except Exception as e:
                print(f"Error fetching enrollment counts: {e}")
                # Initialize all courses with 0 enrollments
                for course_id in course_ids:
                    enrollment_counts[course_id] = 0

        # Add enrollment counts to course data
        courses_with_enrollment_counts = []
        for course in courses_response.data:
            course_data = {
                **course,
                'enrollment_count': enrollment_counts.get(course['id'], 0)
            }
            courses_with_enrollment_counts.append(course_data)

        return {
            "success": True,
            "data": courses_with_enrollment_counts,
            "message": f"Found {len(courses_with_enrollment_counts)} courses"
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
