"""
Course Progress Tracking API
Handles student progress through course materials, similar to Coursera/Udemy
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

            # Check if this is a new completion (not already completed)
            was_previously_completed = False
            if course_progress_response.data:
                was_previously_completed = course_progress_response.data[0].get('is_completed', False)

            # Send completion email if this is a new completion
            if not was_previously_completed:
                await send_course_completion_email(student_id, course_id)

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

async def send_course_completion_email(student_id: str, course_id: str):
    """Send email notification when student completes a course"""
    try:
        # Get student and course information
        student_response = supabase.table('profiles').select('*').eq('id', student_id).single().execute()
        course_response = supabase.table('courses').select('*').eq('id', course_id).single().execute()

        if not student_response.data or not course_response.data:
            print("Student or course not found for completion email")
            return

        student = student_response.data
        course = course_response.data

        # Email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured, skipping email")
            return

        # Create email content
        subject = f"🎉 Congratulations! You've completed {course['title']}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🎉 Course Completed!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">Congratulations on your achievement!</p>
                </div>

                <div style="padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #667eea; margin-top: 0;">Dear {student['full_name']},</h2>

                    <p>We're thrilled to congratulate you on successfully completing the course:</p>

                    <div style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0;">
                        <h3 style="margin: 0; color: #333;">{course['title']}</h3>
                        <p style="margin: 5px 0 0 0; color: #666;">{course.get('description', 'Course completed successfully!')}</p>
                    </div>

                    <p>Your dedication and hard work have paid off! This achievement demonstrates your commitment to learning and personal growth.</p>

                    <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h4 style="margin: 0 0 10px 0; color: #1976d2;">🏆 What's Next?</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Continue your learning journey with more courses</li>
                            <li>Share your achievement with friends and colleagues</li>
                            <li>Apply your new knowledge in real-world projects</li>
                            <li>Leave a review to help other learners</li>
                        </ul>
                    </div>

                    <p>Thank you for choosing LearnSphere for your educational journey. We're proud to be part of your success!</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://localhost:3000/dashboard" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold;">Continue Learning</a>
                    </div>
                </div>

                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p>Best regards,<br>The LearnSphere Team</p>
                    <p style="margin-top: 20px;">
                        <a href="http://localhost:3000" style="color: #667eea;">LearnSphere</a> |
                        <a href="mailto:support@learnsphere.com" style="color: #667eea;">Support</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = student['email']

        # Add HTML content
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        print(f"Course completion email sent to {student['email']} for course {course['title']}")

        # Log the email notification
        try:
            supabase.table('email_notifications').insert({
                'recipient_id': student_id,
                'subject': subject,
                'content': html_body,
                'type': 'course_completion',
                'status': 'sent',
                'sent_at': datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception as log_error:
            print(f"Failed to log email notification: {log_error}")

    except Exception as e:
        print(f"Error sending course completion email: {e}")
        # Don't raise the exception to avoid breaking the progress update
