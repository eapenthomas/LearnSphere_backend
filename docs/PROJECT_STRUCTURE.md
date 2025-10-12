# 🏗️ LearnSphere Project Structure

## 📁 Complete Directory Structure

```
LearnSphere/                                    # Root directory
├── 📁 backend/                                 # FastAPI Backend Server
│   ├── 📄 main.py                             # Main server entry point (optimized)
│   ├── 📄 requirements.txt                    # Python dependencies
│   ├── 📄 env.example                         # Environment variables template
│   ├── 📄 .env                                # Environment variables (create from template)
│   ├── 📄 clear_db.py                         # Database cleanup script
│   ├── 📄 __pycache__/                        # Python cache directory
│   │
│   ├── 📁 api/                                # API Route Modules
│   │   ├── 📄 auth_api.py                     # Authentication endpoints
│   │   ├── 📄 course_api.py                   # Course management
│   │   ├── 📄 enrollment_api.py               # Course enrollment
│   │   ├── 📄 course_materials_enhanced.py    # Multiple file upload system
│   │   ├── 📄 course_completion_api.py        # Course completion tracking
│   │   ├── 📄 notifications_api.py            # Notification system
│   │   ├── 📄 notifications_api_enhanced.py   # Enhanced notifications
│   │   ├── 📄 quiz_api.py                     # Quiz system
│   │   ├── 📄 assignments_api.py              # Assignment management
│   │   ├── 📄 payment_system.py               # Payment processing
│   │   ├── 📄 admin_api.py                    # Admin functionality
│   │   ├── 📄 user_management_api.py          # User management
│   │   ├── 📄 teacher_analytics_api.py        # Teacher analytics
│   │   ├── 📄 teacher_rating_api.py           # Teacher rating system
│   │   ├── 📄 teacher_verification_api.py     # Teacher verification
│   │   ├── 📄 admin_notifications_api.py      # Admin notifications
│   │   ├── 📄 admin_dashboard_api.py          # Admin dashboard
│   │   ├── 📄 admin_email_service.py          # Admin email service
│   │   ├── 📄 ai_tutor_api.py                 # AI tutoring features
│   │   ├── 📄 ai_usage_api.py                 # AI usage tracking
│   │   ├── 📄 notes_summarizer_api.py         # Notes summarization
│   │   ├── 📄 quiz_generator_api.py           # AI quiz generation
│   │   ├── 📄 summarizer_service.py           # Content summarization
│   │   ├── 📄 notification_service.py         # Notification service
│   │   ├── 📄 email_service.py                # Email delivery service
│   │   ├── 📄 file_download_api.py            # File download handling
│   │   ├── 📄 profile_picture_api.py          # Profile picture management
│   │   ├── 📄 student_deadlines_api.py        # Student deadline tracking
│   │   ├── 📄 teacher_reports_api.py          # Teacher reports
│   │   └── 📄 thumbnail_api.py                # Thumbnail generation
│   │
│   ├── 📁 models/                             # Pydantic Data Models
│   │   ├── 📄 auth_models.py                  # Authentication models
│   │   ├── 📄 course_models.py                # Course data models
│   │   ├── 📄 user_models.py                  # User data models
│   │   ├── 📄 notification_models.py          # Notification models
│   │   ├── 📄 assignment_models.py            # Assignment models
│   │   ├── 📄 quiz_models.py                  # Quiz models
│   │   └── 📄 payment_models.py               # Payment models
│   │
│   ├── 📁 middleware/                         # Custom Middleware
│   │   ├── 📄 auth_middleware.py              # Authentication middleware
│   │   ├── 📄 auth_middleware_enhanced.py     # Enhanced auth middleware
│   │   ├── 📄 cors_middleware.py              # CORS configuration
│   │   └── 📄 logging_middleware.py           # Request logging
│   │
│   ├── 📁 services/                           # Business Logic Services
│   │   ├── 📄 auth_service.py                 # Authentication logic
│   │   ├── 📄 course_service.py               # Course business logic
│   │   ├── 📄 notification_service.py         # Notification logic
│   │   ├── 📄 file_service.py                 # File handling logic
│   │   ├── 📄 email_service.py                # Email delivery service
│   │   ├── 📄 payment_service.py              # Payment processing
│   │   ├── 📄 analytics_service.py            # Analytics processing
│   │   └── 📄 ai_service.py                   # AI services
│   │
│   ├── 📁 utils/                              # Utility Functions
│   │   ├── 📄 database.py                     # Database utilities
│   │   ├── 📄 security.py                     # Security utilities
│   │   ├── 📄 file_utils.py                   # File handling utilities
│   │   ├── 📄 validation.py                   # Data validation
│   │   ├── 📄 thumbnail_utils.py              # Thumbnail processing
│   │   └── 📄 email_templates.py              # Email templates
│   │
│   └── 📁 config/                             # Configuration
│       ├── 📄 settings.py                     # Application settings
│       ├── 📄 database_config.py              # Database configuration
│       ├── 📄 email_config.py                 # Email configuration
│       └── 📄 payment_config.py               # Payment configuration
│
├── 📁 frontend/                               # React Frontend Application
│   ├── 📄 package.json                        # Node.js dependencies
│   ├── 📄 package-lock.json                   # Dependency lock file
│   ├── 📄 .env.local                          # Frontend environment variables
│   ├── 📄 public/                             # Static assets
│   │   ├── 📄 index.html                      # Main HTML template
│   │   ├── 📄 favicon.ico                     # Site icon
│   │   ├── 📄 manifest.json                   # PWA manifest
│   │   └── 📁 images/                         # Static images
│   │
│   └── 📁 src/                                # Source code
│       ├── 📄 index.js                        # Application entry point
│       ├── 📄 App.js                          # Main application component
│       ├── 📄 App.css                         # Global styles
│       │
│       ├── 📁 components/                     # Reusable UI Components
│       │   ├── 📄 DashboardLayout.jsx         # Main dashboard wrapper
│       │   ├── 📄 NotificationBell.jsx        # Notification system UI
│       │   ├── 📄 TeacherNotificationBell.jsx # Teacher notification bell
│       │   ├── 📄 AdminNotificationBell.jsx   # Admin notification bell
│       │   ├── 📄 CourseThumbnail.jsx         # Course image display
│       │   ├── 📄 FileUpload.jsx              # File upload component
│       │   ├── 📄 LoadingSpinner.jsx          # Loading states
│       │   ├── 📄 ErrorBoundary.jsx           # Error handling
│       │   ├── 📄 ProtectedRoute.jsx          # Route protection
│       │   └── 📄 ConfirmDialog.jsx           # Confirmation dialogs
│       │
│       ├── 📁 pages/                          # Page-level Components
│       │   ├── 📁 student/                    # Student-specific pages
│       │   │   ├── 📄 Dashboard.jsx           # Student dashboard
│       │   │   ├── 📄 AllCourses.jsx          # Course catalog
│       │   │   ├── 📄 MyCourses.jsx           # Enrolled courses
│       │   │   ├── 📄 Profile.jsx             # Student profile
│       │   │   ├── 📄 CourseDetail.jsx        # Course details
│       │   │   ├── 📄 AssignmentDetail.jsx    # Assignment details
│       │   │   ├── 📄 QuizDetail.jsx          # Quiz details
│       │   │   └── 📄 Progress.jsx            # Progress tracking
│       │   │
│       │   ├── 📁 teacher/                    # Teacher-specific pages
│       │   │   ├── 📄 TeacherDashboard.jsx    # Teacher dashboard
│       │   │   ├── 📄 CreateCourse.jsx        # Course creation
│       │   │   ├── 📄 ManageCourses.jsx       # Course management
│       │   │   ├── 📄 Analytics.jsx           # Teacher analytics
│       │   │   ├── 📄 CreateAssignment.jsx    # Assignment creation
│       │   │   ├── 📄 CreateQuiz.jsx          # Quiz creation
│       │   │   ├── 📄 GradeAssignments.jsx    # Assignment grading
│       │   │   └── 📄 TeacherProfile.jsx      # Teacher profile
│       │   │
│       │   ├── 📁 admin/                      # Admin-specific pages
│       │   │   ├── 📄 AdminDashboard.jsx      # Admin dashboard
│       │   │   ├── 📄 UserManagement.jsx      # User management
│       │   │   ├── 📄 SystemSettings.jsx      # System configuration
│       │   │   ├── 📄 TeacherVerification.jsx # Teacher verification
│       │   │   └── 📄 SystemAnalytics.jsx     # System analytics
│       │   │
│       │   ├── 📁 auth/                       # Authentication pages
│       │   │   ├── 📄 Login.jsx               # Login page
│       │   │   ├── 📄 Register.jsx            # Registration page
│       │   │   ├── 📄 ForgotPassword.jsx      # Password reset
│       │   │   └── 📄 ResetPassword.jsx       # Password reset form
│       │   │
│       │   ├── 📄 NotificationSettings.jsx    # Notification preferences
│       │   ├── 📄 NotFound.jsx                # 404 page
│       │   └── 📄 ErrorPage.jsx               # Error page
│       │
│       ├── 📁 contexts/                       # React Context Providers
│       │   ├── 📄 AuthContext.jsx             # Authentication state
│       │   ├── 📄 NotificationContext.jsx     # Notification state
│       │   ├── 📄 ThemeContext.jsx            # Theme management
│       │   └── 📄 CourseContext.jsx           # Course state
│       │
│       ├── 📁 hooks/                          # Custom React Hooks
│       │   ├── 📄 useAuth.js                  # Authentication hook
│       │   ├── 📄 useNotifications.js         # Notification hook
│       │   ├── 📄 useApi.js                   # API interaction hook
│       │   ├── 📄 useCourses.js               # Course management hook
│       │   ├── 📄 useFileUpload.js            # File upload hook
│       │   └── 📄 useLocalStorage.js          # Local storage hook
│       │
│       ├── 📁 utils/                          # Utility Functions
│       │   ├── 📄 api.js                      # API client configuration
│       │   ├── 📄 thumbnailUtils.jsx          # Image handling utilities
│       │   ├── 📄 fileUtils.js                # File handling utilities
│       │   ├── 📄 validation.js               # Form validation
│       │   ├── 📄 dateUtils.js                # Date formatting utilities
│       │   ├── 📄 constants.js                # Application constants
│       │   └── 📄 helpers.js                  # General helper functions
│       │
│       ├── 📁 services/                       # Service Layer
│       │   ├── 📄 authService.js              # Authentication service
│       │   ├── 📄 courseService.js            # Course management service
│       │   ├── 📄 notificationService.js      # Notification service
│       │   ├── 📄 fileService.js              # File upload service
│       │   ├── 📄 emailService.js             # Email service
│       │   ├── 📄 paymentService.js           # Payment service
│       │   └── 📄 analyticsService.js         # Analytics service
│       │
│       └── 📁 styles/                         # Styling
│           ├── 📄 globals.css                 # Global styles
│           ├── 📄 components.css              # Component styles
│           ├── 📄 utilities.css               # Utility classes
│           └── 📄 themes.css                  # Theme definitions
│
├── 📁 database/                               # Database Schemas and Migrations
│   ├── 📄 README.md                           # Database documentation
│   ├── 📄 database_schema.sql                 # Core database schema
│   ├── 📄 courses_schema.sql                  # Courses table with categories
│   ├── 📄 course_materials_schema.sql         # Course materials schema
│   ├── 📄 course_progress_schema.sql          # Progress tracking schema
│   ├── 📄 enrollment_schema.sql               # Enrollment system schema
│   ├── 📄 assignments_schema.sql              # Assignment system schema
│   ├── 📄 quiz_schema.sql                     # Quiz system schema
│   ├── 📄 notifications_schema.sql            # Notification system schema
│   ├── 📄 admin_schema.sql                    # Admin system schema
│   ├── 📄 forum_schema.sql                    # Forum system schema
│   ├── 📄 analytics_queries.sql               # Analytics queries
│   ├── 📄 create_storage_bucket.sql           # Storage bucket creation
│   ├── 📄 create_teacher_ratings_table.sql    # Teacher ratings table
│   ├── 📄 course_completions_schema.sql       # Course completion tracking
│   ├── 📄 sample_courses.sql                  # Sample course data
│   └── 📄 latest_updates_december_2024.sql    # Latest schema updates
│
├── 📁 docs/                                   # Documentation
│   ├── 📄 README.md                           # Documentation index
│   ├── 📄 PROJECT_OVERVIEW.md                 # Project overview
│   ├── 📄 PROJECT_STRUCTURE.md                # This file
│   ├── 📄 FEATURES_DOCUMENTATION.md           # Complete feature list
│   ├── 📄 TECHNICAL_ARCHITECTURE.md           # Technical architecture
│   ├── 📄 SETUP_GUIDE.md                      # Setup instructions
│   ├── 📄 API_DOCUMENTATION.md                # API reference
│   ├── 📄 AUTH_SYSTEM_README.md               # Authentication system
│   ├── 📄 NOTIFICATION_SYSTEM_README.md       # Notification system
│   ├── 📄 COURSE_MANAGEMENT_README.md         # Course management
│   ├── 📄 ASSIGNMENTS_MODULE_README.md        # Assignment system
│   ├── 📄 QUIZ_SYSTEM_README.md               # Quiz system
│   ├── 📄 TEACHER_ANALYTICS_SYSTEM.md         # Analytics system
│   ├── 📄 TEACHER_RATING_SYSTEM.md            # Rating system
│   ├── 📄 TEACHER_VERIFICATION_SYSTEM.md      # Verification system
│   ├── 📄 DATABASE_SCHEMA_README.md           # Database documentation
│   ├── 📄 FRONTEND_STRUCTURE_GUIDE.md         # Frontend architecture
│   ├── 📄 PROFILE_PICTURE_SYSTEM.md           # Profile picture system
│   ├── 📄 PROGRESS_TRACKING_SYSTEM.md         # Progress tracking
│   ├── 📄 CALENDAR_SYSTEM_README.md           # Calendar system
│   ├── 📄 DEADLINE_MANAGEMENT_GUIDE.md        # Deadline management
│   ├── 📄 VOICE_NAVIGATION_GUIDE.md           # Voice navigation
│   ├── 📄 SUPABASE_STORAGE_MIGRATION_GUIDE.md # Storage migration
│   ├── 📄 TEACHER_COURSES_SETUP.md            # Teacher setup
│   ├── 📄 FORGOT_PASSWORD_SETUP.md            # Password reset
│   ├── 📄 FEATURE_IMPLEMENTATION_GUIDE.md     # Implementation guide
│   ├── 📄 COMPLETE_SETUP_GUIDE.md             # Complete setup
│   └── 📄 FUNCTIONALITY.md                    # System functionality
│
├── 📁 scripts/                                # Utility Scripts
│   └── 📄 setup_environment.py                # Environment setup script
│
├── 📄 README.md                               # Main project README
├── 📄 start_learnsphere.py                    # Professional startup script
├── 📄 api_performance_report.py               # API performance testing
├── 📄 supabase_performance_analyzer.py        # Database performance analysis
├── 📄 test_email_specific.py                  # Email system testing
├── 📄 DEPLOYMENT_GUIDE.md                     # Deployment instructions
├── 📄 DEPLOYMENT_CHECKLIST.md                 # Deployment checklist
├── 📄 TESTING_GUIDE.md                        # Testing procedures
└── 📄 .gitignore                              # Git ignore rules
```

