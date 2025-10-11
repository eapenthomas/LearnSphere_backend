# 📚 Course Management System - LearnSphere

A comprehensive course management system that allows teachers to create and manage courses, and students to enroll and track their progress with real-time analytics.

## 🌟 Overview

The Course Management System is the core of LearnSphere, enabling teachers to create structured learning experiences and students to access educational content. It includes course creation, enrollment management, **automatic progress tracking**, real-time analytics, and course materials organization with **Coursera/Udemy-style progress monitoring**.

## ✨ Features

### 👨‍🏫 **Teacher Features**

- **Course Creation** - Create courses with rich descriptions and custom thumbnails
- **Thumbnail Upload** - Upload custom course images stored in Supabase Storage
- **Course Management** - Edit, update, and organize courses
- **Student Management** - View enrolled students and their progress
- **Content Organization** - Structure course materials and resources
- **Analytics** - Track course performance and engagement

### 👨‍🎓 **Student Features**

- **Course Discovery** - Browse available courses
- **Easy Enrollment** - One-click course enrollment
- **Progress Tracking** - Monitor learning progress
- **Course Materials** - Access all course resources
- **Dashboard View** - Personalized course overview

### 🔧 **System Features**

- **Role-Based Access** - Different views for teachers and students
- **Real-time Updates** - Live course data synchronization
- **Search & Filter** - Find courses easily
- **Responsive Design** - Works on all devices

## 🏗️ Architecture

### Frontend Structure

#### **Course Components**

```
frontend/src/pages/
├── teacher/
│   ├── Courses.jsx         # Teacher course management
│   ├── CreateCourse.jsx    # Course creation form
│   └── CourseDetails.jsx   # Individual course management
├── student/
│   ├── Dashboard.jsx       # Student course overview
│   ├── AllCourses.jsx      # Course discovery page
│   └── MyCourses.jsx       # Enrolled courses
└── shared/
    └── CourseCard.jsx      # Reusable course card component
```

#### **Course Context**

```javascript
// frontend/src/context/CourseContext.jsx
const CourseContext = {
  courses: [], // All courses
  myCourses: [], // User's courses
  loading: false, // Loading state
  createCourse: () => {}, // Create new course
  enrollInCourse: () => {}, // Enroll in course
  updateCourse: () => {}, // Update course
};
```

### Backend Structure

#### **Course API Module**

```
backend/
├── course_api.py           # Course management endpoints
├── enrollment_api.py       # Enrollment management
├── course_permissions.py   # Access control
└── models.py              # Course data models
```

## 🔧 Implementation Details

### Frontend Implementation

#### **Teacher Course Management**

```jsx
// frontend/src/pages/teacher/Courses.jsx
import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";

const TeacherCourses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchTeacherCourses();
  }, []);

  const fetchTeacherCourses = async () => {
    try {
      const response = await fetch(`/api/courses/teacher/${user.id}`);
      const data = await response.json();
      setCourses(data);
    } catch (error) {
      toast.error("Failed to load courses");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (courseData) => {
    try {
      const response = await fetch("/api/courses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(courseData),
      });

      if (response.ok) {
        toast.success("Course created successfully!");
        fetchTeacherCourses(); // Refresh list
      }
    } catch (error) {
      toast.error("Failed to create course");
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Courses</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
        >
          Create New Course
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <CourseCard
            key={course.id}
            course={course}
            isTeacher={true}
            onEdit={handleEditCourse}
          />
        ))}
      </div>
    </div>
  );
};
```

#### **Student Course Discovery**

```jsx
// frontend/src/pages/student/AllCourses.jsx
const AllCourses = () => {
  const [courses, setCourses] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("all");

  const filteredCourses = courses.filter((course) => {
    const matchesSearch = course.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesFilter = filter === "all" || course.category === filter;
    return matchesSearch && matchesFilter;
  });

  const handleEnrollment = async (courseId) => {
    try {
      const response = await fetch(`/api/enrollments`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          course_id: courseId,
          student_id: user.id,
        }),
      });

      if (response.ok) {
        toast.success("Successfully enrolled in course!");
        // Update UI to reflect enrollment
      }
    } catch (error) {
      toast.error("Enrollment failed");
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-4">All Courses</h1>

        {/* Search and Filter */}
        <div className="flex gap-4 mb-4">
          <input
            type="text"
            placeholder="Search courses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="all">All Categories</option>
            <option value="programming">Programming</option>
            <option value="design">Design</option>
            <option value="business">Business</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCourses.map((course) => (
          <CourseCard
            key={course.id}
            course={course}
            onEnroll={() => handleEnrollment(course.id)}
            showEnrollButton={true}
          />
        ))}
      </div>
    </div>
  );
};
```

