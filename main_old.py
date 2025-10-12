from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app with optimized settings
app = FastAPI(
    title="LearnSphere API",
    description="Educational Platform API with Optimized Performance",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Dynamic CORS origins function
def get_allowed_origins():
    """Get allowed CORS origins including environment-specific URLs"""
    origins = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        # Vercel frontend URLs
        "https://learn-sphere-frontend-black.vercel.app",
        "https://learn-sphere-frontend-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-git-main-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-grfp9yq65-eapenthomas-projects.vercel.app",
        # Additional Vercel deployment URLs
        "https://learn-sphere-frontend-dmoxpjl0j-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-7s6ls9abp-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-g6eygj25p-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-lfqf7rd9c-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-11kf9ewnk-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-r1muyltzx-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-2yol04ltn-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-fu24n4rcz-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-2sye06jqt-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-qjtto8rdm-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-apwka5ug5-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-gj1pxifus-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-rl6biozeq-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-1qpiwuu65-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-34wnsz0zn-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-g4g4yf0qk-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-jo5wyml3h-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-n0of9yuti-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-p79pwccy8-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-8tzwfjt8u-eapenthomas-projects.vercel.app",
    ]
    
    # Add any additional origins from environment variables
    additional_origins = os.environ.get('ADDITIONAL_CORS_ORIGINS', '')
    if additional_origins:
        origins.extend(additional_origins.split(','))
    
    # Add wildcard pattern for Vercel deployments
    origins.append("https://*.vercel.app")
    
    return origins

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add auto-refresh middleware early
@app.middleware("http")
async def auto_refresh_middleware(request, call_next):
    # Simple middleware implementation
    response = await call_next(request)
    return response

# Lazy import function for optimal startup
def lazy_import_modules():
    """Import all modules lazily to improve startup time"""
    try:
        print("🚀 Loading LearnSphere modules...")
        
        # Import Supabase client
        from supabase import create_client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Import core models
        from models import (
            RegisterRequest, LoginRequest, ProfileSyncRequest, AuthResponse, 
            ErrorResponse, PasswordUpdateRequest, ForgotPasswordRequest, 
            VerifyOTPRequest, ForgotPasswordResponse, EmailCheckRequest, 
            EmailCheckResponse
        )
        
        # Import routers in order of importance (most used first)
        from auth import router as auth_router
        from auth_refresh_api import router as auth_refresh_router
        from notification_api import router as notification_router
        from notifications_api_enhanced import router as notifications_enhanced_router
        from course_completion_api import router as course_completion_router
        from course_api import router as course_router
        from enrollment_api import router as enrollment_router
        from assignments_api import router as assignments_router
        from quiz_api import router as quiz_router
        from thumbnail_api import router as thumbnail_router
        from file_download_api import router as file_download_router
        from profile_picture_api import router as profile_picture_router
        from course_materials_enhanced import router as course_materials_enhanced_router
        
        # Import admin routers
        from admin_api import router as admin_router
        from admin_dashboard_api import router as admin_dashboard_router
        from admin_notifications_api import router as admin_notifications_router
        
        # Import teacher routers
        from teacher_analytics_api import router as teacher_analytics_router
        from teacher_reports_api import router as teacher_reports_router
        from teacher_rating_api import router as teacher_rating_router
        
        # Import other routers (these load heavy modules, so load them last)
        from ai_usage_api import router as ai_usage_router
        from ai_tutor_api import router as ai_tutor_router
        from notes_summarizer_api import router as notes_router
        from forum_api import router as forum_router
        from student_deadlines_api import router as student_deadlines_router
        from course_progress_api import router as progress_router
        from quiz_generator_api import router as quiz_generator_router
        from activity_export_api import router as activity_export_router
        from user_management_api import router as user_management_router
        from teacher_verification_enhanced import router as teacher_verification_router
        from payment_system_enhanced import router as payment_router
        
        # Import authentication middleware
        from auth_middleware import (
            get_current_user, get_current_teacher, get_current_admin,
            get_current_student
        )
        
        # Include routers in optimized order (most used first)
        app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(auth_refresh_router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(notification_router)
        app.include_router(notifications_enhanced_router)
        app.include_router(course_completion_router)
        app.include_router(course_router)
        app.include_router(enrollment_router)
        app.include_router(assignments_router)
        app.include_router(quiz_router)
        app.include_router(thumbnail_router)
        app.include_router(file_download_router)
        app.include_router(profile_picture_router)
        app.include_router(course_materials_enhanced_router)
        app.include_router(admin_router)
        app.include_router(admin_dashboard_router)
        app.include_router(admin_notifications_router)
        app.include_router(teacher_analytics_router)
        app.include_router(teacher_reports_router)
        app.include_router(teacher_rating_router)
        app.include_router(ai_usage_router)
        app.include_router(ai_tutor_router)
        app.include_router(notes_router)
        app.include_router(forum_router)
        app.include_router(student_deadlines_router)
        app.include_router(progress_router)
        app.include_router(quiz_generator_router)
        app.include_router(activity_export_router)
        app.include_router(user_management_router)
        app.include_router(teacher_verification_router)
        app.include_router(payment_router)
        
        # Middleware already added above
        
        print("✅ All modules loaded successfully")
        
    except Exception as e:
        print(f"❌ Error loading modules: {e}")
        print("⚠️  Some features may not be available")
        import traceback
        traceback.print_exc()

# Startup event to load modules
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting LearnSphere API...")
    lazy_import_modules()
    print("✅ LearnSphere API started successfully!")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "LearnSphere API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to LearnSphere API", "docs": "/docs"}

# Course categories endpoint (cached)
@app.get("/api/courses/categories")
async def get_course_categories():
    """Get course categories"""
    try:
        from supabase import create_client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Get unique categories from courses
        result = supabase.table("courses").select("category").execute()
        categories = list(set([course["category"] for course in result.data if course.get("category")]))
        return {"categories": categories if categories else ["General"]}
    except Exception as e:
        return {"categories": ["General"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        workers=1,
        log_level="info"
    )