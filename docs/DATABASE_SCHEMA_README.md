# 🗄️ LearnSphere Database Schema Documentation

## Overview

This document provides a comprehensive overview of all database tables, their structure, relationships, and constraints in the LearnSphere Supabase database.

## 📋 Table of Contents

- [Core Tables](#core-tables)
- [Authentication & User Management](#authentication--user-management)
- [Course Management](#course-management)
- [Quiz System](#quiz-system)
- [Admin & Notifications](#admin--notifications)
- [Storage & Files](#storage--files)
- [Views](#views)
- [Indexes](#indexes)
- [Row Level Security (RLS)](#row-level-security-rls)

---

## Core Tables

### 1. profiles

**Purpose**: Core user table for authentication and user management

| Column             | Type        | Constraints                                                                        | Description                         |
| ------------------ | ----------- | ---------------------------------------------------------------------------------- | ----------------------------------- |
| `id`               | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                                             | Unique user identifier              |
| `email`            | TEXT        | UNIQUE, NOT NULL                                                                   | User's email address                |
| `full_name`        | TEXT        | NOT NULL                                                                           | User's full name                    |
| `role`             | TEXT        | DEFAULT 'student'                                                                  | User role (student, teacher, admin) |
| `password_salt`    | TEXT        |                                                                                    | Password salt for hashing           |
| `password_hash`    | TEXT        |                                                                                    | Hashed password                     |
| `approval_status`  | TEXT        | CHECK (approval_status IN ('pending', 'approved', 'rejected')), DEFAULT 'approved' | Account approval status             |
| `is_active`        | BOOLEAN     | DEFAULT true                                                                       | Account active status               |
| `approved_by`      | UUID        | REFERENCES profiles(id)                                                            | Admin who approved the account      |
| `approved_at`      | TIMESTAMPTZ |                                                                                    | Approval timestamp                  |
| `rejection_reason` | TEXT        |                                                                                    | Reason for rejection                |
| `created_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                                      | Account creation timestamp          |
| `updated_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                                      | Last update timestamp               |

**Indexes**:

- `idx_profiles_email` ON (email)
- `idx_profiles_role` ON (role)

**RLS**: Enabled with policies for user self-access and service role management

---

## Authentication & User Management

### 2. teacher_approval_requests

**Purpose**: Track teacher registration approval workflow

| Column         | Type        | Constraints                                                              | Description                  |
| -------------- | ----------- | ------------------------------------------------------------------------ | ---------------------------- |
| `id`           | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                                   | Unique request identifier    |
| `teacher_id`   | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE                      | Teacher requesting approval  |
| `request_date` | TIMESTAMPTZ | DEFAULT NOW()                                                            | Request submission date      |
| `status`       | TEXT        | CHECK (status IN ('pending', 'approved', 'rejected')), DEFAULT 'pending' | Request status               |
| `admin_id`     | UUID        | REFERENCES profiles(id)                                                  | Admin processing the request |
| `admin_notes`  | TEXT        |                                                                          | Admin notes/comments         |
| `processed_at` | TIMESTAMPTZ |                                                                          | Processing timestamp         |
| `created_at`   | TIMESTAMPTZ | DEFAULT NOW()                                                            | Record creation timestamp    |

### 3. password_reset_otps

**Purpose**: Store OTP codes for password reset functionality

| Column       | Type        | Constraints                            | Description                      |
| ------------ | ----------- | -------------------------------------- | -------------------------------- |
| `id`         | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid() | Unique OTP identifier            |
| `email`      | TEXT        | NOT NULL                               | Email address for password reset |
| `otp_code`   | TEXT        | NOT NULL                               | 6-digit OTP code                 |
| `expires_at` | TIMESTAMPTZ | NOT NULL                               | OTP expiration time (10 minutes) |
| `is_used`    | BOOLEAN     | DEFAULT false                          | Whether OTP has been used        |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW()                          | OTP creation timestamp           |
| `used_at`    | TIMESTAMPTZ |                                        | OTP usage timestamp              |

---

## Course Management

### 4. courses

**Purpose**: Store course information and metadata

| Column          | Type        | Constraints                                             | Description                  |
| --------------- | ----------- | ------------------------------------------------------- | ---------------------------- |
| `id`            | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                  | Unique course identifier     |
| `teacher_id`    | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE     | Course instructor            |
| `title`         | TEXT        | NOT NULL                                                | Course title                 |
| `description`   | TEXT        |                                                         | Course description           |
| `code`          | TEXT        | UNIQUE                                                  | Course code (auto-generated) |
| `thumbnail_url` | TEXT        |                                                         | Course thumbnail image URL   |
| `status`        | TEXT        | CHECK (status IN ('active', 'draft')), DEFAULT 'active' | Course status                |
| `created_at`    | TIMESTAMPTZ | DEFAULT NOW()                                           | Course creation timestamp    |
| `updated_at`    | TIMESTAMPTZ | DEFAULT NOW()                                           | Last update timestamp        |

**Indexes**:

- `idx_courses_teacher_id` ON (teacher_id)
- `idx_courses_status` ON (status)
- `idx_courses_created_at` ON (created_at)

### 5. enrollments

**Purpose**: Track student course enrollments and progress

| Column        | Type        | Constraints                                                            | Description                  |
| ------------- | ----------- | ---------------------------------------------------------------------- | ---------------------------- |
| `id`          | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                                 | Unique enrollment identifier |
| `student_id`  | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE                    | Enrolled student             |
| `course_id`   | UUID        | NOT NULL, REFERENCES courses(id) ON DELETE CASCADE                     | Enrolled course              |
| `enrolled_at` | TIMESTAMPTZ | DEFAULT NOW()                                                          | Enrollment timestamp         |
| `progress`    | INTEGER     | DEFAULT 0, CHECK (progress >= 0 AND progress <= 100)                   | Course completion percentage |
| `status`      | TEXT        | CHECK (status IN ('active', 'completed', 'dropped')), DEFAULT 'active' | Enrollment status            |

**Constraints**:

- UNIQUE(student_id, course_id) - Prevents duplicate enrollments

**Indexes**:

- `idx_enrollments_student_id` ON (student_id)
- `idx_enrollments_course_id` ON (course_id)
- `idx_enrollments_status` ON (status)

### 6. course_materials

**Purpose**: Store course materials and file metadata

| Column        | Type        | Constraints                                         | Description                |
| ------------- | ----------- | --------------------------------------------------- | -------------------------- |
| `id`          | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique material identifier |
| `course_id`   | UUID        | NOT NULL, REFERENCES courses(id) ON DELETE CASCADE  | Associated course          |
| `file_name`   | TEXT        | NOT NULL                                            | Original file name         |
| `file_url`    | TEXT        | NOT NULL                                            | File storage URL (S3)      |
| `file_size`   | BIGINT      |                                                     | File size in bytes         |
| `file_type`   | TEXT        |                                                     | MIME type                  |
| `uploaded_by` | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE | User who uploaded the file |
| `uploaded_at` | TIMESTAMPTZ | DEFAULT NOW()                                       | Upload timestamp           |
| `updated_at`  | TIMESTAMPTZ | DEFAULT NOW()                                       | Last update timestamp      |
| `description` | TEXT        |                                                     | File description           |
| `is_active`   | BOOLEAN     | DEFAULT true                                        | Soft delete flag           |

**Indexes**:

- `idx_course_materials_course_id` ON (course_id)
- `idx_course_materials_uploaded_by` ON (uploaded_by)
- `idx_course_materials_uploaded_at` ON (uploaded_at)

---

## Quiz System

### 7. quizzes

**Purpose**: Store quiz metadata and configuration

| Column             | Type        | Constraints                                                           | Description                    |
| ------------------ | ----------- | --------------------------------------------------------------------- | ------------------------------ |
| `id`               | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                                | Unique quiz identifier         |
| `course_id`        | UUID        | NOT NULL, REFERENCES courses(id) ON DELETE CASCADE                    | Associated course              |
| `teacher_id`       | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE                   | Quiz creator                   |
| `title`            | TEXT        | NOT NULL                                                              | Quiz title                     |
| `description`      | TEXT        |                                                                       | Quiz description               |
| `instructions`     | TEXT        |                                                                       | Quiz instructions for students |
| `total_marks`      | INTEGER     | DEFAULT 0                                                             | Total possible marks           |
| `duration_minutes` | INTEGER     | DEFAULT 60                                                            | Quiz duration in minutes       |
| `start_time`       | TIMESTAMPTZ |                                                                       | Quiz availability start time   |
| `end_time`         | TIMESTAMPTZ |                                                                       | Quiz availability end time     |
| `status`           | TEXT        | CHECK (status IN ('draft', 'published', 'archived')), DEFAULT 'draft' | Quiz status                    |
| `created_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                         | Quiz creation timestamp        |
| `updated_at`       | TIMESTAMPTZ | DEFAULT NOW()                                                         | Last update timestamp          |

### 8. quiz_questions

**Purpose**: Store individual quiz questions

| Column           | Type        | Constraints                                                              | Description                        |
| ---------------- | ----------- | ------------------------------------------------------------------------ | ---------------------------------- |
| `id`             | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                                   | Unique question identifier         |
| `quiz_id`        | UUID        | NOT NULL, REFERENCES quizzes(id) ON DELETE CASCADE                       | Associated quiz                    |
| `question_text`  | TEXT        | NOT NULL                                                                 | Question content                   |
| `question_type`  | TEXT        | NOT NULL, CHECK (question_type IN ('mcq', 'true_false', 'short_answer')) | Question type                      |
| `options`        | JSONB       |                                                                          | MCQ options (for mcq type)         |
| `correct_answer` | TEXT        |                                                                          | Correct answer (for non-mcq types) |
| `marks`          | INTEGER     | DEFAULT 1                                                                | Points for this question           |
| `order_index`    | INTEGER     | DEFAULT 0                                                                | Question order in quiz             |
| `created_at`     | TIMESTAMPTZ | DEFAULT NOW()                                                            | Question creation timestamp        |

### 9. quiz_submissions

**Purpose**: Track student quiz attempts and scores

| Column               | Type        | Constraints                                         | Description                  |
| -------------------- | ----------- | --------------------------------------------------- | ---------------------------- |
| `id`                 | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique submission identifier |
| `quiz_id`            | UUID        | NOT NULL, REFERENCES quizzes(id) ON DELETE CASCADE  | Associated quiz              |
| `student_id`         | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE | Student who submitted        |
| `answers`            | JSONB       | NOT NULL                                            | Student's answers            |
| `score`              | INTEGER     | DEFAULT 0                                           | Calculated score             |
| `total_marks`        | INTEGER     | DEFAULT 0                                           | Total possible marks         |
| `time_taken_minutes` | INTEGER     |                                                     | Time taken to complete       |
| `submitted_at`       | TIMESTAMPTZ | DEFAULT NOW()                                       | Submission timestamp         |
| `started_at`         | TIMESTAMPTZ |                                                     | Quiz start timestamp         |

**Constraints**:

- UNIQUE(quiz_id, student_id) - One submission per student per quiz

---

## Admin & Notifications

### 10. user_activity_logs

**Purpose**: Track user actions for audit and monitoring

| Column       | Type        | Constraints                                         | Description                                |
| ------------ | ----------- | --------------------------------------------------- | ------------------------------------------ |
| `id`         | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()              | Unique log identifier                      |
| `user_id`    | UUID        | NOT NULL, REFERENCES profiles(id) ON DELETE CASCADE | User who performed action                  |
| `action`     | TEXT        | NOT NULL                                            | Action performed                           |
| `details`    | JSONB       |                                                     | Additional action details                  |
| `admin_id`   | UUID        | REFERENCES profiles(id)                             | Admin who performed action (if applicable) |
| `created_at` | TIMESTAMPTZ | DEFAULT NOW()                                       | Action timestamp                           |

### 11. email_notifications

**Purpose**: Queue and track email notifications

| Column              | Type        | Constraints                                                        | Description                    |
| ------------------- | ----------- | ------------------------------------------------------------------ | ------------------------------ |
| `id`                | UUID        | PRIMARY KEY, DEFAULT gen_random_uuid()                             | Unique notification identifier |
| `recipient_email`   | TEXT        | NOT NULL                                                           | Recipient email address        |
| `recipient_id`      | UUID        | REFERENCES profiles(id)                                            | Recipient user ID              |
| `subject`           | TEXT        | NOT NULL                                                           | Email subject                  |
| `body`              | TEXT        | NOT NULL                                                           | Email body content             |
| `notification_type` | TEXT        | NOT NULL                                                           | Type of notification           |
| `status`            | TEXT        | CHECK (status IN ('pending', 'sent', 'failed')), DEFAULT 'pending' | Delivery status                |
| `sent_at`           | TIMESTAMPTZ |                                                                    | Delivery timestamp             |
| `created_at`        | TIMESTAMPTZ | DEFAULT NOW()                                                      | Creation timestamp             |

---

## Storage & Files

### Storage Buckets

#### course-thumbnails

**Purpose**: Store course thumbnail images

- **Public**: Yes
- **File Size Limit**: 5MB
- **Allowed MIME Types**: image/jpeg, image/png, image/webp, image/gif

#### course-materials

**Purpose**: Store course materials and documents

- **Public**: No (access controlled by RLS)
- **File Size Limit**: 100MB
- **Allowed MIME Types**: All document types

---

## Views

### public_profiles

**Purpose**: Public profile information without sensitive data

```sql
SELECT id, full_name, role, created_at FROM profiles;
```

### course_enrollment_stats

**Purpose**: Course enrollment statistics

```sql
SELECT
    c.id as course_id,
    c.title,
    c.teacher_id,
    COUNT(e.id) as total_enrollments,
    COUNT(CASE WHEN e.status = 'active' THEN 1 END) as active_enrollments,
    COUNT(CASE WHEN e.status = 'completed' THEN 1 END) as completed_enrollments
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
GROUP BY c.id, c.title, c.teacher_id;
```

### course_materials_with_metadata

**Purpose**: Course materials with additional metadata

```sql
SELECT
    cm.*,
    c.title as course_title,
    p.full_name as uploader_name
FROM course_materials cm
JOIN courses c ON c.id = cm.course_id
JOIN profiles p ON p.id = cm.uploaded_by
WHERE cm.is_active = true;
```

---

## Indexes

### Performance Indexes

- **profiles**: email, role
- **courses**: teacher_id, status, created_at
- **enrollments**: student_id, course_id, status
- **course_materials**: course_id, uploaded_by, uploaded_at
- **quiz_questions**: quiz_id, order_index
- **quiz_submissions**: quiz_id, student_id, submitted_at

---

## Row Level Security (RLS)

### Enabled Tables

- `profiles` - Users can access own profile, service role has full access
- `courses` - Teachers can manage own courses, students can view active courses
- `course_materials` - Teachers can manage materials for their courses, students can view materials for enrolled courses

### Disabled Tables (Custom Auth)

- `enrollments` - Managed by FastAPI backend
- `quizzes` - Managed by FastAPI backend
- `quiz_questions` - Managed by FastAPI backend
- `quiz_submissions` - Managed by FastAPI backend
- `teacher_approval_requests` - Managed by FastAPI backend
- `user_activity_logs` - Managed by FastAPI backend
- `email_notifications` - Managed by FastAPI backend

---

## Triggers & Functions

### Automatic Timestamp Updates

- `update_profiles_updated_at()` - Updates profiles.updated_at on changes
- `update_courses_updated_at()` - Updates courses.updated_at on changes
- `update_course_materials_updated_at()` - Updates course_materials.updated_at on changes

### Notification Triggers

- `notify_teacher_approval()` - Sends email on teacher approval status change
- `notify_user_status_change()` - Sends email on user account status change

---

## Realtime Subscriptions

The following tables have realtime enabled for live updates:

- `courses`
- `enrollments`
- `course_materials`
- `teacher_approval_requests`
- `user_activity_logs`
- `email_notifications`

---

## Migration Notes

1. **Initial Setup**: Run `database_schema.sql` for profiles table
2. **Courses**: Run `courses_schema.sql` for course management
3. **Enrollments**: Run `enrollment_schema.sql` for student enrollments
4. **Materials**: Run `course_materials_schema.sql` for file management
5. **Admin**: Run `admin_schema.sql` for admin features
6. **Quiz System**: Tables created dynamically by quiz_api.py

---

## Backup & Maintenance

### Regular Backups

- **Daily**: Automated Supabase backups
- **Weekly**: Manual export of critical tables
- **Monthly**: Full database backup with schema

### Cleanup Tasks

- Remove expired OTP codes (older than 24 hours)
- Archive old activity logs (older than 1 year)
- Clean up failed email notifications (older than 30 days)

---

## SQL Schema Creation Scripts

### Complete Quiz System Schema

```sql
-- Create quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    total_marks INTEGER DEFAULT 0,
    duration_minutes INTEGER DEFAULT 60,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status TEXT CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create quiz_questions table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL CHECK (question_type IN ('mcq', 'true_false', 'short_answer')),
    options JSONB,
    correct_answer TEXT,
    marks INTEGER DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create quiz_submissions table
CREATE TABLE IF NOT EXISTS quiz_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,
    score INTEGER DEFAULT 0,
    total_marks INTEGER DEFAULT 0,
    time_taken_minutes INTEGER,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    UNIQUE(quiz_id, student_id)
);

-- Create indexes for quiz tables
CREATE INDEX IF NOT EXISTS idx_quizzes_course_id ON quizzes(course_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_teacher_id ON quizzes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_status ON quizzes(status);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_quiz_id ON quiz_questions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_order_index ON quiz_questions(order_index);
CREATE INDEX IF NOT EXISTS idx_quiz_submissions_quiz_id ON quiz_submissions(quiz_id);
CREATE INDEX IF NOT EXISTS idx_quiz_submissions_student_id ON quiz_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_quiz_submissions_submitted_at ON quiz_submissions(submitted_at);

-- Grant permissions
GRANT ALL ON quizzes TO authenticated;
GRANT ALL ON quizzes TO anon;
GRANT ALL ON quizzes TO service_role;
GRANT ALL ON quiz_questions TO authenticated;
GRANT ALL ON quiz_questions TO anon;
GRANT ALL ON quiz_questions TO service_role;
GRANT ALL ON quiz_submissions TO authenticated;
GRANT ALL ON quiz_submissions TO anon;
GRANT ALL ON quiz_submissions TO service_role;

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE quizzes;
ALTER PUBLICATION supabase_realtime ADD TABLE quiz_questions;
ALTER PUBLICATION supabase_realtime ADD TABLE quiz_submissions;
```

### Password Reset OTP Schema

```sql
-- Create password_reset_otps table
CREATE TABLE IF NOT EXISTS password_reset_otps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_used BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    used_at TIMESTAMPTZ
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_password_reset_otps_email ON password_reset_otps(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_otps_expires_at ON password_reset_otps(expires_at);

-- Grant permissions
GRANT ALL ON password_reset_otps TO authenticated;
GRANT ALL ON password_reset_otps TO anon;
GRANT ALL ON password_reset_otps TO service_role;
```

---

## Quick Setup Commands

### 1. Initialize Core Tables

```bash
# Run in Supabase SQL Editor
\i backend/database_schema.sql
\i backend/courses_schema.sql
\i backend/enrollment_schema.sql
\i backend/course_materials_schema.sql
\i backend/admin_schema.sql
```

### 2. Add Quiz System

```sql
-- Copy and paste the Quiz System Schema above
```

### 3. Add Password Reset

```sql
-- Copy and paste the Password Reset OTP Schema above
```

### 4. Verify Setup

```sql
-- Check all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check table relationships
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

---

_Last Updated: December 2024_
_Version: 1.0_
