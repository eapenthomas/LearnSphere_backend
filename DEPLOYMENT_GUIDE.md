# 🚀 LearnSphere Deployment Guide

Complete guide for deploying LearnSphere to Render (Backend) and Vercel (Frontend) from scratch.

## 📋 Prerequisites

- GitHub repository with your LearnSphere code
- Render account (for backend)
- Vercel account (for frontend)
- Supabase project setup
- Domain name (optional, for custom domains)

## 🗂️ Project Structure

```
LearnSphere/
├── backend/                 # FastAPI backend
│   ├── main.py             # Entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── ...
├── frontend/               # React frontend
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── .env.example        # Environment variables template
│   └── ...
├── database/               # SQL schemas
├── docs/                   # Documentation
└── DEPLOYMENT_GUIDE.md     # This file
```

## 🔧 Environment Variables Setup

### Backend Environment Variables (.env)

Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_production_ready
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
SUMMARY_API_KEY=your_openai_api_key
SUMMARY_API_PROVIDER=openai
SUMMARY_MODEL=gpt-4
SUMMARY_MAX_INPUT_CHARS=10000

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
FROM_NAME=LearnSphere

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Razorpay Payment Configuration
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables (.env)

Create a `.env` file in the `frontend/` directory:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# API Configuration
VITE_API_URL=https://your-backend-app.onrender.com

# Google OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your_google_client_id

# Razorpay Configuration
VITE_RAZORPAY_KEY_ID=your_razorpay_key_id
```

## 🌐 Backend Deployment (Render)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your GitHub repository

### Step 2: Deploy Backend Service

1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:

```
Name: learnsphere-backend
Environment: Python 3
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Environment Variables

Add all backend environment variables in Render dashboard:

1. Go to your service → Environment
2. Add each variable from your `.env` file
3. Use production values (not local development values)

### Step 4: Advanced Settings

```
Auto-Deploy: Yes (for automatic deployments on push)
Health Check Path: /health
```

### Step 5: Database Setup

1. In Render, create a PostgreSQL database:

   - Click "New" → "PostgreSQL"
   - Name: `learnsphere-db`
   - Plan: Free tier (or paid for production)

2. Update your Supabase connection or use Render's PostgreSQL:
   - Get connection string from Render database
   - Update `SUPABASE_URL` in environment variables

## ⚡ Frontend Deployment (Vercel)

### Step 1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your GitHub repository

### Step 2: Configure Project

1. Framework Preset: `Vite`
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`

### Step 3: Environment Variables

Add all frontend environment variables in Vercel dashboard:

1. Go to your project → Settings → Environment Variables
2. Add each variable from your frontend `.env` file
3. Update `VITE_API_URL` to your Render backend URL

### Step 4: Domain Configuration

1. Custom Domain (optional):
   - Add your domain in Vercel dashboard
   - Update DNS records as instructed
   - Update CORS settings in backend

## 🔄 CORS Configuration

Update your backend `main.py` to allow frontend domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://your-frontend-domain.vercel.app",  # Vercel
        "https://your-custom-domain.com",  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Database Setup

### Option 1: Use Supabase (Recommended)

1. Keep using your existing Supabase setup
2. Ensure all tables are created
3. Run any pending migrations

### Option 2: Use Render PostgreSQL

1. Connect to Render PostgreSQL
2. Run your SQL scripts from `database/` folder
3. Update environment variables

## 🔐 Security Checklist

### Backend Security

- [ ] Use strong JWT secret key
- [ ] Set secure CORS origins
- [ ] Use HTTPS only
- [ ] Validate all inputs
- [ ] Rate limiting implemented
- [ ] Environment variables secured

### Frontend Security

- [ ] No sensitive data in client-side code
- [ ] Environment variables prefixed with `VITE_`
- [ ] HTTPS enforced
- [ ] Content Security Policy headers

## 🚀 Deployment Commands

### Local Testing

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production Deployment

```bash
# Commit and push to GitHub
git add .
git commit -m "Deploy to production"
git push origin main

# Both Render and Vercel will auto-deploy
```

## 📈 Monitoring & Maintenance

### Render Monitoring

1. Check service logs regularly
2. Monitor resource usage
3. Set up uptime monitoring
4. Configure alerts

### Vercel Monitoring

1. Monitor build logs
2. Check function execution logs
3. Monitor performance metrics
4. Set up error tracking

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues

- **Build fails**: Check `requirements.txt` and Python version
- **Environment variables**: Ensure all required vars are set
- **Database connection**: Verify connection strings
- **CORS errors**: Update allowed origins

#### Frontend Issues

- **Build fails**: Check `package.json` dependencies
- **API calls fail**: Verify `VITE_API_URL` is correct
- **Environment variables**: Ensure `VITE_` prefix is used
- **Routing issues**: Check Vercel configuration

#### Database Issues

- **Connection timeout**: Check database credentials
- **Missing tables**: Run SQL scripts from `database/` folder
- **Migration errors**: Check SQL syntax

### Debug Commands

```bash
# Check backend logs
render logs your-service-name

# Check frontend build logs
vercel logs your-deployment-url

# Test API endpoints
curl https://your-backend.onrender.com/health

# Test frontend
curl https://your-frontend.vercel.app
```

## 📞 Support

### Render Support

- Documentation: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)

### Vercel Support

- Documentation: [vercel.com/docs](https://vercel.com/docs)
- Community: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)

### LearnSphere Support

- GitHub Issues: Create issues in your repository
- Documentation: Check `docs/` folder

## 🎯 Post-Deployment Checklist

- [ ] Backend service is running and healthy
- [ ] Frontend is accessible and loading
- [ ] Database connection is working
- [ ] Authentication is functional
- [ ] Email notifications are working
- [ ] Payment integration is tested
- [ ] Admin dashboard is accessible
- [ ] All API endpoints are responding
- [ ] CORS is properly configured
- [ ] Environment variables are secure
- [ ] Custom domains are working (if applicable)
- [ ] SSL certificates are active
- [ ] Monitoring is set up
- [ ] Backup strategy is in place

## 📝 Notes

- **Free Tier Limits**: Both Render and Vercel have free tier limitations
- **Auto-Deploy**: Both platforms auto-deploy on GitHub push
- **Environment Variables**: Never commit `.env` files to Git
- **Database**: Consider upgrading to paid plans for production
- **Monitoring**: Set up proper monitoring for production use
- **Backup**: Regular database backups are essential

---

**Happy Deploying! 🚀**

For questions or issues, please refer to the troubleshooting section or create an issue in your GitHub repository.
