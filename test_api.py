#!/usr/bin/env python3
"""
Test the API endpoints
"""

import requests
import json

API_BASE_URL = 'http://localhost:8000'

def test_login_api():
    """Test the login API endpoint"""
    print("🔐 Testing Login API...")
    
    login_data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/login", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Login API successful!")
            print(f"User ID: {result.get('user_id')}")
            print(f"Role: {result.get('role')}")
            print(f"Full Name: {result.get('full_name')}")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Login API failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login API error: {str(e)}")
        return False

def test_register_api():
    """Test the register API endpoint"""
    print("\n📝 Testing Register API...")

    # Generate unique email to avoid duplicates
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    register_data = {
        "email": f"testuser_{unique_id}@example.com",
        "password": "testpass123",
        "full_name": "Test User API",
        "role": "student"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/register", json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Register API successful!")
            print(f"User ID: {result.get('user_id')}")
            print(f"Role: {result.get('role')}")
            print(f"Full Name: {result.get('full_name')}")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Register API failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Register API error: {str(e)}")
        return False

def test_health_api():
    """Test the health check endpoint"""
    print("\n🏥 Testing Health API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health API successful!")
            print(f"Status: {result.get('status')}")
            print(f"Service: {result.get('service')}")
            return True
        else:
            print(f"❌ Health API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health API error: {str(e)}")
        return False

def main():
    print("🔧 LearnSphere API Test")
    print("=" * 50)
    
    # Test health endpoint first
    if not test_health_api():
        print("❌ Server not responding. Make sure the backend is running.")
        return
    
    # Test login with existing user
    test_login_api()
    
    # Test registration (this might fail due to foreign key constraint)
    test_register_api()
    
    print("\n" + "=" * 50)
    print("🏁 API Test completed!")

if __name__ == "__main__":
    main()
