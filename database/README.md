# 🗄️ LearnSphere Database Documentation

## Overview

This directory contains all database-related files for the LearnSphere Learning Management System, including schema definitions, SQL scripts, and database documentation.

## Recent Updates

### 🆕 December 2024 Updates (Latest)

- **Voice Navigation Logging**: Added `voice_navigation_logs` table for debugging voice commands
- **Deadline Debugging**: Enhanced deadline tables with debugging columns and visibility tracking
- **Profile Picture Metadata**: Added `profile_picture_metadata` table for better file management
- **Performance Monitoring**: Added `system_performance_logs` for API performance tracking
- **Sample Data**: Added sample assignments and quizzes for testing deadline visibility
- **Enhanced Queries**: New `get_urgent_deadlines_debug()` function with comprehensive debugging
- **Performance Indexes**: Added indexes for better deadline and voice navigation query performance

### Teacher Analytics System

- Added comprehensive analytics queries for teacher dashboard
- Implemented performance tracking over 6-week periods
- Created course-wise performance aggregation queries
- Added upcoming deadlines and recent activity monitoring
- Optimized database queries for real-time analytics

### Enrollment System Enhancement

- Updated enrollment status constraints to support 'dropped' status
- Fixed unenrollment functionality with proper status handling
- Enhanced error handling for enrollment operations

### Storage Upload Fix

- Resolved Supabase storage upload compatibility issues
- Updated error handling for newer client versions
- Improved file upload reliability

## File Structure

```
database/
├── README.md                           # This documentation file
├── enrollment_schema.sql               # Enrollment system schema
├── supabase_storage_fix.sql           # Storage upload fix documentation
└── analytics_queries.sql              # Teacher analytics queries (new)
```

## Core Database Tables

### User Management

- **profiles**: User profiles with role-based access control
- **teacher_approval_requests**: Teacher registration approval workflow

### Course Management

- **courses**: Course information and metadata
- **enrollments**: Student-course enrollment relationships
- **course_materials**: Course files and resources

### Assessment System

- **assignments**: Assignment definitions and metadata
- **assignment_submissions**: Student assignment submissions
- **quizzes**: Quiz definitions and questions
- **quiz_submissions**: Student quiz attempts and scores

### Analytics & Tracking

- **performance_data**: Student performance metrics over time
- **activity_logs**: User activity tracking for analytics

## Key Features

### 🔐 Row Level Security (RLS)

All tables implement comprehensive RLS policies to ensure data security:

- Students can only access their own data
- Teachers can access data for their courses
- Admins have full access with proper authentication

### 📊 Analytics Optimization

- Indexed columns for performance queries
- Optimized joins for real-time analytics
- Efficient aggregation queries for dashboard data

### 🔄 Real-time Updates

- Supabase real-time subscriptions for live data
- Optimized queries for minimal latency
- Efficient change tracking and notifications

## Database Schema Highlights

### Enrollment System

```sql
-- Supports multiple enrollment statuses
CHECK (status IN ('active', 'completed', 'dropped', 'suspended'))

-- Prevents duplicate enrollments
UNIQUE(student_id, course_id)
```

### Performance Tracking

```sql
-- Weekly performance aggregation
SELECT
  DATE_TRUNC('week', created_at) as week,
  AVG(score) as average_score,
  COUNT(*) as total_submissions
FROM quiz_submissions
WHERE teacher_id = $1
GROUP BY week
ORDER BY week DESC
LIMIT 6;
```

### Course Analytics

```sql
-- Course performance with enrollment data
SELECT
  c.title as course,
  COUNT(DISTINCT e.student_id) as students,
  AVG(qs.score) as avg_score
FROM courses c
LEFT JOIN enrollments e ON c.id = e.course_id
LEFT JOIN quiz_submissions qs ON c.id = qs.course_id
WHERE c.teacher_id = $1 AND e.status = 'active'
GROUP BY c.id, c.title;
```

## Performance Optimizations

### Indexes

- **Composite indexes** on frequently queried column combinations
- **Partial indexes** for filtered queries (e.g., active enrollments)
- **Expression indexes** for computed values and aggregations

### Query Optimization

- **Efficient joins** to minimize data transfer
- **Aggregation pushdown** for better performance
- **Query result caching** for frequently accessed data

## Maintenance Guidelines

### Regular Tasks

1. **Index Maintenance**: Monitor and rebuild indexes as needed
2. **Statistics Updates**: Keep table statistics current for optimal query plans
3. **Data Cleanup**: Archive old submissions and activity logs
4. **Performance Monitoring**: Track slow queries and optimize

### Backup Strategy

1. **Daily Backups**: Automated daily database backups
2. **Point-in-time Recovery**: Continuous WAL archiving
3. **Cross-region Replication**: Geographic backup distribution
4. **Backup Testing**: Regular restore testing procedures

## Security Considerations

### Data Protection

- **Encryption at Rest**: All data encrypted in storage
- **Encryption in Transit**: TLS for all database connections
- **Access Control**: Role-based access with minimal privileges
- **Audit Logging**: Comprehensive audit trail for all operations

### Privacy Compliance

- **Data Anonymization**: Personal data protection measures
- **GDPR Compliance**: Right to deletion and data portability
- **Access Logging**: Track all data access for compliance
- **Data Retention**: Automated cleanup of expired data

## Troubleshooting

### Common Issues

#### Slow Query Performance

1. Check query execution plans
2. Verify index usage
3. Update table statistics
4. Consider query rewriting

#### Connection Issues

1. Verify connection string
2. Check firewall settings
3. Monitor connection pool usage
4. Review authentication settings

#### Data Consistency

1. Check foreign key constraints
2. Verify RLS policy enforcement
3. Monitor replication lag
4. Review transaction isolation levels

### Monitoring Tools

- **Query Performance**: Built-in Supabase analytics
- **Connection Monitoring**: Real-time connection tracking
- **Error Logging**: Comprehensive error reporting
- **Performance Metrics**: Database performance dashboards

## Development Guidelines

### Schema Changes

1. **Migration Scripts**: Always use versioned migration scripts
2. **Backward Compatibility**: Ensure changes don't break existing code
3. **Testing**: Test all schema changes in staging environment
4. **Documentation**: Update documentation with all changes

### Query Best Practices

1. **Use Prepared Statements**: Prevent SQL injection attacks
2. **Limit Result Sets**: Always use appropriate LIMIT clauses
3. **Optimize Joins**: Use efficient join strategies
4. **Index Usage**: Ensure queries use appropriate indexes

## Related Documentation

- [API Documentation](../docs/API_DOCUMENTATION.md)
- [Teacher Analytics System](../docs/TEACHER_ANALYTICS_SYSTEM.md)
- [Security Guide](../docs/SECURITY_GUIDE.md)
- [Performance Optimization](../docs/PERFORMANCE_GUIDE.md)

## Support

For database-related issues or questions:

1. Check this documentation first
2. Review the troubleshooting section
3. Consult the related documentation
4. Contact the development team with specific details
