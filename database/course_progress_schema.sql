-- Course Progress Tracking Schema
-- This schema tracks student progress through course materials, similar to Coursera/Udemy

-- Table to track individual material interactions
CREATE TABLE IF NOT EXISTS course_material_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    material_id UUID NOT NULL REFERENCES course_materials(id) ON DELETE CASCADE,
    
    -- Progress tracking
    status VARCHAR(20) NOT NULL DEFAULT 'not_started', -- not_started, in_progress, completed
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    
    -- Interaction tracking
    first_accessed_at TIMESTAMPTZ,
    last_accessed_at TIMESTAMPTZ,
    total_time_spent INTEGER DEFAULT 0, -- in seconds
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    
    -- Completion tracking
    completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id, material_id)
);

-- Table to track overall course progress
CREATE TABLE IF NOT EXISTS course_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    
    -- Overall progress
    overall_progress_percentage INTEGER DEFAULT 0 CHECK (overall_progress_percentage >= 0 AND overall_progress_percentage <= 100),
    materials_completed INTEGER DEFAULT 0,
    total_materials INTEGER DEFAULT 0,
    
    -- Time tracking
    total_time_spent INTEGER DEFAULT 0, -- in seconds
    last_activity_at TIMESTAMPTZ,
    
    -- Completion tracking
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id, course_id)
);

-- Table to track learning streaks and achievements
CREATE TABLE IF NOT EXISTS learning_streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    
    -- Streak tracking
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    
    -- Weekly/Monthly goals
    weekly_goal_minutes INTEGER DEFAULT 0,
    weekly_minutes_completed INTEGER DEFAULT 0,
    monthly_goal_minutes INTEGER DEFAULT 0,
    monthly_minutes_completed INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id)
);

-- Table to track course certificates and achievements
CREATE TABLE IF NOT EXISTS course_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    
    -- Certificate details
    certificate_url TEXT,
    completion_percentage INTEGER NOT NULL CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    final_grade DECIMAL(5,2),
    
    -- Timestamps
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(student_id, course_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_material_progress_student_id ON course_material_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_course_id ON course_material_progress(course_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_material_id ON course_material_progress(material_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_status ON course_material_progress(status);
CREATE INDEX IF NOT EXISTS idx_material_progress_last_accessed ON course_material_progress(last_accessed_at DESC);

CREATE INDEX IF NOT EXISTS idx_course_progress_student_id ON course_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_course_progress_course_id ON course_progress(course_id);
CREATE INDEX IF NOT EXISTS idx_course_progress_percentage ON course_progress(overall_progress_percentage);
CREATE INDEX IF NOT EXISTS idx_course_progress_last_activity ON course_progress(last_activity_at DESC);

CREATE INDEX IF NOT EXISTS idx_learning_streaks_student_id ON learning_streaks(student_id);
CREATE INDEX IF NOT EXISTS idx_learning_streaks_current_streak ON learning_streaks(current_streak DESC);

CREATE INDEX IF NOT EXISTS idx_certificates_student_id ON course_certificates(student_id);
CREATE INDEX IF NOT EXISTS idx_certificates_course_id ON course_certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_certificates_issued_at ON course_certificates(issued_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE course_material_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_certificates ENABLE ROW LEVEL SECURITY;

-- RLS Policies for course_material_progress
CREATE POLICY "Students can view their own material progress" ON course_material_progress
    FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can update their own material progress" ON course_material_progress
    FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can modify their own material progress" ON course_material_progress
    FOR UPDATE USING (auth.uid() = student_id);

-- Teachers can view progress for their courses
CREATE POLICY "Teachers can view material progress for their courses" ON course_material_progress
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE courses.id = course_material_progress.course_id 
            AND courses.teacher_id = auth.uid()
        )
    );

-- RLS Policies for course_progress
CREATE POLICY "Students can view their own course progress" ON course_progress
    FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can update their own course progress" ON course_progress
    FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can modify their own course progress" ON course_progress
    FOR UPDATE USING (auth.uid() = student_id);

-- Teachers can view progress for their courses
CREATE POLICY "Teachers can view course progress for their courses" ON course_progress
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE courses.id = course_progress.course_id 
            AND courses.teacher_id = auth.uid()
        )
    );

-- RLS Policies for learning_streaks
CREATE POLICY "Students can view their own learning streaks" ON learning_streaks
    FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can update their own learning streaks" ON learning_streaks
    FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can modify their own learning streaks" ON learning_streaks
    FOR UPDATE USING (auth.uid() = student_id);

-- RLS Policies for course_certificates
CREATE POLICY "Students can view their own certificates" ON course_certificates
    FOR SELECT USING (auth.uid() = student_id);

-- Teachers can view certificates for their courses
CREATE POLICY "Teachers can view certificates for their courses" ON course_certificates
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE courses.id = course_certificates.course_id 
            AND courses.teacher_id = auth.uid()
        )
    );

-- Grant necessary permissions
GRANT ALL ON course_material_progress TO authenticated;
GRANT ALL ON course_progress TO authenticated;
GRANT ALL ON learning_streaks TO authenticated;
GRANT ALL ON course_certificates TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Function to automatically update course progress when material progress changes
CREATE OR REPLACE FUNCTION update_course_progress()
RETURNS TRIGGER AS $$
BEGIN
    -- Update overall course progress
    INSERT INTO course_progress (student_id, course_id, overall_progress_percentage, materials_completed, total_materials, last_activity_at)
    SELECT 
        NEW.student_id,
        NEW.course_id,
        CASE 
            WHEN total_materials > 0 THEN (completed_materials * 100 / total_materials)
            ELSE 0
        END as overall_progress_percentage,
        completed_materials,
        total_materials,
        NOW()
    FROM (
        SELECT 
            COUNT(*) FILTER (WHERE status = 'completed') as completed_materials,
            COUNT(*) as total_materials
        FROM course_material_progress cmp
        JOIN course_materials cm ON cmp.material_id = cm.id
        WHERE cmp.student_id = NEW.student_id 
        AND cmp.course_id = NEW.course_id
        AND cm.is_active = true
    ) progress_stats
    ON CONFLICT (student_id, course_id) 
    DO UPDATE SET
        overall_progress_percentage = EXCLUDED.overall_progress_percentage,
        materials_completed = EXCLUDED.materials_completed,
        total_materials = EXCLUDED.total_materials,
        last_activity_at = EXCLUDED.last_activity_at,
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update course progress
CREATE TRIGGER trigger_update_course_progress
    AFTER INSERT OR UPDATE ON course_material_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_course_progress();
