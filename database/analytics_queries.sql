-- =====================================================
-- LearnSphere Teacher Analytics Queries
-- =====================================================
-- This file contains optimized SQL queries used by the
-- teacher analytics system for real-time dashboard data
-- =====================================================

-- =====================================================
-- 1. STUDENT PERFORMANCE TRENDS (6-Week Analysis)
-- =====================================================
-- Aggregates student performance over the last 6 weeks
-- Used for: Performance trend charts in teacher dashboard

WITH weekly_performance AS (
  SELECT 
    DATE_TRUNC('week', qs.created_at) as week_start,
    AVG(qs.score) as avg_score,
    COUNT(*) as total_submissions,
    COUNT(DISTINCT qs.student_id) as unique_students
  FROM quiz_submissions qs
  JOIN quizzes q ON qs.quiz_id = q.id
  WHERE q.teacher_id = $1 
    AND qs.created_at >= NOW() - INTERVAL '6 weeks'
  GROUP BY DATE_TRUNC('week', qs.created_at)
  
  UNION ALL
  
  SELECT 
    DATE_TRUNC('week', asub.submitted_at) as week_start,
    AVG(asub.score) as avg_score,
    COUNT(*) as total_submissions,
    COUNT(DISTINCT asub.student_id) as unique_students
  FROM assignment_submissions asub
  JOIN assignments a ON asub.assignment_id = a.id
  WHERE a.teacher_id = $1 
    AND asub.submitted_at >= NOW() - INTERVAL '6 weeks'
    AND asub.score IS NOT NULL
  GROUP BY DATE_TRUNC('week', asub.submitted_at)
)
SELECT 
  week_start,
  ROUND(AVG(avg_score), 1) as average_score,
  SUM(total_submissions) as total_submissions,
  SUM(unique_students) as unique_students
FROM weekly_performance
GROUP BY week_start
ORDER BY week_start DESC
LIMIT 6;

-- =====================================================
-- 2. COURSE-WISE PERFORMANCE ANALYSIS
-- =====================================================
-- Analyzes performance metrics for each course
-- Used for: Course performance comparison charts

SELECT 
  c.id as course_id,
  c.title as course_name,
  COUNT(DISTINCT e.student_id) as enrolled_students,
  COUNT(DISTINCT CASE WHEN e.status = 'active' THEN e.student_id END) as active_students,
  
  -- Quiz performance
  COUNT(DISTINCT qs.id) as quiz_submissions,
  ROUND(AVG(qs.score), 1) as avg_quiz_score,
  
  -- Assignment performance  
  COUNT(DISTINCT asub.id) as assignment_submissions,
  ROUND(AVG(asub.score), 1) as avg_assignment_score,
  
  -- Overall performance
  ROUND(
    (COALESCE(AVG(qs.score), 0) + COALESCE(AVG(asub.score), 0)) / 
    CASE 
      WHEN AVG(qs.score) IS NOT NULL AND AVG(asub.score) IS NOT NULL THEN 2
      WHEN AVG(qs.score) IS NOT NULL OR AVG(asub.score) IS NOT NULL THEN 1
      ELSE 1
    END, 1
  ) as overall_avg_score

FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN quizzes q ON c.id = q.course_id
LEFT JOIN quiz_submissions qs ON q.id = qs.quiz_id AND qs.student_id = e.student_id
LEFT JOIN assignments a ON c.id = a.course_id
LEFT JOIN assignment_submissions asub ON a.id = asub.assignment_id AND asub.student_id = e.student_id

WHERE c.teacher_id = $1
GROUP BY c.id, c.title
HAVING COUNT(DISTINCT e.student_id) > 0
ORDER BY enrolled_students DESC;

-- =====================================================
-- 3. UPCOMING DEADLINES ANALYSIS
-- =====================================================
-- Retrieves upcoming assignments and quizzes with submission stats
-- Used for: Deadline management in teacher dashboard

-- Upcoming Assignments
SELECT 
  'assignment' as type,
  a.id,
  a.title,
  c.title as course_name,
  a.due_date,
  a.description,
  
  -- Submission statistics
  COUNT(DISTINCT e.student_id) as total_students,
  COUNT(DISTINCT asub.student_id) as submitted_count,
  ROUND(
    (COUNT(DISTINCT asub.student_id)::float / NULLIF(COUNT(DISTINCT e.student_id), 0)) * 100, 
    1
  ) as submission_percentage,
  
  -- Priority calculation based on due date
  CASE 
    WHEN a.due_date <= NOW() + INTERVAL '1 day' THEN 'high'
    WHEN a.due_date <= NOW() + INTERVAL '3 days' THEN 'medium'
    ELSE 'low'
  END as priority,
  
  -- Time until due
  EXTRACT(EPOCH FROM (a.due_date - NOW())) / 3600 as hours_until_due

FROM assignments a
JOIN courses c ON a.course_id = c.id
LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'active'
LEFT JOIN assignment_submissions asub ON a.id = asub.assignment_id AND asub.student_id = e.student_id

WHERE a.teacher_id = $1 
  AND a.due_date > NOW()
  AND a.due_date <= NOW() + INTERVAL '7 days'

GROUP BY a.id, a.title, c.title, a.due_date, a.description

UNION ALL

