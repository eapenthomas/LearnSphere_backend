#!/usr/bin/env python3
"""
Debug what emails are in the database
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

def check_emails():
    """Check what emails are in the database"""
    print("🔍 Checking emails in profiles table...")
    
    try:
        all_profiles = supabase_admin.table("profiles").select("id, email, full_name").execute()
        
        print(f"📋 Found {len(all_profiles.data or [])} profiles:")
        
        for profile in all_profiles.data or []:
            email = profile.get("email")
            print(f"  - ID: {profile.get('id')}")
            print(f"    Name: {profile.get('full_name')}")
            print(f"    Email: {email if email else 'None'}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking emails: {str(e)}")

def test_email_check():
    """Test the email checking logic"""
    print("🧪 Testing email check logic...")
    
    test_email = "testuser_12345@example.com"
    print(f"Testing with email: {test_email}")
    
    try:
        all_profiles = supabase_admin.table("profiles").select("id, email").execute()
        
        found = False
        for profile in all_profiles.data or []:
            if profile.get("email") and profile.get("email").lower() == test_email.lower():
                found = True
                print(f"❌ Email {test_email} already exists!")
                break
        
        if not found:
            print(f"✅ Email {test_email} is available")
            
    except Exception as e:
        print(f"❌ Error testing email: {str(e)}")

def main():
    print("🔧 Email Debug Tool")
    print("=" * 50)
    
    check_emails()
    test_email_check()

if __name__ == "__main__":
    main()