---

## 🎯 Key File Descriptions

### **🚀 Core Application Files**

#### **Backend Core**

- **`backend/main.py`** - Main FastAPI server with optimized startup
- **`backend/requirements.txt`** - Python dependencies
- **`backend/.env`** - Environment variables (create from `env.example`)

#### **Frontend Core**

- **`frontend/src/App.js`** - Main React application
- **`frontend/package.json`** - Node.js dependencies and scripts
- **`frontend/src/index.js`** - Application entry point

### **🔧 Configuration Files**

#### **Environment Configuration**

- **`backend/env.example`** - Template for backend environment variables
- **`frontend/.env.local`** - Frontend environment variables
- **`.gitignore`** - Git ignore rules for the project

#### **Database Configuration**

- **`database/database_schema.sql`** - Core database schema
- **`database/courses_schema.sql`** - Courses with category support
- **`database/notifications_schema.sql`** - Notification system schema

### **📚 Documentation Files**

#### **Main Documentation**

- **`README.md`** - Main project documentation
- **`docs/README.md`** - Documentation index
- **`docs/PROJECT_OVERVIEW.md`** - Complete project overview
- **`docs/SETUP_GUIDE.md`** - Installation and setup guide

#### **Technical Documentation**

- **`docs/TECHNICAL_ARCHITECTURE.md`** - System architecture
- **`docs/API_DOCUMENTATION.md`** - API reference
- **`docs/FEATURES_DOCUMENTATION.md`** - Feature documentation

