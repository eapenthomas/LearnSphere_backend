-- Admin Dashboard Schema
-- Run this in your Supabase SQL Editor

-- Update profiles table to include approval status and admin role
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected')) DEFAULT 'approved';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES profiles(id);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Set default approval status for teachers to pending
UPDATE profiles SET approval_status = 'pending' WHERE role = 'teacher' AND approval_status IS NULL;

-- Create teacher approval requests table
CREATE TABLE IF NOT EXISTS teacher_approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    request_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT CHECK (status IN ('pending', 'approved', 'rejected')) DEFAULT 'pending',
    admin_id UUID REFERENCES profiles(id),
    admin_notes TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user activity logs table
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    details JSONB,
    admin_id UUID REFERENCES profiles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create email notifications table
CREATE TABLE IF NOT EXISTS email_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_email TEXT NOT NULL,
    recipient_id UUID REFERENCES profiles(id),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    notification_type TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_status ON teacher_approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_teacher_approval_requests_teacher_id ON teacher_approval_requests(teacher_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_logs_user_id ON user_activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_logs_created_at ON user_activity_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_email_notifications_status ON email_notifications(status);
CREATE INDEX IF NOT EXISTS idx_profiles_approval_status ON profiles(approval_status);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Disable RLS for admin tables (since we're using custom auth)
ALTER TABLE teacher_approval_requests DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity_logs DISABLE ROW LEVEL SECURITY;
ALTER TABLE email_notifications DISABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT ALL ON teacher_approval_requests TO authenticated;
GRANT ALL ON teacher_approval_requests TO anon;
GRANT ALL ON teacher_approval_requests TO service_role;

GRANT ALL ON user_activity_logs TO authenticated;
GRANT ALL ON user_activity_logs TO anon;
GRANT ALL ON user_activity_logs TO service_role;

GRANT ALL ON email_notifications TO authenticated;
GRANT ALL ON email_notifications TO anon;
GRANT ALL ON email_notifications TO service_role;

-- Enable realtime for admin tables
ALTER PUBLICATION supabase_realtime ADD TABLE teacher_approval_requests;
ALTER PUBLICATION supabase_realtime ADD TABLE user_activity_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE email_notifications;

-- Create function to automatically create approval request when teacher registers
CREATE OR REPLACE FUNCTION create_teacher_approval_request()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create approval request for teachers
    IF NEW.role = 'teacher' THEN
        INSERT INTO teacher_approval_requests (teacher_id, status)
        VALUES (NEW.id, 'pending');
        
        -- Create email notification for admin
        INSERT INTO email_notifications (
            recipient_email,
            recipient_id,
            subject,
            body,
            notification_type
        ) VALUES (
            'eapentkadamapuzha@gmail.com', -- Replace with actual admin email
            NULL,
            'New Teacher Registration Request',
            'A new teacher has registered and is awaiting approval. Teacher: ' || NEW.full_name || ' (' || NEW.email || ')',
            'teacher_registration'
        );
        
        -- Set teacher approval status to pending
        NEW.approval_status = 'pending';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for teacher registration
DROP TRIGGER IF EXISTS trigger_teacher_approval_request ON profiles;
CREATE TRIGGER trigger_teacher_approval_request
    BEFORE INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION create_teacher_approval_request();

-- Create function to send email notifications when approval status changes
CREATE OR REPLACE FUNCTION notify_approval_status_change()
RETURNS TRIGGER AS $$
DECLARE
    user_email TEXT;
    user_name TEXT;
    email_subject TEXT;
    email_body TEXT;
BEGIN
    -- Get user details
    SELECT email, full_name INTO user_email, user_name
    FROM profiles WHERE id = NEW.teacher_id;
    
    -- Prepare email content based on status
    IF NEW.status = 'approved' THEN
        email_subject = 'Teacher Account Approved - Welcome to LearnSphere!';
        email_body = 'Dear ' || user_name || ',

Congratulations! Your teacher account has been approved. You can now access your teacher dashboard and start creating courses.

Login at: ' || 'https://learnsphere.com/login' || '

Best regards,
LearnSphere Admin Team';
    ELSIF NEW.status = 'rejected' THEN
        email_subject = 'Teacher Account Application Update';
        email_body = 'Dear ' || user_name || ',

We regret to inform you that your teacher account application has not been approved at this time.

Reason: ' || COALESCE(NEW.admin_notes, 'No specific reason provided') || '

If you have any questions, please contact our support team.

Best regards,
LearnSphere Admin Team';
    END IF;
    
    -- Insert email notification
    IF email_subject IS NOT NULL THEN
        INSERT INTO email_notifications (
            recipient_email,
            recipient_id,
            subject,
            body,
            notification_type
        ) VALUES (
            user_email,
            NEW.teacher_id,
            email_subject,
            email_body,
            'approval_status_change'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for approval status changes
DROP TRIGGER IF EXISTS trigger_approval_status_change ON teacher_approval_requests;
CREATE TRIGGER trigger_approval_status_change
    AFTER UPDATE OF status ON teacher_approval_requests
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION notify_approval_status_change();

-- Create function to notify when user is disabled/enabled
CREATE OR REPLACE FUNCTION notify_user_status_change()
RETURNS TRIGGER AS $$
DECLARE
    email_subject TEXT;
    email_body TEXT;
    status_text TEXT;
BEGIN
    -- Only notify if is_active status changed
    IF OLD.is_active IS DISTINCT FROM NEW.is_active THEN
        status_text = CASE WHEN NEW.is_active THEN 'enabled' ELSE 'disabled' END;
        
        email_subject = 'Account Status Update - LearnSphere';
        email_body = 'Dear ' || NEW.full_name || ',

Your account has been ' || status_text || ' by the administrator.

' || CASE 
    WHEN NEW.is_active THEN 'You can now access your account normally.'
    ELSE 'You will not be able to access your account until it is re-enabled.'
END || '

If you have any questions, please contact our support team.

Best regards,
LearnSphere Admin Team';
        
        -- Insert email notification
        INSERT INTO email_notifications (
            recipient_email,
            recipient_id,
            subject,
            body,
            notification_type
        ) VALUES (
            NEW.email,
            NEW.id,
            email_subject,
            email_body,
            'account_status_change'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for user status changes
DROP TRIGGER IF EXISTS trigger_user_status_change ON profiles;
CREATE TRIGGER trigger_user_status_change
    AFTER UPDATE OF is_active ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION notify_user_status_change();

-- Create admin user (update with actual admin details)
INSERT INTO profiles (
    id,
    email,
    full_name,
    role,
    approval_status,
    is_active
) VALUES (
    gen_random_uuid(),
    'admin@learnsphere.com',
    'System Administrator',
    'admin',
    'approved',
    true
) ON CONFLICT (email) DO UPDATE SET
    role = 'admin',
    approval_status = 'approved',
    is_active = true;

-- Create view for admin dashboard statistics
CREATE OR REPLACE VIEW admin_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM profiles WHERE role = 'student' AND is_active = true) as active_students,
    (SELECT COUNT(*) FROM profiles WHERE role = 'teacher' AND is_active = true AND approval_status = 'approved') as active_teachers,
    (SELECT COUNT(*) FROM teacher_approval_requests WHERE status = 'pending') as pending_approvals,
    (SELECT COUNT(*) FROM courses WHERE status = 'active') as active_courses,
    (SELECT COUNT(*) FROM enrollments WHERE status = 'active') as total_enrollments,
    (SELECT COUNT(*) FROM profiles WHERE is_active = false) as disabled_users;

-- Grant access to the view
GRANT SELECT ON admin_dashboard_stats TO authenticated;
GRANT SELECT ON admin_dashboard_stats TO anon;

SELECT 'Admin system setup complete!' as message;
