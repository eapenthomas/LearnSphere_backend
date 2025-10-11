# 🏗️ LearnSphere Technical Architecture

## 📋 Architecture Overview

LearnSphere follows a modern three-tier architecture with clear separation of concerns, ensuring scalability, maintainability, and performance.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│                    (React Frontend)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   Student   │ │   Teacher   │ │    Admin    │            │
│  │  Dashboard  │ │  Dashboard  │ │  Dashboard  │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                      │
│                   (FastAPI Backend)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    Auth     │ │   Course    │ │ Notification│          │
│  │   Service   │ │  Service    │ │   Service   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Assessment │ │    File     │ │   Payment   │          │
│  │   Service   │ │  Service    │ │   Service   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└───────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────── ──┐
│                      DATA LAYER                           │
│                   (Supabase/PostgreSQL)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  Database   │ │   Storage   │ │  Real-time  │          │
│  │  (PostgreSQL│ │ (Supabase   │ │ (WebSocket) │          │
│  │             │ │  Storage)   │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└───────────────────────────────────────────────────────────┘
```

---

## 🎨 Frontend Architecture

### **React Application Structure**

```
frontend/src/
├── 📁 components/              # Reusable UI Components
│   ├── 📄 DashboardLayout.jsx          # Main dashboard wrapper
│   ├── 📄 NotificationBell.jsx         # Notification system UI
│   ├── 📄 CourseThumbnail.jsx          # Course image display
│   ├── 📄 FileUpload.jsx               # File upload component
│   └── 📄 LoadingSpinner.jsx           # Loading states
├── 📁 pages/                   # Page-level Components
│   ├── 📁 student/             # Student-specific pages
│   │   ├── 📄 Dashboard.jsx            # Student dashboard
│   │   ├── 📄 AllCourses.jsx           # Course catalog
│   │   ├── 📄 MyCourses.jsx            # Enrolled courses
│   │   └── 📄 Profile.jsx              # Student profile
│   ├── 📁 teacher/             # Teacher-specific pages
│   │   ├── 📄 TeacherDashboard.jsx     # Teacher dashboard
│   │   ├── 📄 CreateCourse.jsx         # Course creation
│   │   ├── 📄 ManageCourses.jsx        # Course management
│   │   └── 📄 Analytics.jsx            # Teacher analytics
│   └── 📁 admin/               # Admin-specific pages
│       ├── 📄 AdminDashboard.jsx       # Admin dashboard
│       ├── 📄 UserManagement.jsx       # User management
│       └── 📄 SystemSettings.jsx       # System configuration
├── 📁 contexts/                # React Context Providers
│   ├── 📄 AuthContext.jsx              # Authentication state
│   ├── 📄 NotificationContext.jsx      # Notification state
│   └── 📄 ThemeContext.jsx             # Theme management
├── 📁 hooks/                   # Custom React Hooks
│   ├── 📄 useAuth.js                   # Authentication hook
│   ├── 📄 useNotifications.js          # Notification hook
│   └── 📄 useApi.js                    # API interaction hook
├── 📁 utils/                   # Utility Functions
│   ├── 📄 api.js                       # API client configuration
│   ├── 📄 thumbnailUtils.jsx           # Image handling utilities
│   ├── 📄 fileUtils.js                 # File handling utilities
│   └── 📄 validation.js                # Form validation
├── 📁 services/                # Service Layer
│   ├── 📄 authService.js               # Authentication service
│   ├── 📄 courseService.js             # Course management service
│   ├── 📄 notificationService.js       # Notification service
│   └── 📄 fileService.js               # File upload service
└── 📁 styles/                  # Styling
    ├── 📄 globals.css                  # Global styles
    ├── 📄 components.css               # Component styles
    └── 📄 utilities.css                # Utility classes
```

### **State Management Architecture**

```javascript
// Context-based state management
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AuthContext   │    │NotificationContext│   │  ThemeContext   │
│                 │    │                 │    │                 │
│ • user state    │    │ • notifications │    │ • theme state   │
│ • login/logout  │    │ • preferences   │    │ • dark/light    │
│ • permissions   │    │ • real-time     │    │ • colors        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Components    │
                    │                 │
                    │ • Dashboard     │
                    │ • Course Pages  │
                    │ • Notifications │
                    └─────────────────┘
```

### **Component Design Patterns**

#### **1. Container/Presentational Pattern**

```javascript
// Container Component (Smart)
const CourseContainer = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses()
      .then(setCourses)
      .finally(() => setLoading(false));
  }, []);

  return <CourseList courses={courses} loading={loading} />;
};

