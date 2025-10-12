# LearnSphere Project Structure

## 📁 Directory Organization

```
Learn_Sphere/
├── 📄 README.md                    # Main project documentation
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization guide
├── 🐍 start.py                     # Quick start script for development
├── 🔧 .gitignore                   # Git ignore rules
│
├── 📁 backend/                     # Backend API (FastAPI + Python)
│   ├── 🐍 main.py                  # FastAPI application entry point
│   ├── 🐍 models.py                # Pydantic data models
│   ├── 🐍 auth.py                  # Authentication system
│   ├── 🐍 auth_middleware.py       # JWT middleware
│   ├── 🐍 email_service.py         # Email notification service
│   ├── 🐍 supabase_storage.py      # File storage management
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 env.example              # Environment variables template
│   │
│   ├── 📁 API Modules/
│   │   ├── 🐍 admin_*.py           # Admin management APIs
│   │   ├── 🐍 assignment*.py       # Assignment management
│   │   ├── 🐍 course*.py           # Course management
│   │   ├── 🐍 quiz*.py             # Quiz system
│   │   ├── 🐍 teacher*.py          # Teacher verification & analytics
│   │   ├── 🐍 student*.py          # Student features
│   │   ├── 🐍 ai_*.py              # AI-powered features
│   │   └── 🐍 notification*.py     # Notification system
│   │
│   └── 📁 __pycache__/             # Python bytecode cache
│
├── 📁 frontend/                    # Frontend (React + Vite)
│   ├── 📄 package.json             # Node.js dependencies
│   ├── 📄 vite.config.js           # Vite configuration
│   ├── 📄 tailwind.config.cjs      # Tailwind CSS configuration
│   ├── 📄 env.example              # Environment variables template
│   │
│   ├── 📁 src/                     # Source code
│   │   ├── 📄 main.jsx             # React application entry point
│   │   ├── 📄 App.jsx              # Main application component
│   │   ├── 📄 index.css            # Global styles
│   │   │
│   │   ├── 📁 components/          # Reusable UI components
│   │   ├── 📁 pages/               # Page components
│   │   │   ├── 📁 admin/           # Admin dashboard pages
│   │   │   ├── 📁 teacher/         # Teacher dashboard pages
│   │   │   └── 📁 student/         # Student dashboard pages
│   │   ├── 📁 layouts/             # Layout components
│   │   ├── 📁 contexts/            # React contexts
│   │   ├── 📁 hooks/               # Custom React hooks
│   │   └── 📁 utils/               # Utility functions
│   │
│   ├── 📁 public/                  # Static assets
│   ├── 📁 dist/                    # Built application
│   └── 📁 node_modules/            # Node.js dependencies
│
├── 📁 database/                    # Database schemas and migrations
│   ├── 📄 current_database_schema.sql    # Current complete schema
│   ├── 📄 database_snapshot_20250111.sql # Database snapshot
│   ├── 📄 database_schema.sql            # Legacy schema
│   ├── 📄 admin_schema.sql               # Admin tables
│   ├── 📄 assignments_schema.sql         # Assignment tables
│   ├── 📄 courses_schema.sql             # Course tables
│   ├── 📄 forum_schema.sql               # Forum tables
│   ├── 📄 notifications_schema.sql       # Notification tables
│   └── 📄 *.sql                           # Other schema files
│
├── 📁 docs/                        # Documentation
│   ├── 📄 MAIN_README.md           # Main documentation
│   ├── 📄 PROJECT_OVERVIEW.md      # Project overview
│   ├── 📄 SETUP_GUIDE.md           # Setup instructions
│   ├── 📄 API_DOCUMENTATION.md     # API documentation
│   ├── 📄 DEPLOYMENT_GUIDE.md      # Deployment guide
│   ├── 📄 FEATURES_DOCUMENTATION.md # Features documentation
│   ├── 📄 TECHNICAL_ARCHITECTURE.md # Technical architecture
│   ├── 📄 AUTH_SYSTEM_README.md    # Authentication system
│   ├── 📄 COURSE_MANAGEMENT_README.md # Course management
│   ├── 📄 NOTIFICATION_SYSTEM_README.md # Notification system
│   ├── 📄 DATABASE_SCHEMA_README.md # Database documentation
│   ├── 📄 PROJECT_STRUCTURE.md     # Project structure
│   ├── 📄 COMPREHENSIVE_ANALYSIS_REPORT.md # Analysis report
│   ├── 📄 TEACHER_VERIFICATION_COMPLETE.md # Teacher verification
│   ├── 📄 TEACHER_VERIFICATION_QUICK_START.md # Quick start guide
│   ├── 📄 OCR_EMAIL_NOTIFICATIONS_IMPLEMENTATION.md # OCR implementation
│   └── 📄 TESTING_GUIDE.md         # Testing guide
│
├── 📁 scripts/                     # Utility and startup scripts
│   ├── 🐍 start_dev.py             # Development environment starter
│   ├── 🐍 start_learnsphere.py     # Basic startup script
│   ├── 🐍 start_learnsphere_professional.py # Professional startup
│   ├── 🐍 start_backend_simple.py  # Backend-only startup
│   ├── 🐍 deploy_to_production.py  # Production deployment
│   ├── 🐍 api_performance_report.py # API performance testing
│   └── 🐍 supabase_performance_analyzer.py # Database performance
│
├── 📁 tests/                       # Test files and reports
│   ├── 🐍 test_auth_endpoints.py   # Authentication tests
│   ├── 🐍 test_jwt_persistence.py  # JWT persistence tests
│   ├── 🐍 test_teacher_verification.py # Teacher verification tests
│   ├── 📄 test_modal_display.html  # Modal display test
│   └── 📄 *.json                   # Performance reports
│
└── 📁 testing materials/           # Test assets
    ├── 📁 course materials/        # Sample course files
    ├── 📁 id cards/                # Sample ID cards for testing
    └── 📁 thumbnails/              # Sample thumbnails
```

