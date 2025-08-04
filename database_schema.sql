-- LearnSphere Database Schema
-- Updated profiles table with password support for manual authentication

-- Drop existing table if it exists
DROP TABLE IF EXISTS profiles CASCADE;

-- Create profiles table with password support
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    password_salt TEXT,
    password_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on email for faster lookups
CREATE INDEX idx_profiles_email ON profiles(email);

-- Create index on role for role-based queries
CREATE INDEX idx_profiles_role ON profiles(role);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies for secure access
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Service role can manage all profiles" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data (optional)
-- INSERT INTO profiles (email, full_name, role) VALUES 
-- ('admin@learnsphere.com', 'Admin User', 'admin'),
-- ('teacher@learnsphere.com', 'Teacher User', 'teacher'),
-- ('student@learnsphere.com', 'Student User', 'student');

-- Grant necessary permissions
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON profiles TO service_role;

-- Create a view for public profile information (without sensitive data)
CREATE VIEW public_profiles AS
SELECT 
    id,
    full_name,
    role,
    created_at
FROM profiles;

-- Grant access to the view
GRANT SELECT ON public_profiles TO authenticated; 