### **🛠️ Utility Scripts**

#### **Performance Testing**

- **`api_performance_report.py`** - Comprehensive API performance testing
- **`supabase_performance_analyzer.py`** - Database performance analysis
- **`test_email_specific.py`** - Email system testing

#### **Development Tools**

- **`start_learnsphere.py`** - Professional startup script
- **`backend/clear_db.py`** - Database cleanup utility

### **📁 Directory Purposes**

#### **Backend Structure**

- **`api/`** - All API endpoint modules
- **`models/`** - Pydantic data models
- **`services/`** - Business logic services
- **`middleware/`** - Custom middleware
- **`utils/`** - Utility functions
- **`config/`** - Configuration files

#### **Frontend Structure**

- **`components/`** - Reusable UI components
- **`pages/`** - Page-level components
- **`contexts/`** - React context providers
- **`hooks/`** - Custom React hooks
- **`services/`** - Frontend services
- **`utils/`** - Utility functions

#### **Database Structure**

- **`database/`** - SQL schemas and migrations
- **`docs/`** - Comprehensive documentation
- **`scripts/`** - Utility scripts

---

## 🔄 File Relationships

### **Backend Dependencies**

```
main.py
├── api/ (all API modules)
├── middleware/ (auth, cors, logging)
├── services/ (business logic)
├── models/ (data validation)
└── utils/ (helper functions)
```

