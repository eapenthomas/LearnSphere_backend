"""
Course Progress Tracking API
Handles student progress through course materials, similar to Coursera/Udemy
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(supabase_url, supabase_key)

router = APIRouter(prefix="/api/progress", tags=["Course Progress"])

# Pydantic models
class MaterialProgressUpdate(BaseModel):
    material_id: str
    status: str  # not_started, in_progress, completed
    progress_percentage: int = 0
    time_spent: int = 0  # seconds spent in this session

class MaterialProgressResponse(BaseModel):
    id: str
    material_id: str
    material_name: str
    status: str
    progress_percentage: int
    total_time_spent: int
    view_count: int
    download_count: int
    first_accessed_at: Optional[datetime]
    last_accessed_at: Optional[datetime]
    completed_at: Optional[datetime]

class CourseProgressResponse(BaseModel):
    id: str
    course_id: str
    course_title: str
    overall_progress_percentage: int
    materials_completed: int
    total_materials: int
    total_time_spent: int
    last_activity_at: Optional[datetime]
    is_completed: bool
    completed_at: Optional[datetime]

class LearningStreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[str]
    weekly_goal_minutes: int
    weekly_minutes_completed: int
    monthly_goal_minutes: int
    monthly_minutes_completed: int

@router.post("/material/track")
async def track_material_progress(
    progress_update: MaterialProgressUpdate,
    student_id: str = Query(...),
    course_id: str = Query(...)
):
    """Track student progress on a specific material"""
    try:
        # Get material info
        material_response = supabase.table('course_materials').select('*').eq('id', progress_update.material_id).single().execute()
        if not material_response.data:
            raise HTTPException(status_code=404, detail="Material not found")
        
        material = material_response.data
        
        # Check if progress record exists
        existing_progress = supabase.table('course_material_progress').select('*').eq('student_id', student_id).eq('material_id', progress_update.material_id).execute()
        
        current_time = datetime.now(timezone.utc)
        
        if existing_progress.data:
            # Update existing progress
            existing = existing_progress.data[0]
            new_total_time = existing['total_time_spent'] + progress_update.time_spent
            new_view_count = existing['view_count'] + 1
            
            update_data = {
                'status': progress_update.status,
                'progress_percentage': progress_update.progress_percentage,
                'total_time_spent': new_total_time,
                'view_count': new_view_count,
                'last_accessed_at': current_time.isoformat(),
                'updated_at': current_time.isoformat()
            }
            
            # Set completion time if completed
            if progress_update.status == 'completed' and not existing.get('completed_at'):
                update_data['completed_at'] = current_time.isoformat()
            
            supabase.table('course_material_progress').update(update_data).eq('id', existing['id']).execute()
        else:
            # Create new progress record
            progress_data = {
                'student_id': student_id,
                'course_id': course_id,
                'material_id': progress_update.material_id,
                'status': progress_update.status,
                'progress_percentage': progress_update.progress_percentage,
                'total_time_spent': progress_update.time_spent,
                'view_count': 1,
                'first_accessed_at': current_time.isoformat(),
                'last_accessed_at': current_time.isoformat(),
                'created_at': current_time.isoformat(),
                'updated_at': current_time.isoformat()
            }
            
            if progress_update.status == 'completed':
                progress_data['completed_at'] = current_time.isoformat()
            
            supabase.table('course_material_progress').insert(progress_data).execute()
        
        # Update learning streak
        await update_learning_streak(student_id, progress_update.time_spent)

        # Recalculate overall course progress
        await recalculate_course_progress(student_id, course_id)

        return {"success": True, "message": "Progress tracked successfully"}
        
    except Exception as e:
        print(f"Error tracking material progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/material/download")
async def track_material_download(
    material_id: str,
    student_id: str = Query(...),
    course_id: str = Query(...)
):
    """Track when a student downloads a material"""
    try:
        # Update download count
        existing_progress = supabase.table('course_material_progress').select('*').eq('student_id', student_id).eq('material_id', material_id).execute()
        
        current_time = datetime.now(timezone.utc)
        
        if existing_progress.data:
            # Update existing progress
            existing = existing_progress.data[0]
            new_download_count = existing['download_count'] + 1
            
            supabase.table('course_material_progress').update({
                'download_count': new_download_count,
                'last_accessed_at': current_time.isoformat(),
                'updated_at': current_time.isoformat()
            }).eq('id', existing['id']).execute()
        else:
            # Create new progress record for download
            progress_data = {
                'student_id': student_id,
                'course_id': course_id,
                'material_id': material_id,
                'status': 'in_progress',
                'download_count': 1,
                'view_count': 0,
                'first_accessed_at': current_time.isoformat(),
                'last_accessed_at': current_time.isoformat(),
                'created_at': current_time.isoformat(),
                'updated_at': current_time.isoformat()
            }
            
            supabase.table('course_material_progress').insert(progress_data).execute()

        # Recalculate overall course progress
        await recalculate_course_progress(student_id, course_id)

        return {"success": True, "message": "Download tracked successfully"}
        
    except Exception as e:
        print(f"Error tracking material download: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/course/{course_id}/student/{student_id}", response_model=CourseProgressResponse)
async def get_course_progress(course_id: str, student_id: str):
    """Get overall progress for a student in a specific course"""
    try:
        # Get course progress
        progress_response = supabase.table('course_progress').select('*').eq('student_id', student_id).eq('course_id', course_id).execute()
        
        # Get course info
        course_response = supabase.table('courses').select('title').eq('id', course_id).single().execute()
        course_title = course_response.data['title'] if course_response.data else 'Unknown Course'
        
        if progress_response.data:
            progress = progress_response.data[0]
            return CourseProgressResponse(
                id=progress['id'],
                course_id=course_id,
                course_title=course_title,
                overall_progress_percentage=progress['overall_progress_percentage'],
                materials_completed=progress['materials_completed'],
                total_materials=progress['total_materials'],
                total_time_spent=progress['total_time_spent'],
                last_activity_at=datetime.fromisoformat(progress['last_activity_at'].replace('Z', '+00:00')) if progress.get('last_activity_at') else None,
                is_completed=progress['is_completed'],
                completed_at=datetime.fromisoformat(progress['completed_at'].replace('Z', '+00:00')) if progress.get('completed_at') else None
            )
        else:
            # Return default progress if no record exists
            return CourseProgressResponse(
                id="",
                course_id=course_id,
                course_title=course_title,
                overall_progress_percentage=0,
                materials_completed=0,
                total_materials=0,
                total_time_spent=0,
                last_activity_at=None,
                is_completed=False,
                completed_at=None
            )
            
    except Exception as e:
        print(f"Error getting course progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/courses", response_model=List[CourseProgressResponse])
async def get_student_all_progress(student_id: str):
    """Get progress for all courses a student is enrolled in"""
    try:
        # Get all course progress for student
        progress_response = supabase.table('course_progress').select('''
            *,
            courses (
                title
            )
        ''').eq('student_id', student_id).execute()
        
        progress_list = []
        for progress in progress_response.data:
            progress_list.append(CourseProgressResponse(
                id=progress['id'],
                course_id=progress['course_id'],
                course_title=progress['courses']['title'] if progress.get('courses') else 'Unknown Course',
                overall_progress_percentage=progress['overall_progress_percentage'],
                materials_completed=progress['materials_completed'],
                total_materials=progress['total_materials'],
                total_time_spent=progress['total_time_spent'],
                last_activity_at=datetime.fromisoformat(progress['last_activity_at'].replace('Z', '+00:00')) if progress.get('last_activity_at') else None,
                is_completed=progress['is_completed'],
                completed_at=datetime.fromisoformat(progress['completed_at'].replace('Z', '+00:00')) if progress.get('completed_at') else None
            ))
        
        return progress_list
        
    except Exception as e:
        print(f"Error getting student progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/streak", response_model=LearningStreakResponse)
async def get_learning_streak(student_id: str):
    """Get learning streak information for a student"""
    try:
        streak_response = supabase.table('learning_streaks').select('*').eq('student_id', student_id).execute()
        
        if streak_response.data:
            streak = streak_response.data[0]
            return LearningStreakResponse(
                current_streak=streak['current_streak'],
                longest_streak=streak['longest_streak'],
                last_activity_date=streak['last_activity_date'],
                weekly_goal_minutes=streak['weekly_goal_minutes'],
                weekly_minutes_completed=streak['weekly_minutes_completed'],
                monthly_goal_minutes=streak['monthly_goal_minutes'],
                monthly_minutes_completed=streak['monthly_minutes_completed']
            )
        else:
            # Return default streak if no record exists
            return LearningStreakResponse(
                current_streak=0,
                longest_streak=0,
                last_activity_date=None,
                weekly_goal_minutes=0,
                weekly_minutes_completed=0,
                monthly_goal_minutes=0,
                monthly_minutes_completed=0
            )
            
    except Exception as e:
        print(f"Error getting learning streak: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def update_learning_streak(student_id: str, time_spent_seconds: int):
    """Update learning streak for a student"""
    try:
        from datetime import date, timedelta

        today = date.today()
        time_spent_minutes = time_spent_seconds // 60
        
        # Get existing streak
        streak_response = supabase.table('learning_streaks').select('*').eq('student_id', student_id).execute()
        
        if streak_response.data:
            streak = streak_response.data[0]
            last_activity = streak.get('last_activity_date')
            
            # Convert string date to date object if needed
            if isinstance(last_activity, str):
                last_activity = datetime.strptime(last_activity, '%Y-%m-%d').date()
            
            # Update streak logic
            if last_activity == today:
                # Same day, just update time
                new_current_streak = streak['current_streak']
            elif last_activity == today - timedelta(days=1):
                # Consecutive day, increment streak
                new_current_streak = streak['current_streak'] + 1
            else:
                # Streak broken, reset to 1
                new_current_streak = 1
            
            new_longest_streak = max(streak['longest_streak'], new_current_streak)
            
            # Update weekly and monthly minutes
            new_weekly_minutes = streak['weekly_minutes_completed'] + time_spent_minutes
            new_monthly_minutes = streak['monthly_minutes_completed'] + time_spent_minutes
            
            supabase.table('learning_streaks').update({
                'current_streak': new_current_streak,
                'longest_streak': new_longest_streak,
                'last_activity_date': today.isoformat(),
                'weekly_minutes_completed': new_weekly_minutes,
                'monthly_minutes_completed': new_monthly_minutes,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', streak['id']).execute()
        else:
            # Create new streak record
            supabase.table('learning_streaks').insert({
                'student_id': student_id,
                'current_streak': 1,
                'longest_streak': 1,
                'last_activity_date': today.isoformat(),
                'weekly_minutes_completed': time_spent_minutes,
                'monthly_minutes_completed': time_spent_minutes,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            
    except Exception as e:
        print(f"Error updating learning streak: {e}")
        # Don't raise exception as this is a background operation

async def recalculate_course_progress(student_id: str, course_id: str):
    """Recalculate overall course progress based on material completion"""
    try:
        # Get all materials for the course
        materials_response = supabase.table('course_materials').select('id').eq('course_id', course_id).execute()
        total_materials = len(materials_response.data) if materials_response.data else 0

        if total_materials == 0:
            return

        # Get completed materials for this student
        completed_response = supabase.table('course_material_progress').select('*').eq('student_id', student_id).eq('course_id', course_id).eq('status', 'completed').execute()
        completed_materials = len(completed_response.data) if completed_response.data else 0

        # Calculate progress percentage
        progress_percentage = int((completed_materials / total_materials) * 100) if total_materials > 0 else 0

        # Calculate total time spent
        all_progress_response = supabase.table('course_material_progress').select('total_time_spent').eq('student_id', student_id).eq('course_id', course_id).execute()
        total_time_spent = sum(p['total_time_spent'] for p in all_progress_response.data) if all_progress_response.data else 0

        # Check if course progress entry exists
        course_progress_response = supabase.table('course_progress').select('*').eq('student_id', student_id).eq('course_id', course_id).execute()

        current_time = datetime.now(timezone.utc)
        is_completed = progress_percentage == 100

        progress_data = {
            'overall_progress_percentage': progress_percentage,
            'materials_completed': completed_materials,
            'total_materials': total_materials,
            'total_time_spent': total_time_spent,
            'is_completed': is_completed,
            'last_activity_at': current_time.isoformat(),
            'updated_at': current_time.isoformat()
        }

        if is_completed:
            progress_data['completed_at'] = current_time.isoformat()

        if course_progress_response.data:
            # Update existing progress
            supabase.table('course_progress').update(progress_data).eq('student_id', student_id).eq('course_id', course_id).execute()
        else:
            # Create new progress entry
            progress_data.update({
                'student_id': student_id,
                'course_id': course_id,
                'created_at': current_time.isoformat()
            })
            supabase.table('course_progress').insert(progress_data).execute()

        print(f"Course progress updated: {progress_percentage}% ({completed_materials}/{total_materials} materials)")

    except Exception as e:
        print(f"Error recalculating course progress: {e}")
