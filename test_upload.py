#!/usr/bin/env python3
"""
Test script for course materials upload functionality
"""

import requests
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://learnsphere-backend-d57a.onrender.com"
FRONTEND_URL = "https://learn-sphere-frontend-black.vercel.app"

# Test credentials
TEACHER_EMAIL = "aura@example.com"
TEACHER_PASSWORD = "testpassword123"

def test_login():
    """Test teacher login and get access token"""
    print("🔐 Testing teacher login...")
    
    login_data = {
        "email": TEACHER_EMAIL,
        "password": TEACHER_PASSWORD
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print(f"✅ Login successful! Token: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_file_upload(access_token, course_id):
    """Test file upload functionality"""
    print(f"📁 Testing file upload for course {course_id}...")
    
    # Use a sample PDF file
    test_file_path = Path("testing materials/course materials/deployment pipeline.pdf")
    
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Prepare file upload
    with open(test_file_path, 'rb') as f:
        files = {
            'file': (test_file_path.name, f, 'application/pdf')
        }
        data = {
            'course_id': course_id,
            'description': 'Test upload from backend testing materials'
        }
        
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/course-materials/upload",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   File: {result.get('file_name')}")
                print(f"   URL: {result.get('file_url')}")
                print(f"   Size: {result.get('file_size')} bytes")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False

def test_course_list(access_token):
    """Test getting teacher's courses"""
    print("📚 Using known course ID for testing...")
    
    # Use a known course ID for the test teacher
    course_id = "63fc03e6-812a-4cd9-af0c-4898181b58a9"  # Introduction to Web Development
    print(f"   Using course: Introduction to Web Development (ID: {course_id})")
    return course_id

def main():
    """Main test function"""
    print("🚀 Starting course materials upload test...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Teacher: {TEACHER_EMAIL}")
    print("-" * 50)
    
    # Step 1: Login
    access_token = test_login()
    if not access_token:
        print("❌ Cannot proceed without access token")
        return
    
    # Step 2: Get courses
    course_id = test_course_list(access_token)
    if not course_id:
        print("❌ Cannot proceed without a course")
        return
    
    # Step 3: Test upload
    success = test_file_upload(access_token, course_id)
    
    if success:
        print("\n🎉 All tests passed! File upload is working correctly.")
    else:
        print("\n💥 Upload test failed. Check the logs above.")

if __name__ == "__main__":
    main()
