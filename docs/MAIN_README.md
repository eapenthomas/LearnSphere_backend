# 🎓 LearnSphere - Professional Learning Management System

<div align="center">

![LearnSphere Logo](https://img.shields.io/badge/LearnSphere-v2.0.0-blue?style=for-the-badge&logo=graduation-cap)

**A comprehensive Learning Management System built with React, FastAPI, and Supabase**

[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react&logoColor=white)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=flat&logo=supabase&logoColor=white)](https://supabase.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.3.0-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

</div>

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🏗️ Project Structure](#️-project-structure)
- [✨ Features & Functionalities](#-features--functionalities)
- [🛠️ Technology Stack](#️-technology-stack)
- [📊 Performance Metrics](#-performance-metrics)
- [🔧 Configuration](#-configuration)
- [📚 API Documentation](#-api-documentation)
- [🧪 Testing & Analysis](#-testing--analysis)

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **Git**
- **Supabase Account**

### Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd LearnSphere
   ```

2. **Backend Setup**

   ```bash
   cd backend
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Starting the Application

#### Option 1: Professional Startup Script

```bash
python start_learnsphere_professional.py
```

_This will automatically start both backend and frontend servers, open the application in your browser, and show professional status output._

#### Option 2: Manual Startup

**Backend Server:**

```bash
cd backend
python main.py
```

**Backend URL:** [http://localhost:8000](http://localhost:8000)

**Frontend Application:**

```bash
cd frontend
npm run dev
```

**Frontend URL:** [http://localhost:3000](http://localhost:3000)

### Quick Access Links

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

---

## 🏗️ Project Structure

```
LearnSphere/
├── 📁 backend/                          # FastAPI Backend
│   ├── 📄 main.py                      # Main server file (optimized)
│   ├── 📁 api/                         # API endpoint modules
│   │   ├── 📄 auth_api.py              # Authentication endpoints
│   │   ├── 📄 course_api.py            # Course management
│   │   ├── 📄 enrollment_api.py        # Course enrollment
│   │   ├── 📄 notifications_api.py     # Notification system
│   │   ├── 📄 course_completion_api.py # Course completion tracking
│   │   └── 📄 course_materials_enhanced.py # Multiple file upload
│   ├── 📁 models/                      # Pydantic data models
│   ├── 📁 utils/                       # Utility functions
│   ├── 📁 middleware/                  # Custom middleware
│   ├── 📄 requirements.txt             # Python dependencies
│   └── 📄 .env                         # Environment variables
├── 📁 frontend/                        # React Frontend
│   ├── 📁 src/
│   │   ├── 📁 components/              # Reusable UI components
│   │   │   ├── 📄 DashboardLayout.jsx  # Student dashboard layout
│   │   │   ├── 📄 NotificationBell.jsx # Notification component
│   │   │   └── 📄 CourseThumbnail.jsx  # Course thumbnail display
│   │   ├── 📁 pages/                   # Page components
│   │   │   ├── 📁 student/             # Student-specific pages
│   │   │   └── 📁 teacher/             # Teacher-specific pages
│   │   ├── 📁 contexts/                # React contexts
│   │   │   └── 📄 AuthContext.jsx      # Authentication context
│   │   ├── 📁 utils/                   # Utility functions
│   │   │   └── 📄 thumbnailUtils.jsx   # Thumbnail handling
│   │   └── 📁 styles/                  # CSS and styling
│   ├── 📄 package.json                 # Node dependencies
│   └── 📄 public/                      # Static assets
├── 📁 database/                        # Database schemas and migrations
│   ├── 📄 courses_schema.sql           # Courses table with categories
│   ├── 📄 notifications_schema.sql     # Notification system schema
│   └── 📄 sample_courses.sql           # Sample course data
├── 📁 docs/                            # Documentation
│   ├── 📄 NOTIFICATION_SYSTEM_README.md
│   ├── 📄 COURSE_MANAGEMENT_README.md
│   └── 📄 AUTH_SYSTEM_README.md
├── 📄 api_performance_report.py        # API performance testing
├── 📄 supabase_performance_analyzer.py # Database performance analysis
├── 📄 start_learnsphere.py             # Professional startup script
└── 📄 README.md                        # This file
```

---

## ✨ Features & Functionalities

### 🎓 **Course Management System**

#### **Course Creation & Management**

- ✅ **Create courses** with detailed information (title, description, category)
- ✅ **Course categories** (Programming, Data Science, Design, Business, etc.)
- ✅ **Course thumbnails** with support for uploaded images and external URLs
- ✅ **Course status management** (Active, Draft)
- ✅ **Teacher course dashboard** with analytics

#### **Course Enrollment System**

- ✅ **Student enrollment** in courses
- ✅ **Enrollment tracking** and management
- ✅ **Course progress tracking** for students
- ✅ **Enrollment analytics** for teachers

#### **Course Materials Management**

- ✅ **Multiple file upload** (up to 10 files simultaneously)
- ✅ **Supported file types**: PDF, DOC, PPT, images, videos, archives
- ✅ **File size limit**: 50MB per file
- ✅ **Automatic file organization** by course and timestamp
- ✅ **Material description** and metadata
- ✅ **File download** and preview functionality

### 🔔 **Advanced Notification System**

#### **In-App Notifications**

- ✅ **31 different notification types** covering all system events
- ✅ **Real-time notifications** with WebSocket support
- ✅ **Notification preferences** and settings
- ✅ **Notification history** and management
- ✅ **Unread notification count** display

#### **Email Notification System**

- ✅ **Course completion emails** with beautiful HTML templates
- ✅ **Assignment and quiz notifications**
- ✅ **System announcements** and updates
- ✅ **Email templates** with responsive design
- ✅ **SMTP configuration** for reliable delivery

### 🎨 **User Interface & Experience**

#### **Responsive Design**

- ✅ **Mobile-first design** with TailwindCSS
- ✅ **Dark/Light theme** support
- ✅ **Professional UI components** with consistent styling
- ✅ **Smooth animations** with Framer Motion
- ✅ **Accessible design** following WCAG guidelines

#### **Dashboard Systems**

- ✅ **Student Dashboard** with course overview and progress
- ✅ **Teacher Dashboard** with course management and analytics
- ✅ **Admin Dashboard** with system management tools
- ✅ **Role-based access control** for different user types

#### **Course Discovery & Filtering**

- ✅ **All Courses page** with comprehensive course listing
- ✅ **Category filtering** with dynamic category extraction
- ✅ **Search functionality** across courses, teachers, and content
- ✅ **Course sorting** by date, popularity, rating
- ✅ **Thumbnail display** with proper fallbacks

### 🔐 **Authentication & Security**

#### **User Authentication**

- ✅ **JWT-based authentication** with refresh tokens
- ✅ **Role-based access control** (Student, Teacher, Admin)
- ✅ **Secure password handling** with hashing
- ✅ **Session management** with auto-refresh
- ✅ **Profile management** with avatar uploads

#### **Security Features**

- ✅ **Row Level Security (RLS)** in Supabase
- ✅ **API endpoint protection** with middleware
- ✅ **File upload validation** and security
- ✅ **CORS configuration** for cross-origin requests
- ✅ **Input validation** with Pydantic models

### 📊 **Analytics & Reporting**

#### **Teacher Analytics**

- ✅ **Course performance metrics**
- ✅ **Student enrollment statistics**
- ✅ **Assignment and quiz analytics**
- ✅ **Revenue tracking** (for paid courses)
- ✅ **Course completion rates**

#### **System Analytics**

- ✅ **API performance monitoring**
- ✅ **Database query optimization**
- ✅ **User activity tracking**
- ✅ **System health monitoring**

### 🧪 **Assessment & Evaluation**

#### **Assignment System**

- ✅ **Create assignments** with detailed instructions
- ✅ **File submission** support
- ✅ **Grading system** with feedback
- ✅ **Due date management** with notifications
- ✅ **Submission tracking** and analytics

#### **Quiz System**

- ✅ **Create quizzes** with multiple question types
- ✅ **Auto-grading** for objective questions
- ✅ **Quiz analytics** and performance tracking
- ✅ **Time-limited quizzes** with countdown
- ✅ **Question bank** management

### 💰 **Payment & Monetization**

#### **Payment Integration**

- ✅ **Razorpay integration** for Indian payments
- ✅ **Course pricing** and payment processing
- ✅ **Revenue tracking** for teachers
- ✅ **Payment history** and receipts
- ✅ **Refund management**

### 🔧 **System Features**

#### **Performance Optimization**

- ✅ **Lazy loading** for heavy modules
- ✅ **Database connection pooling**
- ✅ **Query optimization** with proper indexing
- ✅ **Caching layer** for frequent queries
- ✅ **Fast server startup** (3-5 seconds)

#### **File Management**

- ✅ **Supabase Storage** integration
- ✅ **File upload** with progress tracking
- ✅ **Image optimization** and resizing
- ✅ **Secure file serving** with access control
- ✅ **File cleanup** and maintenance

#### **Developer Experience**

- ✅ **Comprehensive API documentation** with Swagger
- ✅ **Performance testing tools**
- ✅ **Database migration scripts**
- ✅ **Environment configuration** management
- ✅ **Professional startup scripts**

---

## 🛠️ Technology Stack

### **Frontend Technologies**

- **React 18.2.0** - Modern UI framework with hooks
- **TailwindCSS 3.3.0** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **React Hot Toast** - Beautiful notifications
- **Lucide React** - Consistent icon library

### **Backend Technologies**

- **FastAPI 0.104.1** - Modern, fast web framework
- **Python 3.8+** - Programming language
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production
- **SQLAlchemy** - Database ORM (optional)
- **SMTP** - Email delivery system

### **Database & Storage**

- **Supabase** - Backend-as-a-Service platform
- **PostgreSQL** - Primary relational database
- **Supabase Storage** - File storage and CDN
- **Row Level Security** - Database-level security
- **Real-time subscriptions** - Live data updates

### **Development Tools**

- **ESLint** - Code linting and formatting
- **Prettier** - Code formatting
- **Jest** - Testing framework
- **Git** - Version control
- **Docker** - Containerization (optional)

---

## 📊 Performance Metrics

| Feature             | Performance                   | Status               |
| ------------------- | ----------------------------- | -------------------- |
| Server Startup      | ~3-5 seconds                  | ✅ Optimized         |
| API Response Time   | ~2-3 seconds                  | ⚠️ Network dependent |
| File Upload         | Up to 10 files simultaneously | ✅ Excellent         |
| Database Queries    | Optimized with caching        | ✅ Good              |
| Frontend Load Time  | ~1-2 seconds                  | ✅ Fast              |
| Notification System | Real-time                     | ✅ Excellent         |
| Concurrent Users    | 100+ supported                | ✅ Scalable          |

---

## 🔧 Configuration

### Environment Variables

**Backend (.env file):**

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=LearnSphere

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Payment Configuration (Optional)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### Database Setup

1. **Create Supabase Project**
2. **Run Database Migrations:**
   ```sql
   -- Run in Supabase SQL Editor
   -- Execute: database/courses_schema.sql
   -- Execute: database/notifications_schema.sql
   -- Execute: database/sample_courses.sql (optional)
   ```

---

## 📚 API Documentation

### **Core Endpoints**

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### **Authentication Endpoints**

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### **Course Management**

- `GET /api/courses/` - Get all courses
- `POST /api/courses/` - Create new course
- `GET /api/courses/categories` - Get course categories
- `GET /api/courses/{id}` - Get specific course
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course

### **Course Materials**

- `POST /api/course-materials/upload-multiple` - Upload multiple files
- `GET /api/course-materials/course/{id}` - Get course materials
- `DELETE /api/course-materials/{id}` - Delete material
- `PUT /api/course-materials/{id}` - Update material

### **Notifications**

- `GET /api/notifications/` - Get user notifications
- `GET /api/notifications/types` - Get notification types
- `POST /api/notifications/mark-read/{id}` - Mark as read
- `POST /api/notifications/mark-all-read` - Mark all as read

### **Course Completion**

- `POST /api/course-completion/mark-complete` - Mark course complete
- `GET /api/course-completion/my-completions` - Get user completions
- `GET /api/course-completion/stats` - Get completion statistics

---

## 🧪 Testing & Analysis

### **Performance Testing**

```bash
# Generate API performance report
python api_performance_report.py

# Analyze Supabase database performance
python supabase_performance_analyzer.py

# Test email system
python test_email_specific.py
```

### **Available Test Reports**

- **API Performance Report** - Comprehensive endpoint testing
- **Database Performance Analysis** - Supabase query optimization
- **Email System Test** - SMTP configuration validation
- **Concurrent Request Testing** - Load testing capabilities

---

## 🚀 Deployment

### **Production Deployment**

#### Quick Deployment Setup

```bash
# Prepare deployment configuration
python deploy_to_production.py
```

#### Manual Deployment Steps

1. **Backend Deployment (Render):**

   - Deploy to [Render.com](https://render.com)
   - Use `backend/render.yaml` configuration
   - Set environment variables in Render dashboard

2. **Frontend Deployment (Vercel):**

   - Deploy to [Vercel.com](https://vercel.com)
   - Use `frontend/vercel.json` configuration
   - Set environment variables in Vercel dashboard

3. **Database Setup:**
   - Use Supabase production instance
   - Configure RLS policies
   - Set up monitoring

**See `DEPLOYMENT_INSTRUCTIONS.md` for detailed deployment guide.**

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

- **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **Performance Reports:** Run analysis scripts
- **Issues:** Create GitHub issues for bugs or features

---

<div align="center">

**🎉 LearnSphere - Empowering Education Through Technology**

_Built with ❤️ for educators and learners worldwide_

**Version 2.0.0** | **Last Updated:** December 2024

</div>
