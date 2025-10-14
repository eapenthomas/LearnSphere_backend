#!/usr/bin/env python3
"""
Test script for course materials fetch functionality
"""

import requests
import json

# Configuration
BACKEND_URL = "https://learnsphere-backend-d57a.onrender.com"
TEACHER_EMAIL = "aura@example.com"
TEACHER_PASSWORD = "testpassword123"
COURSE_ID = "63fc03e6-812a-4cd9-af0c-4898181b58a9"  # Introduction to Web Development

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
            print(f"✅ Login successful!")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_fetch_materials(access_token, course_id):
    """Test fetching course materials"""
    print(f"📁 Testing materials fetch for course {course_id}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/course-materials/course/{course_id}",
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            materials = response.json()
            print(f"✅ Materials fetch successful!")
            print(f"   Found {len(materials)} materials")
            
            for i, material in enumerate(materials):
                print(f"   {i+1}. {material.get('file_name')} ({material.get('file_size')} bytes)")
                print(f"      Uploaded: {material.get('uploaded_at')}")
                print(f"      URL: {material.get('file_url')}")
            
            return True
        else:
            print(f"❌ Materials fetch failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Materials fetch error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting course materials fetch test...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Course ID: {COURSE_ID}")
    print("-" * 50)
    
    # Step 1: Login
    access_token = test_login()
    if not access_token:
        print("❌ Cannot proceed without access token")
        return
    
    # Step 2: Test fetch
    success = test_fetch_materials(access_token, COURSE_ID)
    
    if success:
        print("\n🎉 Materials fetch test passed!")
    else:
        print("\n💥 Materials fetch test failed.")

if __name__ == "__main__":
    main()
