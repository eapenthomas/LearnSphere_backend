#!/usr/bin/env python3
"""
Script to help update Render deployment with correct environment variables
"""

import os
import subprocess
import sys

def main():
    print("LearnSphere Backend Deployment Update")
    print("=" * 50)
    
    print("\nIssues Fixed:")
    print("- Google OAuth redirect URL now uses FRONTEND_URL environment variable")
    print("- CORS configuration updated for Vercel frontend")
    print("- All hardcoded localhost URLs replaced with environment variables")
    
    print("\nRequired Actions:")
    print("\n1. Update Render Environment Variables:")
    print("   Go to your Render dashboard:")
    print("   - Navigate to your 'learnsphere-backend' service")
    print("   - Go to Environment tab")
    print("   - Add/Update this environment variable:")
    print("   FRONTEND_URL=https://learn-sphere-frontend-black.vercel.app")
    
    print("\n2. Update Supabase OAuth Settings:")
    print("   Go to your Supabase dashboard:")
    print("   - Navigate to Authentication > Settings")
    print("   - Under 'Site URL', set:")
    print("   https://learn-sphere-frontend-black.vercel.app")
    print("   - Under 'Redirect URLs', add:")
    print("   https://learn-sphere-frontend-black.vercel.app/auth/callback")
    
    print("\n3. Deploy the Changes:")
    print("   Option A - Automatic (if auto-deploy is enabled):")
    print("   git add .")
    print("   git commit -m 'Fix OAuth redirect and CORS for production'")
    print("   git push origin main")
    
    print("\n   Option B - Manual deployment:")
    print("   - Go to Render Dashboard")
    print("   - Find your backend service")
    print("   - Click 'Manual Deploy' -> 'Deploy latest commit'")
    
    print("\nEnvironment Variables to Set in Render:")
    env_vars = {
        "FRONTEND_URL": "https://learn-sphere-frontend-black.vercel.app",
        "SUPABASE_URL": "your_supabase_url",
        "SUPABASE_ANON_KEY": "your_supabase_anon_key", 
        "SUPABASE_SERVICE_ROLE_KEY": "your_supabase_service_role_key",
        "GOOGLE_CLIENT_ID": "your_google_client_id",
        "GOOGLE_CLIENT_SECRET": "your_google_client_secret",
        "JWT_SECRET_KEY": "your_jwt_secret_key",
        "EMAIL_HOST": "smtp.gmail.com",
        "EMAIL_PORT": "587",
        "EMAIL_USER": "your_email@gmail.com",
        "EMAIL_PASS": "your_app_password",
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "your_email@gmail.com",
        "SMTP_PASSWORD": "your_app_password",
        "FROM_EMAIL": "your_email@gmail.com",
        "FROM_NAME": "LearnSphere"
    }
    
    for key, value in env_vars.items():
        print(f"   {key}={value}")
    
    print("\nTroubleshooting:")
    print("   - If CORS errors persist, wait 2-3 minutes for deployment to complete")
    print("   - Check Render logs for any startup errors")
    print("   - Verify all environment variables are set correctly")
    print("   - Test the health endpoint: https://learnsphere-backend-d57a.onrender.com/health")
    
    print("\nAfter deployment, test:")
    print("   1. Google OAuth login should redirect to Vercel frontend")
    print("   2. Registration should work without CORS errors")
    print("   3. All API calls from frontend should work")

if __name__ == "__main__":
    main()
