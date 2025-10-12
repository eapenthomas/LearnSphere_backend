-- LearnSphere Course Materials Table Schema
-- Run this SQL in your Supabase SQL editor

-- Create course_materials table
CREATE TABLE IF NOT EXISTS course_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size BIGINT, -- File size in bytes
    file_type TEXT, -- MIME type (e.g., 'application/pdf', 'image/jpeg')
    uploaded_by UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT, -- Optional description of the material
    is_active BOOLEAN DEFAULT true -- Soft delete flag
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_course_materials_course_id ON course_materials(course_id);
CREATE INDEX IF NOT EXISTS idx_course_materials_uploaded_by ON course_materials(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_course_materials_uploaded_at ON course_materials(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_course_materials_is_active ON course_materials(is_active);

-- Enable Row Level Security
ALTER TABLE course_materials ENABLE ROW LEVEL SECURITY;

-- Create policies for secure access
-- Teachers can view materials for their own courses
CREATE POLICY "Teachers can view own course materials" ON course_materials
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN courses c ON c.teacher_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'teacher'
            AND c.id = course_materials.course_id
            AND course_materials.is_active = true
        )
    );

-- Teachers can insert materials for their own courses
CREATE POLICY "Teachers can insert own course materials" ON course_materials
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN courses c ON c.teacher_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'teacher'
            AND c.id = course_materials.course_id
            AND p.id = course_materials.uploaded_by
        )
    );

-- Teachers can update materials for their own courses
CREATE POLICY "Teachers can update own course materials" ON course_materials
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN courses c ON c.teacher_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'teacher'
            AND c.id = course_materials.course_id
        )
    );

-- Teachers can delete materials for their own courses
CREATE POLICY "Teachers can delete own course materials" ON course_materials
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN courses c ON c.teacher_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'teacher'
            AND c.id = course_materials.course_id
        )
    );

-- Students can view materials for courses they are enrolled in
CREATE POLICY "Students can view enrolled course materials" ON course_materials
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles p
            JOIN enrollments e ON e.student_id = p.id
            WHERE p.id = auth.uid() 
            AND p.role = 'student'
            AND e.course_id = course_materials.course_id
            AND e.status = 'active'
            AND course_materials.is_active = true
        )
    );

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_course_materials_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_course_materials_updated_at 
    BEFORE UPDATE ON course_materials 
    FOR EACH ROW 
    EXECUTE FUNCTION update_course_materials_updated_at();

-- Disable RLS for now (since we're using custom auth in FastAPI)
ALTER TABLE course_materials DISABLE ROW LEVEL SECURITY;

-- Grant necessary permissions
GRANT ALL ON course_materials TO authenticated;
GRANT ALL ON course_materials TO anon;
GRANT ALL ON course_materials TO service_role;

-- Enable realtime for course_materials
ALTER PUBLICATION supabase_realtime ADD TABLE course_materials;

-- Create a view for course materials with additional metadata
CREATE OR REPLACE VIEW course_materials_with_metadata AS
SELECT 
    cm.id,
    cm.course_id,
    cm.file_name,
    cm.file_url,
    cm.file_size,
    cm.file_type,
    cm.uploaded_by,
    cm.uploaded_at,
    cm.updated_at,
    cm.description,
    cm.is_active,
    c.title as course_title,
    p.full_name as uploader_name
FROM course_materials cm
JOIN courses c ON c.id = cm.course_id
JOIN profiles p ON p.id = cm.uploaded_by
WHERE cm.is_active = true;

-- Grant access to the view
GRANT SELECT ON course_materials_with_metadata TO authenticated;
GRANT SELECT ON course_materials_with_metadata TO anon;
GRANT SELECT ON course_materials_with_metadata TO service_role;

-- Test the setup
SELECT 'Course materials system setup complete!' as message;

COMMIT;
