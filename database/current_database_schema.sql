-- LearnSphere Database Schema - Current State
-- Generated on: 2025-01-11
-- This file contains the complete current database structure

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Profiles table (users)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student',
    email TEXT UNIQUE,
    password TEXT,
    password_salt TEXT,
    password_hash TEXT,
    approval_status TEXT DEFAULT 'approved',
    is_active BOOLEAN DEFAULT true,
    approved_by UUID,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    profile_picture TEXT,
    institution_name TEXT,
    id_card_url TEXT,
    ocr_status TEXT DEFAULT 'pending',
    ai_confidence INTEGER DEFAULT 0,
    verification_reason TEXT,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    code VARCHAR(50),
    thumbnail_url TEXT,
    status TEXT DEFAULT 'active',
    category TEXT DEFAULT 'General',
    price NUMERIC DEFAULT 0.00,
    is_paid BOOLEAN DEFAULT false,
    razorpay_product_id TEXT,
    razorpay_price_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enrollments table
CREATE TABLE IF NOT EXISTS enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    progress INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    payment_id UUID,
    enrollment_type VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(student_id, course_id)
);

-- ============================================================================
-- ASSIGNMENTS & QUIZZES
-- ============================================================================

-- Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    teacher_id UUID NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    file_url TEXT,
    due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    max_score INTEGER DEFAULT 100,
    allow_late_submission BOOLEAN DEFAULT false,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Assignment submissions table
CREATE TABLE IF NOT EXISTS assignment_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL,
    student_id UUID NOT NULL,
    file_url TEXT NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    score INTEGER,
    feedback TEXT,
    status TEXT DEFAULT 'submitted',
    graded_by UUID,
    graded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(assignment_id, student_id)
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    course_id UUID,
    teacher_id UUID,
    instructions TEXT,
    total_marks INTEGER DEFAULT 0,
    duration_minutes INTEGER,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Quiz questions table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    options JSONB,
    correct_answer TEXT,
    marks INTEGER DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Quiz submissions table
CREATE TABLE IF NOT EXISTS quiz_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID,
    student_id UUID,
    answers JSONB,
    score INTEGER DEFAULT 0,
    total_marks INTEGER DEFAULT 0,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    time_taken_minutes INTEGER,
    UNIQUE(quiz_id, student_id)
);

-- ============================================================================
-- COURSE MATERIALS & PROGRESS
-- ============================================================================

-- Course materials table
CREATE TABLE IF NOT EXISTS course_materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_type TEXT,
    uploaded_by UUID NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Course material progress table
CREATE TABLE IF NOT EXISTS course_material_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    material_id UUID NOT NULL,
    status VARCHAR(20) DEFAULT 'not_started',
    progress_percentage INTEGER DEFAULT 0,
    first_accessed_at TIMESTAMP WITH TIME ZONE,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    total_time_spent INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(student_id, material_id)
);

-- Course progress table
CREATE TABLE IF NOT EXISTS course_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    overall_progress_percentage INTEGER DEFAULT 0,
    materials_completed INTEGER DEFAULT 0,
    total_materials INTEGER DEFAULT 0,
    total_time_spent INTEGER DEFAULT 0,
    last_activity_at TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(student_id, course_id)
);

-- ============================================================================
-- TEACHER VERIFICATION & APPROVAL
-- ============================================================================

-- Teacher verification requests table
CREATE TABLE IF NOT EXISTS teacher_verification_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    institution_name TEXT NOT NULL,
    id_card_url TEXT NOT NULL,
    ocr_text TEXT,
    ai_confidence INTEGER DEFAULT 0,
    ai_reason TEXT,
    ocr_status TEXT DEFAULT 'pending',
    admin_notes TEXT,
    processed_by UUID,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Teacher approval requests table
CREATE TABLE IF NOT EXISTS teacher_approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL,
    request_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT DEFAULT 'pending',
    admin_id UUID,
    admin_notes TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================================================
-- AUTHENTICATION & SESSIONS
-- ============================================================================

