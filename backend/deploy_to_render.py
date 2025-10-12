#!/usr/bin/env python3
"""
Script to help deploy updated backend to Render
This script provides instructions for updating your Render deployment
"""

import os
import subprocess
import sys

def main():
    print("🚀 LearnSphere Backend Deployment Helper")
    print("=" * 50)
    
    print("\n📋 Current Status:")
    print("✅ Frontend deployed to Vercel")
    print("⚠️  Backend needs CORS update on Render")
    
    print("\n🔧 To fix the CORS issues:")
    print("1. Commit your changes to Git:")
    print("   git add .")
    print("   git commit -m 'Fix CORS for Vercel frontend'")
    print("   git push origin main")
    
    print("\n2. Render will automatically redeploy with the new CORS settings")
    print("   Your backend URL: https://learnsphere-backend-d57a.onrender.com")
    
    print("\n3. Alternative: Manual Render deployment")
    print("   - Go to Render Dashboard")
    print("   - Find your 'learnsphere-backend' service")
    print("   - Click 'Manual Deploy' -> 'Deploy latest commit'")
    
    print("\n🌐 Updated CORS Origins:")
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://learn-sphere-frontend-black.vercel.app",
        "https://learn-sphere-frontend-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-git-main-eapenthomas-projects.vercel.app",
        "https://learn-sphere-frontend-grfp9yq65-eapenthomas-projects.vercel.app"
    ]
    
    for origin in origins:
        print(f"   ✅ {origin}")
    
    print("\n📝 Environment Variable Option:")
    print("You can also set ADDITIONAL_CORS_ORIGINS in Render environment variables")
    print("Format: https://new-domain.com,https://another-domain.com")

if __name__ == "__main__":
    main()
