-- LearnSphere Database Snapshot
-- Date: 2025-01-11
-- This file contains the current state of the database with sample data

-- ============================================================================
-- CURRENT DATA SUMMARY
-- ============================================================================

-- Total Tables: 22
-- Total Records: 
--   - profiles: 1 (admin user only)
--   - courses: 0
--   - enrollments: 0
--   - assignments: 0
--   - quizzes: 0
--   - teacher_verification_requests: 0
--   - All other tables: 0

-- ============================================================================
-- CURRENT USER DATA
-- ============================================================================

-- Admin User (only remaining user after cleanup)
INSERT INTO profiles (
    id, 
    full_name, 
    role, 
    email, 
    approval_status, 
    is_active, 
    is_verified,
    created_at
) VALUES (
    '7edf16d1-902f-485a-a3a7-2437689fa074',
    'Eapen',
    'admin',
    'eapentkadamapuzha@gmail.com',
    'approved',
    true,
    true,
    '2025-09-13 06:06:56.438814+00'
) ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- DATABASE STATISTICS
-- ============================================================================

-- Table sizes and row counts (as of snapshot date)
/*
profiles: 1 row
refresh_tokens: 7 rows (admin sessions)
courses: 0 rows
enrollments: 0 rows
assignments: 0 rows
assignment_submissions: 0 rows
quizzes: 0 rows
quiz_questions: 0 rows
quiz_submissions: 0 rows
course_materials: 0 rows
course_material_progress: 0 rows
course_progress: 0 rows
course_certificates: 0 rows
course_completions: 0 rows
teacher_verification_requests: 0 rows
teacher_approval_requests: 0 rows
password_reset_otps: 0 rows
payments: 0 rows
ai_tutor_documents: 0 rows
ai_tutor_interactions: 0 rows
ai_usage_logs: 0 rows
forum_questions: 0 rows
forum_answers: 0 rows
teacher_ratings: 0 rows
learning_streaks: 0 rows
email_notifications: 0 rows
user_activity_logs: 0 rows
*/

-- ============================================================================
-- STORAGE BUCKETS STATUS
-- ============================================================================

-- Supabase Storage Buckets:
-- 1. course-materials (for course files)
-- 2. teacher-verification (for ID cards)
-- 3. profile-pictures (for user avatars)
-- 4. assignment-files (for assignment attachments)
-- 5. submission-files (for student submissions)

-- Current storage usage: Minimal (only admin profile picture if any)

-- ============================================================================
-- CLEANUP NOTES
-- ============================================================================

-- The following users were removed during cleanup:
-- 1. Priya Sharma (ankitha@learnsphere.com) - Teacher
-- 2. Eapen Thomas (eapenthomasmca@gmail.com) - Student  
-- 3. Adithyan (adithyanvs@gmail.com) - Student

-- All related data was also cleaned up:
-- - Email notifications
-- - Teacher verification requests
-- - Refresh tokens
-- - Course enrollments
-- - Assignment submissions
-- - Quiz submissions
-- - Any other user-related records

-- ============================================================================
-- SYSTEM STATUS
-- ============================================================================

-- Database Status: Clean and ready for fresh testing
-- Admin Access: Available (eapentkadamapuzha@gmail.com)
-- Teacher Verification: Ready for new applications
-- OCR System: Functional and tested
-- Email Notifications: Configured and working
-- File Storage: Available and organized

-- ============================================================================
-- NEXT STEPS FOR DEVELOPMENT
-- ============================================================================

-- 1. Test teacher registration with OCR verification
-- 2. Test manual teacher approval workflow
-- 3. Test student enrollment and course access
-- 4. Test assignment and quiz creation
-- 5. Test AI tutor functionality
-- 6. Test email notifications
-- 7. Test file upload and storage
-- 8. Test admin dashboard functionality

-- ============================================================================
-- BACKUP RECOMMENDATIONS
-- ============================================================================

-- Before adding new test data:
-- 1. Create a backup of current clean state
-- 2. Document any new features being tested
-- 3. Keep admin user intact for system access
-- 4. Regular cleanup of test data to maintain performance

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================

-- Database is optimized with:
-- - Proper indexing on all frequently queried columns
-- - Foreign key constraints for data integrity
-- - Row Level Security (RLS) for data protection
-- - Efficient views for common queries
-- - Automatic timestamp updates via triggers

-- Current performance: Excellent (minimal data)
-- Expected performance with full data: Good (with proper indexing)