// Presentational Component (Dumb)
const CourseList = ({ courses, loading }) => {
  if (loading) return <LoadingSpinner />;
  return (
    <div className="course-grid">
      {courses.map((course) => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  );
};
```

#### **2. Custom Hooks Pattern**

```javascript
// Custom hook for course management
const useCourses = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const data = await courseService.getCourses();
      setCourses(data);
    } catch (error) {
      console.error("Failed to fetch courses:", error);
    } finally {
      setLoading(false);
    }
  };

  return { courses, loading, fetchCourses };
};
```

---

## ⚙️ Backend Architecture

### **FastAPI Application Structure**

```
backend/
├── 📄 main.py                      # Application entry point
├── 📁 api/                         # API Route Modules
│   ├── 📄 auth_api.py              # Authentication endpoints
│   ├── 📄 course_api.py            # Course management
│   ├── 📄 enrollment_api.py        # Enrollment system
│   ├── 📄 notifications_api.py     # Notification system
│   ├── 📄 course_materials_enhanced.py # File upload system
│   ├── 📄 course_completion_api.py # Progress tracking
│   ├── 📄 quiz_api.py              # Assessment system
│   ├── 📄 assignments_api.py       # Assignment management
│   ├── 📄 payment_system.py        # Payment processing
│   ├── 📄 admin_api.py             # Admin functionality
│   └── 📄 user_management_api.py   # User management
├── 📁 models/                      # Pydantic Data Models
│   ├── 📄 auth_models.py           # Authentication models
│   ├── 📄 course_models.py         # Course data models
│   ├── 📄 user_models.py           # User data models
│   └── 📄 notification_models.py   # Notification models
├── 📁 middleware/                  # Custom Middleware
│   ├── 📄 auth_middleware.py       # Authentication middleware
│   ├── 📄 cors_middleware.py       # CORS configuration
│   └── 📄 logging_middleware.py    # Request logging
├── 📁 services/                    # Business Logic Services
│   ├── 📄 auth_service.py          # Authentication logic
│   ├── 📄 course_service.py        # Course business logic
│   ├── 📄 notification_service.py  # Notification logic
│   ├── 📄 file_service.py          # File handling logic
│   └── 📄 email_service.py         # Email delivery service
├── 📁 utils/                       # Utility Functions
│   ├── 📄 database.py              # Database utilities
│   ├── 📄 security.py              # Security utilities
│   ├── 📄 file_utils.py            # File handling utilities
│   └── 📄 validation.py            # Data validation
└── 📁 config/                      # Configuration
    ├── 📄 settings.py              # Application settings
    ├── 📄 database_config.py       # Database configuration
    └── 📄 email_config.py          # Email configuration
```

### **API Layer Architecture**

```python
# API Router Structure
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Middleware Layer                     │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │    CORS     │ │    Auth     │ │   Logging   │    │    │
│  │  │ Middleware  │ │ Middleware  │ │ Middleware  │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Router Layer                       │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │   Auth      │ │   Course    │ │Notification │    │    │
│  │  │  Router     │ │  Router     │ │   Router    │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ Assessment  │ │    File     │ │   Payment   │    │    │
│  │  │   Router    │ │   Router    │ │   Router    │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### **Service Layer Pattern**

```python
# Service Layer Example
class CourseService:
    def __init__(self, db: SupabaseClient):
        self.db = db

    async def create_course(self, course_data: CourseCreate) -> Course:
        # Business logic validation
        if not course_data.title:
            raise ValueError("Course title is required")

        # Database operation
        result = self.db.table("courses").insert(course_data.dict()).execute()

        # Post-processing
        course = Course(**result.data[0])
        await self._send_course_created_notification(course)

        return course

    async def _send_course_created_notification(self, course: Course):
        # Notification logic
        pass

# API Endpoint
@router.post("/courses/", response_model=Course)
async def create_course(
    course_data: CourseCreate,
    current_user: dict = Depends(get_current_user),
    course_service: CourseService = Depends(get_course_service)
):
    return await course_service.create_course(course_data)
```

---

## 🗄️ Database Architecture

### **PostgreSQL Schema Design**