### **Frontend Dependencies**

```
App.js
├── components/ (UI components)
├── pages/ (page components)
├── contexts/ (state management)
├── hooks/ (custom hooks)
├── services/ (API services)
└── utils/ (utilities)
```

### **Database Dependencies**

```
database_schema.sql (core)
├── courses_schema.sql
├── notifications_schema.sql
├── assignments_schema.sql
├── quiz_schema.sql
└── admin_schema.sql
```

---

## 📊 File Statistics

| Category           | Count | Description                        |
| ------------------ | ----- | ---------------------------------- |
| **Backend Files**  | 40+   | API endpoints, services, utilities |
| **Frontend Files** | 60+   | Components, pages, hooks, services |
| **Database Files** | 15+   | SQL schemas and migrations         |
| **Documentation**  | 25+   | Comprehensive documentation        |
| **Configuration**  | 5+    | Environment and config files       |
| **Scripts**        | 5+    | Utility and testing scripts        |

---

## 🚀 Quick Navigation

### **For Development**

1. **`backend/main.py`** - Start backend server
2. **`frontend/src/App.js`** - Main frontend application
3. **`database/database_schema.sql`** - Database structure

### **For Setup**

1. **`docs/SETUP_GUIDE.md`** - Complete setup instructions
2. **`backend/env.example`** - Environment configuration
3. **`start_learnsphere.py`** - Professional startup

### **For Testing**

1. **`api_performance_report.py`** - API testing
2. **`supabase_performance_analyzer.py`** - Database testing
3. **`test_email_specific.py`** - Email testing

### **For Documentation**

1. **`README.md`** - Main documentation
2. **`docs/README.md`** - Documentation index
3. **`docs/API_DOCUMENTATION.md`** - API reference

---

**Last Updated**: December 2024  
**Structure Version**: 2.0.0  
**Total Files**: 150+ files across all directories
