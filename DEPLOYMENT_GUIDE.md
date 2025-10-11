# LearnSphere Deployment Guide

## Complete Step-by-Step Deployment Instructions

This guide will walk you through deploying LearnSphere to production using Render (Backend) and Vercel (Frontend).

---

## Prerequisites

### Required Accounts

1. **Render Account** (Free tier available)

   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account

2. **Vercel Account** (Free tier available)

   - Sign up at [vercel.com](https://vercel.com)
   - Connect your GitHub account

3. **Supabase Account** (Free tier available)

   - Sign up at [supabase.com](https://supabase.com)
   - Create a new project

4. **Razorpay Account** (For payments)
   - Sign up at [razorpay.com](https://razorpay.com)
   - Complete KYC for live payments

### Required Information

- GitHub repository with LearnSphere code
- Supabase project URL and keys
- Razorpay API keys (test/live)
- OpenAI/DeepSeek API key (for AI features)

---

## Part 1: Backend Deployment on Render

### Step 1: Prepare Backend for Production

#### 1.1 Create Production Requirements File

Create `backend/requirements.txt` with all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
supabase==2.0.0
python-dotenv==1.0.0
pydantic==2.5.0
requests==2.31.0
razorpay==1.3.0
openai==1.3.0
Pillow==10.1.0
aiofiles==23.2.1
```

#### 1.2 Create Render Configuration

Create `backend/render.yaml`:

```yaml
services:
  - type: web
    name: learnsphere-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: SECRET_KEY
        generateValue: true
      - key: RAZORPAY_KEY_ID
        sync: false
      - key: RAZORPAY_KEY_SECRET
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: DEEPSEEK_OPENAI_API_KEY
        sync: false
```

#### 1.3 Update CORS Settings

Update `backend/main.py` CORS configuration:

```python
# CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://learnsphere-frontend.vercel.app",  # Your Vercel URL
        "https://your-custom-domain.com"  # Your custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Deploy to Render

#### 2.1 Connect GitHub Repository

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your LearnSphere repository
5. Choose the repository

#### 2.2 Configure Service Settings

Fill in the following details:

**Basic Settings:**

- **Name**: `learnsphere-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your main branch)
- **Root Directory**: `backend`

**Build & Deploy:**

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 2.3 Set Environment Variables

Click **"Environment"** tab and add:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SECRET_KEY=your_jwt_secret_key_here
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret
OPENAI_API_KEY=sk-your_openai_key
DEEPSEEK_OPENAI_API_KEY=sk-your_deepseek_key
```

**Important**:

- Use **test keys** for Razorpay initially
- Generate a strong `SECRET_KEY` (32+ characters)
- Keep all keys secure

#### 2.4 Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build the application
   - Deploy to a public URL

#### 2.5 Verify Deployment

1. Wait for deployment to complete (5-10 minutes)
2. Check the **"Logs"** tab for any errors
3. Visit your service URL (e.g., `https://learnsphere-backend.onrender.com`)
4. You should see: `{"message": "LearnSphere API is running"}`

#### 2.6 Test API Endpoints

Test a few endpoints:

```bash
# Health check
curl https://your-backend-url.onrender.com/

# All courses
curl https://your-backend-url.onrender.com/api/courses/all

# API docs
curl https://your-backend-url.onrender.com/docs
```

---

## Part 2: Frontend Deployment on Vercel

### Step 1: Prepare Frontend for Production

#### 1.1 Create Vercel Configuration

Create `frontend/vercel.json`:

```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_SUPABASE_URL": "@supabase_url",
    "VITE_SUPABASE_ANON_KEY": "@supabase_anon_key",
    "VITE_API_URL": "@api_url",
    "VITE_RAZORPAY_KEY_ID": "@razorpay_key_id"
  }
}
```

#### 1.2 Update Environment Variables

Create `frontend/.env.production`:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=https://your-backend-url.onrender.com
VITE_RAZORPAY_KEY_ID=rzp_test_your_key_id
```

#### 1.3 Update API Base URL

Update `frontend/src/config/api.js` (if exists) or create it:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
};

export default apiConfig;
```

#### 1.4 Update Axios Configuration

Update all API calls to use the environment variable:

```javascript
// In your API files
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Example usage
const response = await axios.get(`${API_URL}/api/courses/all`);
```

### Step 2: Deploy to Vercel

#### 2.1 Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. Select your LearnSphere repository

#### 2.2 Configure Project Settings

Fill in the following:

**Project Settings:**

- **Project Name**: `learnsphere-frontend`
- **Framework Preset**: `Vite`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### 2.3 Set Environment Variables

In the **"Environment Variables"** section, add:

```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=https://your-backend-url.onrender.com
VITE_RAZORPAY_KEY_ID=rzp_test_your_key_id
```

#### 2.4 Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Install dependencies
   - Build the React app
   - Deploy to a public URL
   - Provide you with a URL like `https://learnsphere-frontend.vercel.app`

#### 2.5 Verify Deployment

1. Wait for deployment to complete (3-5 minutes)
2. Visit your Vercel URL
3. Test the application:
   - Try logging in
   - Browse courses
   - Test file uploads
   - Check if thumbnails display

---

## Part 3: Database Setup (Supabase)

### Step 1: Production Database Configuration

#### 1.1 Create Production Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click **"New Project"**
3. Choose organization
4. Enter project details:
   - **Name**: `learnsphere-production`
   - **Database Password**: Generate strong password
   - **Region**: Choose closest to your users

#### 1.2 Run Database Migrations

Execute all SQL files in your `database/` folder:

1. **Core Schema**:

```sql
-- Run all files in order:
-- 1. profiles_schema.sql
-- 2. courses_schema.sql
-- 3. enrollments_schema.sql
-- 4. course_materials_schema.sql
-- 5. assignments_schema.sql
-- 6. quizzes_schema.sql
-- 7. forum_schema.sql
-- 8. notifications_schema.sql
-- 9. payments_schema.sql
-- 10. indexes.sql
```

#### 1.3 Configure Row Level Security (RLS)

Enable RLS on all tables and create policies:

```sql
-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
-- ... (repeat for all tables)

-- Create policies (example for profiles)
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id);
```

#### 1.4 Set Up Storage Buckets

Create storage buckets in Supabase Dashboard:

1. Go to **Storage** → **Buckets**
2. Create these buckets:

   - `course-materials` (Public)
   - `course-thumbnails` (Public)
   - `profile-pictures` (Public)
   - `assignments` (Public)
   - `teacher-verifications` (Private)

3. Set bucket policies:

```sql
-- Example for course-thumbnails
CREATE POLICY "Anyone can view thumbnails" ON storage.objects
    FOR SELECT USING (bucket_id = 'course-thumbnails');

CREATE POLICY "Authenticated users can upload thumbnails" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'course-thumbnails' AND auth.role() = 'authenticated');
```

### Step 2: Authentication Setup

#### 2.1 Configure Auth Settings

In Supabase Dashboard → **Authentication** → **Settings**:

- **Site URL**: `https://your-frontend-url.vercel.app`
- **Redirect URLs**:
  - `https://your-frontend-url.vercel.app/auth/callback`
  - `https://your-frontend-url.vercel.app/dashboard`

#### 2.2 Set Up Email Templates

Configure email templates for:

- Email confirmation
- Password reset
- Magic link

---

## Part 4: Payment Setup (Razorpay)

### Step 1: Production Razorpay Configuration

#### 1.1 Complete KYC

1. Log in to Razorpay Dashboard
2. Complete KYC verification:
   - Business details
   - PAN card
   - Bank account details
   - GST information
   - Director/Owner documents

#### 1.2 Get Live API Keys

1. Switch to **Live Mode**
2. Go to **Settings** → **API Keys**
3. Generate **Live Key**
4. Copy:
   - **Key ID** (starts with `rzp_live_`)
   - **Key Secret**

#### 1.3 Update Environment Variables

Update your Render environment variables:

```
RAZORPAY_KEY_ID=rzp_live_your_live_key_id
RAZORPAY_KEY_SECRET=your_live_secret
```

#### 1.4 Configure Webhooks

1. Go to **Settings** → **Webhooks**
2. Add webhook URL: `https://your-backend-url.onrender.com/api/payment/webhook`
3. Select events:
   - `payment.authorized`
   - `payment.captured`
   - `payment.failed`
   - `order.paid`

---

## Part 5: Custom Domain Setup (Optional)

### Step 1: Backend Custom Domain (Render)

#### 1.1 Add Custom Domain

1. Go to your Render service
2. Click **"Settings"** → **"Custom Domains"**
3. Add your domain: `api.yourdomain.com`
4. Configure DNS:
   - Add CNAME record: `api` → `your-service.onrender.com`

#### 1.2 Update CORS

Update backend CORS to include your domain:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://your-frontend-url.vercel.app"
]
```

### Step 2: Frontend Custom Domain (Vercel)

#### 2.1 Add Custom Domain

1. Go to your Vercel project
2. Click **"Settings"** → **"Domains"**
3. Add your domain: `yourdomain.com`
4. Configure DNS:
   - Add A record: `@` → `76.76.19.61`
   - Add CNAME record: `www` → `cname.vercel-dns.com`

#### 2.2 Update Environment Variables

Update frontend environment:

```
VITE_API_URL=https://api.yourdomain.com
```

---

## Part 6: Monitoring & Maintenance

### Step 1: Set Up Monitoring

#### 1.1 Render Monitoring

- Monitor service health in Render dashboard
- Set up uptime monitoring
- Monitor resource usage

#### 1.2 Vercel Analytics

- Enable Vercel Analytics
- Monitor Core Web Vitals
- Track user interactions

#### 1.3 Error Tracking

Add Sentry for error tracking:

1. Sign up at [sentry.io](https://sentry.io)
2. Create project for LearnSphere
3. Add to both frontend and backend
4. Monitor errors and performance

### Step 2: Backup Strategy

#### 2.1 Database Backups

- Supabase automatically backs up daily
- Export data regularly
- Test restore procedures

#### 2.2 Code Backups

- Use Git for version control
- Tag releases
- Keep deployment logs

---

## Part 7: Testing Production Deployment

### Step 1: Comprehensive Testing

#### 1.1 Authentication Flow

- [ ] User registration works
- [ ] Email verification works
- [ ] Login/logout works
- [ ] Password reset works
- [ ] Session persistence works

#### 1.2 Course Management

- [ ] Teacher can create courses
- [ ] Thumbnail upload works
- [ ] Course materials upload works
- [ ] Students can enroll
- [ ] Payment integration works

#### 1.3 File Uploads

- [ ] Course materials (PDF, DOCX)
- [ ] Assignment files
- [ ] Profile pictures
- [ ] Course thumbnails
- [ ] File size validation works

#### 1.4 AI Features

- [ ] AI quiz generation works
- [ ] AI tutor responds
- [ ] Notes summarizer works
- [ ] API keys are configured

### Step 2: Performance Testing

#### 2.1 Load Testing

- Test with multiple concurrent users
- Monitor response times
- Check database performance
- Verify file upload limits

#### 2.2 Mobile Testing

- Test on different devices
- Check responsive design
- Verify touch interactions
- Test mobile file uploads

---

## Troubleshooting Common Issues

### Backend Issues

#### Issue: Service Won't Start

**Solution**:

- Check logs in Render dashboard
- Verify all environment variables
- Check Python version compatibility
- Ensure all dependencies are in requirements.txt

#### Issue: Database Connection Failed

**Solution**:

- Verify Supabase URL and keys
- Check network connectivity
- Verify database is running
- Check RLS policies

#### Issue: File Upload Fails

**Solution**:

- Check Supabase Storage configuration
- Verify bucket policies
- Check file size limits
- Verify CORS settings

### Frontend Issues

#### Issue: API Calls Fail

**Solution**:

- Check CORS configuration
- Verify API URL in environment
- Check network tab for errors
- Verify authentication tokens

#### Issue: Images Don't Load

**Solution**:

- Check Supabase Storage policies
- Verify image URLs
- Check CORS for images
- Verify bucket is public

#### Issue: Build Fails

**Solution**:

- Check Node.js version
- Verify all dependencies
- Check for TypeScript errors
- Review build logs

---

## Production Checklist

### Pre-Deployment

- [ ] All tests pass locally
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Storage buckets created
- [ ] Payment gateway configured
- [ ] SSL certificates active
- [ ] Custom domains configured
- [ ] Monitoring set up

### Post-Deployment

- [ ] All features tested
- [ ] Performance verified
- [ ] Security scan completed
- [ ] Backup strategy implemented
- [ ] Documentation updated
- [ ] Team access configured
- [ ] Support process defined

---

## Cost Estimation

### Free Tier Limits

- **Render**: 750 hours/month (free tier)
- **Vercel**: 100GB bandwidth/month
- **Supabase**: 500MB database, 1GB storage
- **Razorpay**: 2% transaction fee

### Scaling Costs

- **Render**: $7/month for always-on
- **Vercel Pro**: $20/month for unlimited
- **Supabase Pro**: $25/month for more resources
- **Custom Domain**: $10-15/year

---

## Security Best Practices

### Environment Variables

- Never commit secrets to Git
- Use different keys for test/production
- Rotate keys regularly
- Use strong passwords

### Database Security

- Enable RLS on all tables
- Use least privilege principle
- Regular security audits
- Monitor access logs

### API Security

- Rate limiting implemented
- Input validation
- SQL injection prevention
- XSS protection

---

## Support & Maintenance

### Regular Tasks

- Monitor service health
- Update dependencies
- Review security logs
- Backup data
- Performance optimization

### Emergency Procedures

- Service outage response
- Data recovery process
- Security incident response
- Rollback procedures

---

## Conclusion

Your LearnSphere application is now deployed to production!

**Backend**: `https://your-backend-url.onrender.com`
**Frontend**: `https://your-frontend-url.vercel.app`
**Database**: Supabase Production
**Payments**: Razorpay Live Mode

### Next Steps:

1. Test all features thoroughly
2. Set up monitoring and alerts
3. Configure backups
4. Plan for scaling
5. Gather user feedback
6. Iterate and improve

**Congratulations! Your Learning Management System is live! 🚀**
