-- Update profiles table to support email/password authentication
-- Run this SQL in your Supabase SQL editor

-- First, remove foreign key constraint if it exists (to allow custom user IDs)
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_pkey;

-- Add missing columns to existing profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS email TEXT,
ADD COLUMN IF NOT EXISTS password_salt TEXT,
ADD COLUMN IF NOT EXISTS password_hash TEXT,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Re-add primary key constraint
ALTER TABLE profiles ADD CONSTRAINT profiles_pkey PRIMARY KEY (id);

-- Create unique constraint on email (after adding the column)
-- First, let's make sure there are no duplicate emails
-- You may need to clean up any duplicates manually before running this
ALTER TABLE profiles 
ADD CONSTRAINT profiles_email_unique UNIQUE (email);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Update Row Level Security policies
-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Service role can manage all profiles" ON profiles;

-- Create new policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Service role can manage all profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Grant necessary permissions
GRANT ALL ON profiles TO service_role;
GRANT SELECT, UPDATE ON profiles TO authenticated;

-- Optional: Update existing user to have an email (replace with actual email)
-- UPDATE profiles SET email = 'user@example.com' WHERE id = '8f267d13-8852-4b25-868f-7855445fb6bd';

COMMIT;
