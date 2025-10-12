# 🚀 LearnSphere Deployment Guide

Complete step-by-step guide for deploying LearnSphere to production using Render (Backend) and Vercel (Frontend).

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Render)](#backend-deployment-render)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [Database Setup (Supabase)](#database-setup-supabase)
5. [Environment Configuration](#environment-configuration)
6. [Domain Configuration](#domain-configuration)
7. [Post-Deployment Testing](#post-deployment-testing)
8. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Accounts
- **Render Account** (for backend hosting)
- **Vercel Account** (for frontend hosting)
- **Supabase Account** (for database)
- **GitHub Account** (for code repository)

### Required Tools
- Git
- Node.js 16+
- Python 3.8+

## 🖥️ Backend Deployment (Render)

### Step 1: Prepare Backend for Production

1. **Update requirements.txt**
```bash
cd backend
pip freeze > requirements.txt
```

2. **Create Render-specific files**

Create `backend/start.sh`:
```bash
#!/bin/bash
# Render startup script
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

Make it executable:
```bash
chmod +x backend/start.sh
```

3. **Update main.py for production**
```python
# Add at the end of backend/main.py
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### Step 2: Deploy to Render

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   ```
   Name: learnsphere-backend
   Environment: Python 3
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: ./start.sh
   ```

3. **Environment Variables**
   Add these environment variables in Render dashboard:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   JWT_SECRET_KEY=your_jwt_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   REFRESH_TOKEN_EXPIRE_DAYS=7
   OPENAI_API_KEY=your_openai_api_key (optional)
   SUMMARY_API_KEY=your_summary_api_key (optional)
   DEEPSEEK_OPENAI_API_KEY=your_deepseek_api_key (optional)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the service URL (e.g., `https://learnsphere-backend.onrender.com`)

### Step 3: Test Backend Deployment

```bash
# Test health endpoint
curl https://your-backend-url.onrender.com/health

# Test API documentation
# Visit: https://your-backend-url.onrender.com/docs
```

## 🌐 Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Production

1. **Update environment variables**

Create `frontend/.env.production`:
```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

2. **Update package.json**
```json
{
  "name": "learnsphere-frontend",
  "version": "1.0.0",
  "scripts": {
    "build": "vite build",
    "dev": "vite",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "framer-motion": "^10.0.0",
    "lucide-react": "^0.263.0",
    "react-hot-toast": "^2.4.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0"
  }
}
```

3. **Create Vercel configuration**

Create `vercel.json` in project root:
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/frontend/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

### Step 2: Deploy to Vercel

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Project**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

3. **Environment Variables**
   Add in Vercel dashboard:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note the frontend URL (e.g., `https://learnsphere.vercel.app`)

### Step 3: Test Frontend Deployment

1. Visit your Vercel URL
2. Test user registration
3. Test user login
4. Test course creation
5. Test all major features

## 🗄️ Database Setup (Supabase)

### Step 1: Production Database Configuration

1. **Create Production Project**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Create a new project for production
   - Note the URL and API keys

2. **Run Database Migrations**
   ```sql
   -- Run all SQL files in database/ folder
   -- Execute in order:
   -- 1. database_schema.sql
   -- 2. admin_schema.sql
   -- 3. courses_schema.sql
   -- 4. assignments_schema.sql
   -- 5. course_materials_schema.sql
   -- 6. course_progress_schema.sql
   -- 7. enrollment_schema.sql
   -- 8. forum_schema.sql
   -- 9. notifications_schema.sql
   -- 10. create_storage_bucket.sql
   -- 11. create_teacher_ratings_table.sql
   -- 12. latest_updates_december_2024.sql
   ```

3. **Configure Row Level Security (RLS)**
   - Enable RLS on all tables
   - Configure policies for each table
   - Test access controls

4. **Setup Storage**
   - Create storage buckets for course materials
   - Configure storage policies
   - Test file uploads

### Step 2: Database Optimization

1. **Create Indexes**
   ```sql
   -- Performance indexes
   CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
   CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
   CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);
   CREATE INDEX IF NOT EXISTS idx_forum_questions_course_id ON forum_questions(course_id);
   CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
   ```

2. **Configure Connection Pooling**
   - Enable connection pooling in Supabase
   - Set appropriate pool size

## ⚙️ Environment Configuration

### Production Environment Variables

#### Backend (Render)
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Services (Optional)
OPENAI_API_KEY=your_openai_key
SUMMARY_API_KEY=your_summary_key
DEEPSEEK_OPENAI_API_KEY=your_deepseek_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# Payment (Optional)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

#### Frontend (Vercel)
```bash
# API Configuration
VITE_API_BASE_URL=https://your-backend-url.onrender.com

# Optional: Analytics
VITE_GA_TRACKING_ID=your_google_analytics_id
```

## 🌍 Domain Configuration

### Custom Domain Setup

1. **Backend Domain (Render)**
   - Go to Render dashboard
   - Click on your service
   - Go to Settings → Custom Domains
   - Add your domain (e.g., `api.learnsphere.com`)
   - Update DNS records as instructed

2. **Frontend Domain (Vercel)**
   - Go to Vercel dashboard
   - Click on your project
   - Go to Settings → Domains
   - Add your domain (e.g., `learnsphere.com`)
   - Update DNS records as instructed

3. **Update Environment Variables**
   - Update `VITE_API_BASE_URL` to use custom backend domain
   - Redeploy frontend

## 🧪 Post-Deployment Testing

### Automated Testing Script

Create `test_production.py`:
```python
import requests
import time

def test_production_deployment():
    """Test production deployment"""
    backend_url = "https://your-backend-url.onrender.com"
    frontend_url = "https://your-frontend-url.vercel.app"
    
    tests = [
        ("Backend Health", f"{backend_url}/health"),
        ("Backend API Docs", f"{backend_url}/docs"),
        ("Frontend", frontend_url),
    ]
    
    for test_name, url in tests:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {test_name}: OK")
            else:
                print(f"❌ {test_name}: {response.status_code}")
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")

if __name__ == "__main__":
    test_production_deployment()
```

### Manual Testing Checklist

- [ ] Backend health endpoint responds
- [ ] API documentation loads
- [ ] Frontend loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] Course creation works
- [ ] File uploads work
- [ ] Email notifications work
- [ ] Database queries perform well
- [ ] All major features functional

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend Deployment Issues

**Issue**: Build fails on Render
**Solution**: 
```bash
# Check requirements.txt
pip freeze > requirements.txt

# Ensure all dependencies are included
# Check Python version compatibility
```

**Issue**: Environment variables not loading
**Solution**:
- Double-check variable names in Render dashboard
- Ensure no trailing spaces
- Restart service after adding variables

#### 2. Frontend Deployment Issues

**Issue**: Build fails on Vercel
**Solution**:
```bash
# Check Node.js version
node --version

# Update package.json engines
{
  "engines": {
    "node": ">=16.0.0"
  }
}
```

**Issue**: API calls failing
**Solution**:
- Verify `VITE_API_BASE_URL` is correct
- Check CORS configuration in backend
- Ensure backend is accessible

#### 3. Database Issues

**Issue**: Connection timeouts
**Solution**:
- Enable connection pooling in Supabase
- Optimize database queries
- Check RLS policies

**Issue**: File uploads failing
**Solution**:
- Verify storage bucket configuration
- Check storage policies
- Ensure proper file permissions

### Performance Optimization

#### Backend Optimization
```python
# Add to main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Connection pooling
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# Caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_data():
    # Cache frequently accessed data
    pass
```

#### Frontend Optimization
```javascript
// Lazy loading
const LazyComponent = React.lazy(() => import('./Component'));

// Code splitting
import { Suspense } from 'react';

// Image optimization
<img 
  src={imageUrl} 
  loading="lazy" 
  alt="Course thumbnail"
/>
```

### Monitoring and Logging

#### Backend Monitoring
```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Add health checks
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.now().isoformat()
    }
```

#### Frontend Monitoring
```javascript
// Error tracking
window.addEventListener('error', (event) => {
  console.error('Frontend Error:', event.error);
  // Send to monitoring service
});

// Performance monitoring
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Performance:', entry.name, entry.duration);
  }
});
observer.observe({ entryTypes: ['navigation', 'measure'] });
```

## 📊 Production Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates configured
- [ ] Domain DNS configured

### Post-Deployment
- [ ] Health checks passing
- [ ] All features working
- [ ] Performance acceptable
- [ ] Error monitoring setup
- [ ] Backup strategy implemented

### Ongoing Maintenance
- [ ] Regular security updates
- [ ] Performance monitoring
- [ ] Database optimization
- [ ] Log analysis
- [ ] User feedback collection

## 🔒 Security Considerations

### Production Security
1. **Environment Variables**
   - Never commit secrets to repository
   - Use strong, unique secrets
   - Rotate keys regularly

2. **Database Security**
   - Enable RLS on all tables
   - Use least privilege principle
   - Regular security audits

3. **API Security**
   - Implement rate limiting
   - Validate all inputs
   - Use HTTPS everywhere

4. **Frontend Security**
   - Sanitize user inputs
   - Implement CSP headers
   - Regular dependency updates

This deployment guide ensures a robust, scalable, and secure production deployment of LearnSphere.
