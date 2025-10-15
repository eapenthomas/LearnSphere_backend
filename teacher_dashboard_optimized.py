"""
Optimized Teacher Dashboard API
Provides all dashboard data in a single efficient query
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta
from auth_middleware import get_current_user
from auth import supabase

router = APIRouter(prefix="/api/teacher/dashboard", tags=["Teacher Dashboard"])


@router.get("/stats/{teacher_id}")
async def get_optimized_teacher_stats(teacher_id: str):
    """
    Get all teacher dashboard statistics in a single optimized call
    Returns: courses, students, assignments, recent activity, and analytics
    """
    try:
        print(f"📊 Fetching optimized dashboard stats for teacher: {teacher_id}")
        
        # Fetch all courses for this teacher
        courses_response = supabase.table('courses')\
            .select('*')\
            .eq('teacher_id', teacher_id)\
            .eq('status', 'active')\
            .order('created_at', desc=True)\
            .execute()
        
        courses = courses_response.data if courses_response.data else []
        course_ids = [course['id'] for course in courses]
        
        # Fetch enrollments for all courses in one query
        enrollments_data = {}
        total_students_set = set()
        
        if course_ids:
            enrollments_response = supabase.table('enrollments')\
                .select('course_id, student_id')\
                .in_('course_id', course_ids)\
                .execute()
            
            enrollments = enrollments_response.data if enrollments_response.data else []
            
            # Count enrollments per course and track unique students
            for enrollment in enrollments:
                course_id = enrollment['course_id']
                student_id = enrollment['student_id']
                total_students_set.add(student_id)
                
                if course_id not in enrollments_data:
                    enrollments_data[course_id] = 0
                enrollments_data[course_id] += 1
        
        # Add enrollment count to courses
        for course in courses:
            course['enrollment_count'] = enrollments_data.get(course['id'], 0)
        
        # Get total assignments
        assignments_response = supabase.table('assignments')\
            .select('id', count='exact')\
            .eq('teacher_id', teacher_id)\
            .execute()
        
        total_assignments = assignments_response.count if assignments_response.count else 0
        
        # Get pending assignment submissions
        if total_assignments > 0:
            # Get all assignments by this teacher
            teacher_assignments_response = supabase.table('assignments')\
                .select('id')\
                .eq('teacher_id', teacher_id)\
                .execute()
            
            assignment_ids = [a['id'] for a in teacher_assignments_response.data] if teacher_assignments_response.data else []
            
            if assignment_ids:
                pending_submissions_response = supabase.table('assignment_submissions')\
                    .select('id', count='exact')\
                    .in_('assignment_id', assignment_ids)\
                    .neq('status', 'graded')\
                    .execute()
                
                pending_submissions = pending_submissions_response.count if pending_submissions_response.count else 0
            else:
                pending_submissions = 0
        else:
            pending_submissions = 0
        
        # Get total quizzes
        quizzes_response = supabase.table('quizzes')\
            .select('id', count='exact')\
            .eq('teacher_id', teacher_id)\
            .execute()
        
        total_quizzes = quizzes_response.count if quizzes_response.count else 0
        
        # Get quiz submissions for average score
        quiz_submissions_response = supabase.table('quiz_submissions')\
            .select('score, total_marks')\
            .in_('quiz_id', [q['id'] for q in quizzes_response.data] if quizzes_response.data else [])\
            .execute()
        
        quiz_submissions = quiz_submissions_response.data if quiz_submissions_response.data else []
        
        if quiz_submissions:
            total_score = sum((sub['score'] / sub['total_marks'] * 100) for sub in quiz_submissions if sub['total_marks'] > 0)
            avg_quiz_score = total_score / len(quiz_submissions)
        else:
            avg_quiz_score = 0
        
        # Get recent enrollments for activity
        recent_enrollments_response = supabase.table('enrollments')\
            .select('student_id, course_id, enrolled_at')\
            .in_('course_id', course_ids)\
            .order('enrolled_at', desc=True)\
            .limit(10)\
            .execute()
        
        recent_enrollments = recent_enrollments_response.data if recent_enrollments_response.data else []
        
        # Get enrollment trends for the last 7 days (for charts)
        enrollment_trends = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            start_of_day = datetime.combine(date, datetime.min.time())
            end_of_day = datetime.combine(date, datetime.max.time())
            
            daily_enrollments_response = supabase.table('enrollments')\
                .select('id', count='exact')\
                .in_('course_id', course_ids)\
                .gte('enrolled_at', start_of_day.isoformat())\
                .lte('enrolled_at', end_of_day.isoformat())\
                .execute()
            
            count = daily_enrollments_response.count if daily_enrollments_response.count else 0
            enrollment_trends.append({
                'date': date.strftime('%b %d'),
                'enrollments': count
            })
        
        # Get course performance data (completion rates)
        course_performance = []
        for course in courses[:5]:  # Top 5 courses
            course_id = course['id']
            
            # Get total enrollments for this course
            total_enrollments_response = supabase.table('enrollments')\
                .select('id', count='exact')\
                .eq('course_id', course_id)\
                .execute()
            
            total_enrollments = total_enrollments_response.count if total_enrollments_response.count else 0
            
            # Get completion data (students who completed the course - 100% completion)
            completed_response = supabase.table('course_completions')\
                .select('id', count='exact')\
                .eq('course_id', course_id)\
                .eq('completion_percentage', 100)\
                .execute()
            
            completed_count = completed_response.count if completed_response.count else 0
            completion_rate = round((completed_count / total_enrollments * 100) if total_enrollments > 0 else 0, 1)
            
            course_performance.append({
                'course_id': course_id,
                'course_title': course['title'][:20] + '...' if len(course['title']) > 20 else course['title'],
                'enrollment_count': total_enrollments,
                'completion_rate': completion_rate
            })
        
        # Build response
        response = {
            'success': True,
            'data': {
                'stats': {
                    'total_courses': len(courses),
                    'total_students': len(total_students_set),
                    'total_assignments': total_assignments,
                    'total_quizzes': total_quizzes,
                    'pending_submissions': pending_submissions,
                    'avg_quiz_score': round(avg_quiz_score, 1)
                },
                'courses': courses[:5],  # Top 5 recent courses
                'recent_activity': recent_enrollments,
                'enrollment_trends': enrollment_trends,
                'course_performance': course_performance
            },
            'cached': False,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Dashboard stats fetched successfully")
        return response
        
    except Exception as e:
        print(f"❌ Error fetching optimized dashboard stats: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@router.get("/pending-work/{teacher_id}")
async def get_pending_work(teacher_id: str):
    """
    Get pending assignments and quiz submissions that need grading
    """
    try:
        # Get all assignments by this teacher
        assignments_response = supabase.table('assignments')\
            .select('id, title, course_id, due_date')\
            .eq('teacher_id', teacher_id)\
            .order('due_date')\
            .limit(10)\
            .execute()
        
        assignments = assignments_response.data if assignments_response.data else []
        pending_work = []
        
        for assignment in assignments:
            # Get pending submissions for this assignment
            submissions_response = supabase.table('assignment_submissions')\
                .select('id', count='exact')\
                .eq('assignment_id', assignment['id'])\
                .neq('status', 'graded')\
                .execute()
            
            pending_count = submissions_response.count if submissions_response.count else 0
            
            if pending_count > 0:
                # Get course info
                course_response = supabase.table('courses')\
                    .select('title')\
                    .eq('id', assignment['course_id'])\
                    .single()\
                    .execute()
                
                course_title = course_response.data['title'] if course_response.data else 'Unknown Course'
                
                pending_work.append({
                    'assignment_id': assignment['id'],
                    'assignment_title': assignment['title'],
                    'course_title': course_title,
                    'pending_count': pending_count,
                    'due_date': assignment['due_date']
                })
        
        return {
            'success': True,
            'data': {
                'pending_assignments': pending_work,
                'total_pending': sum(item['pending_count'] for item in pending_work)
            }
        }
        
    except Exception as e:
        print(f"❌ Error fetching pending work: {e}")
        raise HTTPException(status_code=500, detail=str(e))

