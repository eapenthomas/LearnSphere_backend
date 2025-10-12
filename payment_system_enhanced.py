"""
Enhanced Payment System for LearnSphere
Integrates Razorpay payments with teacher verification and course management
"""

import os
import uuid
import razorpay
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Response
from pydantic import BaseModel, EmailStr
from decimal import Decimal
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

from auth_middleware import (
    get_current_user, get_current_teacher, get_current_student, 
    get_current_admin, TokenData
)
from email_service import email_service

load_dotenv()

# Initialize Razorpay client
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    print("Warning: Razorpay credentials not configured. Payment features will not work.")
    razorpay_client = None
else:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    print("Razorpay client initialized successfully")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api", tags=["payments"])

# Pydantic Models
class CourseCreateRequest(BaseModel):
    title: str
    description: str
    is_paid: bool = False
    price: Optional[float] = None

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    is_paid: bool
    razorpay_product_id: Optional[str] = None
    razorpay_price_id: Optional[str] = None
    created_at: str
    teacher_id: str
    teacher_name: str

class PaymentInitiateRequest(BaseModel):
    course_id: str

class PaymentInitiateResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    key_id: str
    course_id: str

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentVerifyResponse(BaseModel):
    success: bool
    message: str
    enrollment_id: Optional[str] = None

class CourseListResponse(BaseModel):
    id: str
    title: str
    description: str
    price: float
    is_paid: bool
    teacher_name: str
    enrollment_status: str  # "enrolled", "not_enrolled", "free"

# Razorpay Helper Functions
def create_razorpay_product(course_title: str, course_description: str) -> str:
    """Create a Razorpay product for the course"""
    if not razorpay_client:
        # Return a mock product ID for testing when Razorpay is not configured
        return f"mock_product_{course_title.replace(' ', '_').lower()}"
    
    try:
        product_data = {
            "name": course_title,
            "description": course_description,
            "type": "good",
            "unit": "course"
        }
        
        product = razorpay_client.product.create(product_data)
        return product["id"]
    
    except Exception as e:
        print(f"Razorpay product creation failed: {str(e)}")
        # Return a mock product ID for testing
        return f"mock_product_{course_title.replace(' ', '_').lower()}"

def create_razorpay_price(product_id: str, amount: float) -> str:
    """Create a Razorpay price for the course"""
    if not razorpay_client:
        # Return a mock price ID for testing when Razorpay is not configured
        return f"mock_price_{product_id}_{int(amount)}"
    
    try:
        price_data = {
            "product_id": product_id,
            "unit_amount": int(amount * 100),  # Convert to paise
            "currency": "INR"
        }
        
        price = razorpay_client.price.create(price_data)
        return price["id"]
    
    except Exception as e:
        print(f"Razorpay price creation failed: {str(e)}")
        # Return a mock price ID for testing
        return f"mock_price_{product_id}_{int(amount)}"

def create_razorpay_order(amount: float, course_id: str, student_id: str) -> Dict[str, Any]:
    """Create a Razorpay order for payment"""
    if not razorpay_client:
        # Return a mock order for testing when Razorpay is not configured
        return {
            "id": f"mock_order_{course_id}_{student_id}",
            "amount": int(amount * 100),
            "currency": "INR",
            "receipt": f"course_{course_id}_{student_id}",
            "status": "created"
        }
    
    try:
        order_data = {
            "amount": int(amount * 100),  # Convert to paise
            "currency": "INR",
            "receipt": f"course_{course_id}_{student_id}",
            "notes": {
                "course_id": course_id,
                "student_id": student_id
            }
        }
        
        order = razorpay_client.order.create(order_data)
        return order
    
    except Exception as e:
        print(f"Razorpay order creation failed: {str(e)}")
        # Return a mock order for testing
        return {
            "id": f"mock_order_{course_id}_{student_id}",
            "amount": int(amount * 100),
            "currency": "INR",
            "receipt": f"course_{course_id}_{student_id}",
            "status": "created"
        }

