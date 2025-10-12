# 📚 LearnSphere API Documentation

## 🌐 API Overview

LearnSphere provides a comprehensive REST API built with FastAPI, offering endpoints for course management, user authentication, file uploads, notifications, and more.

### **Base URL**

```
Development: http://localhost:8000
Production: https://your-domain.com
```

### **API Version**

```
v2.0.0
```

### **Interactive Documentation**

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔐 Authentication

All protected endpoints require a valid JWT token in the Authorization header.

### **Headers**

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### **Token Structure**

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "student|teacher|admin",
  "exp": 1640995200,
  "iat": 1640908800
}
```

---

## 📋 API Endpoints

### **🔑 Authentication Endpoints**

#### **POST /api/auth/login**

Login with email and password.

**Request Body:**

```json
{
  "email": "student@example.com",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

#### **POST /api/auth/register**

Register a new user account.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "Jane Doe",
  "role": "student"
}
```

#### **POST /api/auth/refresh**

Refresh an expired access token.

**Request Body:**

```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### **POST /api/auth/logout**

Logout and invalidate tokens.

**Headers:** `Authorization: Bearer <token>`

---

### **🎓 Course Management Endpoints**

#### **GET /api/courses/**

Get all available courses with optional filtering.

**Query Parameters:**

- `category` (string): Filter by category
- `status` (string): Filter by status (active, draft)
- `teacher_id` (string): Filter by teacher
- `limit` (int): Number of courses to return (default: 20)
- `offset` (int): Number of courses to skip (default: 0)

**Response:**

```json
{
  "courses": [
    {
      "id": "uuid",
      "title": "Python Programming Basics",
      "description": "Learn Python from scratch",
      "category": "Programming",
      "thumbnail_url": "https://example.com/image.jpg",
      "teacher": {
        "id": "uuid",
        "full_name": "Dr. Smith"
      },
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 25,
  "limit": 20,
  "offset": 0
}
```

#### **GET /api/courses/{course_id}**

Get detailed information about a specific course.

**Response:**

```json
{
  "id": "uuid",
  "title": "Python Programming Basics",
  "description": "Comprehensive Python course...",
  "category": "Programming",
  "thumbnail_url": "https://example.com/image.jpg",
  "teacher": {
    "id": "uuid",
    "full_name": "Dr. Smith",
    "email": "teacher@example.com"
  },
  "materials": [
    {
      "id": "uuid",
      "file_name": "lesson1.pdf",
      "file_url": "https://storage.supabase.co/...",
      "file_size": 1024000,
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ],
  "assignments": [
    {
      "id": "uuid",
      "title": "Assignment 1",
      "description": "Complete the exercises...",
      "due_date": "2024-01-15T23:59:59Z",
      "max_marks": 100
    }
  ],
  "enrollment_count": 45,
  "status": "active"
}
```

#### **POST /api/courses/**

Create a new course (Teacher/Admin only).

**Headers:** `Authorization: Bearer <teacher_token>`

**Request Body:**

```json
{
  "title": "Advanced Python",
  "description": "Advanced Python concepts and techniques",
  "category": "Programming",
  "thumbnail_url": "https://example.com/thumbnail.jpg"
}
```

#### **PUT /api/courses/{course_id}**

Update course information (Teacher/Admin only).

**Headers:** `Authorization: Bearer <teacher_token>`

#### **DELETE /api/courses/{course_id}**

Delete a course (Teacher/Admin only).

**Headers:** `Authorization: Bearer <teacher_token>`

#### **GET /api/courses/categories**

Get all available course categories.

**Response:**

```json
{
  "categories": [
    "Programming",
    "Data Science",
    "Design",
    "Business",
    "Marketing",
    "Language Learning",
    "Photography",
    "Music",
    "General"
  ]
}
```

---

### **📁 Course Materials Endpoints**

#### **POST /api/course-materials/upload-multiple**

Upload multiple files for a course (Teacher only).

**Headers:** `Authorization: Bearer <teacher_token>`

**Request:** `multipart/form-data`

- `course_id` (string): Course ID
- `files` (file[]): Array of files to upload (max 10)
- `descriptions` (string[]): Array of descriptions for each file

**Response:**

```json
{
  "uploaded_files": [
    {
      "id": "uuid",
      "file_name": "lesson1.pdf",
      "file_url": "https://storage.supabase.co/...",
      "file_size": 1024000,
      "description": "Introduction to Python basics"
    }
  ],
  "total_uploaded": 3,
  "failed_uploads": []
}
```

#### **GET /api/course-materials/course/{course_id}**

Get all materials for a specific course.

**Response:**

