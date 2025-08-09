-- EMERGENCY FIX: Completely disable the problematic trigger
-- This will allow registration to work immediately

-- Step 1: Drop ALL triggers that might be causing issues
DROP TRIGGER IF EXISTS trigger_teacher_approval_request ON profiles;
DROP TRIGGER IF EXISTS trigger_teacher_approval_request_after ON profiles;
DROP TRIGGER IF EXISTS trigger_set_teacher_approval_status ON profiles;

-- Step 2: Drop the problematic functions
DROP FUNCTION IF EXISTS create_teacher_approval_request();
DROP FUNCTION IF EXISTS create_teacher_approval_request_after();
DROP FUNCTION IF EXISTS set_teacher_approval_status();

-- Step 3: Ensure the tables exist and have correct structure
-- Check if teacher_approval_requests table exists, if not create it
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

-- Step 4: Add approval_status column to profiles if it doesn't exist
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approval_status TEXT CHECK (approval_status IN ('pending', 'approved', 'rejected')) DEFAULT 'approved';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approved_by UUID REFERENCES profiles(id);
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Step 5: Create a simple, safe function that only sets approval status
CREATE OR REPLACE FUNCTION set_teacher_pending_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Only set approval status for teachers, don't create approval requests here
    IF NEW.role = 'teacher' THEN
        NEW.approval_status = 'pending';
    ELSE
        NEW.approval_status = 'approved';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 6: Create ONLY a BEFORE INSERT trigger for setting status
CREATE TRIGGER trigger_set_teacher_pending_status
    BEFORE INSERT ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION set_teacher_pending_status();

-- Step 7: We'll handle approval request creation in the backend code instead of triggers
-- This is safer and more reliable

-- Step 8: Clean up any orphaned records
DELETE FROM teacher_approval_requests 
WHERE teacher_id NOT IN (SELECT id FROM profiles);

-- Step 9: Create approval requests for existing teachers who don't have them
INSERT INTO teacher_approval_requests (teacher_id, status)
SELECT p.id, 'pending'
FROM profiles p
LEFT JOIN teacher_approval_requests tar ON p.id = tar.teacher_id
WHERE p.role = 'teacher' 
  AND tar.teacher_id IS NULL
  AND p.approval_status = 'pending';

-- Verification queries (run these to check if fix worked)
-- SELECT COUNT(*) as total_profiles FROM profiles;
-- SELECT COUNT(*) as total_teachers FROM profiles WHERE role = 'teacher';
-- SELECT COUNT(*) as total_approval_requests FROM teacher_approval_requests;
-- SELECT p.email, p.role, p.approval_status, tar.status as request_status 
-- FROM profiles p 
-- LEFT JOIN teacher_approval_requests tar ON p.id = tar.teacher_id 
-- WHERE p.role = 'teacher';
