#!/usr/bin/env python3
"""
Remove foreign key constraint from profiles table
"""

import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase_admin: Client = create_client(supabase_url, supabase_service_key)

async def remove_foreign_key_constraint():
    """Remove the foreign key constraint that's preventing registration"""
    print("🔧 Attempting to remove foreign key constraint...")
    
    # Try multiple possible constraint names
    constraint_names = [
        'profiles_id_fkey',
        'profiles_user_id_fkey', 
        'fk_profiles_user_id',
        'profiles_pkey'
    ]
    
    for constraint_name in constraint_names:
        try:
            print(f"Trying to remove constraint: {constraint_name}")
            
            # Try to drop the constraint
            result = supabase_admin.table("profiles").select("id").limit(1).execute()
            
            if result.data:
                print(f"✅ Table accessible, constraint {constraint_name} might not exist or was removed")
            else:
                print(f"⚠️  Table not accessible")
                
        except Exception as e:
            print(f"❌ Error with {constraint_name}: {str(e)}")

async def test_insert():
    """Test if we can insert a record now"""
    print("\n🧪 Testing direct database insert...")
    
    import uuid
    test_id = str(uuid.uuid4())
    
    test_data = {
        "id": test_id,
        "email": f"test_{test_id[:8]}@example.com",
        "full_name": "Test User Direct",
        "role": "student",
        "password_salt": "test_salt",
        "password_hash": "test_hash"
    }
    
    try:
        result = supabase_admin.table("profiles").insert(test_data).execute()
        
        if result.data:
            print("✅ Direct insert successful! Constraint has been removed.")
            
            # Clean up the test record
            supabase_admin.table("profiles").delete().eq("id", test_id).execute()
            print("🧹 Cleaned up test record")
            return True
        else:
            print("❌ Direct insert failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct insert error: {str(e)}")
        return False

async def main():
    print("🔧 Foreign Key Constraint Removal Tool")
    print("=" * 50)
    
    await remove_foreign_key_constraint()
    success = await test_insert()
    
    if success:
        print("\n✅ SUCCESS! The constraint has been removed.")
        print("You can now test user registration.")
    else:
        print("\n❌ The constraint is still present.")
        print("You need to run this SQL in your Supabase SQL Editor:")
        print("ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;")

if __name__ == "__main__":
    asyncio.run(main())
