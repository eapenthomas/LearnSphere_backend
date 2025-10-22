from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from datetime import datetime
from auth_middleware import get_current_user, TokenData
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

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
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server
        # Vercel frontend URLs
        "https://learn-sphere-frontend-black.vercel.app",
        "https://learn-sphere-frontend-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-git-main-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-grfp9yq65-eapenthomas-projects.vercel.app",
        # Additional Vercel deployment URLs
        "https://learn-sphere-frontend-dmoxpjl0j-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-9v5k7y8x2-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-8x3k2n5m1-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-7w2j1l4k9-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-6v1i0k3j8-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-5u0h9j2i7-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-4t9g8i1h6-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-3s8f7h0g5-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-2r7e6g9f4-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-1q6d5f8e3-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-0p5c4e7d2-eapenthomas-projects.vercel.app",
    ]
    
    # Add any additional origins from environment variables
    additional_origins = os.environ.get('ADDITIONAL_CORS_ORIGINS', '')
    if additional_origins:
        origins.extend(additional_origins.split(','))
    
    # Add wildcard pattern for Vercel deployments
    origins.append("https://*.vercel.app")
    
    # Add specific Vercel pattern matching
    origins.extend([
        "https://learn-sphere-frontend-black.vercel.app",
        "https://learn-sphere-frontend-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-git-main-eapenthomas-projects.vercel.app"
    ])
    
    return origins

# Add CORS middleware with comprehensive handling
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "Cache-Control", "Pragma"],
)

