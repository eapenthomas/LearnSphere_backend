-- =====================================================
-- LearnSphere Database Updates - December 2024
-- Latest fixes and enhancements for voice navigation,
-- deadline management, and system improvements
-- =====================================================

-- Voice Navigation System Enhancements
-- =====================================

-- Create voice_navigation_logs table for debugging
CREATE TABLE IF NOT EXISTS voice_navigation_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    recognized_text TEXT,
    action_taken TEXT,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    session_id TEXT
);

-- Add RLS policies for voice navigation logs
ALTER TABLE voice_navigation_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own voice logs" ON voice_navigation_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own voice logs" ON voice_navigation_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Deadline Management Enhancements
-- =================================

-- Add debugging columns to assignments table
ALTER TABLE assignments 
ADD COLUMN IF NOT EXISTS debug_info JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS visibility_status TEXT DEFAULT 'visible',
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Add debugging columns to quizzes table
ALTER TABLE quizzes 
ADD COLUMN IF NOT EXISTS debug_info JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS visibility_status TEXT DEFAULT 'visible',
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create deadline_visibility_logs for debugging deadline display issues
CREATE TABLE IF NOT EXISTS deadline_visibility_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    deadline_type TEXT NOT NULL, -- 'assignment' or 'quiz'
    deadline_id UUID NOT NULL,
    api_endpoint TEXT,
    response_status INTEGER,
    response_data JSONB,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS policies for deadline visibility logs
ALTER TABLE deadline_visibility_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Students can view their own deadline logs" ON deadline_visibility_logs
    FOR SELECT USING (auth.uid() = student_id);

CREATE POLICY "Students can insert their own deadline logs" ON deadline_visibility_logs
    FOR INSERT WITH CHECK (auth.uid() = student_id);

-- Profile Picture System Enhancements
-- ====================================

-- Add profile picture metadata table
CREATE TABLE IF NOT EXISTS profile_picture_metadata (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    original_filename TEXT,
    file_size INTEGER,
    mime_type TEXT,
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    storage_path TEXT,
    thumbnail_path TEXT,
    is_active BOOLEAN DEFAULT true
);

-- Add RLS policies for profile picture metadata
ALTER TABLE profile_picture_metadata ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile picture metadata" ON profile_picture_metadata
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own profile picture metadata" ON profile_picture_metadata
    FOR ALL USING (auth.uid() = user_id);

-- System Performance Monitoring
-- ==============================

-- Create system_performance_logs table
CREATE TABLE IF NOT EXISTS system_performance_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    response_time_ms INTEGER,
    status_code INTEGER,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET
);

-- Add RLS policies for system performance logs (admin only)
ALTER TABLE system_performance_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view all performance logs" ON system_performance_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_profiles 
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- Enhanced Deadline Queries
-- ==========================

