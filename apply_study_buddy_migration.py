import os
import sys
from supabase import create_client

def apply_migration():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
        sys.exit(1)
        
    print(f"Connecting to Supabase at {supabase_url}...")
    supabase = create_client(supabase_url, supabase_key)
    
    migration_file = os.path.join(os.path.dirname(__file__), "database", "feature_study_buddy.sql")
    
    if not os.path.exists(migration_file):
        print(f"Error: Migration file not found at {migration_file}")
        sys.exit(1)
        
    print(f"Reading migration file: {migration_file}")
    with open(migration_file, 'r') as f:
        sql = f.read()
        
    print("Executing migration...")
    
    # Unfortunately supabase-py doesn't have a direct raw SQL execution method via the data API
    # for full schema changes. We have to use the REST API via RPC if a generic 'exec_sql' exists,
    # OR we can just instruct the user/system to run it via the dashboard/CLI.
    # We will try a common hack: querying a custom RPC if set up, but usually DDL requires
    # the psql tool or Supabase dashboard.
    
    print("Note: Applying DDL via python client might fail if RPC 'exec_sql' isn't configured.")
    print("If this fails, please run the contents of 'database/feature_study_buddy.sql' in the Supabase SQL Editor.")
    
    try:
        # Try to use an exec_sql RPC if the user set one up previously
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print("Migration applied successfully via RPC!")
    except Exception as e:
        print(f"\nFailed to apply via RPC: {e}")
        print("\n--- ACTION REQUIRED ---")
        print("Please copy the contents of 'backend/database/feature_study_buddy.sql'")
        print("and run them manually in your Supabase SQL Editor.")

if __name__ == "__main__":
    apply_migration()