-- Refresh tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Password reset OTPs table
CREATE TABLE IF NOT EXISTS password_reset_otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    used_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- PAYMENTS & CERTIFICATES
-- ============================================================================

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID,
    course_id UUID,
    razorpay_order_id TEXT NOT NULL,
    razorpay_payment_id TEXT,
    amount NUMERIC NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    currency VARCHAR(3) DEFAULT 'INR',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Course certificates table
CREATE TABLE IF NOT EXISTS course_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    certificate_url TEXT,
    completion_percentage INTEGER NOT NULL,
    final_grade NUMERIC,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(student_id, course_id)
);

-- Course completions table
CREATE TABLE IF NOT EXISTS course_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    completion_percentage INTEGER DEFAULT 100,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(student_id, course_id)
);

-- ============================================================================
-- AI FEATURES
-- ============================================================================

-- AI tutor documents table
CREATE TABLE IF NOT EXISTS ai_tutor_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    text_content TEXT NOT NULL,
    chunks TEXT[] NOT NULL,
    chunk_count INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- AI tutor interactions table
CREATE TABLE IF NOT EXISTS ai_tutor_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    document_id UUID NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd NUMERIC NOT NULL,
    context_chunks_used INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- AI usage logs table
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    cost_usd NUMERIC NOT NULL,
    request_type VARCHAR(100) NOT NULL,
    user_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================================================
-- FORUM & RATINGS
-- ============================================================================

-- Forum questions table
CREATE TABLE IF NOT EXISTS forum_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    course_id UUID,
    student_id UUID NOT NULL,
    tags TEXT[] DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Forum answers table
CREATE TABLE IF NOT EXISTS forum_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL,
    content TEXT NOT NULL,
    teacher_id UUID NOT NULL,
    is_accepted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Teacher ratings table
CREATE TABLE IF NOT EXISTS teacher_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL,
    student_id UUID NOT NULL,
    course_id UUID NOT NULL,
    rating INTEGER NOT NULL,
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(teacher_id, student_id, course_id)
);

-- ============================================================================
-- LEARNING ANALYTICS
-- ============================================================================

-- Learning streaks table
CREATE TABLE IF NOT EXISTS learning_streaks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL UNIQUE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    weekly_goal_minutes INTEGER DEFAULT 0,
    weekly_minutes_completed INTEGER DEFAULT 0,
    monthly_goal_minutes INTEGER DEFAULT 0,
    monthly_minutes_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================================================
-- NOTIFICATIONS & LOGGING
-- ============================================================================

-- Email notifications table
CREATE TABLE IF NOT EXISTS email_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_email TEXT NOT NULL,
    recipient_id UUID,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- User activity logs table
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    action TEXT NOT NULL,
    details JSONB,
    admin_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_role_is_active ON profiles(role, is_active);
CREATE INDEX IF NOT EXISTS idx_profiles_approval_status ON profiles(approval_status);
CREATE INDEX IF NOT EXISTS idx_profiles_verification_status ON profiles(role, is_verified, approval_status);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_profiles_is_active ON profiles(is_active);

-- Courses indexes
CREATE INDEX IF NOT EXISTS idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX IF NOT EXISTS idx_courses_status ON courses(status);
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);
CREATE INDEX IF NOT EXISTS idx_courses_created_at ON courses(created_at);

-- Enrollments indexes
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_status ON enrollments(status);
CREATE INDEX IF NOT EXISTS idx_enrollments_status_course_id ON enrollments(status, course_id);

-- Assignments indexes
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_assignments_teacher_id ON assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_assignments_due_date ON assignments(due_date);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);

-- Assignment submissions indexes
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_assignment_id ON assignment_submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_student_id ON assignment_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_status ON assignment_submissions(status);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_submitted_at ON assignment_submissions(submitted_at);

-- Quizzes indexes
CREATE INDEX IF NOT EXISTS idx_quizzes_course_id ON quizzes(course_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_teacher_id ON quizzes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_status ON quizzes(status);

-- Quiz questions indexes
CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);

-- Quiz submissions indexes
CREATE INDEX IF NOT EXISTS idx_quiz_submissions_quiz_id ON quiz_submissions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_quiz_submissions_student_id ON quiz_submissions(student_id);