-- Upcoming Quizzes
SELECT 
  'quiz' as type,
  q.id,
  q.title,
  c.title as course_name,
  q.due_date,
  q.description,
  
  -- Submission statistics
  COUNT(DISTINCT e.student_id) as total_students,
  COUNT(DISTINCT qs.student_id) as submitted_count,
  ROUND(
    (COUNT(DISTINCT qs.student_id)::float / NULLIF(COUNT(DISTINCT e.student_id), 0)) * 100, 
    1
  ) as submission_percentage,
  
  -- Priority calculation
  CASE 
    WHEN q.due_date <= NOW() + INTERVAL '1 day' THEN 'high'
    WHEN q.due_date <= NOW() + INTERVAL '3 days' THEN 'medium'
    ELSE 'low'
  END as priority,
  
  -- Time until due
  EXTRACT(EPOCH FROM (q.due_date - NOW())) / 3600 as hours_until_due

FROM quizzes q
JOIN courses c ON q.course_id = c.id
LEFT JOIN enrollments e ON c.id = e.course_id AND e.status = 'active'
LEFT JOIN quiz_submissions qs ON q.id = qs.quiz_id AND qs.student_id = e.student_id

WHERE q.teacher_id = $1 
  AND q.due_date > NOW()
  AND q.due_date <= NOW() + INTERVAL '7 days'

GROUP BY q.id, q.title, c.title, q.due_date, q.description

ORDER BY due_date ASC
LIMIT 10;

-- =====================================================
-- 4. RECENT STUDENT ACTIVITY
-- =====================================================
-- Tracks recent student submissions and activities
-- Used for: Activity feed in teacher dashboard

-- Recent Assignment Submissions
SELECT 
  'assignment_submission' as activity_type,
  asub.id as activity_id,
  p.full_name as student_name,
  a.title as item_title,
  c.title as course_name,
  asub.submitted_at as activity_time,
  asub.score,
  CASE 
    WHEN asub.submitted_at > a.due_date THEN 'late'
    ELSE 'on_time'
  END as submission_status,
  'Assignment submitted' as activity_description

FROM assignment_submissions asub
JOIN assignments a ON asub.assignment_id = a.id
JOIN courses c ON a.course_id = c.id
JOIN profiles p ON asub.student_id = p.id

WHERE a.teacher_id = $1 
  AND asub.submitted_at >= NOW() - INTERVAL '7 days'

UNION ALL

-- Recent Quiz Completions
SELECT 
  'quiz_completion' as activity_type,
  qs.id as activity_id,
  p.full_name as student_name,
  q.title as item_title,
  c.title as course_name,
  qs.created_at as activity_time,
  qs.score,
  CASE 
    WHEN qs.created_at > q.due_date THEN 'late'
    ELSE 'on_time'
  END as submission_status,
  CONCAT('Quiz completed with ', qs.score, '% score') as activity_description

FROM quiz_submissions qs
JOIN quizzes q ON qs.quiz_id = q.id
JOIN courses c ON q.course_id = c.id
JOIN profiles p ON qs.student_id = p.id

WHERE q.teacher_id = $1 
  AND qs.created_at >= NOW() - INTERVAL '7 days'

ORDER BY activity_time DESC
LIMIT 20;

-- =====================================================
-- 5. PERFORMANCE OPTIMIZATION INDEXES
-- =====================================================
-- Recommended indexes for optimal query performance

-- Index for teacher-specific queries
CREATE INDEX IF NOT EXISTS idx_assignments_teacher_due_date 
ON assignments(teacher_id, due_date) 
WHERE due_date > NOW();

CREATE INDEX IF NOT EXISTS idx_quizzes_teacher_due_date 
ON quizzes(teacher_id, due_date) 
WHERE due_date > NOW();

-- Index for submission queries
CREATE INDEX IF NOT EXISTS idx_assignment_submissions_created_at 
ON assignment_submissions(assignment_id, submitted_at, student_id);

CREATE INDEX IF NOT EXISTS idx_quiz_submissions_created_at 
ON quiz_submissions(quiz_id, created_at, student_id);

-- Index for enrollment queries
CREATE INDEX IF NOT EXISTS idx_enrollments_course_status 
ON enrollments(course_id, status, student_id) 
WHERE status = 'active';

-- Composite index for performance queries
CREATE INDEX IF NOT EXISTS idx_performance_analysis 
ON quiz_submissions(quiz_id, student_id, score, created_at);

-- =====================================================
-- 6. MAINTENANCE QUERIES
-- =====================================================
-- Queries for database maintenance and cleanup

-- Clean up old performance data (older than 1 year)
DELETE FROM quiz_submissions 
WHERE created_at < NOW() - INTERVAL '1 year'
  AND id NOT IN (
    SELECT DISTINCT qs.id 
    FROM quiz_submissions qs
    JOIN quizzes q ON qs.quiz_id = q.id
    WHERE q.is_archived = false
  );

-- Update statistics for better query planning
ANALYZE assignments;
ANALYZE quizzes;
ANALYZE assignment_submissions;
ANALYZE quiz_submissions;
ANALYZE enrollments;
ANALYZE courses;

-- =====================================================
-- 7. MONITORING QUERIES
-- =====================================================
-- Queries for monitoring system performance

-- Check query performance
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  rows
FROM pg_stat_statements 
WHERE query LIKE '%teacher_id%'
ORDER BY total_time DESC
LIMIT 10;

-- Monitor table sizes
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats 
WHERE tablename IN ('assignments', 'quizzes', 'assignment_submissions', 'quiz_submissions')
ORDER BY tablename, attname;
