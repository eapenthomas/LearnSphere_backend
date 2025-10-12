from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.STUDENT

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user_id: str
    role: str
    full_name: str
    message: str
    approval_status: Optional[str] = None
    is_active: Optional[bool] = True

class ProfileSyncRequest(BaseModel):
    user_id: str
    full_name: str
    role: UserRole = UserRole.STUDENT

class PasswordUpdateRequest(BaseModel):
    user_id: str
    current_password: str
    new_password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str

class EmailCheckRequest(BaseModel):
    email: EmailStr

class EmailCheckResponse(BaseModel):
    email: str
    exists: bool
    message: str

class ForgotPasswordResponse(BaseModel):
    message: str
    email: str

class ErrorResponse(BaseModel):
    error: str
    message: str

# =====================================================
# Teacher Verification Models
# =====================================================

class TeacherRegistrationRequest(BaseModel):
    """Request model for teacher registration with ID verification"""
    full_name: str
    email: EmailStr
    institution_name: str
    password: str

class TeacherRegistrationResponse(BaseModel):
    """Response model for teacher registration"""
    success: bool
    user_id: str
    message: str
    ocr_status: str
    ai_confidence: int
    reason: Optional[str] = None

class OCRValidationResult(BaseModel):
    """Model for OCR validation results"""
    match_confidence: int
    reason: str

class TeacherApprovalRequest(BaseModel):
    """Request model for admin teacher approval/rejection"""
    user_id: str
    approve: bool
    admin_notes: Optional[str] = None

class TeacherApprovalResponse(BaseModel):
    """Response model for teacher approval actions"""
    success: bool
    message: str
    user_id: str
    status: str

class TeacherVerificationStatus(BaseModel):
    """Model for teacher verification status"""
    user_id: str
    full_name: str
    email: str
    institution_name: str
    ocr_status: str
    ai_confidence: int
    approval_status: str
    is_verified: bool
    verification_document_url: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

class TeacherApprovalRequestModel(BaseModel):
    """Model for teacher approval request data"""
    id: str
    user_id: str
    name: str
    institution: str
    status: str
    confidence: int
    reason: Optional[str] = None
    admin_id: Optional[str] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

class TeacherRequestsListResponse(BaseModel):
    """Response model for listing teacher approval requests"""
    success: bool
    approval_requests: List[TeacherApprovalRequestModel]
    profiles_passed: List[TeacherVerificationStatus]

class EmailNotificationRequest(BaseModel):
    """Model for email notification requests"""
    recipient_email: str
    subject: str
    body: str
    notification_type: str
    recipient_id: Optional[str] = None