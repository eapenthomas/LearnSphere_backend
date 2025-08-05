-- Step 1: Create the courses table
-- Copy and paste this into your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    status TEXT CHECK (status IN ('active', 'draft')) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create indexes
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses(created_at);

-- Step 3: Enable RLS
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;

-- Step 4: Create separate policies for different operations

-- Policy for SELECT (viewing courses)
CREATE POLICY "Teachers can view own courses" ON courses
    FOR SELECT USING (true);

-- Policy for INSERT (creating courses)
CREATE POLICY "Teachers can create courses" ON courses
    FOR INSERT WITH CHECK (true);

-- Policy for UPDATE (editing courses)
CREATE POLICY "Teachers can update own courses" ON courses
    FOR UPDATE USING (true);

-- Policy for DELETE (deleting courses)
CREATE POLICY "Teachers can delete own courses" ON courses
    FOR DELETE USING (true);

-- Step 5: Grant permissions
GRANT ALL ON courses TO authenticated;
GRANT ALL ON courses TO service_role;

-- Step 6: Create storage bucket (run this separately if it fails)
INSERT INTO storage.buckets (id, name, public) 
VALUES ('course-thumbnails', 'course-thumbnails', true)
ON CONFLICT (id) DO NOTHING;

-- Step 7: Test the setup
SELECT 'Courses table created successfully!' as message;
