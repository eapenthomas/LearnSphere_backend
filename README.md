# 🎓 LearnSphere - Complete Learning Management System

<div align="center">
  <img src="https://img.shields.io/badge/React-18.2.0-blue?style=for-the-badge&logo=react" alt="React Version"/>
  <img src="https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi" alt="FastAPI Version"/>
  <img src="https://img.shields.io/badge/Supabase-Database-orange?style=for-the-badge&logo=supabase" alt="Supabase Database"/>
  <img src="https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python" alt="Python Version"/>
</div>

## 🌟 Overview

LearnSphere is a comprehensive Learning Management System (LMS) built with modern web technologies. It provides a complete platform for educational institutions, teachers, and students to manage courses, assignments, quizzes, and learning materials.

## ✨ Key Features

### 🎯 Core Functionality

- **User Management**: Student, Teacher, and Admin roles with secure authentication
- **Course Management**: Create, manage, and organize courses with thumbnails and categories
- **Assignment System**: Create assignments, track submissions, and grade student work
- **Quiz System**: Interactive quizzes with AI-powered question generation
- **Forum System**: Course-specific doubt forums with role-based access control
- **File Management**: Upload and organize course materials with Supabase storage
- **Progress Tracking**: Monitor student progress and course completion
- **Notification System**: Real-time notifications for assignments, grades, and updates

### 🤖 AI-Powered Features

- **Notes Summarizer**: Upload PDFs and get AI-generated summaries
- **Quiz Generator**: Automatically generate quiz questions from course materials
- **Smart Recommendations**: AI-driven course and content suggestions

### 💰 Payment Integration

- **Razorpay Integration**: Secure payment processing for paid courses
- **Subscription Management**: Handle course subscriptions and payments

## 🚀 Quick Start

### Option 1: Professional Startup Script

```bash
# Clone the repository
git clone https://github.com/your-username/LearnSphere.git
cd LearnSphere

# Start both backend and frontend with one command
python scripts/start_learnsphere_professional.py
```

### Option 2: Manual Startup

#### Backend Application

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will be available at: http://localhost:8000

#### Frontend Application

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🌐 Quick Access Links

Once the application is running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin

## 📚 Documentation

All documentation is organized in the `docs/` folder:

### 📖 Main Documentation

- **[Main README](docs/MAIN_README.md)** - Detailed project overview and setup
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete development environment setup
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment to Render & Vercel
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing with Selenium

### 🏗️ Architecture & Features

- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - System architecture and vision
- **[Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)** - Detailed technical specifications
- **[Features Documentation](docs/FEATURES_DOCUMENTATION.md)** - Complete feature list
- **[API Documentation](docs/API_DOCUMENTATION.md)** - API endpoints reference

### 🔧 System Components

- **[Authentication System](docs/AUTH_SYSTEM_README.md)** - User authentication and authorization
- **[Course Management](docs/COURSE_MANAGEMENT_README.md)** - Course creation and management
- **[Notification System](docs/NOTIFICATION_SYSTEM_README.md)** - Real-time notifications
- **[Database Schema](docs/DATABASE_SCHEMA_README.md)** - Database structure and relationships

### 🎨 UI/UX Components

- **[Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)** - Frontend and backend architecture

### 📊 Analytics & Management

- **[Course Management](docs/COURSE_MANAGEMENT_README.md)** - Course creation and management features

### 🗄️ Database & Storage

- **[Database Schema](docs/DATABASE_SCHEMA_README.md)** - Database setup and configuration

### 🔐 Security & Payments

- **[Authentication System](docs/AUTH_SYSTEM_README.md)** - User authentication and security

## 🛠️ Technology Stack

### Frontend

- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Framer Motion** - Smooth animations
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons

### Backend

- **FastAPI** - Modern Python web framework
- **Python 3.8+** - Programming language
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **SQLAlchemy** - Database ORM
- **Uvicorn** - ASGI server

### Database & Storage

- **Supabase** - PostgreSQL database and real-time features
- **PostgreSQL** - Primary database
- **Supabase Storage** - File storage solution

### AI & External Services

- **OpenAI API** - AI-powered features
- **DeepSeek API** - Alternative AI provider
- **SMTP** - Email notifications
- **Razorpay** - Payment processing

## 🏃‍♂️ Getting Started

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/LearnSphere.git
   cd LearnSphere
   ```

2. **Setup Environment**

   - Copy `backend/.env.example` to `backend/.env`
   - Copy `frontend/.env.example` to `frontend/.env`
   - Configure your environment variables

3. **Install Dependencies**

   ```bash
   # Backend dependencies
   cd backend && pip install -r requirements.txt

   # Frontend dependencies
   cd frontend && npm install
   ```

4. **Start the Application**

   ```bash
   # Use the professional startup script
   python scripts/start_learnsphere_professional.py
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🧪 Testing

Comprehensive testing guide available in [Testing Guide](docs/TESTING_GUIDE.md):

```bash
# Run automated tests
python scripts/run_tests.py

# Run specific test suites
python -c "from tests.test_setup import LearnSphereTester; t = LearnSphereTester(); t.setup_driver(); t.test_course_creation(); t.teardown_driver()"
```

## 🚀 Deployment

Complete deployment guide available in [Deployment Guide](docs/DEPLOYMENT_GUIDE.md):

- **Backend**: Deploy to Render
- **Frontend**: Deploy to Vercel
- **Database**: Configure Supabase production
- **Custom Domains**: Setup production domains

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for help and ideas

## 🎯 Roadmap

- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Video conferencing integration
- [ ] Gamification features
- [ ] Multi-language support
- [ ] Advanced AI tutoring

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by the need for accessible education
- Community-driven development approach

---

<div align="center">
  <p>Made with ❤️ for the education community</p>
  <p>
    <a href="docs/MAIN_README.md">📖 Full Documentation</a> •
    <a href="docs/DEPLOYMENT_GUIDE.md">🚀 Deployment Guide</a> •
    <a href="docs/TESTING_GUIDE.md">🧪 Testing Guide</a>
  </p>
</div>