# Add custom CORS handler for better wildcard support
@app.middleware("http")
async def custom_cors_handler(request: Request, call_next):
    """Custom CORS handler for better wildcard support"""
    origin = request.headers.get("origin")
    
    # Handle preflight requests
    if request.method == "OPTIONS":
        response = JSONResponse(content={"message": "OK"})
        if origin:
            # Check if origin matches any allowed pattern
            allowed_origins = get_allowed_origins()
            is_allowed = False
            
            for allowed_origin in allowed_origins:
                if allowed_origin == "*" or origin == allowed_origin:
                    is_allowed = True
                    break
                elif allowed_origin.endswith("*.vercel.app") and origin.endswith(".vercel.app"):
                    is_allowed = True
                    break
            
            if is_allowed:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, Pragma"
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Max-Age"] = "86400"
        
        return response
    
    response = await call_next(request)
    
    # Add CORS headers to response
    if origin:
        allowed_origins = get_allowed_origins()
        is_allowed = False
        
        for allowed_origin in allowed_origins:
            if allowed_origin == "*" or origin == allowed_origin:
                is_allowed = True
                break
            elif allowed_origin.endswith("*.vercel.app") and origin.endswith(".vercel.app"):
                is_allowed = True
                break
        
        if is_allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Add global exception handler for CORS
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper CORS headers"""
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    
    # Add CORS headers to all error responses
    origin = request.headers.get("origin")
    if origin and any(origin.startswith(prefix) for prefix in [
        "http://localhost", "https://learn-sphere-frontend", "https://*.vercel.app"
    ]):
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Add auto-refresh middleware early
@app.middleware("http")
async def auto_refresh_middleware(request, call_next):
    # Simple middleware implementation
    response = await call_next(request)
    return response

# Import routers at module level for proper registration
try:
    print("🚀 Loading LearnSphere modules...")
    
    # Import routers in order of importance (most used first)
    print("📦 Importing auth router...")
    from auth import router as auth_router, AuthService
    print(f"✅ Auth router imported: {auth_router}")
    from google_auth_v2 import router as google_auth_router
    print(f"✅ Google auth router imported (v2)")
    from auth_refresh_api import router as auth_refresh_router
    from notification_api import router as notification_router
    from notifications_api_enhanced import router as notifications_enhanced_router
    from activity_notifications_api import router as activity_notifications_router
    from teacher_activity_notifications_api import router as teacher_activity_notifications_router
    from course_completion_api import router as course_completion_router
    from course_api import router as course_router
    from enrollment_api import router as enrollment_router
    from assignments_api import router as assignments_router
    from quiz_api import router as quiz_router
    from thumbnail_api import router as thumbnail_router
    from file_download_api import router as file_download_router
    from profile_picture_api import router as profile_picture_router
    from course_materials_v2 import router as course_materials_router
    
    # Import admin routers
    from admin_api import router as admin_router
    from admin_dashboard_api import router as admin_dashboard_router
    from admin_notifications_api import router as admin_notifications_router
    
    # Import teacher routers
    from teacher_analytics_api import router as teacher_analytics_router
    from teacher_reports_api import router as teacher_reports_router
    from teacher_rating_api import router as teacher_rating_router
    from teacher_dashboard_optimized import router as teacher_dashboard_router
    
    # Import other routers (with error handling for optional dependencies)
    try:
        from ai_usage_api import router as ai_usage_router
        print("✅ AI usage router imported")
    except ImportError as e:
        print(f"⚠️  AI usage router failed to import: {e}")
        ai_usage_router = None

    try:
        from ai_tutor_api import router as ai_tutor_router
        print("✅ AI tutor router imported")
    except ImportError as e:
        print(f"⚠️  AI tutor router failed to import: {e}")
        ai_tutor_router = None

    try:
        from notes_summarizer_api import router as notes_router
        print("✅ Notes router imported")
    except ImportError as e:
        print(f"⚠️  Notes router failed to import: {e}")
        notes_router = None
    try:
        from forum_api import router as forum_router
        print("✅ Forum router imported")
    except ImportError as e:
        print(f"⚠️  Forum router failed to import: {e}")
        forum_router = None

    try:
        from student_deadlines_api import router as student_deadlines_router
        print("✅ Student deadlines router imported")
    except ImportError as e:
        print(f"⚠️  Student deadlines router failed to import: {e}")
        student_deadlines_router = None

    try:
        from course_progress_api import router as progress_router
        print("✅ Course progress router imported")
    except ImportError as e:
        print(f"⚠️  Course progress router failed to import: {e}")
        progress_router = None

    try:
        from quiz_generator_api import router as quiz_generator_router
        print("✅ Quiz generator router imported")
    except ImportError as e:
        print(f"⚠️  Quiz generator router failed to import: {e}")
        quiz_generator_router = None

    try:
        from activity_export_api import router as activity_export_router
        print("✅ Activity export router imported")
    except ImportError as e:
        print(f"⚠️  Activity export router failed to import: {e}")
        activity_export_router = None

    try:
        from user_management_api import router as user_management_router
        print("✅ User management router imported")
    except ImportError as e:
        print(f"⚠️  User management router failed to import: {e}")
        user_management_router = None

    try:
        from teacher_verification_enhanced import router as teacher_verification_router
        print("✅ Teacher verification router imported")
    except ImportError as e:
        print(f"⚠️  Teacher verification router failed to import: {e}")
        teacher_verification_router = None

    try:
        from payment_system_enhanced import router as payment_router
        print("✅ Payment router imported")
    except ImportError as e:
        print(f"⚠️  Payment router failed to import: {e}")
        payment_router = None

    try:
        from system_settings_api import router as system_settings_router
        print("✅ System settings router imported")
    except ImportError as e:
        print(f"⚠️  System settings router failed to import: {e}")
        system_settings_router = None
    
    # Include routers in optimized order (most used first)
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(google_auth_router, prefix="/api/auth", tags=["Google Auth"])
    app.include_router(auth_refresh_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(notification_router)
    app.include_router(notifications_enhanced_router)
    app.include_router(activity_notifications_router)
    app.include_router(teacher_activity_notifications_router)
    app.include_router(course_completion_router)
    app.include_router(course_router)
    app.include_router(enrollment_router)
    app.include_router(assignments_router)
    app.include_router(quiz_router)
    app.include_router(thumbnail_router)
    app.include_router(file_download_router)
    app.include_router(profile_picture_router)
    app.include_router(course_materials_router)
    app.include_router(admin_router)
    app.include_router(admin_dashboard_router)
    app.include_router(admin_notifications_router)
    app.include_router(teacher_analytics_router)
    app.include_router(teacher_reports_router)
    app.include_router(teacher_rating_router)
    app.include_router(teacher_dashboard_router)
    
    # Include system settings router
    if system_settings_router:
        app.include_router(system_settings_router)
    
    # Include optional routers only if they were imported successfully
    if ai_usage_router:
        app.include_router(ai_usage_router)
    if ai_tutor_router:
        app.include_router(ai_tutor_router)
    if notes_router:
        app.include_router(notes_router)
    # Include optional routers only if they were imported successfully
    if forum_router:
        app.include_router(forum_router)
    if student_deadlines_router:
        app.include_router(student_deadlines_router)
    if progress_router:
        app.include_router(progress_router)
    if quiz_generator_router:
        app.include_router(quiz_generator_router)
    if activity_export_router:
        app.include_router(activity_export_router)
    if user_management_router:
        app.include_router(user_management_router)
    if teacher_verification_router:
        app.include_router(teacher_verification_router)
    if payment_router:
        app.include_router(payment_router)
    
    print("✅ All modules loaded successfully")
    
except Exception as e:
    print(f"❌ Error loading modules: {e}")
    print("⚠️  Some features may not be available")
    import traceback
    traceback.print_exc()

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "LearnSphere API is running"}

# Test endpoint to verify app is working
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint working", "timestamp": "2025-01-12"}

# Simple login test endpoint
@app.post("/api/test-login")
async def test_login():
    return {"message": "Test login endpoint working"}

# Test teacher creation endpoint
@app.post("/api/test/create-teacher")
async def create_test_teacher():
    """Create a fully operational test teacher with Supabase Auth account"""
    try:
        from supabase import create_client
        import uuid
        import hashlib
        import secrets
        
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        email = "aura@example.com"
        password = "testpassword123"
        
        # Check if test teacher already exists in profiles
        existing_profile = supabase.table('profiles').select('*').eq('email', email).execute()
        
        # Check if auth user exists
        try:
            auth_users = supabase.auth.admin.list_users()
            auth_user_exists = any(user.email == email for user in auth_users)
        except:
            auth_user_exists = False
        
        # Always update password fields even if teacher exists
        print("✅ Updating test teacher with password fields for direct login")
        
        # Create or update auth user
        try:
            if not auth_user_exists:
                # Create new auth user
                auth_result = supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {
                        "full_name": "Aura Test Teacher",
                        "role": "teacher"
                    }
                })
                auth_user_id = auth_result.user.id
                print(f"✅ Created auth user: {auth_user_id}")
            else:
                # Update existing auth user password
                auth_users = supabase.auth.admin.list_users()
                auth_user = next((user for user in auth_users if user.email == email), None)
                if auth_user:
                    auth_user_id = auth_user.id
                    supabase.auth.admin.update_user_by_id(auth_user_id, {
                        "password": password,
                        "email_confirm": True
                    })
                    print(f"✅ Updated auth user: {auth_user_id}")
                else:
                    raise Exception("Auth user not found")
        except Exception as auth_error:
            print(f"Auth user creation/update failed: {auth_error}")
            # Fallback: try to get user ID from existing profile
            if existing_profile.data:
                auth_user_id = existing_profile.data[0]["id"]
            else:
                auth_user_id = str(uuid.uuid4())
        
        # Create custom password hash for direct login
        import hashlib
        import secrets
        
        salt, hashed_password = AuthService.hash_password(password)
        
        # Create or update profile
        teacher_data = {
            "id": auth_user_id,  # Use same ID as auth user
            "email": email,
            "full_name": "Aura Test Teacher",
            "role": "teacher",
            "approval_status": "approved",
            "is_active": True,
            "institution_name": "Test University",
            "is_verified": True,
            "ocr_status": "verified",
            "ai_confidence": 95,
            "verification_reason": "Test teacher for testing purposes",
            # Add custom password fields for direct login
            "password_salt": salt,
            "password_hash": hashed_password
        }
        
        if existing_profile.data:
            # Update existing profile
            result = supabase.table('profiles').update(teacher_data).eq('email', email).execute()
            print("✅ Updated existing profile")
        else:
            # Create new profile
            result = supabase.table('profiles').insert(teacher_data).execute()
            print("✅ Created new profile")
        
        return {
            "message": "Test teacher created/updated successfully and is fully operational",
            "teacher": result.data[0] if result.data else teacher_data,
            "login_info": {
                "email": email,
                "password": password,
                "note": "Test teacher is ready to use - you can login now!"
            },
            "status": "ready",
            "auth_user_id": auth_user_id
        }
        
    except Exception as e:
        print(f"Error creating test teacher: {e}")
        return {"error": f"Failed to create test teacher: {str(e)}", "details": str(e)}

# Test authentication endpoint
@app.get("/api/test/auth-check")
async def test_auth_check():
    """Test endpoint to check authentication status"""
    return {
        "message": "Authentication test endpoint working",
        "timestamp": "2025-01-12",
        "note": "This endpoint doesn't require authentication"
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to LearnSphere API", "docs": "/docs"}

@app.get("/api/cors-test")
async def cors_test():
    """Test endpoint to verify CORS is working"""
    return {"message": "CORS is working", "status": "ok", "timestamp": datetime.now().isoformat()}

@app.options("/api/profile-pictures/{user_id}")
async def profile_pictures_options(user_id: str):
    """Handle OPTIONS requests for profile pictures endpoint"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With, Accept, Origin, Cache-Control, Pragma",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
    )

@app.get("/api/profile")
async def get_user_profile(current_user: TokenData = Depends(get_current_user)):
    """Get current user's profile information"""
    try:
        # Get user profile from Supabase
        response = supabase.table("profiles").select("*").eq("id", current_user.user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = response.data
        
        return {
            "id": profile.get("id"),
            "email": profile.get("email"),
            "full_name": profile.get("full_name"),
            "phone": profile.get("phone"),
            "bio": profile.get("bio"),
            "location": profile.get("location"),
            "role": profile.get("role"),
            "avatar_url": profile.get("avatar_url"),
            "created_at": profile.get("created_at"),
            "updated_at": profile.get("updated_at")
        }
    except Exception as e:
        print(f"Error fetching profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")

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
