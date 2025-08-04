#!/usr/bin/env python3
"""
Fix foreign key constraints on profiles table
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

def check_constraints():
    """Check what constraints exist on the profiles table"""
    print("🔍 Checking current constraints on profiles table...")
    
    query = """
    SELECT 
        conname as constraint_name,
        contype as constraint_type,
        pg_get_constraintdef(oid) as constraint_definition
    FROM pg_constraint 
    WHERE conrelid = 'profiles'::regclass;
    """
    
    try:
        result = supabase_admin.rpc('exec_sql', {'sql': query}).execute()
        
        if result.data:
            print("📋 Current constraints:")
            for constraint in result.data:
                print(f"  - {constraint['constraint_name']} ({constraint['constraint_type']})")
                print(f"    Definition: {constraint['constraint_definition']}")
        else:
            print("✅ No constraints found or unable to query")
            
    except Exception as e:
        print(f"❌ Error checking constraints: {str(e)}")

def remove_foreign_key_constraints():
    """Remove foreign key constraints that prevent custom user IDs"""
    print("\n🔧 Removing foreign key constraints...")
    
    constraints_to_remove = [
        'profiles_id_fkey',
        'profiles_user_id_fkey', 
        'fk_profiles_user_id'
    ]
    
    for constraint in constraints_to_remove:
        try:
            sql = f"ALTER TABLE profiles DROP CONSTRAINT IF EXISTS {constraint};"
            result = supabase_admin.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Attempted to remove constraint: {constraint}")
        except Exception as e:
            print(f"⚠️  Error removing {constraint}: {str(e)}")

def main():
    print("🔧 LearnSphere Constraint Fix Tool")
    print("=" * 50)
    
    # Check current constraints
    check_constraints()
    
    # Remove problematic constraints
    remove_foreign_key_constraints()
    
    # Check constraints again
    print("\n" + "=" * 50)
    check_constraints()
    
    print("\n🏁 Constraint fix completed!")
    print("Now try testing registration again.")

if __name__ == "__main__":
    main()
