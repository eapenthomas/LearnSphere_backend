"""
Optimized User Management API
Handles user operations with email verification and profile management
"""

import os
import smtplib
import asyncio
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, EmailStr
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/users", tags=["user-management"])

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    approval_status: str
    profile_picture_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    approval_status: Optional[str] = None
    disable_reason: Optional[str] = None

class EmailVerification(BaseModel):
    email: str
    verification_code: str

# Optimized user queries with indexes
@router.get("/students", response_model=List[UserProfile])
async def get_all_students(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all students with optimized pagination and filtering"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query with optimized indexes
        query = supabase.table('profiles').select(
            'id, email, full_name, role, is_active, approval_status, profile_picture_url, created_at, last_login'
        ).eq('role', 'student')
        
        # Apply filters
        if status == 'active':
            query = query.eq('is_active', True)
        elif status == 'inactive':
            query = query.eq('is_active', False)
        
        if search:
            query = query.or_(f'full_name.ilike.%{search}%,email.ilike.%{search}%')
        
        # Execute with pagination
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        print(f"Error fetching students: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teachers", response_model=List[UserProfile])
async def get_all_teachers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all teachers with optimized pagination and filtering"""
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Build query with optimized indexes
        query = supabase.table('profiles').select(
            'id, email, full_name, role, is_active, approval_status, profile_picture_url, created_at, last_login'
        ).eq('role', 'teacher')
        
        # Apply filters
        if status == 'active':
            query = query.eq('is_active', True).eq('approval_status', 'approved')
        elif status == 'inactive':
            query = query.eq('is_active', False)
        elif status == 'pending':
            query = query.eq('approval_status', 'pending')
        
        if search:
            query = query.or_(f'full_name.ilike.%{search}%,email.ilike.%{search}%')
        
        # Execute with pagination
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        
        return result.data or []
        
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update/{user_id}")
async def update_user_status(user_id: str, update_data: UserUpdate):
    """Update user status with email notification"""
    try:
        # Get current user data
        user_response = supabase.table('profiles').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = user_response.data[0]
        
        # Prepare update data
        update_fields = {}
        if update_data.is_active is not None:
            update_fields['is_active'] = update_data.is_active
        if update_data.approval_status is not None:
            update_fields['approval_status'] = update_data.approval_status
        
        # Update user
        result = supabase.table('profiles').update(update_fields).eq('id', user_id).execute()
        
        # Send email notification
        await send_status_update_email(
            user['email'], 
            user['full_name'], 
            update_data.is_active, 
            update_data.disable_reason
        )
        
        return {"message": "User updated successfully", "user": result.data[0]}
        
    except Exception as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_status_update_email(email: str, name: str, is_active: bool, reason: str = None):
    """Send email notification for status updates"""
    try:
        # Email configuration
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured, skipping email")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "LearnSphere Account Status Update"
        
        # Email body
        if is_active:
            body = f"""
Dear {name},

Your LearnSphere account has been activated! You can now access all features of the platform.

Login at: http://localhost:3000

Best regards,
LearnSphere Team
"""
        else:
            body = f"""
Dear {name},

Your LearnSphere account has been temporarily disabled.

{f'Reason: {reason}' if reason else ''}

If you have any questions, please contact our support team.

Best regards,
LearnSphere Team
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        print(f"Status update email sent to {email}")
        
    except Exception as e:
        print(f"Error sending email: {e}")

@router.post("/verify-email")
async def send_verification_email(email: EmailStr):
    """Send email verification code"""
    try:
        # Generate verification code
        import random
        verification_code = str(random.randint(100000, 999999))
        
        # Store verification code in database
        verification_data = {
            "email": email,
            "verification_code": verification_code,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
        
        supabase.table('email_verifications').insert(verification_data).execute()
        
        # Send verification email
        await send_verification_code_email(email, verification_code)
        
        return {"message": "Verification code sent successfully"}
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def send_verification_code_email(email: str, code: str):
    """Send verification code email"""
    try:
        # Email configuration
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_username = os.environ.get("SMTP_USERNAME")
        smtp_password = os.environ.get("SMTP_PASSWORD")
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured, skipping verification email")
            return
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email
        msg['Subject'] = "LearnSphere Email Verification"
        
        body = f"""
Dear User,

Your LearnSphere email verification code is: {code}

This code will expire in 15 minutes.

If you didn't request this verification, please ignore this email.

Best regards,
LearnSphere Team
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email, text)
        server.quit()
        
        print(f"Verification email sent to {email}")
        
    except Exception as e:
        print(f"Error sending verification email: {e}")

@router.post("/verify-code")
async def verify_email_code(verification: EmailVerification):
    """Verify email verification code"""
    try:
        # Check verification code
        result = supabase.table('email_verifications').select('*').eq('email', verification.email).eq('verification_code', verification.verification_code).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        verification_record = result.data[0]
        
        # Check if code is expired
        expires_at = datetime.fromisoformat(verification_record['expires_at'].replace('Z', '+00:00'))
        if datetime.now() > expires_at:
            raise HTTPException(status_code=400, detail="Verification code expired")
        
        # Mark email as verified
        supabase.table('profiles').update({'email_verified': True}).eq('email', verification.email).execute()
        
        # Delete verification record
        supabase.table('email_verifications').delete().eq('id', verification_record['id']).execute()
        
        return {"message": "Email verified successfully"}
        
    except Exception as e:
        print(f"Error verifying email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_user_stats():
    """Get optimized user statistics"""
    try:
        # Use concurrent queries for better performance
        async def get_counts():
            students = supabase.table('profiles').select('id').eq('role', 'student').eq('is_active', True).execute()
            teachers = supabase.table('profiles').select('id').eq('role', 'teacher').eq('is_active', True).eq('approval_status', 'approved').execute()
            pending_teachers = supabase.table('profiles').select('id').eq('role', 'teacher').eq('approval_status', 'pending').execute()
            
            return {
                'active_students': len(students.data or []),
                'active_teachers': len(teachers.data or []),
                'pending_teachers': len(pending_teachers.data or [])
            }
        
        stats = await get_counts()
        return stats
        
    except Exception as e:
        print(f"Error fetching user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
