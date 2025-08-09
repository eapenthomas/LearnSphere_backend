from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthService
from models import RegisterRequest, LoginRequest, ProfileSyncRequest, AuthResponse, ErrorResponse, PasswordUpdateRequest, ForgotPasswordRequest, VerifyOTPRequest, ForgotPasswordResponse, EmailCheckRequest, EmailCheckResponse
from notification_api import router as notification_router
from admin_api import router as admin_router
from quiz_api import router as quiz_router

app = FastAPI(
    title="LearnSphere API",
    description="E-learning platform API with authentication and user management",
    version="1.0.0"
)

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
app.include_router(quiz_router)

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LearnSphere API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 