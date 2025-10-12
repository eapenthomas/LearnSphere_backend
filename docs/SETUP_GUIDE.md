# 🚀 LearnSphere Setup Guide

## 📋 Prerequisites

Before setting up LearnSphere, ensure you have the following installed on your system:

### **Required Software**

- **Node.js** (v16.0.0 or higher) - [Download here](https://nodejs.org/)
- **Python** (v3.8 or higher) - [Download here](https://python.org/)
- **Git** - [Download here](https://git-scm.com/)
- **Code Editor** (VS Code recommended) - [Download here](https://code.visualstudio.com/)

### **Required Accounts**

- **Supabase Account** - [Sign up here](https://supabase.com/)
- **Email Account** (Gmail recommended) for SMTP configuration

---

## 🏗️ Project Setup

### **Step 1: Clone the Repository**

```bash
# Clone the repository
git clone <repository-url>
cd LearnSphere

# Verify the project structure
ls -la
```

**Expected Structure:**

```
LearnSphere/
├── backend/
├── frontend/
├── database/
├── docs/
├── README.md
└── start_learnsphere.py
```

### **Step 2: Supabase Setup**

#### **2.1 Create Supabase Project**

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `learnsphere`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your location
5. Click "Create new project"

#### **2.2 Get Project Credentials**

1. Go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**
   - **Service Role Key** (keep this secret!)

#### **2.3 Run Database Migrations**

1. Go to **SQL Editor** in Supabase Dashboard
2. Run the following SQL files in order:

```sql
-- 1. Core database schema
-- Copy and paste contents of database/database_schema.sql

-- 2. Courses schema with categories
-- Copy and paste contents of database/courses_schema.sql

-- 3. Notifications schema
-- Copy and paste contents of database/notifications_schema.sql

-- 4. Course materials schema
-- Copy and paste contents of database/course_materials_schema.sql

-- 5. Assignments schema
-- Copy and paste contents of database/assignments_schema.sql

-- 6. Quiz schema
-- Copy and paste contents of database/quiz_schema.sql

-- 7. Admin schema
-- Copy and paste contents of database/admin_schema.sql
```

#### **2.4 Enable Row Level Security (RLS)**

```sql
-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (examples)
CREATE POLICY "Users can view their own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Teachers can manage their own courses"
ON courses FOR ALL
USING (auth.uid() = teacher_id);
```

---

## ⚙️ Backend Setup

### **Step 1: Navigate to Backend Directory**

```bash
cd backend
```

### **Step 2: Install Python Dependencies**

```bash
# Install dependencies
pip install -r requirements.txt

# If you encounter issues, try:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### **Step 3: Environment Configuration**

```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

#### **Environment Variables (.env file):**

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password-here
FROM_EMAIL=your-email@gmail.com
FROM_NAME=LearnSphere

# Payment Configuration (Optional - for Razorpay)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Application Settings
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### **Step 4: Gmail SMTP Setup (for Email Notifications)**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `EMAIL_PASS`

### **Step 5: Test Backend Setup**

```bash
# Test the backend server
python main.py
```

**Expected Output:**

```
🚀 Starting LearnSphere API...
🚀 Loading LearnSphere modules...
✅ All modules loaded successfully
✅ LearnSphere API started successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Access Points:**

- **API Server**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 🎨 Frontend Setup

### **Step 1: Navigate to Frontend Directory**

```bash
# From project root
cd frontend
```

### **Step 2: Install Node Dependencies**

```bash
# Install dependencies
npm install

# If you encounter issues, try:
npm cache clean --force
npm install
```

### **Step 3: Environment Configuration**

```bash
# Create environment file
touch .env.local

# Edit the file
nano .env.local  # or use your preferred editor
```

#### **Frontend Environment Variables (.env.local):**

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Supabase Configuration (for direct client access if needed)
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key-here

# Application Settings
REACT_APP_APP_NAME=LearnSphere
REACT_APP_VERSION=2.0.0
```

### **Step 4: Test Frontend Setup**

```bash
# Start the development server
npm start
```

**Expected Output:**

```
Compiled successfully!

You can now view learnsphere in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000

Note that the development build is not optimized.
To create a production build, use npm run build.
```

**Access Points:**

- **Frontend Application**: [http://localhost:3000](http://localhost:3000)

---

## 🚀 Professional Startup

### **Option 1: Professional Startup Script (Recommended)**

```bash
# From project root directory
python start_learnsphere.py
```

This script will:

- ✅ Start both backend and frontend servers
- ✅ Open the application in your browser
- ✅ Display professional startup information
- ✅ Provide clickable links

### **Option 2: Manual Startup**

#### **Terminal 1 - Backend:**

```bash
cd backend
python main.py
```

#### **Terminal 2 - Frontend:**

```bash
cd frontend
npm start
```

---

## 🧪 Testing the Setup

### **Backend API Tests**

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test API documentation
open http://localhost:8000/docs
```

### **Frontend Tests**

```bash
# Test frontend
open http://localhost:3000
```

### **Database Connection Test**

```bash
# Run database performance test
python supabase_performance_analyzer.py
```

### **Email System Test**

```bash
# Test email configuration
python test_email_specific.py
```

---

## 📊 Performance Testing

### **API Performance Analysis**

```bash
# Generate comprehensive API performance report
python api_performance_report.py
```

**Expected Output:**

```
🚀 API Performance Analyzer
========================
📅 Generated: 2024-12-XX XX:XX:XX
🌐 Backend URL: http://localhost:8000

🔍 Testing Core Endpoints
-------------------------
✅ Authentication Endpoints
   Average: 45.2ms
   Success Rate: 100.0%

✅ Course Management Endpoints
   Average: 123.4ms
   Success Rate: 100.0%

✅ File Upload Endpoints
   Average: 234.5ms
   Success Rate: 100.0%

📊 Performance Summary
   Total Endpoints: 45
   Average Response Time: 156.7ms
   Performance Rating: ✅ Good
```

### **Database Performance Analysis**

```bash
# Analyze Supabase database performance
python supabase_performance_analyzer.py
```

---

## 🔧 Troubleshooting

### **Common Issues & Solutions**

#### **1. Backend Won't Start**

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:

```bash
cd backend
pip install -r requirements.txt
```

#### **2. Frontend Won't Start**

**Error**: `Module not found: Can't resolve 'react'`

**Solution**:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### **3. Database Connection Error**

**Error**: `supabase_url is required`

**Solution**:

1. Check your `.env` file in backend directory
2. Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
3. Verify Supabase project is active

#### **4. Email Not Working**

**Error**: `SMTPAuthenticationError`

**Solution**:

1. Enable 2-Factor Authentication on Gmail
2. Generate App Password
3. Use App Password in `EMAIL_PASS` (not your regular password)

#### **5. Port Already in Use**

**Error**: `[Errno 10048] error while attempting to bind`

**Solution**:

```bash
# Kill existing Python processes
taskkill /f /im python.exe

# Or change ports in configuration
```

#### **6. CORS Issues**

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**:

1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure frontend URL is included
3. Restart backend server

### **Performance Issues**

#### **Slow API Responses**

```bash
# Run performance analysis
python api_performance_report.py

# Optimize database queries
python supabase_performance_analyzer.py
```

#### **Slow Frontend Loading**

```bash
# Clear browser cache
# Check network tab in browser dev tools
# Ensure backend is responding quickly
```

---

## 📚 Additional Resources

### **Documentation**

- **Project Overview**: [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)
- **Features Documentation**: [docs/FEATURES_DOCUMENTATION.md](docs/FEATURES_DOCUMENTATION.md)
- **Technical Architecture**: [docs/TECHNICAL_ARCHITECTURE.md](docs/TECHNICAL_ARCHITECTURE.md)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### **Useful Commands**

```bash
# Clear database (start fresh)
cd backend
python clear_db.py

# Generate sample courses
# Run database/sample_courses.sql in Supabase SQL Editor

# Test email system
python test_email_specific.py

# Performance testing
python api_performance_report.py
python supabase_performance_analyzer.py

# Professional startup
python start_learnsphere.py
```

### **Development Tools**

```bash
# Backend development
cd backend
python main.py --reload  # Auto-reload on changes

# Frontend development
cd frontend
npm start  # Hot reload enabled by default
```

---

## 🎉 Success Checklist

After completing the setup, you should have:

- ✅ **Backend Server** running on [http://localhost:8000](http://localhost:8000)
- ✅ **Frontend Application** running on [http://localhost:3000](http://localhost:3000)
- ✅ **API Documentation** accessible at [http://localhost:8000/docs](http://localhost:8000/docs)
- ✅ **Database** connected and configured
- ✅ **Email System** configured and tested
- ✅ **Performance Tests** passing
- ✅ **Professional Startup** script working

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify environment variables** are correctly set
3. **Test individual components** (backend, frontend, database)
4. **Run performance tests** to identify bottlenecks
5. **Check the troubleshooting section** above
6. **Review the documentation** in the `docs/` folder

---

**Last Updated**: December 2024  
**Version**: 2.0.0  
**Setup Time**: ~15-30 minutes
