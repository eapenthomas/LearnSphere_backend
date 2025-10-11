-- LearnSphere Database Schema
-- Updated profiles table with password support for manual authentication
--
-- Recent Updates (2025-09-07):
-- - Added comprehensive course API endpoints for student course discovery
-- - Fixed enrollment data structure for frontend compatibility
-- - Enhanced course management with teacher information and enrollment counts
-- - See database/course_api_endpoints.sql for detailed API documentation

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

-- ========================================
-- RECENT UPDATES (December 2024)
-- ========================================

-- Add profile picture column to profiles table (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'profiles' AND column_name = 'profile_picture') THEN
        ALTER TABLE profiles ADD COLUMN profile_picture TEXT;
    END IF;
END $$;

-- Teacher Ratings Table
CREATE TABLE IF NOT EXISTS teacher_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, teacher_id, course_id)
);

-- Indexes for teacher_ratings
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_teacher_id ON teacher_ratings(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_course_id ON teacher_ratings(course_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_student_id ON teacher_ratings(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_created_at ON teacher_ratings(created_at);

-- Index for profile pictures
CREATE INDEX IF NOT EXISTS idx_profiles_picture ON profiles(profile_picture);

-- Enable RLS for teacher_ratings
ALTER TABLE teacher_ratings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for teacher_ratings
-- Students can only view and manage their own ratings
CREATE POLICY "Students can manage own ratings" ON teacher_ratings
    FOR ALL USING (auth.uid()::text = student_id::text);

-- Teachers can view ratings for their courses
CREATE POLICY "Teachers can view their ratings" ON teacher_ratings
    FOR SELECT USING (
        teacher_id::text = auth.uid()::text OR
        EXISTS (
            SELECT 1 FROM courses
            WHERE courses.id = teacher_ratings.course_id
            AND courses.teacher_id::text = auth.uid()::text
        )
    );

-- Admins can view all ratings
CREATE POLICY "Admins can view all ratings" ON teacher_ratings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles
            WHERE profiles.id::text = auth.uid()::text
            AND profiles.role = 'admin'
        )
    );

-- Service role can manage all ratings
CREATE POLICY "Service role can manage all ratings" ON teacher_ratings
    FOR ALL USING (auth.role() = 'service_role');

-- Grant permissions for teacher_ratings
GRANT ALL ON teacher_ratings TO authenticated;
GRANT ALL ON teacher_ratings TO service_role;

-- Update trigger for teacher_ratings
CREATE TRIGGER update_teacher_ratings_updated_at
    BEFORE UPDATE ON teacher_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();