-- LearnSphere Notifications System Schema
-- Run this SQL in your Supabase SQL editor

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN (
        -- Assignment notifications
        'assignment_created', 'assignment_due_soon', 'assignment_due_today', 'assignment_overdue',
        'assignment_submitted', 'assignment_graded',
        -- Quiz notifications
        'quiz_available', 'quiz_due_soon', 'quiz_due_today', 'quiz_overdue',
        'quiz_completed', 'quiz_graded',
        -- Course notifications
        'course_enrolled', 'course_updated', 'new_material', 'course_completed',
        -- Forum notifications
        'forum_question_answered', 'forum_new_question', 'forum_question_resolved',
        -- Teacher notifications
        'student_enrolled', 'assignment_submission_received', 'quiz_submission_received',
        'student_question_asked', 'course_rating_received',
        -- System notifications
        'account_approved', 'account_rejected', 'password_changed', 'login_alert',
        'payment_successful', 'payment_failed', 'subscription_expired'
    )),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB, -- Additional data like course_id, assignment_id, etc.
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    action_url TEXT, -- URL to navigate to when clicked
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE -- Optional expiration date
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_expires_at ON notifications(expires_at);

-- Composite index for user notifications with read status
CREATE INDEX IF NOT EXISTS idx_notifications_user_read_created ON notifications(user_id, is_read, created_at DESC);

-- Disable RLS for notifications table (using custom auth)
ALTER TABLE notifications DISABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT ALL ON notifications TO authenticated;
GRANT ALL ON notifications TO anon;
GRANT ALL ON service_role;

-- Enable realtime for notifications
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;