-- Function to get urgent deadlines with enhanced debugging
CREATE OR REPLACE FUNCTION get_urgent_deadlines_debug(
    p_student_id UUID,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    course_name TEXT,
    due_date TIMESTAMP WITH TIME ZONE,
    category TEXT,
    priority TEXT,
    debug_info JSONB
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.title,
        c.title as course_name,
        a.due_date,
        'assignment'::TEXT as category,
        CASE 
            WHEN a.due_date <= NOW() + INTERVAL '1 day' THEN 'urgent'
            WHEN a.due_date <= NOW() + INTERVAL '2 days' THEN 'high'
            ELSE 'normal'
        END as priority,
        jsonb_build_object(
            'type', 'assignment',
            'course_id', a.course_id,
            'submission_status', COALESCE(s.submission_status, 'not_submitted'),
            'days_until_due', EXTRACT(days FROM (a.due_date - NOW())),
            'visibility_status', a.visibility_status
        ) as debug_info
    FROM assignments a
    JOIN courses c ON a.course_id = c.id
    JOIN enrollments e ON c.id = e.course_id
    LEFT JOIN assignment_submissions s ON a.id = s.assignment_id AND s.student_id = p_student_id
    WHERE e.student_id = p_student_id
        AND a.due_date > NOW()
        AND (s.submission_status IS NULL OR s.submission_status = 'not_submitted')
        AND a.visibility_status = 'visible'
    
    UNION ALL
    
    SELECT 
        q.id,
        q.title,
        c.title as course_name,
        q.due_date,
        'quiz'::TEXT as category,
        CASE 
            WHEN q.due_date <= NOW() + INTERVAL '1 day' THEN 'urgent'
            WHEN q.due_date <= NOW() + INTERVAL '2 days' THEN 'high'
            ELSE 'normal'
        END as priority,
        jsonb_build_object(
            'type', 'quiz',
            'course_id', q.course_id,
            'submission_status', CASE WHEN qs.id IS NOT NULL THEN 'submitted' ELSE 'not_submitted' END,
            'days_until_due', EXTRACT(days FROM (q.due_date - NOW())),
            'visibility_status', q.visibility_status
        ) as debug_info
    FROM quizzes q
    JOIN courses c ON q.course_id = c.id
    JOIN enrollments e ON c.id = e.course_id
    LEFT JOIN quiz_submissions qs ON q.id = qs.quiz_id AND qs.student_id = p_student_id
    WHERE e.student_id = p_student_id
        AND q.due_date > NOW()
        AND qs.id IS NULL
        AND q.visibility_status = 'visible'
    
    ORDER BY due_date ASC
    LIMIT p_limit;
END;
$$;

-- Sample Data for Testing Deadlines
-- ==================================

-- Insert sample assignments for testing (only if no real data exists)
INSERT INTO assignments (id, course_id, title, description, due_date, max_points, visibility_status, debug_info)
SELECT 
    gen_random_uuid(),
    c.id,
    'Sample Assignment - ' || c.title,
    'This is a sample assignment for testing deadline visibility',
    NOW() + INTERVAL '1 day',
    100,
    'visible',
    '{"sample": true, "created_for": "testing"}'
FROM courses c
WHERE NOT EXISTS (
    SELECT 1 FROM assignments WHERE title LIKE 'Sample Assignment%'
)
LIMIT 3;

-- Insert sample quizzes for testing (only if no real data exists)
INSERT INTO quizzes (id, course_id, title, description, due_date, time_limit, visibility_status, debug_info)
SELECT 
    gen_random_uuid(),
    c.id,
    'Sample Quiz - ' || c.title,
    'This is a sample quiz for testing deadline visibility',
    NOW() + INTERVAL '2 days',
    30,
    'visible',
    '{"sample": true, "created_for": "testing"}'
FROM courses c
WHERE NOT EXISTS (
    SELECT 1 FROM quizzes WHERE title LIKE 'Sample Quiz%'
)
LIMIT 2;

-- Performance Indexes
-- ===================

-- Indexes for better deadline query performance
CREATE INDEX IF NOT EXISTS idx_assignments_due_date_visibility 
    ON assignments(due_date, visibility_status) WHERE visibility_status = 'visible';

CREATE INDEX IF NOT EXISTS idx_quizzes_due_date_visibility 
    ON quizzes(due_date, visibility_status) WHERE visibility_status = 'visible';

CREATE INDEX IF NOT EXISTS idx_voice_navigation_logs_user_timestamp 
    ON voice_navigation_logs(user_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_deadline_visibility_logs_student_timestamp 
    ON deadline_visibility_logs(student_id, timestamp);

-- Update Triggers
-- ===============

-- Trigger to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to relevant tables
DROP TRIGGER IF EXISTS update_assignments_last_updated ON assignments;
CREATE TRIGGER update_assignments_last_updated 
    BEFORE UPDATE ON assignments 
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_column();

DROP TRIGGER IF EXISTS update_quizzes_last_updated ON quizzes;
CREATE TRIGGER update_quizzes_last_updated 
    BEFORE UPDATE ON quizzes 
    FOR EACH ROW EXECUTE FUNCTION update_last_updated_column();

-- =====================================================
-- End of December 2024 Updates
-- =====================================================

-- Payment System Schema Updates
-- =============================

-- Courses table with payment support
CREATE TABLE IF NOT EXISTS courses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    teacher_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) DEFAULT 0.00,
    is_paid BOOLEAN DEFAULT FALSE,
    razorpay_product_id TEXT,
    razorpay_price_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    razorpay_order_id TEXT UNIQUE,
    razorpay_payment_id TEXT,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enrollments table (updated to support payments)
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    student_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    payment_id UUID REFERENCES payments(id) ON DELETE SET NULL,
    UNIQUE(student_id, course_id)
);

