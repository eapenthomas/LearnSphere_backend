#!/usr/bin/env python3
"""
Simple registration test to see exactly what's happening
"""

import requests
import uuid

API_BASE_URL = 'http://localhost:8000'

def test_simple_registration():
    """Test registration with a completely unique email"""
    
    # Generate a truly unique email
    unique_id = str(uuid.uuid4())
    test_email = f"test_{unique_id}@example.com"
    
    print(f"🧪 Testing registration with email: {test_email}")
    
    register_data = {
        "email": test_email,
        "password": "testpass123",
        "full_name": "Test User Simple",
        "role": "student"
    }
    
    try:
        print("📤 Sending registration request...")
        response = requests.post(f"{API_BASE_URL}/register", json=register_data)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration successful!")
            print(f"User ID: {result.get('user_id')}")
            print(f"Role: {result.get('role')}")
            print(f"Full Name: {result.get('full_name')}")
            print(f"Message: {result.get('message')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Simple Registration Test")
    print("=" * 50)
    test_simple_registration()
