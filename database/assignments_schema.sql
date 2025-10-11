-- LearnSphere Assignments System Schema
-- Run this SQL in your Supabase SQL editor

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    file_url TEXT, -- S3 URL for assignment file (PDF/DOCX)
    due_date TIMESTAMPTZ NOT NULL,
    max_score INTEGER DEFAULT 100,
    allow_late_submission BOOLEAN DEFAULT false,
    status TEXT CHECK (status IN ('active', 'draft', 'archived')) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create assignment_submissions table
CREATE TABLE IF NOT EXISTS assignment_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL, -- S3 URL for submitted file
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    score INTEGER,
    feedback TEXT,
    status TEXT CHECK (status IN ('pending', 'submitted', 'reviewed', 'late')) DEFAULT 'submitted',
    graded_by UUID REFERENCES profiles(id),
    graded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(assignment_id, student_id) -- One submission per student per assignment
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_assignments_teacher_id ON assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_assignments_due_date ON assignments(due_date);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON assignments(status);

CREATE INDEX IF NOT EXISTS idx_assignment_submissions_assignment_id ON assignment_submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_student_id ON assignment_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_status ON assignment_submissions(status);
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_submitted_at ON assignment_submissions(submitted_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_assignments_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_assignment_submissions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic timestamp updates
CREATE TRIGGER trigger_update_assignments_updated_at
    BEFORE UPDATE ON assignments
    FOR EACH ROW
    EXECUTE FUNCTION update_assignments_updated_at();

CREATE TRIGGER trigger_update_assignment_submissions_updated_at
    BEFORE UPDATE ON assignment_submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_assignment_submissions_updated_at();

-- Create view for assignments with course and teacher information
CREATE OR REPLACE VIEW assignments_with_details AS
SELECT 
    a.*,
    c.title as course_title,
    p.full_name as teacher_name,
    (
        SELECT COUNT(*) 
        FROM assignment_submissions asub 
        WHERE asub.assignment_id = a.id
    ) as submission_count,
    (
        SELECT COUNT(*) 
        FROM enrollments e 
        WHERE e.course_id = a.course_id AND e.status = 'active'
    ) as total_students
FROM assignments a
JOIN courses c ON c.id = a.course_id
JOIN profiles p ON p.id = a.teacher_id
WHERE a.status = 'active';

-- Create view for assignment submissions with student and assignment details
CREATE OR REPLACE VIEW assignment_submissions_with_details AS
SELECT 
    asub.*,
    a.title as assignment_title,
    a.due_date,
    a.max_score,
    c.title as course_title,
    p.full_name as student_name,
    p.email as student_email,
    CASE 
        WHEN asub.submitted_at > a.due_date THEN true
        ELSE false
    END as is_late_submission
FROM assignment_submissions asub
JOIN assignments a ON a.id = asub.assignment_id
JOIN courses c ON c.id = a.course_id
JOIN profiles p ON p.id = asub.student_id;

-- Grant permissions (RLS disabled for custom auth)
GRANT ALL ON assignments TO authenticated;
GRANT ALL ON assignments TO anon;
GRANT ALL ON assignments TO service_role;

GRANT ALL ON assignment_submissions TO authenticated;
GRANT ALL ON assignment_submissions TO anon;
GRANT ALL ON assignment_submissions TO service_role;

-- Grant permissions on views
GRANT SELECT ON assignments_with_details TO authenticated;
GRANT SELECT ON assignments_with_details TO anon;
GRANT SELECT ON assignments_with_details TO service_role;

GRANT SELECT ON assignment_submissions_with_details TO authenticated;
GRANT SELECT ON assignment_submissions_with_details TO anon;
GRANT SELECT ON assignment_submissions_with_details TO service_role;

-- Enable realtime for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE assignments;
ALTER PUBLICATION supabase_realtime ADD TABLE assignment_submissions;

-- Insert sample data for testing
INSERT INTO assignments (course_id, teacher_id, title, description, due_date, max_score) 
SELECT 
    c.id,
    c.teacher_id,
    'Sample Assignment: ' || c.title,
    'This is a sample assignment for ' || c.title || '. Please submit your work before the due date.',
    NOW() + INTERVAL '7 days',
    100
FROM courses c
WHERE c.status = 'active'
LIMIT 3;

-- Add some sample submissions
INSERT INTO assignment_submissions (assignment_id, student_id, file_url, status)
SELECT 
    a.id,
    e.student_id,
    'https://example.com/submissions/sample_submission.pdf',
    'submitted'
FROM assignments a
JOIN enrollments e ON e.course_id = a.course_id
WHERE e.status = 'active'
LIMIT 5;

-- Create notification function for new assignments
CREATE OR REPLACE FUNCTION notify_new_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert notification for all enrolled students
    INSERT INTO email_notifications (recipient_email, recipient_id, subject, body, notification_type)
    SELECT 
        p.email,
        p.id,
        'New Assignment: ' || NEW.title,
        'A new assignment "' || NEW.title || '" has been posted for your course. Due date: ' || NEW.due_date::date,
        'assignment_created'
    FROM enrollments e
    JOIN profiles p ON p.id = e.student_id
    WHERE e.course_id = NEW.course_id AND e.status = 'active';
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for assignment notifications
CREATE TRIGGER trigger_notify_new_assignment
    AFTER INSERT ON assignments
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_assignment();

-- Create notification function for graded assignments
CREATE OR REPLACE FUNCTION notify_assignment_graded()
RETURNS TRIGGER AS $$
BEGIN
    -- Only notify when status changes to 'reviewed' and score is added
    IF NEW.status = 'reviewed' AND OLD.status != 'reviewed' AND NEW.score IS NOT NULL THEN
        INSERT INTO email_notifications (recipient_email, recipient_id, subject, body, notification_type)
        SELECT 
            p.email,
            p.id,
            'Assignment Graded: ' || a.title,
            'Your assignment "' || a.title || '" has been graded. Score: ' || NEW.score || '/' || a.max_score,
            'assignment_graded'
        FROM assignments a
        JOIN profiles p ON p.id = NEW.student_id
        WHERE a.id = NEW.assignment_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for grading notifications
CREATE TRIGGER trigger_notify_assignment_graded
    AFTER UPDATE ON assignment_submissions
    FOR EACH ROW
    EXECUTE FUNCTION notify_assignment_graded();

-- Comments for documentation
COMMENT ON TABLE assignments IS 'Stores assignment information created by teachers';
COMMENT ON TABLE assignment_submissions IS 'Stores student submissions for assignments';
COMMENT ON VIEW assignments_with_details IS 'Assignments with course and teacher information plus submission counts';
COMMENT ON VIEW assignment_submissions_with_details IS 'Submissions with assignment, course, and student details';
