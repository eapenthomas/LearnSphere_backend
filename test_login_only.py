#!/usr/bin/env python3
"""
Test login functionality with existing user
"""

import os
import asyncio
from auth import AuthService
from models import LoginRequest
from dotenv import load_dotenv

load_dotenv()

async def test_existing_user_login():
    """Test login with the user we just updated"""
    print("🔐 Testing login with existing user...")
    
    # Test data for the user we just updated
    test_credentials = LoginRequest(
        email="newuser@example.com",
        password="password123"
    )
    
    try:
        result = await AuthService.login_user(test_credentials)
        print(f"✅ Login successful: {result.message}")
        print(f"User ID: {result.user_id}")
        print(f"Email: newuser@example.com")
        print(f"Role: {result.role}")
        print(f"Full Name: {result.full_name}")
        return result
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return None

async def main():
    print("🔧 LearnSphere Login Test")
    print("=" * 50)
    
    # Test login with existing user
    await test_existing_user_login()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
