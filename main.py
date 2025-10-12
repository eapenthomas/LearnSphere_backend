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
    ]
    
    # Add any additional origins from environment variables
    additional_origins = os.environ.get('ADDITIONAL_CORS_ORIGINS', '')
    if additional_origins:
        origins.extend(additional_origins.split(','))
    
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

# Simple auth endpoints for testing
@app.post("/api/auth/login")
async def simple_login(request: dict):
    """Simple login endpoint for testing"""
    try:
        email = request.get("email", "")
        password = request.get("password", "")
        
        if email == "admin@learnsphere.com" and password == "admin123":
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": "admin-001",
                    "email": "admin@learnsphere.com",
                    "role": "admin",
                    "full_name": "System Administrator"
                },
                "token": "test-admin-token"
            }
        elif email == "teacher@learnsphere.com" and password == "teacher123":
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": "teacher-001",
                    "email": "teacher@learnsphere.com",
                    "role": "teacher",
                    "full_name": "Test Teacher"
                },
                "token": "test-teacher-token"
            }
        elif email == "student@learnsphere.com" and password == "student123":
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": "student-001",
                    "email": "student@learnsphere.com",
                    "role": "student",
                    "full_name": "Test Student"
                },
                "token": "test-student-token"
            }
        else:
            return {"success": False, "message": "Invalid credentials"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/auth/register")
async def simple_register(request: dict):
    """Simple register endpoint for testing"""
    try:
        email = request.get("email", "")
        password = request.get("password", "")
        full_name = request.get("full_name", "")
        role = request.get("role", "student")
        
        # Simulate successful registration
        user_id = f"user-{hash(email) % 10000}"
        
        return {
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": user_id,
                "email": email,
                "role": role,
                "full_name": full_name,
                "approval_status": "approved" if role == "student" else "pending"
            },
            "token": f"test-token-{user_id}"
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/auth/check-email")
async def check_email(request: dict):
    """Check if email exists"""
    try:
        email = request.get("email", "")
        
        # Test emails that exist
        existing_emails = [
            "admin@learnsphere.com",
            "teacher@learnsphere.com", 
            "student@learnsphere.com",
            "john@example.com",
            "jane@example.com"
        ]
        
        exists = email in existing_emails
        
        return {
            "exists": exists,
            "message": "Email exists" if exists else "Email available"
        }
    except Exception as e:
        return {"exists": False, "message": f"Error: {str(e)}"}

# Test data endpoints
@app.get("/api/test/courses")
async def get_test_courses():
    """Get test courses"""
    return {
        "courses": [
            {
                "id": "course-001",
                "title": "Introduction to Python Programming",
                "description": "Learn Python from basics to advanced concepts",
                "instructor": "Dr. Smith",
                "duration": "8 weeks",
                "price": 99.99,
                "category": "Programming",
                "level": "Beginner",
                "enrollment_count": 156,
                "rating": 4.8,
                "thumbnail": "/api/thumbnails/python-course.jpg"
            },
            {
                "id": "course-002", 
                "title": "Machine Learning Fundamentals",
                "description": "Comprehensive guide to ML algorithms and applications",
                "instructor": "Dr. Johnson",
                "duration": "12 weeks",
                "price": 199.99,
                "category": "Data Science",
                "level": "Intermediate",
                "enrollment_count": 89,
                "rating": 4.9,
                "thumbnail": "/api/thumbnails/ml-course.jpg"
            },
            {
                "id": "course-003",
                "title": "Web Development with React",
                "description": "Build modern web applications with React",
                "instructor": "Sarah Wilson",
                "duration": "10 weeks", 
                "price": 149.99,
                "category": "Web Development",
                "level": "Intermediate",
                "enrollment_count": 234,
                "rating": 4.7,
                "thumbnail": "/api/thumbnails/react-course.jpg"
            }
        ]
    }

@app.get("/api/test/ai-tutor")
async def ai_tutor_response(request: dict = None):
    """AI Tutor response for testing"""
    return {
        "response": "Hello! I'm your AI tutor. I can help you with:\n\n• Explaining concepts\n• Solving problems\n• Providing examples\n• Answering questions\n\nWhat would you like to learn about today?",
        "suggestions": [
            "Explain Python variables",
            "Help with this math problem",
            "Show me examples of React components",
            "What is machine learning?"
        ]
    }

@app.post("/api/test/quiz-generate")
async def generate_test_quiz(request: dict):
    """Generate test quiz"""
    topic = request.get("topic", "Python Programming")
    
    return {
        "quiz": {
            "id": "quiz-001",
            "title": f"Quiz: {topic}",
            "questions": [
                {
                    "id": "q1",
                    "question": "What is Python?",
                    "options": [
                        "A programming language",
                        "A type of snake", 
                        "A database",
                        "An operating system"
                    ],
                    "correct_answer": 0
                },
                {
                    "id": "q2", 
                    "question": "Which keyword is used to define a function in Python?",
                    "options": [
                        "function",
                        "def",
                        "define",
                        "func"
                    ],
                    "correct_answer": 1
                }
            ],
            "duration": 30
        }
    }

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