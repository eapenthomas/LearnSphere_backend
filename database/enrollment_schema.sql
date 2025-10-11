-- Course Enrollments Schema
-- Run this in your Supabase SQL Editor

-- Create enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    status TEXT CHECK (status IN ('active', 'completed', 'dropped')) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(student_id, course_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status);

-- Enable Row Level Security
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;

-- Create policies for enrollments
CREATE POLICY "Students can view own enrollments" ON enrollments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'student'
            AND profiles.id = enrollments.student_id
        )
    );

CREATE POLICY "Students can enroll in courses" ON enrollments
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'student'
            AND profiles.id = enrollments.student_id
        )
    );

CREATE POLICY "Students can update own enrollments" ON enrollments
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'student'
            AND profiles.id = enrollments.student_id
        )
    );

-- Teachers can view enrollments for their courses
CREATE POLICY "Teachers can view course enrollments" ON enrollments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN courses c ON c.teacher_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'teacher'
            AND c.id = enrollments.course_id
        )
    );

-- Disable RLS for now (since we're using custom auth)
ALTER TABLE enrollments DISABLE ROW LEVEL SECURITY;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_enrollments_updated_at
    BEFORE UPDATE ON enrollments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL ON enrollments TO authenticated;
GRANT ALL ON enrollments TO anon;
GRANT ALL ON enrollments TO service_role;

-- Enable realtime for enrollments
ALTER PUBLICATION supabase_realtime ADD TABLE enrollments;

-- Create a view for course enrollment counts
CREATE OR REPLACE VIEW course_enrollment_stats AS
SELECT 
    c.id as course_id,
    c.title,
    c.teacher_id,
    COUNT(e.id) as total_enrollments,
    COUNT(CASE WHEN e.status = 'active' THEN 1 END) as active_enrollments,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) as completed_enrollments
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY c.id, c.title, c.teacher_id;

-- Grant access to the view
GRANT SELECT ON course_enrollment_stats TO authenticated;
GRANT SELECT ON course_enrollment_stats TO anon;

-- Test the setup
SELECT 'Enrollment system setup complete!' as message;