```json
{
  "materials": [
    {
      "id": "uuid",
      "file_name": "lesson1.pdf",
      "file_url": "https://storage.supabase.co/...",
      "file_size": 1024000,
      "description": "Introduction to Python basics",
      "uploaded_by": {
        "id": "uuid",
        "full_name": "Dr. Smith"
      },
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### **DELETE /api/course-materials/{material_id}**

Delete a course material (Teacher only).

**Headers:** `Authorization: Bearer <teacher_token>`

---

### **🔔 Notification Endpoints**

#### **GET /api/notifications/**

Get user notifications with pagination.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

- `limit` (int): Number of notifications (default: 10)
- `offset` (int): Number to skip (default: 0)
- `unread_only` (bool): Only unread notifications (default: false)

**Response:**

```json
{
  "notifications": [
    {
      "id": "uuid",
      "type": "assignment_created",
      "title": "New Assignment Posted",
      "message": "Assignment 1 has been posted for Python Basics",
      "action_url": "/courses/uuid/assignments/uuid",
      "is_read": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 15,
  "unread_count": 3
}
```

#### **GET /api/notifications/types**

Get all available notification types.

**Response:**

```json
{
  "notification_types": [
    {
      "type": "assignment_created",
      "title": "New Assignment Posted",
      "description": "Notification when a new assignment is created"
    },
    {
      "type": "quiz_created",
      "title": "New Quiz Available",
      "description": "Notification when a new quiz is created"
    }
  ]
}
```

#### **POST /api/notifications/mark-read/{notification_id}**

Mark a specific notification as read.

**Headers:** `Authorization: Bearer <token>`

#### **POST /api/notifications/mark-all-read**

Mark all notifications as read for the current user.

**Headers:** `Authorization: Bearer <token>`

#### **GET /api/notifications/count**

Get unread notification count.

**Headers:** `Authorization: Bearer <token>`

**Response:**

```json
{
  "unread_count": 5
}
```

---

### **📊 Course Progress Endpoints**

#### **POST /api/course-completion/mark-complete**

Mark a course as completed for the current user.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**

```json
{
  "course_id": "uuid",
  "completion_percentage": 100
}
```

#### **GET /api/course-completion/my-completions**

Get completion history for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**

```json
{
  "completions": [
    {
      "id": "uuid",
      "course": {
        "id": "uuid",
        "title": "Python Programming Basics",
        "category": "Programming"
      },
      "completed_at": "2024-01-15T10:30:00Z",
      "completion_percentage": 100,
      "completion_email_sent": true
    }
  ]
}
```

#### **GET /api/course-completion/stats**

Get completion statistics (Teacher/Admin only).

**Headers:** `Authorization: Bearer <teacher_token>`

---

### **📝 Assignment Endpoints**

#### **POST /api/assignments/**

Create a new assignment (Teacher only).

**Headers:** `Authorization: Bearer <teacher_token>`

**Request Body:**

```json
{
  "course_id": "uuid",
  "title": "Python Functions Assignment",
  "description": "Create functions to solve the following problems...",
  "due_date": "2024-01-20T23:59:59Z",
  "max_marks": 100
}
```

#### **GET /api/assignments/course/{course_id}**

Get all assignments for a course.

**Response:**

```json
{
  "assignments": [
    {
      "id": "uuid",
      "title": "Python Functions Assignment",
      "description": "Create functions to solve...",
      "due_date": "2024-01-20T23:59:59Z",
      "max_marks": 100,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### **POST /api/assignments/{assignment_id}/submit**

Submit an assignment (Student only).

**Headers:** `Authorization: Bearer <student_token>`

**Request:** `multipart/form-data`

- `file` (file): Assignment submission file

---

### **🧪 Quiz Endpoints**

#### **POST /api/quizzes/**

Create a new quiz (Teacher only).

**Headers:** `Authorization: Bearer <teacher_token>`

**Request Body:**

```json
{
  "course_id": "uuid",
  "title": "Python Basics Quiz",
  "description": "Test your Python knowledge",
  "time_limit": 30,
  "questions": [
    {
      "question": "What is the correct syntax for creating a variable?",
      "type": "multiple_choice",
      "options": ["var x = 5", "x = 5", "int x = 5", "variable x = 5"],
      "correct_answer": 1,
      "points": 10
    }
  ]
}
```

#### **GET /api/quizzes/course/{course_id}**

Get all quizzes for a course.

#### **POST /api/quizzes/{quiz_id}/submit**

Submit quiz answers (Student only).

---

### **👥 User Management Endpoints**

#### **GET /api/users/profile**

Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:**

```json
{
  "id": "uuid",
  "email": "student@example.com",
  "full_name": "John Doe",
  "role": "student",
  "avatar_url": "https://storage.supabase.co/...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### **PUT /api/users/profile**

Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**

```json
{
  "full_name": "John Smith",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

---

### **📈 Analytics Endpoints**

#### **GET /api/analytics/teacher/dashboard**

Get teacher analytics dashboard (Teacher only).

**Headers:** `Authorization: Bearer <teacher_token>`

**Response:**

```json
{
  "total_courses": 5,
  "total_students": 120,
  "total_revenue": 2500.0,
  "course_stats": [
    {
      "course_id": "uuid",
      "title": "Python Basics",
      "enrollment_count": 45,
      "completion_rate": 85.5,
      "average_rating": 4.8
    }
  ]
}
```

#### **GET /api/analytics/student/progress**

Get student progress analytics.

**Headers:** `Authorization: Bearer <student_token>`

---

### **💰 Payment Endpoints**

#### **POST /api/payments/create-order**

Create a payment order (Razorpay).

**Headers:** `Authorization: Bearer <token>`

**Request Body:**

```json
{
  "course_id": "uuid",
  "amount": 99.99,
  "currency": "INR"
}
```

#### **POST /api/payments/verify-payment**

Verify payment completion.

**Headers:** `Authorization: Bearer <token>`

---

## 📊 Response Formats

### **Success Response**

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### **Error Response**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### **Pagination Response**

```json
{
  "data": [
    // Array of items
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## 🔒 Error Codes

| Code                   | HTTP Status | Description              |
| ---------------------- | ----------- | ------------------------ |
| `VALIDATION_ERROR`     | 422         | Invalid request data     |
| `AUTHENTICATION_ERROR` | 401         | Invalid or missing token |
| `AUTHORIZATION_ERROR`  | 403         | Insufficient permissions |
| `NOT_FOUND`            | 404         | Resource not found       |
| `CONFLICT`             | 409         | Resource already exists  |
| `RATE_LIMIT_EXCEEDED`  | 429         | Too many requests        |
| `SERVER_ERROR`         | 500         | Internal server error    |

---

## 📝 Rate Limits

| Endpoint Category | Limit        | Window   |
| ----------------- | ------------ | -------- |
| Authentication    | 10 requests  | 1 minute |
| File Upload       | 5 requests   | 1 minute |
| General API       | 100 requests | 1 minute |
| Analytics         | 20 requests  | 1 minute |

---

## 🧪 Testing

### **Using cURL**

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "student@example.com", "password": "password123"}'

# Get courses
curl -X GET "http://localhost:8000/api/courses/" \
  -H "Authorization: Bearer <token>"

# Upload file
curl -X POST "http://localhost:8000/api/course-materials/upload-multiple" \
  -H "Authorization: Bearer <token>" \
  -F "course_id=uuid" \
  -F "files=@lesson1.pdf"
```

### **Using JavaScript/Fetch**

```javascript
// Login
const loginResponse = await fetch("http://localhost:8000/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "student@example.com",
    password: "password123",
  }),
});

const { access_token } = await loginResponse.json();

// Get courses
const coursesResponse = await fetch("http://localhost:8000/api/courses/", {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});

const courses = await coursesResponse.json();
```

---

## 🔄 WebSocket Events

### **Real-time Notifications**

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/ws");

// Listen for notifications
ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log("New notification:", notification);
};

// Join user-specific room
ws.send(
  JSON.stringify({
    type: "join",
    user_id: "user-uuid",
  })
);
```

### **Event Types**

| Event Type              | Description      | Data                                  |
| ----------------------- | ---------------- | ------------------------------------- |
| `notification`          | New notification | `{id, type, title, message}`          |
| `assignment_created`    | New assignment   | `{assignment_id, course_id, title}`   |
| `quiz_created`          | New quiz         | `{quiz_id, course_id, title}`         |
| `course_material_added` | New material     | `{material_id, course_id, file_name}` |

---

## 📚 SDKs and Libraries

### **JavaScript/TypeScript**

```bash
npm install axios
```

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### **Python**

```bash
pip install requests
```

```python
import requests

class LearnSphereAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Content-Type': 'application/json'
        }
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

    def get_courses(self):
        response = requests.get(
            f'{self.base_url}/api/courses/',
            headers=self.headers
        )
        return response.json()
```

---

## 🔧 Development Tools

### **API Testing**

- **Postman Collection**: Import from `/docs/postman-collection.json`
- **Insomnia**: Import from `/docs/insomnia-collection.json`
- **Thunder Client**: VS Code extension

### **Performance Testing**

```bash
# Run API performance tests
python api_performance_report.py

# Test specific endpoints
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/courses/"
```

---

**Last Updated**: December 2024  
**API Version**: 2.0.0  
**Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