-- Create function to clean up expired notifications
CREATE OR REPLACE FUNCTION cleanup_expired_notifications()
RETURNS void AS $$
BEGIN
    DELETE FROM notifications 
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create function to get user notification count
CREATE OR REPLACE FUNCTION get_user_notification_count(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    count INTEGER;
BEGIN
    SELECT COUNT(*) INTO count
    FROM notifications
    WHERE user_id = user_uuid 
    AND is_read = FALSE
    AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN COALESCE(count, 0);
END;
$$ LANGUAGE plpgsql;

-- Create function to create notification
CREATE OR REPLACE FUNCTION create_notification(
    p_user_id UUID,
    p_type TEXT,
    p_title TEXT,
    p_message TEXT,
    p_data JSONB DEFAULT NULL,
    p_priority TEXT DEFAULT 'medium',
    p_action_url TEXT DEFAULT NULL,
    p_expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    notification_id UUID;
BEGIN
    INSERT INTO notifications (
        user_id, type, title, message, data, priority, action_url, expires_at
    ) VALUES (
        p_user_id, p_type, p_title, p_message, p_data, p_priority, p_action_url, p_expires_at
    ) RETURNING id INTO notification_id;
    
    RETURN notification_id;
END;
$$ LANGUAGE plpgsql;

-- Create function to mark notification as read
CREATE OR REPLACE FUNCTION mark_notification_read(p_notification_id UUID, p_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE notifications 
    SET is_read = TRUE, read_at = NOW()
    WHERE id = p_notification_id AND user_id = p_user_id;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Create function to mark all user notifications as read
CREATE OR REPLACE FUNCTION mark_all_notifications_read(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE notifications 
    SET is_read = TRUE, read_at = NOW()
    WHERE user_id = p_user_id AND is_read = FALSE;
    
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Create notification triggers for assignments
CREATE OR REPLACE FUNCTION notify_assignment_created()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    teacher_name TEXT;
    due_date_str TEXT;
BEGIN
    -- Get course and teacher information
    SELECT c.title, p.full_name INTO course_title, teacher_name
    FROM courses c
    JOIN profiles p ON p.id = c.teacher_id
    WHERE c.id = NEW.course_id;
    
    due_date_str := to_char(NEW.due_date, 'Mon DD, YYYY at HH24:MI');
    
    -- Create notifications for all enrolled students
    INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
    SELECT 
        e.student_id,
        'assignment_created',
        'New Assignment: ' || NEW.title,
        'A new assignment "' || NEW.title || '" has been posted in ' || course_title || ' by ' || teacher_name || '. Due: ' || due_date_str,
        jsonb_build_object(
            'assignment_id', NEW.id,
            'course_id', NEW.course_id,
            'teacher_id', NEW.teacher_id,
            'due_date', NEW.due_date,
            'course_title', course_title,
            'teacher_name', teacher_name
        ),
        CASE 
            WHEN NEW.due_date - NOW() <= INTERVAL '1 day' THEN 'high'
            WHEN NEW.due_date - NOW() <= INTERVAL '3 days' THEN 'medium'
            ELSE 'low'
        END,
        '/assignments'
    FROM enrollments e
    WHERE e.course_id = NEW.course_id AND e.status = 'active';
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for assignment notifications
DROP TRIGGER IF EXISTS trigger_notify_assignment_created ON assignments;
CREATE TRIGGER trigger_notify_assignment_created
    AFTER INSERT ON assignments
    FOR EACH ROW
    EXECUTE FUNCTION notify_assignment_created();

-- Create notification function for assignment grading
CREATE OR REPLACE FUNCTION notify_assignment_graded()
RETURNS TRIGGER AS $$
DECLARE
    assignment_title TEXT;
    course_title TEXT;
    teacher_name TEXT;
    max_score INTEGER;
BEGIN
    -- Only notify when status changes to 'reviewed' and score is added
    IF NEW.status = 'reviewed' AND OLD.status != 'reviewed' AND NEW.score IS NOT NULL THEN
        -- Get assignment and course information
        SELECT a.title, a.max_score, c.title, p.full_name 
        INTO assignment_title, max_score, course_title, teacher_name
        FROM assignments a
        JOIN courses c ON c.id = a.course_id
        JOIN profiles p ON p.id = a.teacher_id
        WHERE a.id = NEW.assignment_id;
        
        -- Create notification for student
        INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
        VALUES (
            NEW.student_id,
            'assignment_graded',
            'Assignment Graded: ' || assignment_title,
            'Your assignment "' || assignment_title || '" in ' || course_title || ' has been graded by ' || teacher_name || '. Score: ' || NEW.score || '/' || max_score,
            jsonb_build_object(
                'assignment_id', NEW.assignment_id,
                'course_id', (SELECT course_id FROM assignments WHERE id = NEW.assignment_id),
                'score', NEW.score,
                'max_score', max_score,
                'course_title', course_title,
                'teacher_name', teacher_name
            ),
            'medium',
            '/assignments'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for grading notifications
DROP TRIGGER IF EXISTS trigger_notify_assignment_graded ON assignment_submissions;
CREATE TRIGGER trigger_notify_assignment_graded
    AFTER UPDATE ON assignment_submissions
    FOR EACH ROW
    EXECUTE FUNCTION notify_assignment_graded();

-- Create notification function for quiz availability
CREATE OR REPLACE FUNCTION notify_quiz_available()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    teacher_name TEXT;
    end_time_str TEXT;
BEGIN
    -- Only notify for published quizzes
    IF NEW.status = 'published' AND OLD.status != 'published' THEN
        -- Get course and teacher information
        SELECT c.title, p.full_name INTO course_title, teacher_name
        FROM courses c
        JOIN profiles p ON p.id = c.teacher_id
        WHERE c.id = NEW.course_id;
        
        end_time_str := CASE 
            WHEN NEW.end_time IS NOT NULL THEN to_char(NEW.end_time, 'Mon DD, YYYY at HH24:MI')
            ELSE 'No deadline'
        END;
        
        -- Create notifications for all enrolled students
        INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
        SELECT 
            e.student_id,
            'quiz_available',
            'New Quiz Available: ' || NEW.title,
            'A new quiz "' || NEW.title || '" is now available in ' || course_title || ' by ' || teacher_name || '. End time: ' || end_time_str,
            jsonb_build_object(
                'quiz_id', NEW.id,
                'course_id', NEW.course_id,
                'teacher_id', NEW.created_by,
                'end_time', NEW.end_time,
                'course_title', course_title,
                'teacher_name', teacher_name
            ),
            CASE 
                WHEN NEW.end_time IS NOT NULL AND NEW.end_time - NOW() <= INTERVAL '1 day' THEN 'high'
                WHEN NEW.end_time IS NOT NULL AND NEW.end_time - NOW() <= INTERVAL '3 days' THEN 'medium'
                ELSE 'low'
            END,
            '/student/quizzes'
        FROM enrollments e
        WHERE e.course_id = NEW.course_id AND e.status = 'active';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for quiz notifications
DROP TRIGGER IF EXISTS trigger_notify_quiz_available ON quizzes;
CREATE TRIGGER trigger_notify_quiz_available
    AFTER UPDATE ON quizzes
    FOR EACH ROW
    EXECUTE FUNCTION notify_quiz_available();

-- Create notification function for course enrollment
CREATE OR REPLACE FUNCTION notify_course_enrollment()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    teacher_name TEXT;
    student_name TEXT;
BEGIN
    -- Only notify for active enrollments
    IF NEW.status = 'active' AND OLD.status != 'active' THEN
        -- Get course, teacher, and student information
        SELECT c.title, p.full_name INTO course_title, teacher_name
        FROM courses c
        JOIN profiles p ON p.id = c.teacher_id
        WHERE c.id = NEW.course_id;
        
        SELECT full_name INTO student_name
        FROM profiles
        WHERE id = NEW.student_id;
        
        -- Create notification for student
        INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
        VALUES (
            NEW.student_id,
            'course_enrolled',
            'Successfully Enrolled: ' || course_title,
            'You have been successfully enrolled in "' || course_title || '" taught by ' || teacher_name || '. Welcome to the course!',
            jsonb_build_object(
                'course_id', NEW.course_id,
                'teacher_id', (SELECT teacher_id FROM courses WHERE id = NEW.course_id),
                'course_title', course_title,
                'teacher_name', teacher_name
            ),
            'medium',
            '/mycourses'
        );
        
        -- Create notification for teacher
        INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
        VALUES (
            (SELECT teacher_id FROM courses WHERE id = NEW.course_id),
            'student_enrolled',
            'New Student Enrolled: ' || student_name,
            'A new student "' || student_name || '" has enrolled in your course "' || course_title || '".',
            jsonb_build_object(
                'course_id', NEW.course_id,
                'student_id', NEW.student_id,
                'student_name', student_name,
                'course_title', course_title
            ),
            'low',
            '/teacher/students'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for enrollment notifications
DROP TRIGGER IF EXISTS trigger_notify_course_enrollment ON enrollments;
CREATE TRIGGER trigger_notify_course_enrollment
    AFTER UPDATE ON enrollments
    FOR EACH ROW
    EXECUTE FUNCTION notify_course_enrollment();

-- Create notification function for assignment submissions
CREATE OR REPLACE FUNCTION notify_assignment_submission()
RETURNS TRIGGER AS $$
DECLARE
    assignment_title TEXT;
    course_title TEXT;
    student_name TEXT;
    teacher_id UUID;
BEGIN
    -- Only notify when assignment is submitted
    IF NEW.status = 'submitted' AND OLD.status != 'submitted' THEN
        -- Get assignment, course, and student information
        SELECT a.title, a.teacher_id, c.title, p.full_name 
        INTO assignment_title, teacher_id, course_title, student_name
        FROM assignments a
        JOIN courses c ON c.id = a.course_id
        JOIN profiles p ON p.id = NEW.student_id
        WHERE a.id = NEW.assignment_id;
        
        -- Create notification for teacher
        INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
        VALUES (
            teacher_id,
            'assignment_submission_received',
            'Assignment Submitted: ' || assignment_title,
            'Student "' || student_name || '" has submitted the assignment "' || assignment_title || '" in ' || course_title || '.',
            jsonb_build_object(
                'assignment_id', NEW.assignment_id,
                'course_id', (SELECT course_id FROM assignments WHERE id = NEW.assignment_id),
                'student_id', NEW.student_id,
                'student_name', student_name,
                'course_title', course_title,
                'submitted_at', NEW.submitted_at
            ),
            'medium',
            '/teacher/assignments'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for assignment submission notifications
DROP TRIGGER IF EXISTS trigger_notify_assignment_submission ON assignment_submissions;
CREATE TRIGGER trigger_notify_assignment_submission
    AFTER UPDATE ON assignment_submissions
    FOR EACH ROW
    EXECUTE FUNCTION notify_assignment_submission();

-- Create notification function for forum questions
CREATE OR REPLACE FUNCTION notify_forum_question()
RETURNS TRIGGER AS $$
DECLARE
    course_title TEXT;
    student_name TEXT;
    teacher_id UUID;
BEGIN
    -- Get course and student information
    SELECT c.title, c.teacher_id, p.full_name 
    INTO course_title, teacher_id, student_name
    FROM courses c
    JOIN profiles p ON p.id = NEW.student_id
    WHERE c.id = NEW.course_id;
    
    -- Create notification for teacher
    INSERT INTO notifications (user_id, type, title, message, data, priority, action_url)
    VALUES (
        teacher_id,
        'student_question_asked',
        'New Question in ' || course_title,
        'Student "' || student_name || '" has asked a new question in the forum for ' || course_title || ': "' || NEW.title || '"',
        jsonb_build_object(
            'question_id', NEW.id,
            'course_id', NEW.course_id,
            'student_id', NEW.student_id,
            'student_name', student_name,
            'course_title', course_title
        ),
        'medium',
        '/forum'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for forum question notifications
DROP TRIGGER IF EXISTS trigger_notify_forum_question ON forum_questions;
CREATE TRIGGER trigger_notify_forum_question
    AFTER INSERT ON forum_questions
    FOR EACH ROW
    EXECUTE FUNCTION notify_forum_question();

-- Comments for documentation
COMMENT ON TABLE notifications IS 'Stores in-app notifications for users';
COMMENT ON COLUMN notifications.type IS 'Type of notification for categorization';
COMMENT ON COLUMN notifications.data IS 'Additional JSON data related to the notification';
COMMENT ON COLUMN notifications.priority IS 'Priority level for notification display';
COMMENT ON COLUMN notifications.action_url IS 'URL to navigate to when notification is clicked';
COMMENT ON COLUMN notifications.expires_at IS 'Optional expiration date for the notification';