#### **Reusable Course Card Component**

```jsx
// frontend/src/components/CourseCard.jsx
const CourseCard = ({ course, isTeacher, onEnroll, onEdit }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="h-48 bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
        <h3 className="text-white text-xl font-bold text-center px-4">
          {course.title}
        </h3>
      </div>

      <div className="p-4">
        <p className="text-gray-600 mb-3 line-clamp-2">{course.description}</p>

        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <span>👨‍🏫 {course.teacher_name}</span>
          <span>👥 {course.enrolled_count} students</span>
        </div>

        <div className="flex gap-2">
          {isTeacher ? (
            <>
              <button
                onClick={() => onEdit(course)}
                className="flex-1 btn-secondary"
              >
                Manage
              </button>
              <button className="flex-1 btn-primary">View Details</button>
            </>
          ) : (
            <button
              onClick={() => onEnroll(course.id)}
              className="w-full btn-primary"
            >
              Enroll Now
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
```

### Backend Implementation

#### **Course API Endpoints**

```python
# backend/course_api.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.post("/", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new course (Teachers only)"""
    if current_user["role"] != "teacher":
        raise HTTPException(403, "Only teachers can create courses")

    course_data = {
        "id": str(uuid.uuid4()),
        "title": course.title,
        "description": course.description,
        "teacher_id": current_user["id"],
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("courses").insert(course_data).execute()
    return CourseResponse(**result.data[0])

@router.post("/with-thumbnail", response_model=CourseResponse)
async def create_course_with_thumbnail(
    teacher_id: str = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    code: str = Form(...),
    status: str = Form("active"),
    thumbnail: Optional[UploadFile] = File(None)
):
    """Create a new course with optional thumbnail upload"""

    thumbnail_url = None

    # Upload thumbnail to Supabase Storage if provided
    if thumbnail:
        # Validate file type and size
        if not thumbnail.content_type.startswith('image/'):
            raise HTTPException(400, "Thumbnail must be an image file")

        content = await thumbnail.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(400, "File size must be less than 5MB")

        # Generate unique filename and upload to Supabase Storage
        file_extension = thumbnail.filename.split('.')[-1]
        unique_filename = f"course-thumbnails/{uuid.uuid4()}.{file_extension}"

        storage_manager = get_storage_manager()
        upload = await storage_manager.upload_course_thumbnail(thumbnail)
        thumbnail_url = upload["file_url"]

    # Create course with thumbnail URL
    course_data = {
        "teacher_id": teacher_id,
        "title": title,
        "description": description,
        "code": code,
        "status": status,
        "thumbnail_url": thumbnail_url,
        "created_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("courses").insert(course_data).execute()
    return CourseResponse(**result.data[0])

@router.put("/{course_id}/thumbnail", response_model=CourseResponse)
async def update_course_thumbnail(
    course_id: str,
    thumbnail: UploadFile = File(...)
):
    """Update course thumbnail"""

    # Validate file and upload to Supabase Storage
    if not thumbnail.content_type.startswith('image/'):
        raise HTTPException(400, "Thumbnail must be an image file")

    content = await thumbnail.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File size must be less than 5MB")

    # Upload to Supabase Storage
    file_extension = thumbnail.filename.split('.')[-1]
    unique_filename = f"course-thumbnails/{uuid.uuid4()}.{file_extension}"

    storage_manager = get_storage_manager()
    upload = await storage_manager.upload_course_thumbnail(thumbnail)
    thumbnail_url = upload["file_url"]

    # Update course in database
    result = supabase.table("courses").update({
        "thumbnail_url": thumbnail_url,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", course_id).execute()

    return CourseResponse(**result.data[0])

@router.get("/teacher/{teacher_id}", response_model=List[CourseResponse])
async def get_teacher_courses(
    teacher_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all courses for a specific teacher"""
    if current_user["id"] != teacher_id and current_user["role"] != "admin":
        raise HTTPException(403, "Access denied")

    result = supabase.table("courses")\
        .select("*, profiles!teacher_id(full_name)")\
        .eq("teacher_id", teacher_id)\
        .eq("status", "active")\
        .execute()

    return [CourseResponse(**course) for course in result.data]

@router.get("/", response_model=List[CourseResponse])
async def get_all_courses():
    """Get all active courses for course discovery"""
    result = supabase.table("courses")\
        .select("*, profiles!teacher_id(full_name)")\
        .eq("status", "active")\
        .execute()

    # Add enrollment count for each course
    for course in result.data:
        enrollment_count = supabase.table("enrollments")\
            .select("id", count="exact")\
            .eq("course_id", course["id"])\
            .eq("status", "active")\
            .execute()
        course["enrolled_count"] = enrollment_count.count

    return [CourseResponse(**course) for course in result.data]

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update course details (Teacher/Admin only)"""
    # Verify course ownership
    course = supabase.table("courses").select("*").eq("id", course_id).single().execute()
    if not course.data:
        raise HTTPException(404, "Course not found")

    if (course.data["teacher_id"] != current_user["id"] and
        current_user["role"] != "admin"):
        raise HTTPException(403, "Access denied")

    update_data = course_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    result = supabase.table("courses")\
        .update(update_data)\
        .eq("id", course_id)\
        .execute()

    return CourseResponse(**result.data[0])
```