```sql
-- Core Tables Structure
┌─────────────────────────────────────────────────────────────┐
│                    Database Schema                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                User Management                      │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │  profiles   │ │ auth_users  │ │   roles     │    │    │
│  │  │             │ │ (Supabase)  │ │             │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Course Management                    │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │   courses   │ │enrollments  │ │course_progress│   │    │
│  │  │             │ │             │ │             │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Content Management                   │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │course_materials│assignments │ │   quizzes   │    │    │
│  │  │             │ │             │ │             │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Notification System                  │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │notifications│ │notification_│ │email_notifications│   │    │
│  │  │             │ │preferences  │ │             │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### **Database Relationships**

```sql
-- Entity Relationship Diagram
profiles (1) ──────── (n) courses
    │                      │
    │                      │
    │                      │
    │                      │
    │                      │
enrollments (n) ────── (1) courses
    │
    │
    │
course_progress (1) ──── (1) enrollments

courses (1) ──────────── (n) course_materials
courses (1) ──────────── (n) assignments
courses (1) ──────────── (n) quizzes

profiles (1) ──────────── (n) notifications
profiles (1) ──────────── (n) notification_preferences
```

### **Database Optimization**

#### **Indexing Strategy**

```sql
-- Performance Indexes
CREATE INDEX idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_course_materials_course_id ON course_materials(course_id);
```

#### **Row Level Security (RLS)**

```sql
-- Security Policies
CREATE POLICY "Users can view their own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Teachers can manage their own courses"
ON courses FOR ALL
USING (auth.uid() = teacher_id);

CREATE POLICY "Students can view enrolled courses"
ON courses FOR SELECT
USING (id IN (
    SELECT course_id FROM enrollments
    WHERE student_id = auth.uid()
));
```

---

## 🔄 Data Flow Architecture

### **Request Flow Diagram**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───►│   FastAPI   │───►│  Supabase   │───►│ PostgreSQL  │
│  (React)    │    │   Server    │    │   API       │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. User     │    │ 2. Auth     │    │ 3. Query    │    │ 4. Data     │
│ Interaction │    │ Validation  │    │ Processing  │    │ Retrieval   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 8. UI       │◄───│ 7. Response │◄───│ 6. Data     │◄───│ 5. Result   │
│ Update      │    │ Processing  │    │ Formatting  │    │ Processing  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### **Real-time Data Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                    Real-time Updates                       │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ PostgreSQL  │───►│  Supabase   │───►│   FastAPI   │    │
│  │  Database   │    │  Realtime   │    │  WebSocket  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Data Change │    │ Event       │    │ Real-time   │    │
│  │ Trigger     │    │ Broadcasting│    │ Notification│    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Client    │◄───│  WebSocket  │◄───│  Supabase   │    │
│  │  (React)    │    │ Connection  │    │  Client     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Architecture

### **Authentication Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                Authentication Architecture                  │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Client    │    │   FastAPI   │    │  Supabase   │    │
│  │  (React)    │    │   Server    │    │    Auth     │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         │ 1. Login Request  │                   │          │
│         ├──────────────────►│                   │          │
│         │                   │ 2. Auth Request   │          │
│         │                   ├──────────────────►│          │
│         │                   │                   │          │
│         │                   │ 3. JWT Token      │          │
│         │                   │◄──────────────────┤          │
│         │ 4. JWT + Refresh  │                   │          │
│         │◄──────────────────┤                   │          │
│         │                   │                   │          │
│         │ 5. Store Tokens   │                   │          │
│         │                   │                   │          │
│         │ 6. API Requests   │                   │          │
│         ├──────────────────►│                   │          │
│         │                   │ 7. Token Validation│         │
│         │                   ├──────────────────►│          │
│         │                   │                   │          │
│         │ 8. Valid Response │                   │          │
│         │◄──────────────────┤                   │          │
│         │                   │                   │          │
└─────────────────────────────────────────────────────────────┘
```

### **Security Layers**

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Application Layer                    │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ Input       │ │ Business    │ │ Output      │    │    │
│  │  │ Validation  │ │ Logic       │ │ Sanitization│    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Middleware Layer                     │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ CORS        │ │ Auth        │ │ Rate        │    │    │
│  │  │ Protection  │ │ Middleware  │ │ Limiting    │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Database Layer                       │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │    │
│  │  │ Row Level   │ │ Encryption  │ │ Audit       │    │    │
│  │  │ Security    │ │ at Rest     │ │ Logging     │    │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚡ Performance Architecture

### **Optimization Strategies**

#### **1. Lazy Loading**