## 🚀 Quick Start

### Development Environment

```bash
# Option 1: Use the quick start script
python start.py

# Option 2: Manual startup
python scripts/start_dev.py

# Option 3: Backend only
python scripts/start_backend_simple.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📋 Key Features

### 🔐 Authentication System

- JWT-based authentication
- Role-based access control (Admin, Teacher, Student)
- Google OAuth integration
- Password reset with OTP

### 👨‍🏫 Teacher Features

- Course creation and management
- Assignment and quiz creation
- Student progress tracking
- AI-powered quiz generation
- Teacher verification with OCR
- Analytics and reporting

### 👨‍🎓 Student Features

- Course enrollment
- Assignment submission
- Quiz taking
- Progress tracking
- AI tutor assistance
- Forum participation

### 👨‍💼 Admin Features

- User management
- Teacher approval system
- System analytics
- Email notifications
- Activity monitoring

### 🤖 AI Features

- OCR-based teacher verification
- AI-powered quiz generation
- Intelligent tutor assistance
- Document summarization

## 🗄️ Database Structure

### Core Tables

- `profiles` - User accounts and information
- `courses` - Course data
- `enrollments` - Student course enrollments
- `assignments` - Assignment data
- `quizzes` - Quiz data
- `course_materials` - Course files and materials

### Verification & Approval

- `teacher_verification_requests` - OCR verification data
- `teacher_approval_requests` - Manual approval workflow
- `email_notifications` - Email tracking

### Analytics & Progress

- `course_progress` - Student progress tracking
- `learning_streaks` - Learning analytics
- `ai_usage_logs` - AI feature usage tracking

## 🔧 Configuration

### Environment Variables

- Copy `backend/env.example` to `backend/.env`
- Copy `frontend/env.example` to `frontend/.env`
- Configure Supabase, OpenAI, and email settings

### Database Setup

- Use `database/current_database_schema.sql` for setup
- Apply migrations from `database/` folder
- Reference `database/database_snapshot_20250111.sql` for current state

## 📚 Documentation

All documentation is organized in the `docs/` folder:

- **Setup Guide**: Get started quickly
- **API Documentation**: Backend API reference
- **Features Documentation**: Detailed feature descriptions
- **Technical Architecture**: System design and architecture
- **Testing Guide**: How to test the application

## 🧪 Testing

Test files are organized in the `tests/` folder:

- Authentication tests
- Teacher verification tests
- Performance reports
- UI component tests

## 📁 File Organization Principles

1. **Separation of Concerns**: Backend, frontend, and database are separate
2. **Documentation**: All docs in dedicated `docs/` folder
3. **Scripts**: Utility scripts in `scripts/` folder
4. **Testing**: Test files and reports in `tests/` folder
5. **Clean Root**: Only essential files in root directory
6. **Modular Backend**: API modules organized by feature
7. **Component-based Frontend**: React components organized by purpose

## 🔄 Maintenance

### Regular Tasks

- Update documentation when adding features
- Clean up test files and reports
- Keep database schema files updated
- Maintain environment variable templates
- Update README files for new features

### Database Maintenance

- Regular backups using snapshots
- Performance monitoring with analyzer scripts
- Schema updates documented in database folder
- Clean up old test data regularly