#### **Enrollment Management**

````python
# backend/enrollment_api.py
@router.post("/", response_model=EnrollmentResponse)
async def enroll_student(
    enrollment: EnrollmentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Enroll a student in a course"""
    # Verify student is enrolling themselves or admin is enrolling
    if (enrollment.student_id != current_user["id"] and
        current_user["role"] != "admin"):
        raise HTTPException(403, "Access denied")

    # Check if already enrolled
    existing = supabase.table("enrollments")\
        .select("*")\
        .eq("student_id", enrollment.student_id)\
        .eq("course_id", enrollment.course_id)\
        .execute()

    if existing.data:
        raise HTTPException(400, "Already enrolled in this course")

    enrollment_data = {
        "id": str(uuid.uuid4()),
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "status": "active",
        "enrolled_at": datetime.utcnow().isoformat()
    }

    result = supabase.table("enrollments").insert(enrollment_data).execute()

    # Send enrollment confirmation email
    await send_enrollment_email(enrollment.student_id, enrollment.course_id)

    return EnrollmentResponse(**result.data[0])

@router.get("/student/{student_id}", response_model=List[CourseResponse])
async def get_student_courses(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all courses a student is enrolled in"""
    if current_user["id"] != student_id and current_user["role"] != "admin":
        raise HTTPException(403, "Access denied")

    result = supabase.table("enrollments")\
        .select("*, courses(*, profiles!teacher_id(full_name))")\
        .eq("student_id", student_id)\
        .eq("status", "active")\
        .execute()

    courses = [enrollment["courses"] for enrollment in result.data]
    return [CourseResponse(**course) for course in courses]

#### **New Student Course Discovery Endpoints**

```python
# backend/course_api.py - New endpoints added for student course management

@router.get("/all", response_model=Dict[str, Any])
async def get_all_courses():
    """Get all active courses for course discovery (student view)"""
    try:
        # Get all active courses with teacher information
        response = supabase.table('courses').select("""
            *,
            profiles!courses_teacher_id_fkey(full_name)
        """).eq('status', 'active').order('created_at', desc=True).execute()

        # Add enrollment count for each course
        courses_with_stats = []
        for course in response.data:
            # Get enrollment count
            enrollment_response = supabase.table('enrollments').select('id', count='exact').eq('course_id', course['id']).eq('status', 'active').execute()

            course_data = {
                **course,
                'teacher_name': course.get('profiles', {}).get('full_name', 'Unknown Teacher'),
                'enrollment_count': enrollment_response.count or 0
            }
            courses_with_stats.append(course_data)

        return {
            "success": True,
            "data": courses_with_stats,
            "message": f"Found {len(courses_with_stats)} active courses"
        }

    except Exception as e:
        print(f"Error fetching all courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/enrolled", response_model=Dict[str, Any])
async def get_student_enrolled_courses(student_id: str):
    """Get all courses a student is enrolled in"""
    try:
        # Get enrollments with course and teacher information
        response = supabase.table('enrollments').select("""
            *,
            courses(
                *,
                profiles!courses_teacher_id_fkey(full_name)
            )
        """).eq('student_id', student_id).eq('status', 'active').order('enrolled_at', desc=True).execute()

        # Format the response
        enrolled_courses = []
        for enrollment in response.data:
            course = enrollment.get('courses', {})
            if course:
                course_data = {
                    'enrollment_id': enrollment['id'],
                    'student_id': enrollment['student_id'],
                    'course_id': enrollment['course_id'],
                    'enrolled_at': enrollment['enrolled_at'],
                    'progress': enrollment.get('progress', 0),
                    'status': enrollment['status'],
                    'course': {
                        **course,
                        'teacher_name': course.get('profiles', {}).get('full_name', 'Unknown Teacher')
                    }
                }
                enrolled_courses.append(course_data)

        return {
            "success": True,
            "data": enrolled_courses,
            "message": f"Found {len(enrolled_courses)} enrolled courses"
        }

    except Exception as e:
        print(f"Error fetching student enrolled courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/enrollment-status/{course_id}", response_model=Dict[str, Any])
async def check_enrollment_status(student_id: str, course_id: str):
    """Check if a student is enrolled in a specific course"""
    try:
        response = supabase.table('enrollments').select('*').eq('student_id', student_id).eq('course_id', course_id).execute()

        is_enrolled = len(response.data) > 0
        enrollment_data = response.data[0] if is_enrolled else None

        return {
            "success": True,
            "data": {
                "is_enrolled": is_enrolled,
                "enrollment": enrollment_data
            }
        }

    except Exception as e:
        print(f"Error checking enrollment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
````

## 🔗 API Endpoints

### **Course Management Endpoints**

| Method | Endpoint                    | Description            | Auth Required |
| ------ | --------------------------- | ---------------------- | ------------- |
| POST   | `/api/courses`              | Create new course      | Teacher/Admin |
| GET    | `/api/courses`              | Get all active courses | No            |
| GET    | `/api/courses/teacher/{id}` | Get teacher's courses  | Teacher/Admin |
| PUT    | `/api/courses/{id}`         | Update course          | Teacher/Admin |
| DELETE | `/api/courses/{id}`         | Delete course          | Teacher/Admin |

### **Student Course Discovery Endpoints**

| Method | Endpoint                                                          | Description                          | Auth Required |
| ------ | ----------------------------------------------------------------- | ------------------------------------ | ------------- |
| GET    | `/api/courses/all`                                                | Get all active courses for discovery | No            |
| GET    | `/api/courses/student/{student_id}/enrolled`                      | Get student's enrolled courses       | Student/Admin |
| GET    | `/api/courses/student/{student_id}/enrollment-status/{course_id}` | Check enrollment status              | Student/Admin |

### **Enrollment Endpoints**

| Method | Endpoint                        | Description           | Auth Required |
| ------ | ------------------------------- | --------------------- | ------------- |
| POST   | `/api/enrollments`              | Enroll in course      | Student/Admin |
| GET    | `/api/enrollments/student/{id}` | Get student's courses | Student/Admin |
| DELETE | `/api/enrollments/{id}`         | Unenroll from course  | Student/Admin |

## 📊 Data Models

### **Course Model**

```python
class CourseCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    difficulty_level: Optional[str] = "beginner"

class CourseResponse(BaseModel):
    id: str
    title: str
    description: str
    teacher_id: str
    teacher_name: str
    category: Optional[str]
    difficulty_level: str
    status: str
    enrolled_count: int
    created_at: str
    updated_at: Optional[str]
```

### **Enrollment Model**

```python
class EnrollmentCreate(BaseModel):
    student_id: str
    course_id: str

class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    course_id: str
    status: str
    progress: int = 0
    enrolled_at: str
```

## 🎯 User Workflows

### **Teacher Course Creation Flow**

1. Teacher navigates to course management
2. Clicks "Create New Course"
3. Fills course creation form
4. Submits course details
5. Course is created and appears in teacher's dashboard
6. Course becomes available for student enrollment

### **Student Enrollment Flow**

1. Student browses available courses
2. Uses search/filter to find relevant courses
3. Views course details
4. Clicks "Enroll Now"
5. Enrollment is processed
6. Course appears in student's "My Courses"
7. Student receives enrollment confirmation email

## 🧪 Testing

### **Frontend Testing**

```bash
# Test course components
npm test -- --testPathPattern=course
```

### **Backend Testing**

```bash
# Test course API endpoints
python -m pytest tests/test_courses.py
```

## 📈 Analytics & Reporting

### **Course Analytics**

- Student enrollment trends
- Course completion rates
- Popular course categories
- Teacher performance metrics

### **Student Progress Tracking**

- Course completion percentage
- Time spent in courses
- Assignment submission rates
- Quiz performance

---

**📚 Empowering education through comprehensive course management**
