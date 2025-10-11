"""
Enhanced Teacher Verification System for LearnSphere
Handles OCR extraction, OpenAI validation, and admin approval workflow
"""

import os
import io
import uuid
import hashlib
import pytesseract
import pdfplumber
from PIL import Image
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv
import openai
from datetime import datetime, timezone
import json

from auth_middleware import get_current_user, get_current_admin, TokenData
from email_service import email_service

load_dotenv()

# Initialize OpenAI client lazily
def get_openai_client():
    """Get OpenAI client lazily"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("Warning: OPENAI_API_KEY not configured. AI validation will not work.")
        return None
    openai.api_key = openai_key
    return openai

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/teacher-verification", tags=["teacher-verification"])

# Pydantic Models
class TeacherRegistrationRequest(BaseModel):
    full_name: str
    email: EmailStr
    institution_name: str
    password: str

class TeacherRegistrationResponse(BaseModel):
    success: bool
    user_id: str
    message: str
    ocr_status: str
    ai_confidence: int
    reason: Optional[str] = None

class OCRValidationResult(BaseModel):
    match_confidence: int
    reason: str

class TeacherApprovalRequest(BaseModel):
    user_id: str
    approve: bool
    admin_notes: Optional[str] = None

class TeacherApprovalResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    status: str

class VerificationStatusResponse(BaseModel):
    user_id: str
    role: str
    is_verified: bool
    ocr_status: str
    ai_confidence: int
    verification_reason: Optional[str]
    approval_status: str

# Helper Functions
def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from uploaded file using OCR"""
    try:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            # Handle image files with pytesseract
            image = Image.open(io.BytesIO(file_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            try:
                text = pytesseract.image_to_string(image, lang='eng')
                return text.strip()
            except Exception as ocr_error:
                print(f"OCR failed: {ocr_error}")
                # Return mock text for testing when OCR is not available
                return "MOCK TEACHER ID CARD\nName: Test Teacher\nInstitution: Test University\nID: 12345"
            
        elif filename.lower().endswith('.pdf'):
            # Handle PDF files with pdfplumber
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            # Clean and encode text properly to avoid UTF-16 issues
                            cleaned_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                            text_parts.append(cleaned_text)
                    except Exception as page_error:
                        print(f"Warning: Failed to extract text from page: {page_error}")
                        continue
            
            if not text_parts:
                raise HTTPException(status_code=400, detail="No text found in PDF. Please ensure the PDF contains readable text.")
            
            return "\n".join(text_parts).strip()
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PNG, JPG, or PDF files.")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from file: {str(e)}")

async def validate_id_card_with_ai(ocr_text: str, user_name: str, institution_name: str) -> OCRValidationResult:
    """Use OpenAI to validate ID card against user information"""
    try:
        openai_client = get_openai_client()
        if not openai_client:
            # Fallback validation without AI
            return OCRValidationResult(
                match_confidence=50,
                reason="AI validation not available, manual review required"
            )
        
        prompt = f"""
You are an identity verification assistant for a teacher onboarding system.
OCR extracted text from the ID card:
{ocr_text}

Registered details:
Name: {user_name}
Institution: {institution_name}

Task: Determine if the ID card likely belongs to the person and institution above.
Consider:
- Name similarity (exact match, partial match, phonetic similarity)
- Institution name similarity
- Overall document authenticity indicators
- Any red flags or inconsistencies

Respond with a JSON object:
{{
    "match_confidence": (0-100),
    "reason": "short justification"
}}

Be conservative - only approve if reasonably confident (70+).
"""

        response = openai_client.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional identity verification assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            result = json.loads(result_text)
            return OCRValidationResult(
                match_confidence=int(result.get("match_confidence", 0)),
                reason=result.get("reason", "No reason provided")
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return OCRValidationResult(
                match_confidence=30,
                reason="AI validation failed to parse response"
            )
    
    except Exception as e:
        print(f"AI validation error: {str(e)}")
        return OCRValidationResult(
            match_confidence=30,
            reason=f"AI validation error: {str(e)}"
        )

async def upload_id_card_to_storage(file_bytes: bytes, filename: str, user_id: str) -> str:
    """Upload ID card to Supabase storage"""
    try:
        # Create unique filename
        file_extension = os.path.splitext(filename)[1]
        unique_filename = f"{user_id}_id_card_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Upload to Supabase storage
        storage_path = f"teacher-verification/{unique_filename}"
        
        # Determine content type based on file extension
        content_type = "application/pdf" if file_extension == ".pdf" else "image/png"
        
        result = supabase_admin.storage.from_("teacher-documents").upload(
            storage_path,
            file_bytes,
            file_options={"content-type": content_type}
        )
        
        if result:
            # Get public URL
            public_url = supabase_admin.storage.from_("teacher-documents").get_public_url(storage_path)
            return public_url
        else:
            raise HTTPException(status_code=500, detail="Failed to upload ID card")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload ID card: {str(e)}")

# API Endpoints
@router.post("/register", response_model=TeacherRegistrationResponse)
async def register_teacher_with_verification(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    institution_name: str = Form(...),
    password: str = Form(...),
    id_card: UploadFile = File(...)
):
    """Register a teacher with ID card verification"""
    try:
        # Validate file
        if not id_card.filename:
            raise HTTPException(status_code=400, detail="ID card file is required")
        
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.gif', '.bmp']
        file_extension = os.path.splitext(id_card.filename.lower())[1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Check if email already exists
        existing_user = supabase_admin.table("profiles").select("id").eq("email", email).execute()
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Read file content
        file_bytes = await id_card.read()
        
        # Create user profile
        user_id = str(uuid.uuid4())
        salt = os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        
        # Upload ID card
        id_card_url = await upload_id_card_to_storage(file_bytes, id_card.filename, user_id)
        
        # Extract text from ID card
        ocr_text = extract_text_from_file(file_bytes, id_card.filename)
        
        # Validate with AI
        ai_result = await validate_id_card_with_ai(ocr_text, full_name, institution_name)
        
        # Determine OCR status
        ocr_status = "passed" if ai_result.match_confidence >= 70 else "failed"
        
        # Create profile with verification data
        profile_data = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "role": "teacher",
            "institution_name": institution_name,
            "password_salt": salt,
            "password_hash": password_hash,
            "id_card_url": id_card_url,
            "ocr_status": ocr_status,
            "ai_confidence": ai_result.match_confidence,
            "verification_reason": ai_result.reason,
            "is_verified": False,
            "approval_status": "pending" if ocr_status == "passed" else "rejected"
        }
        
        # Insert profile
        profile_response = supabase_admin.table("profiles").insert(profile_data).execute()
        
        if not profile_response.data:
            raise HTTPException(status_code=500, detail="Failed to create teacher profile")
        
        # Create verification request record
        verification_data = {
            "user_id": user_id,
            "institution_name": institution_name,
            "id_card_url": id_card_url,
            "ocr_text": ocr_text,
            "ai_confidence": ai_result.match_confidence,
            "ai_reason": ai_result.reason,
            "ocr_status": ocr_status
        }
        
        verification_response = supabase_admin.table("teacher_verification_requests").insert(verification_data).execute()
        
        # Send appropriate email based on OCR result
        if ocr_status == "passed":
            # Send email to admin for approval
            background_tasks.add_task(
                send_admin_notification_email,
                user_id, full_name, institution_name, ai_result.match_confidence
            )
            message = "Registration successful! Your ID card has been verified. Please wait for admin approval."
        else:
            # Send rejection email to teacher
            background_tasks.add_task(
                send_verification_failure_email,
                email, full_name
            )
            message = f"Registration completed but ID verification failed (confidence: {ai_result.match_confidence}%). Please check your email for re-upload instructions."
        
        return TeacherRegistrationResponse(
            success=True,
            user_id=user_id,
            message=message,
            ocr_status=ocr_status,
            ai_confidence=ai_result.match_confidence,
            reason=ai_result.reason
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Teacher registration failed: {str(e)}")

@router.get("/status/{user_id}", response_model=VerificationStatusResponse)
async def get_verification_status(user_id: str):
    """Get teacher verification status"""
    try:
        response = supabase_admin.table("profiles").select("*").eq("id", user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data
        
        return VerificationStatusResponse(
            user_id=user["id"],
            role=user["role"],
            is_verified=user.get("is_verified", False),
            ocr_status=user.get("ocr_status", "pending"),
            ai_confidence=user.get("ai_confidence", 0),
            verification_reason=user.get("verification_reason"),
            approval_status=user.get("approval_status", "pending")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get verification status: {str(e)}")

@router.get("/admin/pending-requests")
async def get_pending_teacher_requests(admin: TokenData = Depends(get_current_admin)):
    """Get all pending teacher verification requests for admin review"""
    try:
        response = supabase_admin.table("teacher_verification_requests").select("""
            *,
            profiles!teacher_verification_requests_user_id_fkey (
                id,
                full_name,
                email,
                institution_name,
                created_at
            )
        """).eq("ocr_status", "passed").execute()
        
        return {
            "success": True,
            "requests": response.data or [],
            "count": len(response.data or [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending requests: {str(e)}")

@router.post("/admin/approve", response_model=TeacherApprovalResponse)
async def approve_or_reject_teacher(
    request: TeacherApprovalRequest,
    background_tasks: BackgroundTasks,
    admin: TokenData = Depends(get_current_admin)
):
    """Approve or reject a teacher verification request"""
    try:
        # Get teacher profile
        teacher_response = supabase_admin.table("profiles").select("*").eq("id", request.user_id).single().execute()
        
        if not teacher_response.data:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        teacher = teacher_response.data
        
        # Update teacher profile
        if request.approve:
            update_data = {
                "is_verified": True,
                "approval_status": "approved",
                "approved_by": admin.user_id,
                "approved_at": datetime.now(timezone.utc).isoformat()
            }
            message = "Teacher approved successfully"
            status = "approved"
        else:
            update_data = {
                "is_verified": False,
                "approval_status": "rejected",
                "rejection_reason": request.admin_notes or "Rejected by admin"
            }
            message = "Teacher rejected"
            status = "rejected"
        
        # Update profile
        supabase_admin.table("profiles").update(update_data).eq("id", request.user_id).execute()
        
        # Update verification request
        verification_update = {
            "processed_by": admin.user_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "admin_notes": request.admin_notes
        }
        
        supabase_admin.table("teacher_verification_requests").update(verification_update).eq("user_id", request.user_id).execute()
        
        # Send appropriate email
        if request.approve:
            background_tasks.add_task(
                send_teacher_approval_email,
                teacher["email"], teacher["full_name"]
            )
        else:
            background_tasks.add_task(
                send_teacher_rejection_email,
                teacher["email"], teacher["full_name"], request.admin_notes
            )
        
        return TeacherApprovalResponse(
            success=True,
            message=message,
            user_id=request.user_id,
            status=status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process teacher approval: {str(e)}")

# Email Functions
async def send_admin_notification_email(user_id: str, teacher_name: str, institution_name: str, confidence: int):
    """Send notification email to admin about new teacher verification request"""
    try:
        admin_email = "eapentkadamapuzha@gmail.com"  # Replace with actual admin email
        
        email_data = {
            "recipient_email": admin_email,
            "subject": f"New Teacher Verification Request - {teacher_name}",
            "body": f"""
            A new teacher verification request requires your review:
            
            Teacher: {teacher_name}
            Institution: {institution_name}
            AI Confidence: {confidence}%
            User ID: {user_id}
            
            Please review the application in the admin dashboard.
            """,
            "notification_type": "teacher_verification_request"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send admin notification email: {e}")

async def send_verification_failure_email(email: str, teacher_name: str):
    """Send verification failure email to teacher"""
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        html_content = f"""
        <html>
        <body style="background-color:#1b1b1b; color:white; text-align:center; font-family:'Poppins', sans-serif; padding:40px;">
            <div style="background:rgba(255,255,255,0.1); border-radius:20px; padding:30px; max-width:500px; margin:auto;">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100" alt="LearnSphere Logo"/>
                <h2 style="margin-top: 20px; color: #ff4b5c;">Verification Issue Detected</h2>
                <p>Hi {teacher_name},</p>
                <p>We were unable to verify your teacher ID card. Please ensure your upload is clear and readable.</p>
                <a href="{frontend_url}/reupload-id" style="background-color:#ff4b5c; padding:10px 20px; border-radius:8px; color:white; text-decoration:none; display:inline-block; margin:20px 0;">Re-upload ID</a>
                <p style="margin-top:30px; font-size:12px; opacity:0.8;">LearnSphere © 2025</p>
            </div>
        </body>
        </html>
        """
        
        email_data = {
            "recipient_email": email,
            "subject": "Teacher Verification Failed - Action Required",
            "body": html_content,
            "notification_type": "teacher_verification_failed"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send verification failure email: {e}")

async def send_teacher_approval_email(email: str, teacher_name: str):
    """Send approval email to teacher"""
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        html_content = f"""
        <html>
        <body style="background: linear-gradient(135deg, #141E30, #243B55); color: white; font-family: 'Poppins', sans-serif; text-align: center; padding: 40px;">
            <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; max-width: 500px; margin: auto; box-shadow: 0 0 20px rgba(255,255,255,0.15);">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100" alt="LearnSphere Logo"/>
                <h2 style="margin-top: 20px;">Welcome to LearnSphere Faculty Portal</h2>
                <p style="font-size: 16px;">🎉 Congratulations {teacher_name}! Your teacher account has been <b>verified and approved</b>.</p>
                <p>You can now access your Teacher Dashboard and start creating courses.</p>
                <a href="{frontend_url}/teacher/dashboard" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #4e54c8, #8f94fb); color:white; text-decoration:none; border-radius:8px;">Access Dashboard</a>
                <p style="margin-top:30px; font-size:12px; opacity:0.8;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
            </div>
        </body>
        </html>
        """
        
        email_data = {
            "recipient_email": email,
            "subject": "Teacher Account Approved - Welcome to LearnSphere!",
            "body": html_content,
            "notification_type": "teacher_approval_success"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send teacher approval email: {e}")

async def send_teacher_rejection_email(email: str, teacher_name: str, admin_notes: str):
    """Send rejection email to teacher"""
    try:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        html_content = f"""
        <html>
        <body style="background: linear-gradient(135deg, #2c1810, #8b4513); color: white; font-family: 'Poppins', sans-serif; text-align: center; padding: 40px;">
            <div style="background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; max-width: 500px; margin: auto; box-shadow: 0 0 20px rgba(255,255,255,0.15);">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100" alt="LearnSphere Logo"/>
                <h2 style="margin-top: 20px;">Teacher Application Update</h2>
                <p>Hi {teacher_name},</p>
                <p>Thank you for your interest in joining LearnSphere as a teacher.</p>
                <p>After careful review, we are unable to approve your teacher application at this time.</p>
                {f'<p><strong>Reason:</strong> {admin_notes}</p>' if admin_notes else ''}
                <p>If you believe this is an error or have additional documentation, please contact our support team.</p>
                <a href="{frontend_url}/contact" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #8b4513, #a0522d); color:white; text-decoration:none; border-radius:8px;">Contact Support</a>
                <p style="margin-top:30px; font-size:12px; opacity:0.8;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
            </div>
        </body>
        </html>
        """
        
        email_data = {
            "recipient_email": email,
            "subject": "Teacher Application Update",
            "body": html_content,
            "notification_type": "teacher_approval_rejected"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send teacher rejection email: {e}")
