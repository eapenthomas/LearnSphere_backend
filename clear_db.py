#!/usr/bin/env python3
"""
Clear database script for LearnSphere
Removes all course, assignment, and quiz data to start fresh
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def clear_database():
    """Clear all course-related data from the database"""
    
    # Initialize Supabase client (same as main.py)
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase configuration. Please check your .env file.")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    print("🗑️  Starting database cleanup...")
    print("=" * 50)
    
    try:
        # Clear data in dependency order (child tables first)
        tables_to_clear = [
            # Quiz related
            "quiz_submissions",
            "quiz_questions", 
            "quizzes",
            
            # Assignment related
            "assignment_submissions",
            "assignments",
            
            # Course related
            "course_materials",
            "course_progress",
            "enrollments",
            "courses",
            
            # Forum related
            "forum_answers",
            "forum_questions",
            
            # Teacher ratings
            "teacher_ratings",
            
            # Notifications
            "notifications",
            
            # Email notifications
            "email_notifications"
        ]
        
        for table in tables_to_clear:
            try:
                print(f"🧹 Clearing {table}...")
                # Delete all records from table
                result = supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                print(f"   ✅ Cleared {table}")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not clear {table}: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Database cleanup completed!")
        print("\n📋 Cleared tables:")
        for table in tables_to_clear:
            print(f"   - {table}")
        
        print("\n🎯 Next steps:")
        print("1. Start the optimized server")
        print("2. Create new courses with uploaded thumbnails")
        print("3. Test the notification system")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database cleanup: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LearnSphere Database Cleanup Tool")
    print("=" * 60)
    
    success = clear_database()
    if success:
        print("\n🎉 Database cleanup successful!")
    else:
        print("\n💥 Database cleanup failed!")
        sys.exit(1)
