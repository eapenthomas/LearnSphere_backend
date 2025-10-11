-- LearnSphere Courses Table Schema
-- Run this SQL in your Supabase SQL editor

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'General',
    thumbnail_url TEXT,
    status TEXT CHECK (status IN ('active', 'draft')) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses(created_at);

-- Enable Row Level Security
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

-- Create policies for secure access
-- Teachers can view their own courses
CREATE POLICY "Teachers can view own courses" ON courses
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
            AND profiles.id = courses.teacher_id
        )
    );

-- Teachers can insert their own courses
CREATE POLICY "Teachers can insert own courses" ON courses
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
            AND profiles.id = courses.teacher_id
        )
    );

-- Teachers can update their own courses
CREATE POLICY "Teachers can update own courses" ON courses
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
            AND profiles.id = courses.teacher_id
        )
    );

-- Teachers can delete their own courses
CREATE POLICY "Teachers can delete own courses" ON courses
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
            AND profiles.id = courses.teacher_id
        )
    );

-- Students can view active courses
CREATE POLICY "Students can view active courses" ON courses
    FOR SELECT USING (
        status = 'active' AND
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'student'
        )
    );

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create storage bucket for course thumbnails
INSERT INTO storage.buckets (id, name, public) 
VALUES ('course-thumbnails', 'course-thumbnails', true)
ON CONFLICT (id) DO NOTHING;

-- Create storage policies for course thumbnails
CREATE POLICY "Teachers can upload course thumbnails" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'course-thumbnails' AND
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
        )
    );

CREATE POLICY "Anyone can view course thumbnails" ON storage.objects
    FOR SELECT USING (bucket_id = 'course-thumbnails');

CREATE POLICY "Teachers can update course thumbnails" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'course-thumbnails' AND
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
        )
    );

CREATE POLICY "Teachers can delete course thumbnails" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'course-thumbnails' AND
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
        )
    );

-- Grant necessary permissions
GRANT ALL ON courses TO authenticated;
GRANT ALL ON courses TO service_role;

-- Insert some sample data for testing (optional)
-- Uncomment the lines below if you want sample data

/*
-- First, get a teacher's ID (replace with actual teacher ID from your profiles table)
-- You can find teacher IDs by running: SELECT id, full_name, role FROM profiles WHERE role = 'teacher';

INSERT INTO courses (teacher_id, title, description, status) VALUES 
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Introduction to React.js',
    'Learn the fundamentals of React.js including components, state management, and hooks. Perfect for beginners who want to start building modern web applications.',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Advanced JavaScript Concepts',
    'Deep dive into advanced JavaScript topics including closures, prototypes, async/await, and ES6+ features.',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Node.js Backend Development',
    'Build scalable backend applications with Node.js, Express, and MongoDB. Learn REST APIs, authentication, and deployment.',
    'draft'
);
*/

COMMIT;
