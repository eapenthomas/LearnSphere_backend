#!/usr/bin/env python3
"""
Script to update existing user with email and password
Run this after updating your database schema
"""

import os
import asyncio
from auth import AuthService
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

async def update_existing_user():
    """Update existing user with email and password"""
    
    # Your existing user ID
    user_id = "8f267d13-8852-4b25-868f-7855445fb6bd"
    
    # Prompt for email and password
    print("Updating existing user with email and password...")
    print(f"User ID: {user_id}")
    
    email = input("Enter email address for this user: ").strip()
    if not email:
        print("Email is required!")
        return
    
    password = input("Enter password for this user: ").strip()
    if not password:
        print("Password is required!")
        return
    
    try:
        # Hash the password
        salt, hashed_password = AuthService.hash_password(password)
        
        # Update the user record
        update_data = {
            "email": email,
            "password_salt": salt,
            "password_hash": hashed_password
        }
        
        response = supabase_admin.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if response.data:
            print("✅ User updated successfully!")
            print(f"Email: {email}")
            print(f"User can now login with email and password")
        else:
            print("❌ Failed to update user")
            
    except Exception as e:
        print(f"❌ Error updating user: {str(e)}")

async def list_all_users():
    """List all users in the profiles table"""
    try:
        response = supabase_admin.table("profiles").select("*").execute()
        
        print("\n📋 All users in profiles table:")
        print("-" * 80)
        
        for user in response.data or []:
            print(f"ID: {user.get('id')}")
            print(f"Full Name: {user.get('full_name')}")
            print(f"Role: {user.get('role')}")
            print(f"Email: {user.get('email', 'Not set')}")
            print(f"Has Password: {'Yes' if user.get('password_hash') else 'No'}")
            print(f"Created: {user.get('created_at')}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")

async def main():
    print("🔧 LearnSphere User Update Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Update existing user with email/password")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await list_all_users()
        elif choice == "2":
            await update_existing_user()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    asyncio.run(main())
