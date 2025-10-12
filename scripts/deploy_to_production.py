#!/usr/bin/env python3
"""
LearnSphere Production Deployment Script
Automates deployment to Render (Backend) and Vercel (Frontend)
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_banner():
    """Print deployment banner"""
    print("=" * 80)
    print("🚀 LearnSphere Production Deployment")
    print("=" * 80)
    print("📦 Backend: Render.com")
    print("🌐 Frontend: Vercel.com")
    print("🗄️  Database: Supabase")
    print("💳 Payments: Razorpay")
    print("=" * 80)

def check_requirements():
    """Check deployment requirements"""
    print("\n🔍 Checking Deployment Requirements...")
    print("-" * 50)
    
    requirements = [
        ("Git", "git --version"),
        ("Node.js", "node --version"),
        ("npm", "npm --version"),
        ("Python", "python --version")
    ]
    
    for name, command in requirements:
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {name}: {version}")
            else:
                print(f"❌ {name}: Not found")
                return False
        except Exception:
            print(f"❌ {name}: Not found")
            return False
    
    print("-" * 50)
    return True

def create_render_config():
    """Create Render deployment configuration"""
    print("\n📝 Creating Render Configuration...")
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "learnsphere-backend",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {"key": "SUPABASE_URL", "sync": False},
                    {"key": "SUPABASE_SERVICE_ROLE_KEY", "sync": False},
                    {"key": "SECRET_KEY", "generateValue": True},
                    {"key": "RAZORPAY_KEY_ID", "sync": False},
                    {"key": "RAZORPAY_KEY_SECRET", "sync": False},
                    {"key": "OPENAI_API_KEY", "sync": False},
                    {"key": "EMAIL_HOST", "sync": False},
                    {"key": "EMAIL_PORT", "sync": False},
                    {"key": "EMAIL_USER", "sync": False},
                    {"key": "EMAIL_PASS", "sync": False}
                ]
            }
        ]
    }
    
    with open("backend/render.yaml", "w") as f:
        import yaml
        yaml.dump(render_config, f, default_flow_style=False)
    
    print("✅ Render configuration created: backend/render.yaml")

def create_vercel_config():
    """Create Vercel deployment configuration"""
    print("\n📝 Creating Vercel Configuration...")
    
    vercel_config = {
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
            {"handle": "filesystem"},
            {"src": "/(.*)", "dest": "/index.html"}
        ],
        "env": {
            "VITE_SUPABASE_URL": "@supabase_url",
            "VITE_SUPABASE_ANON_KEY": "@supabase_anon_key",
            "VITE_API_URL": "@api_url",
            "VITE_RAZORPAY_KEY_ID": "@razorpay_key_id"
        }
    }
    
    with open("frontend/vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    print("✅ Vercel configuration created: frontend/vercel.json")

def create_deployment_guide():
    """Create step-by-step deployment guide"""
    print("\n📚 Creating Deployment Guide...")
    
    guide = """# LearnSphere Production Deployment Guide

## 🚀 Quick Deployment Steps

### 1. Backend Deployment (Render)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for production deployment"
   git push origin main
   ```

2. **Deploy to Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select LearnSphere repository
   - Configure settings:
     - Name: `learnsphere-backend`
     - Environment: `Python 3`
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_key
   SECRET_KEY=your_jwt_secret
   RAZORPAY_KEY_ID=your_razorpay_key
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   OPENAI_API_KEY=your_openai_key
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USER=your_email
   EMAIL_PASS=your_app_password
   ```

### 2. Frontend Deployment (Vercel)

1. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import GitHub repository
   - Configure settings:
     - Project Name: `learnsphere-frontend`
     - Framework Preset: `Vite`
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`

2. **Set Environment Variables**:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_anon_key
   VITE_API_URL=https://your-backend.onrender.com
   VITE_RAZORPAY_KEY_ID=your_razorpay_key
   ```

### 3. Database Setup (Supabase)

1. **Production Database**:
   - Create new Supabase project for production
   - Run all SQL files from `database/` folder
   - Configure Row Level Security (RLS)
   - Set up storage buckets

2. **Authentication**:
   - Update Site URL to your Vercel URL
   - Configure redirect URLs
   - Set up email templates

### 4. Payment Setup (Razorpay)

1. **Production Keys**:
   - Complete KYC verification
   - Switch to Live Mode
   - Generate Live API keys
   - Update environment variables

2. **Webhooks**:
   - Add webhook URL: `https://your-backend.onrender.com/api/payment/webhook`
   - Select payment events

## 🧪 Testing Production

1. **Health Checks**:
   - Backend: `https://your-backend.onrender.com/health`
   - Frontend: Visit your Vercel URL
   - Database: Test user registration

2. **Feature Testing**:
   - User registration/login
   - Course creation/enrollment
   - File uploads
   - Payment processing
   - Email notifications

## 📊 Monitoring

1. **Render Dashboard**: Monitor backend performance
2. **Vercel Analytics**: Track frontend metrics
3. **Supabase Dashboard**: Monitor database usage
4. **Razorpay Dashboard**: Track payments

## 🔧 Troubleshooting

### Common Issues:

1. **CORS Errors**: Update backend CORS settings
2. **Environment Variables**: Double-check all values
3. **Build Failures**: Check logs in deployment dashboards
4. **Database Connection**: Verify Supabase credentials

### Support:
- Check deployment logs
- Verify environment variables
- Test API endpoints
- Check browser console for errors

## 🎉 Success!

Once deployed, your LearnSphere will be available at:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-service.onrender.com`
- **API Docs**: `https://your-service.onrender.com/docs`

Congratulations! Your Learning Management System is now live! 🚀
"""
    
    with open("DEPLOYMENT_INSTRUCTIONS.md", "w") as f:
        f.write(guide)
    
    print("✅ Deployment guide created: DEPLOYMENT_INSTRUCTIONS.md")

def show_next_steps():
    """Show next steps for deployment"""
    print("\n🎯 Next Steps for Deployment:")
    print("-" * 50)
    print("1. 📝 Review configuration files created")
    print("2. 🔑 Ensure all environment variables are set")
    print("3. 📤 Push code to GitHub repository")
    print("4. 🚀 Deploy backend to Render.com")
    print("5. 🌐 Deploy frontend to Vercel.com")
    print("6. 🗄️  Set up production Supabase database")
    print("7. 💳 Configure Razorpay for live payments")
    print("8. 🧪 Test all features in production")
    print("-" * 50)
    print("📚 See DEPLOYMENT_INSTRUCTIONS.md for detailed steps")

def main():
    """Main deployment preparation function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Missing required tools. Please install them first.")
        return
    
    try:
        # Create configuration files
        create_render_config()
        create_vercel_config()
        create_deployment_guide()
        
        print("\n✅ Deployment preparation completed!")
        show_next_steps()
        
    except Exception as e:
        print(f"❌ Deployment preparation failed: {e}")

if __name__ == "__main__":
    main()