```python
# Backend lazy loading
def get_openai_client():
    if not hasattr(get_openai_client, 'client'):
        get_openai_client.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return get_openai_client.client

# Frontend lazy loading
const CoursePage = lazy(() => import('./pages/CoursePage'));
const TeacherDashboard = lazy(() => import('./pages/TeacherDashboard'));
```

#### **2. Caching Strategy**

```python
# Redis caching (planned)
@cache(expire=300)  # 5 minutes
async def get_courses():
    return await course_service.get_all_courses()

# Browser caching
Cache-Control: public, max-age=3600
ETag: "course-list-v1.2.3"
```

#### **3. Database Optimization**

```sql
-- Query optimization
EXPLAIN ANALYZE SELECT c.*, p.full_name
FROM courses c
JOIN profiles p ON c.teacher_id = p.id
WHERE c.status = 'active'
ORDER BY c.created_at DESC
LIMIT 20;

-- Connection pooling
max_connections = 100
shared_preload_libraries = 'pg_stat_statements'
```

---

## 📊 Monitoring & Observability

### **Monitoring Stack**

```
┌─────────────────────────────────────────────────────────────┐
│                  Monitoring Architecture                    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Application │    │   Database  │    │   System    │    │
│  │ Monitoring  │    │ Monitoring  │    │ Monitoring  │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ API Metrics │    │ Query       │    │ Resource    │    │
│  │ • Response  │    │ Performance │    │ Usage       │    │
│  │ • Error     │    │ • Slow      │    │ • CPU       │    │
│  │ • Throughput│    │ • Indexes   │    │ • Memory    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Alerts    │    │   Logs      │    │  Dashboards │    │
│  │ • Error     │    │ • Access    │    │ • Real-time │    │
│  │ • Performance│   │ • Audit     │    │ • Historical│    │
│  │ • Security  │    │ • Debug     │    │ • Custom    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### **Performance Metrics**

| Metric              | Target  | Current | Status                |
| ------------------- | ------- | ------- | --------------------- |
| API Response Time   | < 200ms | ~300ms  | ⚠️ Needs optimization |
| Database Query Time | < 50ms  | ~100ms  | ⚠️ Needs optimization |
| Frontend Load Time  | < 2s    | ~1.5s   | ✅ Good               |
| Server Startup      | < 5s    | ~3s     | ✅ Excellent          |
| Concurrent Users    | 100+    | 50+     | ⚠️ Limited testing    |

---

## 🚀 Deployment Architecture

### **Production Deployment**

```
┌─────────────────────────────────────────────────────────────┐
│                  Production Environment                     │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   CDN       │    │   Load      │    │   App       │    │
│  │ (CloudFlare)│    │  Balancer   │    │  Servers    │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Static      │    │ SSL         │    │ FastAPI     │    │
│  │ Assets      │    │ Termination │    │ Application │    │
│  │ • Images    │    │ • HTTPS     │    │ • Gunicorn  │    │
│  │ • CSS/JS    │    │ • HTTP/2    │    │ • Workers   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   Redis     │    │  Supabase   │    │   Backup    │    │
│  │  Cache      │    │  Database   │    │   System    │    │
│  │ • Sessions  │    │ • PostgreSQL│    │ • Daily     │    │
│  │ • API Cache │    │ • Storage   │    │ • Automated │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### **Development Environment**

```
┌─────────────────────────────────────────────────────────────┐
│                Development Environment                      │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   React     │    │   FastAPI   │    │  Supabase   │    │
│  │ Development │    │ Development │    │ Development │    │
│  │ Server      │    │ Server      │    │ Project     │    │
│  │ :3000       │    │ :8000       │    │             │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                   │                   │          │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Hot Reload  │    │ Auto Reload │    │ Real-time   │    │
│  │ • CSS       │    │ • Python    │    │ Database    │    │
│  │ • JS        │    │ • API       │    │ • Changes   │    │
│  │ • Components│    │ • Routes    │    │ • Sync      │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Management

### **Environment Configuration**

```python
# settings.py
class Settings:
    # Application
    APP_NAME: str = "LearnSphere"
    DEBUG: bool = False

    # Database
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Email
    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASS: str

    # File Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: list = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]

    # Performance
    CACHE_TTL: int = 300  # 5 minutes
    MAX_CONCURRENT_REQUESTS: int = 100
```

---

**Last Updated**: December 2024  
**Version**: 2.0.0  
**Architecture**: Three-tier with microservices pattern
