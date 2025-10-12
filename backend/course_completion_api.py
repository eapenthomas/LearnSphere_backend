"""
Course Completion API
Handles course completion tracking and email notifications
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from auth_middleware import get_current_user, TokenData

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/api/course-completion", tags=["course-completion"])

# Pydantic models
class CourseCompletionRequest(BaseModel):
    course_id: str
    completion_percentage: int = 100

class CourseCompletionResponse(BaseModel):
    success: bool
    message: str
    completion_id: Optional[str] = None

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
FROM_EMAIL = os.getenv("FROM_EMAIL", EMAIL_USER)
FROM_NAME = os.getenv("FROM_NAME", "LearnSphere")

def send_course_completion_email(user_email: str, user_name: str, course_title: str):
    """Send email notification when user completes a course"""
    try:
        if not EMAIL_USER or not EMAIL_PASS:
            print("Warning: Email credentials not configured. Skipping email notification.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = user_email
        msg['Subject'] = f"🎉 Congratulations! You've completed {course_title}"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🎉 Congratulations!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">You've successfully completed</p>
                    <h2 style="margin: 10px 0 0 0; font-size: 24px;">{course_title}</h2>
                </div>
                
                <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px; margin-bottom: 20px;">Dear {user_name},</p>
                    
                    <p style="font-size: 16px; margin-bottom: 20px;">
                        We're thrilled to congratulate you on completing the course <strong>"{course_title}"</strong>! 
                        Your dedication and hard work have paid off, and you should be proud of this achievement.
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                        <h3 style="color: #667eea; margin-top: 0;">What's Next?</h3>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Download your certificate of completion</li>
                            <li>Explore more courses in our catalog</li>
                            <li>Share your achievement on social media</li>
                            <li>Continue your learning journey with advanced topics</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{os.getenv('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')}/courses" 
                           style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block;">
                            Explore More Courses
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Thank you for choosing LearnSphere for your educational journey. 
                        Keep learning, keep growing!
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        This email was sent by LearnSphere Educational Platform<br>
                        If you have any questions, please contact our support team.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, user_email, text)
        server.quit()
        
        print(f"✅ Course completion email sent to {user_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send course completion email: {e}")
        return False

@router.post("/mark-complete", response_model=CourseCompletionResponse)
async def mark_course_complete(
    request: CourseCompletionRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Mark a course as completed and send email notification"""
    try:
        # Check if course exists
        course_response = supabase.table("courses").select("*").eq("id", request.course_id).single().execute()
        
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course = course_response.data
        
        # Check if user is enrolled in the course
        enrollment_response = supabase.table("enrollments").select("*").eq("student_id", current_user.user_id).eq("course_id", request.course_id).execute()
        
        if not enrollment_response.data:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course")
        
        # Check if already completed
        existing_completion = supabase.table("course_completions").select("*").eq("student_id", current_user.user_id).eq("course_id", request.course_id).execute()
        
        if existing_completion.data:
            raise HTTPException(status_code=400, detail="Course already marked as completed")
        
        # Get user profile for email
        user_response = supabase.table("profiles").select("email, full_name").eq("id", current_user.user_id).single().execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_profile = user_response.data
        
        # Mark course as completed
        completion_data = {
            "student_id": current_user.user_id,
            "course_id": request.course_id,
            "completion_percentage": request.completion_percentage,
            "completed_at": "now()"
        }
        
        completion_response = supabase.table("course_completions").insert(completion_data).execute()
        
        if not completion_response.data:
            raise HTTPException(status_code=500, detail="Failed to mark course as completed")
        
        completion_id = completion_response.data[0]["id"]
        
        # Send email notification
        email_sent = send_course_completion_email(
            user_profile["email"],
            user_profile["full_name"],
            course["title"]
        )
        
        # Update course progress
        supabase.table("course_progress").upsert({
            "student_id": current_user.user_id,
            "course_id": request.course_id,
            "progress_percentage": 100,
            "last_accessed_at": "now()"
        }).execute()
        
        return CourseCompletionResponse(
            success=True,
            message=f"Course '{course['title']}' marked as completed successfully! {'Email notification sent.' if email_sent else 'Email notification could not be sent.'}",
            completion_id=completion_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark course as completed: {str(e)}")

@router.get("/my-completions")
async def get_my_completions(current_user: TokenData = Depends(get_current_user)):
    """Get user's course completions"""
    try:
        completions_response = supabase.table("course_completions").select("""
            *,
            courses (
                id,
                title,
                description,
                category,
                thumbnail_url
            )
        """).eq("student_id", current_user.user_id).order("completed_at", desc=True).execute()
        
        return {
            "success": True,
            "completions": completions_response.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completions: {str(e)}")

@router.get("/stats")
async def get_completion_stats(current_user: TokenData = Depends(get_current_user)):
    """Get user's completion statistics"""
    try:
        # Get total completions
        completions_response = supabase.table("course_completions").select("id").eq("student_id", current_user.user_id).execute()
        total_completions = len(completions_response.data)
        
        # Get enrolled courses count
        enrollments_response = supabase.table("enrollments").select("id").eq("student_id", current_user.user_id).execute()
        total_enrolled = len(enrollments_response.data)
        
        # Get completion rate
        completion_rate = (total_completions / total_enrolled * 100) if total_enrolled > 0 else 0
        
        return {
            "success": True,
            "stats": {
                "total_completions": total_completions,
                "total_enrolled": total_enrolled,
                "completion_rate": round(completion_rate, 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get completion stats: {str(e)}")
