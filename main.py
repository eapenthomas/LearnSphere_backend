from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthService
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(supabase_url, supabase_key)
from models import RegisterRequest, LoginRequest, ProfileSyncRequest, AuthResponse, ErrorResponse, PasswordUpdateRequest, ForgotPasswordRequest, VerifyOTPRequest, ForgotPasswordResponse, EmailCheckRequest, EmailCheckResponse
from notification_api import router as notification_router
from admin_api import router as admin_router
from admin_dashboard_api import router as admin_dashboard_router
from admin_notifications_api import router as admin_notifications_router
from ai_usage_api import router as ai_usage_router
from ai_tutor_api import router as ai_tutor_router
from quiz_api import router as quiz_router
from notes_summarizer_api import router as notes_router
from course_api import router as course_router
from forum_api import router as forum_router
from course_materials_routes import router as course_materials_router
from assignments_api import router as assignments_router
from enrollment_api import router as enrollment_router
from student_deadlines_api import router as student_deadlines_router
from teacher_analytics_api import router as teacher_analytics_router
from teacher_reports_api import router as teacher_reports_router
from teacher_rating_api import router as teacher_rating_router
from profile_picture_simple import router as profile_picture_router
from course_progress_api import router as progress_router
from quiz_generator_api import router as quiz_generator_router
from activity_export_api import router as activity_export_router
from user_management_api import router as user_management_router
from smart_study_planner_api import router as study_planner_router

app = FastAPI(title="LearnSphere API",
    description="E-learning platform API with authentication and user management",
    version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notification_router)
app.include_router(admin_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_notifications_router)
app.include_router(ai_usage_router)
app.include_router(ai_tutor_router)
app.include_router(quiz_router)
app.include_router(course_materials_router)
app.include_router(course_router)
app.include_router(assignments_router)
app.include_router(enrollment_router)
app.include_router(student_deadlines_router)
app.include_router(notes_router)
app.include_router(teacher_analytics_router)
app.include_router(teacher_reports_router)
app.include_router(teacher_rating_router)
app.include_router(profile_picture_router)
app.include_router(forum_router)
app.include_router(progress_router)
app.include_router(quiz_generator_router)
app.include_router(activity_export_router)
app.include_router(user_management_router)
app.include_router(study_planner_router)

@app.get("/")
async def root():
    return {"message": "LearnSphere API is running"}

@app.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user with email/password"""
    try:
        return await AuthService.register_user(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/check-email", response_model=EmailCheckResponse)
async def check_email_availability(request: EmailCheckRequest):
    """Check if email is already registered"""
    try:
        return await AuthService.check_email_availability(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user with email/password"""
    try:
        return await AuthService.login_user(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/google-login")
async def google_login():
    """Get Google OAuth URL for frontend redirection"""
    try:
        return await AuthService.get_google_oauth_url()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/google-callback")
async def google_callback(code: str = Query(...), state: str = Query(...)):
    """Handle Google OAuth callback"""
    try:
        return await AuthService.handle_google_callback(code, state)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-password", response_model=AuthResponse)
async def update_password(request: PasswordUpdateRequest):
    """Update user password"""
    try:
        return await AuthService.update_password(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset OTP"""
    try:
        return await AuthService.forgot_password(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-otp-reset", response_model=AuthResponse)
async def verify_otp_and_reset_password(request: VerifyOTPRequest):
    """Verify OTP and reset password"""
    try:
        return await AuthService.verify_otp_and_reset_password(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-profile", response_model=AuthResponse)
async def sync_profile(request: ProfileSyncRequest):
    """Sync user profile data"""
    try:
        return await AuthService.sync_profile(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/validate-session")
async def validate_session(authorization: str = Header(None)):
    """Validate user session token"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization.split(" ")[1]

        # For our simple implementation, token is the user ID
        user_id = token

        # Verify user exists and is active
        response = supabase.table('profiles').select('*').eq('id', user_id).execute()

        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid session")

        user = response.data[0]

        # Check if account is still active
        if not user.get('is_active', True):
            raise HTTPException(status_code=401, detail="Account has been disabled")

        return {
            "valid": True,
            "user_id": user['id'],
            "role": user['role'],
            "full_name": user['full_name'],
            "approval_status": user.get('approval_status', 'approved'),
            "is_active": user.get('is_active', True)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Session validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid session")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LearnSphere API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 