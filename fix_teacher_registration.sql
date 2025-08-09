-- Fix teacher registration trigger issue
-- The problem is that the trigger is BEFORE INSERT, but we need the profile to exist first
-- before we can create the teacher_approval_request

-- Drop all existing triggers related to teacher approval
DROP TRIGGER IF EXISTS trigger_teacher_approval_request ON profiles;
DROP TRIGGER IF EXISTS trigger_set_teacher_approval_status ON profiles;

-- Create function to set teacher approval status (BEFORE INSERT)
CREATE OR REPLACE FUNCTION set_teacher_approval_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Only set approval status for teachers during INSERT
    IF NEW.role = 'teacher' THEN
        NEW.approval_status = 'pending';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create function for creating approval request (AFTER INSERT)
CREATE OR REPLACE FUNCTION create_teacher_approval_request_after()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create approval request for teachers
    IF NEW.role = 'teacher' THEN
        -- Insert into teacher_approval_requests AFTER the profile is created
        INSERT INTO teacher_approval_requests (teacher_id, status)
        VALUES (NEW.id, 'pending');

        -- Create email notification for admin (if email_notifications table exists)
        BEGIN
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
        EXCEPTION
            WHEN undefined_table THEN
                -- Ignore if email_notifications table doesn't exist
                NULL;
        END;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create BEFORE INSERT trigger for setting approval status
CREATE TRIGGER trigger_set_teacher_approval_status
    BEFORE INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION set_teacher_approval_status();

-- Create AFTER INSERT trigger for creating approval request
CREATE TRIGGER trigger_teacher_approval_request_after
    AFTER INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION create_teacher_approval_request_after();

-- Verify the fix by checking existing data
-- Update any existing teachers without approval requests
INSERT INTO teacher_approval_requests (teacher_id, status)
SELECT p.id, 'pending'
FROM profiles p
LEFT JOIN teacher_approval_requests tar ON p.id = tar.teacher_id
WHERE p.role = 'teacher'
  AND tar.teacher_id IS NULL
  AND p.approval_status = 'pending';

-- Update approval status for existing teachers if not set
UPDATE profiles
SET approval_status = 'pending'
WHERE role = 'teacher'
  AND (approval_status IS NULL OR approval_status = 'approved');
