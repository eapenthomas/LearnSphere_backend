"""Apply plagiarism schema migration directly via service role."""
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# We use raw postgres via rpc or just try inserting; since execute_sql isn't available,
# use postgrest to check and update via a dummy update (safe no-op approach).
# Actually, let's use the management API not available — use raw SQL via postgrest rpc.

# Try via a custom RPC function that doesn't exist, so we'll use the alter table directly
# through the postgrest schema endpoint which doesn't support DDL.
# Best approach: Use the backend startup migration pattern.

print("ℹ️  Schema migration must be applied via Supabase Dashboard SQL editor.")
print("Run this SQL in your Supabase project's SQL editor:")
print("""
ALTER TABLE assignment_submissions
  ADD COLUMN IF NOT EXISTS embedding JSONB,
  ADD COLUMN IF NOT EXISTS submission_text TEXT,
  ADD COLUMN IF NOT EXISTS plagiarism_risk TEXT DEFAULT 'pending',
  ADD COLUMN IF NOT EXISTS plagiarism_similarity FLOAT DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS plagiarism_status TEXT DEFAULT 'pending',
  ADD COLUMN IF NOT EXISTS plagiarism_matched_student_id UUID,
  ADD COLUMN IF NOT EXISTS teacher_remark TEXT;
""")