-- Refresh tokens table for persistent login
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_revoked BOOLEAN DEFAULT FALSE
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_is_paid ON courses(is_paid);
CREATE INDEX IF NOT EXISTS idx_payments_student_id ON payments(student_id);
CREATE INDEX IF NOT EXISTS idx_payments_course_id ON payments(course_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Add RLS policies
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;

-- Courses policies
CREATE POLICY "Teachers can manage their own courses" ON courses
    FOR ALL USING (teacher_id = auth.uid());

CREATE POLICY "Students can view all courses" ON courses
    FOR SELECT USING (true);

-- Payments policies
CREATE POLICY "Students can manage their own payments" ON payments
    FOR ALL USING (student_id = auth.uid());

CREATE POLICY "Teachers can view payments for their courses" ON payments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE courses.id = payments.course_id 
            AND courses.teacher_id = auth.uid()
        )
    );

-- Enrollments policies
CREATE POLICY "Students can manage their own enrollments" ON enrollments
    FOR ALL USING (student_id = auth.uid());

CREATE POLICY "Teachers can view enrollments for their courses" ON enrollments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE courses.id = enrollments.course_id 
            AND courses.teacher_id = auth.uid()
        )
    );

-- Refresh tokens policies
CREATE POLICY "Users can manage their own refresh tokens" ON refresh_tokens
    FOR ALL USING (user_id = auth.uid());

-- Update triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_courses_updated_at ON courses;
CREATE TRIGGER update_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Teacher Verification Flow - Complete Schema
-- =====================================================

-- Add teacher verification columns to profiles table
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS institution_name VARCHAR(255);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS verification_document_url TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS ocr_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS ai_confidence INT DEFAULT 0;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;

-- Ensure role and approval_status exist with proper constraints
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'student';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'approved';

-- Add constraint for role values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'profiles_role_check'
        AND table_name = 'profiles'
    ) THEN
        ALTER TABLE profiles ADD CONSTRAINT profiles_role_check
        CHECK (role IN ('student', 'teacher', 'admin'));
    END IF;
END $$;

-- Add constraint for approval_status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'profiles_approval_status_check'
        AND table_name = 'profiles'
    ) THEN
        ALTER TABLE profiles ADD CONSTRAINT profiles_approval_status_check
        CHECK (approval_status IN ('pending', 'approved', 'rejected'));
    END IF;
END $$;

-- Add constraint for ocr_status values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'profiles_ocr_status_check'
        AND table_name = 'profiles'
    ) THEN
        ALTER TABLE profiles ADD CONSTRAINT profiles_ocr_status_check
        CHECK (ocr_status IN ('pending', 'passed', 'failed'));
    END IF;
END $$;

-- Enhanced teacher_approval_requests table
CREATE TABLE IF NOT EXISTS teacher_approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    institution VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    confidence INT DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 100),
    reason TEXT,
    admin_id UUID REFERENCES profiles(id),
    admin_notes TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for teacher verification
CREATE INDEX IF NOT EXISTS idx_profiles_ocr_status ON profiles(ocr_status);
CREATE INDEX IF NOT EXISTS idx_profiles_verification_status ON profiles(is_verified);
CREATE INDEX IF NOT EXISTS idx_profiles_institution ON profiles(institution_name);
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_status ON teacher_approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_user_id ON teacher_approval_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_created_at ON teacher_approval_requests(created_at);

-- Grant permissions for teacher verification tables
GRANT ALL ON teacher_approval_requests TO authenticated;
GRANT ALL ON teacher_approval_requests TO anon;
GRANT ALL ON teacher_approval_requests TO service_role;

-- Enable realtime for teacher approval requests
ALTER PUBLICATION supabase_realtime ADD TABLE teacher_approval_requests;

-- Verification Queries
-- ====================

-- Check if voice navigation system is ready
SELECT 'Voice Navigation System' as component, 
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'voice_navigation_logs') 
            THEN '✅ Ready' ELSE '❌ Not Ready' END as status;

-- Check if deadline debugging is ready
SELECT 'Deadline Debugging System' as component,
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'deadline_visibility_logs') 
            THEN '✅ Ready' ELSE '❌ Not Ready' END as status;

-- Check if sample data exists
SELECT 'Sample Deadline Data' as component,
       CASE WHEN EXISTS (SELECT 1 FROM assignments WHERE debug_info->>'sample' = 'true') 
            THEN '✅ Available' ELSE '❌ Not Available' END as status;