-- Course materials indexes
CREATE INDEX IF NOT EXISTS idx_course_materials_course_id ON course_materials(course_id);
CREATE INDEX IF NOT EXISTS idx_course_materials_created_at ON course_materials(created_at);
CREATE INDEX IF NOT EXISTS idx_course_materials_is_active ON course_materials(is_active);

-- Course material progress indexes
CREATE INDEX IF NOT EXISTS idx_material_progress_student_id ON course_material_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_course_id ON course_material_progress(course_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_material_id ON course_material_progress(material_id);
CREATE INDEX IF NOT EXISTS idx_material_progress_status ON course_material_progress(status);
CREATE INDEX IF NOT EXISTS idx_material_progress_last_accessed ON course_material_progress(last_accessed_at DESC);

-- Course progress indexes
CREATE INDEX IF NOT EXISTS idx_course_progress_student_id ON course_progress(student_id);
CREATE INDEX IF NOT EXISTS idx_course_progress_course_id ON course_progress(course_id);
CREATE INDEX IF NOT EXISTS idx_course_progress_percentage ON course_progress(overall_progress_percentage);
CREATE INDEX IF NOT EXISTS idx_course_progress_last_activity ON course_progress(last_activity_at DESC);

-- Teacher verification indexes
CREATE INDEX IF NOT EXISTS idx_teacher_verification_user_id ON teacher_verification_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_teacher_verification_status ON teacher_verification_requests(ocr_status);

-- Teacher approval indexes
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_teacher_id ON teacher_approval_requests(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_status ON teacher_approval_requests(status);

-- Refresh tokens indexes
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Password reset OTPs indexes
CREATE INDEX IF NOT EXISTS idx_password_reset_otps_email ON password_reset_otps(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_otps_code ON password_reset_otps(otp_code);
CREATE INDEX IF NOT EXISTS idx_password_reset_otps_expires ON password_reset_otps(expires_at);

-- Payments indexes
CREATE INDEX IF NOT EXISTS idx_payments_student_id ON payments(student_id);
CREATE INDEX IF NOT EXISTS idx_payments_course_id ON payments(course_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Certificates indexes
CREATE INDEX IF NOT EXISTS idx_certificates_student_id ON course_certificates(student_id);
CREATE INDEX IF NOT EXISTS idx_certificates_course_id ON course_certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_certificates_issued_at ON course_certificates(issued_at DESC);

-- Course completions indexes
CREATE INDEX IF NOT EXISTS idx_course_completions_student_id ON course_completions(student_id);
CREATE INDEX IF NOT EXISTS idx_course_completions_course_id ON course_completions(course_id);
CREATE INDEX IF NOT EXISTS idx_course_completions_completed_at ON course_completions(completed_at);

-- AI tutor documents indexes
CREATE INDEX IF NOT EXISTS idx_ai_tutor_documents_user_id ON ai_tutor_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_tutor_documents_created_at ON ai_tutor_documents(created_at);

-- AI tutor interactions indexes
CREATE INDEX IF NOT EXISTS idx_ai_tutor_interactions_user_id ON ai_tutor_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_tutor_interactions_document_id ON ai_tutor_interactions(document_id);
CREATE INDEX IF NOT EXISTS idx_ai_tutor_interactions_created_at ON ai_tutor_interactions(created_at);

-- AI usage logs indexes
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_user_id ON ai_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_provider ON ai_usage_logs(provider);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_request_type ON ai_usage_logs(request_type);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_created_at ON ai_usage_logs(created_at);

-- Forum questions indexes
CREATE INDEX IF NOT EXISTS idx_forum_questions_student_id ON forum_questions(student_id);
CREATE INDEX IF NOT EXISTS idx_forum_questions_course_id ON forum_questions(course_id);
CREATE INDEX IF NOT EXISTS idx_forum_questions_created_at ON forum_questions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_questions_is_resolved ON forum_questions(is_resolved);

-- Forum answers indexes
CREATE INDEX IF NOT EXISTS idx_forum_answers_question_id ON forum_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_forum_answers_teacher_id ON forum_answers(teacher_id);
CREATE INDEX IF NOT EXISTS idx_forum_answers_created_at ON forum_answers(created_at);
CREATE INDEX IF NOT EXISTS idx_forum_answers_is_accepted ON forum_answers(is_accepted);

-- Teacher ratings indexes
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_teacher_id ON teacher_ratings(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_student_id ON teacher_ratings(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_course_id ON teacher_ratings(course_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_rating ON teacher_ratings(rating);

-- Learning streaks indexes
CREATE INDEX IF NOT EXISTS idx_learning_streaks_student_id ON learning_streaks(student_id);
CREATE INDEX IF NOT EXISTS idx_learning_streaks_current_streak ON learning_streaks(current_streak DESC);

-- Email notifications indexes
CREATE INDEX IF NOT EXISTS idx_email_notifications_status ON email_notifications(status);

-- User activity logs indexes
CREATE INDEX IF NOT EXISTS idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_logs_created_at ON user_activity_logs(created_at);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Assignments with details view
CREATE OR REPLACE VIEW assignments_with_details AS
SELECT 
    a.*,
    c.title as course_title,
    p.full_name as teacher_name,
    COUNT(asub.id) as submission_count,
    COUNT(DISTINCT e.student_id) as total_students
FROM assignments a
LEFT JOIN courses c ON a.course_id = c.id
LEFT JOIN profiles p ON a.teacher_id = p.id
LEFT JOIN assignment_submissions asub ON a.id = asub.assignment_id
LEFT JOIN enrollments e ON a.course_id = e.course_id AND e.status = 'active'
GROUP BY a.id, c.title, p.full_name;

-- Assignment submissions with details view
CREATE OR REPLACE VIEW assignment_submissions_with_details AS
SELECT 
    asub.*,
    a.title as assignment_title,
    a.due_date,
    a.max_score,
    c.title as course_title,
    ps.full_name as student_name,
    ps.email as student_email,
    CASE 
        WHEN asub.submitted_at > a.due_date THEN true 
        ELSE false 
    END as is_late_submission
FROM assignment_submissions asub
LEFT JOIN assignments a ON asub.assignment_id = a.id
LEFT JOIN courses c ON a.course_id = c.id
LEFT JOIN profiles ps ON asub.student_id = ps.id;

-- Course materials with metadata view
CREATE OR REPLACE VIEW course_materials_with_metadata AS
SELECT 
    cm.*,
    c.title as course_title,
    p.full_name as uploader_name
FROM course_materials cm
LEFT JOIN courses c ON cm.course_id = c.id
LEFT JOIN profiles p ON cm.uploaded_by = p.id;

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at 
    BEFORE UPDATE ON courses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enrollments_updated_at
    BEFORE UPDATE ON enrollments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assignments_updated_at
    BEFORE UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assignment_submissions_updated_at
    BEFORE UPDATE ON assignment_submissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_quizzes_updated_at 
    BEFORE UPDATE ON quizzes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_materials_updated_at 
    BEFORE UPDATE ON course_materials 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_material_progress_updated_at
    BEFORE UPDATE ON course_material_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_course_progress_updated_at
    BEFORE UPDATE ON course_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_refresh_tokens_updated_at
    BEFORE UPDATE ON refresh_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at 
    BEFORE UPDATE ON payments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forum_questions_updated_at 
    BEFORE UPDATE ON forum_questions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forum_answers_updated_at 
    BEFORE UPDATE ON forum_answers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teacher_ratings_updated_at
    BEFORE UPDATE ON teacher_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_streaks_updated_at
    BEFORE UPDATE ON learning_streaks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teacher_verification_requests_updated_at
    BEFORE UPDATE ON teacher_verification_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE assignment_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE teacher_ratings ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (can be customized based on requirements)
CREATE POLICY "Users can view their own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = id::text);

-- ============================================================================
-- GRANTS AND PERMISSIONS
-- ============================================================================

-- Grant permissions to authenticated users
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant permissions to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;
