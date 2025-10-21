-- Add last_login field to profiles table for login tracking
-- This migration adds the last_login timestamp field to track user login times

-- Add last_login column to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Add index for performance on last_login queries
CREATE INDEX IF NOT EXISTS idx_profiles_last_login ON profiles(last_login);

-- Add comment to document the field
COMMENT ON COLUMN profiles.last_login IS 'Timestamp of the user''s last successful login';