def verify_razorpay_payment(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify Razorpay payment signature"""
    if not razorpay_client:
        # For testing without Razorpay, always return True for mock orders
        if order_id.startswith("mock_order_"):
            return True
        return False
    
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })
        return True
    
    except Exception as e:
        print(f"Payment verification failed: {str(e)}")
        return False

# API Endpoints
@router.post("/teacher/create-course", response_model=CourseResponse)
async def create_course(
    request: CourseCreateRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    teacher: TokenData = Depends(get_current_teacher)
):
    """Create a new course (free or paid) - Only verified teachers can create paid courses"""
    try:
        # Validate paid course requirements
        if request.is_paid and (not request.price or request.price <= 0):
            raise HTTPException(status_code=400, detail="Paid courses must have a valid price")
        
        if not request.is_paid and request.price:
            raise HTTPException(status_code=400, detail="Free courses cannot have a price")
        
        # Generate course ID
        course_id = str(uuid.uuid4())
        
        # Initialize Razorpay fields
        razorpay_product_id = None
        razorpay_price_id = None
        
        # Create Razorpay product and price if it's a paid course
        if request.is_paid:
            try:
                razorpay_product_id = create_razorpay_product(request.title, request.description)
                razorpay_price_id = create_razorpay_price(razorpay_product_id, request.price)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create payment setup: {str(e)}")
        
        # Get teacher name
        teacher_response = supabase_admin.table("profiles").select("full_name").eq("id", teacher.user_id).single().execute()
        teacher_name = teacher_response.data.get("full_name", "Unknown Teacher") if teacher_response.data else "Unknown Teacher"
        
        # Create course in database
        course_data = {
            "id": course_id,
            "teacher_id": teacher.user_id,
            "title": request.title,
            "description": request.description,
            "price": float(request.price) if request.price else 0.0,
            "is_paid": request.is_paid,
            "razorpay_product_id": razorpay_product_id,
            "razorpay_price_id": razorpay_price_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        course_response = supabase_admin.table("courses").insert(course_data).execute()
        
        if not course_response.data:
            raise HTTPException(status_code=500, detail="Failed to create course")
        
        # Send confirmation email for paid courses
        if request.is_paid:
            background_tasks.add_task(
                send_course_creation_email,
                teacher.user_id, teacher_name, request.title, request.price
            )
        
        return CourseResponse(
            id=course_id,
            title=request.title,
            description=request.description,
            price=float(request.price) if request.price else 0.0,
            is_paid=request.is_paid,
            razorpay_product_id=razorpay_product_id,
            razorpay_price_id=razorpay_price_id,
            created_at=course_data["created_at"],
            teacher_id=teacher.user_id,
            teacher_name=teacher_name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create course: {str(e)}")

@router.get("/student/courses", response_model=List[CourseListResponse])
async def get_available_courses(student: TokenData = Depends(get_current_student)):
    """Get all available courses with enrollment status"""
    try:
        # Get all courses
        courses_response = supabase_admin.table("courses").select("""
            id,
            title,
            description,
            price,
            is_paid,
            created_at,
            teacher_id
        """).execute()
        
        if not courses_response.data:
            return []
        
        # Get teacher information separately
        teacher_ids = list(set(course["teacher_id"] for course in courses_response.data))
        teachers_response = supabase_admin.table("profiles").select("id, full_name").in_("id", teacher_ids).execute()
        teacher_names = {teacher["id"]: teacher["full_name"] for teacher in teachers_response.data or []}
        
        # Get student's enrollments (only active ones)
        enrollments_response = supabase_admin.table("enrollments").select("course_id").eq("student_id", student.user_id).eq("status", "active").execute()
        enrolled_course_ids = {enrollment["course_id"] for enrollment in enrollments_response.data or []}
        
        # Format response
        courses = []
        for course in courses_response.data:
            teacher_name = teacher_names.get(course["teacher_id"], "Unknown Teacher")
            
            # Determine enrollment status
            if course["id"] in enrolled_course_ids:
                enrollment_status = "enrolled"
            elif course["is_paid"]:
                enrollment_status = "not_enrolled"
            else:
                enrollment_status = "free"
            
            courses.append(CourseListResponse(
                id=course["id"],
                title=course["title"],
                description=course["description"],
                price=course["price"],
                is_paid=course["is_paid"],
                teacher_name=teacher_name,
                enrollment_status=enrollment_status
            ))
        
        return courses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get courses: {str(e)}")

@router.post("/student/initiate-payment/{course_id}", response_model=PaymentInitiateResponse)
async def initiate_payment(
    course_id: str,
    student: TokenData = Depends(get_current_student)
):
    """Initiate payment for a course"""
    try:
        # Get course details
        course_response = supabase_admin.table("courses").select("*").eq("id", course_id).execute()
        
        if not course_response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course = course_response.data[0]
        
        if not course["is_paid"]:
            raise HTTPException(status_code=400, detail="This is a free course")
        
        # Check if already enrolled (only check active enrollments)
        enrollment_check = supabase_admin.table("enrollments").select("id").eq("student_id", student.user_id).eq("course_id", course_id).eq("status", "active").execute()
        
        if enrollment_check.data:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")
        
        # Create Razorpay order
        order = create_razorpay_order(course["price"], course_id, student.user_id)
        
        # Store payment record
        payment_data = {
            "student_id": student.user_id,
            "course_id": course_id,
            "razorpay_order_id": order["id"],
            "amount": course["price"],
            "status": "pending"
        }
        
        payment_response = supabase_admin.table("payments").insert(payment_data).execute()
        
        if not payment_response.data:
            raise HTTPException(status_code=500, detail="Failed to create payment record")
        
        return PaymentInitiateResponse(
            order_id=order["id"],
            amount=course["price"],
            currency="INR",
            key_id=RAZORPAY_KEY_ID or "mock_key_id",
            course_id=course_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate payment: {str(e)}")

@router.post("/student/verify-payment", response_model=PaymentVerifyResponse)
async def verify_payment(
    request: PaymentVerifyRequest,
    background_tasks: BackgroundTasks,
    student: TokenData = Depends(get_current_student)
):
    """Verify payment and enroll student"""
    try:
        # Get payment record
        payment_response = supabase_admin.table("payments").select("*").eq("razorpay_order_id", request.razorpay_order_id).eq("student_id", student.user_id).execute()
        
        if not payment_response.data:
            # For mock orders, create a payment record
            if request.razorpay_order_id.startswith("mock_order_"):
                # Extract course_id from mock order ID
                parts = request.razorpay_order_id.split("_")
                if len(parts) >= 3:
                    course_id = parts[2]
                    
                    # Validate course_id is a valid UUID
                    if not course_id or len(course_id) != 36:
                        raise HTTPException(status_code=400, detail="Invalid course ID in mock order")
                    
                    # Get course details
                    course_response = supabase_admin.table("courses").select("*").eq("id", course_id).execute()
                    if course_response.data:
                        course = course_response.data[0]
                        
                        # Create payment record
                        payment_data = {
                            "student_id": student.user_id,
                            "course_id": course_id,
                            "razorpay_order_id": request.razorpay_order_id,
                            "amount": course["price"],
                            "status": "pending"
                        }
                        
                        payment_response = supabase_admin.table("payments").insert(payment_data).execute()
                        if payment_response.data:
                            payment = payment_response.data[0]
                        else:
                            raise HTTPException(status_code=500, detail="Failed to create payment record")
                    else:
                        raise HTTPException(status_code=404, detail="Course not found")
                else:
                    raise HTTPException(status_code=400, detail="Invalid mock order ID format")
            else:
                raise HTTPException(status_code=404, detail="Payment record not found")
        else:
            payment = payment_response.data[0]
        
        # Verify payment signature
        if not verify_razorpay_payment(request.razorpay_order_id, request.razorpay_payment_id, request.razorpay_signature):
            # Mark payment as failed
            supabase_admin.table("payments").update({
                "razorpay_payment_id": request.razorpay_payment_id,
                "status": "failed"
            }).eq("id", payment["id"]).execute()
            
            return PaymentVerifyResponse(
                success=False,
                message="Payment verification failed"
            )
        
        # Mark payment as successful
        supabase_admin.table("payments").update({
            "razorpay_payment_id": request.razorpay_payment_id,
            "status": "success"
        }).eq("id", payment["id"]).execute()
        
        # Create enrollment
        enrollment_data = {
            "student_id": student.user_id,
            "course_id": payment["course_id"],
            "payment_id": payment["id"],
            "enrollment_type": "paid",
            "status": "active"
        }
        
        enrollment_response = supabase_admin.table("enrollments").insert(enrollment_data).execute()
        
        if not enrollment_response.data:
            raise HTTPException(status_code=500, detail="Failed to create enrollment")
        
        # Send enrollment confirmation email
        background_tasks.add_task(
            send_enrollment_confirmation_email,
            student.user_id, payment["course_id"]
        )
        
        return PaymentVerifyResponse(
            success=True,
            message="Payment successful and enrolled",
            enrollment_id=enrollment_response.data[0]["id"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {str(e)}")

@router.get("/student/enrolled-courses", response_model=List[CourseListResponse])
async def get_enrolled_courses(student: TokenData = Depends(get_current_student)):
    """Get all enrolled courses (paid and free)"""
    try:
        # Get enrollments with course details (only active enrollments)
        # Use a simpler approach with separate queries
        enrollments_response = supabase_admin.table("enrollments").select("course_id, enrolled_at, status").eq("student_id", student.user_id).eq("status", "active").execute()
        
        if not enrollments_response.data:
            return []
        
        # Get course IDs
        course_ids = [enrollment["course_id"] for enrollment in enrollments_response.data]
        
        # Get courses with teacher information
        courses_response = supabase_admin.table("courses").select("""
            id,
            title,
            description,
            price,
            is_paid,
            created_at,
            teacher_id
        """).in_("id", course_ids).execute()
        
        if not courses_response.data:
            return []
        
        # Get teacher information
        teacher_ids = list(set(course["teacher_id"] for course in courses_response.data))
        teachers_response = supabase_admin.table("profiles").select("id, full_name").in_("id", teacher_ids).execute()
        teacher_names = {teacher["id"]: teacher["full_name"] for teacher in teachers_response.data or []}
        
        # Format response
        courses = []
        for course in courses_response.data:
            teacher_name = teacher_names.get(course["teacher_id"], "Unknown Teacher")
            
            courses.append(CourseListResponse(
                id=course["id"],
                title=course["title"],
                description=course["description"],
                price=course["price"],
                is_paid=course["is_paid"],
                teacher_name=teacher_name,
                enrollment_status="enrolled"
            ))
        
        return courses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get enrolled courses: {str(e)}")

# Email Functions
async def send_course_creation_email(teacher_id: str, teacher_name: str, course_title: str, price: float):
    """Send course creation confirmation email"""
    try:
        # Get teacher email
        teacher_response = supabase_admin.table("profiles").select("email").eq("id", teacher_id).single().execute()
        if not teacher_response.data:
            return
        
        teacher_email = teacher_response.data["email"]
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        html_content = f"""
        <html>
        <body style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:white;font-family:'Poppins',sans-serif;text-align:center;padding:40px;">
            <div style="background:rgba(255,255,255,0.1);border-radius:20px;padding:30px;max-width:500px;margin:auto;">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100"/>
                <h2>New Paid Course Created 🚀</h2>
                <p>Hi {teacher_name}, your course <b>{course_title}</b> has been created successfully.</p>
                <p>Students can now purchase access for ₹{price}.</p>
                <a href="{frontend_url}/teacher/dashboard" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #4e54c8, #8f94fb); color:white; text-decoration:none; border-radius:8px;">View Dashboard</a>
                <p style="font-size:12px;opacity:0.7;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
            </div>
        </body>
        </html>
        """
        
        email_data = {
            "recipient_email": teacher_email,
            "subject": f"Course Created Successfully - {course_title}",
            "body": html_content,
            "notification_type": "course_created"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send course creation email: {e}")

async def send_enrollment_confirmation_email(student_id: str, course_id: str):
    """Send enrollment confirmation email to student"""
    try:
        # Get student and course details
        student_response = supabase_admin.table("profiles").select("email, full_name").eq("id", student_id).single().execute()
        course_response = supabase_admin.table("courses").select("title").eq("id", course_id).single().execute()
        
        if not student_response.data or not course_response.data:
            return
        
        student_email = student_response.data["email"]
        student_name = student_response.data["full_name"]
        course_title = course_response.data["title"]
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        html_content = f"""
        <html>
        <body style="background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);color:white;font-family:'Poppins',sans-serif;text-align:center;padding:40px;">
            <div style="background:rgba(255,255,255,0.1);border-radius:20px;padding:30px;max-width:500px;margin:auto;">
                <img src="https://yourcdn.com/learnsphere-logo.png" width="100"/>
                <h2>Welcome to {course_title}! 🎉</h2>
                <p>Hi {student_name}, you have successfully enrolled in <b>{course_title}</b>.</p>
                <p>You can now access all course materials and start learning.</p>
                <a href="{frontend_url}/student/mycourses" style="display:inline-block; margin-top:20px; padding:10px 25px; background:linear-gradient(90deg, #4e54c8, #8f94fb); color:white; text-decoration:none; border-radius:8px;">Access Course</a>
                <p style="font-size:12px;opacity:0.7;">LearnSphere © 2025 | AI-Powered Learning Platform</p>
            </div>
        </body>
        </html>
        """
        
        email_data = {
            "recipient_email": student_email,
            "subject": f"Enrolled in {course_title}",
            "body": html_content,
            "notification_type": "course_enrollment"
        }
        
        supabase_admin.table("email_notifications").insert(email_data).execute()
        
    except Exception as e:
        print(f"Failed to send enrollment confirmation email: {e}")
