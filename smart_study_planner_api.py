"""
Smart Study Planner API
AI-powered study planning and recommendation system
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/study-planner", tags=["study-planner"])

class StudySession(BaseModel):
    id: Optional[str] = None
    student_id: str
    course_id: str
    topic: str
    planned_duration: int  # minutes
    actual_duration: Optional[int] = None
    completion_status: str = "planned"  # planned, in_progress, completed, skipped
    scheduled_date: datetime
    difficulty_level: str = "medium"  # easy, medium, hard
    study_type: str = "review"  # review, practice, new_material, exam_prep
    ai_recommendations: Optional[Dict] = None
    created_at: Optional[datetime] = None

class StudyPlan(BaseModel):
    student_id: str
    course_id: str
    target_date: datetime
    study_goal: str
    weekly_hours: int
    preferred_session_duration: int
    difficulty_preference: str = "adaptive"

class StudyAnalytics(BaseModel):
    total_study_time: int
    sessions_completed: int
    average_session_duration: int
    completion_rate: float
    productivity_score: float
    weekly_progress: List[Dict]
    subject_breakdown: List[Dict]
    recommendations: List[str]

@router.post("/create-plan")
async def create_study_plan(plan: StudyPlan):
    """Create an AI-powered personalized study plan"""
    try:
        # Get student's course progress and performance data
        enrollments = supabase.table('enrollments').select('*').eq('student_id', plan.student_id).eq('course_id', plan.course_id).execute()
        
        if not enrollments.data:
            raise HTTPException(status_code=404, detail="Student not enrolled in this course")
        
        # Get course materials and assignments
        course_materials = supabase.table('course_materials').select('*').eq('course_id', plan.course_id).execute()
        assignments = supabase.table('assignments').select('*').eq('course_id', plan.course_id).execute()
        
        # Generate AI-powered study schedule
        study_schedule = await generate_smart_schedule(
            plan, 
            course_materials.data or [], 
            assignments.data or []
        )
        
        # Save study plan
        plan_data = {
            "student_id": plan.student_id,
            "course_id": plan.course_id,
            "target_date": plan.target_date.isoformat(),
            "study_goal": plan.study_goal,
            "weekly_hours": plan.weekly_hours,
            "preferred_session_duration": plan.preferred_session_duration,
            "difficulty_preference": plan.difficulty_preference,
            "schedule_data": json.dumps(study_schedule),
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table('study_plans').insert(plan_data).execute()
        
        return {
            "success": True,
            "plan_id": result.data[0]['id'],
            "schedule": study_schedule,
            "message": "Smart study plan created successfully"
        }
        
    except Exception as e:
        print(f"Error creating study plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_smart_schedule(plan: StudyPlan, materials: List[Dict], assignments: List[Dict]) -> List[Dict]:
    """Generate AI-powered study schedule based on student data and course content"""
    
    schedule = []
    current_date = datetime.now()
    target_date = plan.target_date
    days_available = (target_date - current_date).days
    
    # Calculate total content to cover
    total_materials = len(materials)
    total_assignments = len(assignments)
    
    # Distribute study sessions across available days
    sessions_per_week = plan.weekly_hours * 60 // plan.preferred_session_duration
    total_sessions = (days_available // 7) * sessions_per_week
    
    # Prioritize content based on deadlines and difficulty
    prioritized_content = []
    
    # Add assignments with deadlines
    for assignment in assignments:
        if assignment.get('due_date'):
            due_date = datetime.fromisoformat(assignment['due_date'].replace('Z', '+00:00'))
            days_until_due = (due_date - current_date).days
            priority = max(1, 10 - days_until_due)  # Higher priority for closer deadlines
            
            prioritized_content.append({
                'type': 'assignment',
                'title': assignment['title'],
                'priority': priority,
                'estimated_hours': 2,  # Default 2 hours per assignment
                'due_date': due_date,
                'difficulty': 'medium'
            })
    
    # Add course materials
    for material in materials:
        prioritized_content.append({
            'type': 'material',
            'title': material['title'],
            'priority': 5,  # Medium priority
            'estimated_hours': 1,  # Default 1 hour per material
            'difficulty': 'easy'
        })
    
    # Sort by priority
    prioritized_content.sort(key=lambda x: x['priority'], reverse=True)
    
    # Generate study sessions
    session_date = current_date + timedelta(days=1)
    content_index = 0
    
    for week in range(days_available // 7 + 1):
        for session in range(min(sessions_per_week, len(prioritized_content) - content_index)):
            if content_index >= len(prioritized_content):
                break
                
            content = prioritized_content[content_index]
            
            # AI recommendations based on content type and student preferences
            ai_recommendations = {
                'study_techniques': get_study_techniques(content['type'], content['difficulty']),
                'break_intervals': get_break_recommendations(plan.preferred_session_duration),
                'focus_areas': get_focus_areas(content),
                'resources': get_recommended_resources(content['type'])
            }
            
            schedule.append({
                'date': session_date.isoformat(),
                'topic': content['title'],
                'type': content['type'],
                'duration': plan.preferred_session_duration,
                'difficulty': content['difficulty'],
                'ai_recommendations': ai_recommendations,
                'priority': content['priority']
            })
            
            content_index += 1
            session_date += timedelta(days=1)
            
            # Skip weekends if preferred
            if session_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                session_date += timedelta(days=2)
    
    return schedule

def get_study_techniques(content_type: str, difficulty: str) -> List[str]:
    """Get AI-recommended study techniques"""
    techniques = {
        'assignment': [
            'Break down into smaller tasks',
            'Create a timeline with milestones',
            'Practice similar problems first',
            'Review relevant course materials'
        ],
        'material': [
            'Active reading with note-taking',
            'Summarize key concepts',
            'Create mind maps',
            'Use spaced repetition'
        ]
    }
    
    if difficulty == 'hard':
        techniques[content_type].extend([
            'Seek help from instructor',
            'Form study groups',
            'Use additional resources'
        ])
    
    return techniques.get(content_type, ['Review and practice'])

def get_break_recommendations(session_duration: int) -> Dict:
    """Get AI-recommended break intervals"""
    if session_duration <= 30:
        return {'breaks': 1, 'duration': 5, 'technique': 'Pomodoro (25min work, 5min break)'}
    elif session_duration <= 60:
        return {'breaks': 2, 'duration': 10, 'technique': 'Two 10-minute breaks'}
    else:
        return {'breaks': 3, 'duration': 15, 'technique': 'Three 15-minute breaks'}

def get_focus_areas(content: Dict) -> List[str]:
    """Get AI-recommended focus areas"""
    if content['type'] == 'assignment':
        return [
            'Understanding requirements',
            'Planning approach',
            'Implementation/execution',
            'Review and refinement'
        ]
    else:
        return [
            'Key concepts identification',
            'Practical applications',
            'Connection to previous topics',
            'Self-assessment'
        ]

def get_recommended_resources(content_type: str) -> List[str]:
    """Get AI-recommended study resources"""
    resources = {
        'assignment': [
            'Course lecture notes',
            'Practice problems',
            'Online tutorials',
            'Study group discussions'
        ],
        'material': [
            'Course textbook',
            'Supplementary readings',
            'Video lectures',
            'Interactive exercises'
        ]
    }
    return resources.get(content_type, ['Course materials'])

@router.get("/student/{student_id}/plans")
async def get_student_plans(student_id: str):
    """Get all study plans for a student"""
    try:
        plans = supabase.table('study_plans').select('*').eq('student_id', student_id).execute()
        
        plans_with_courses = []
        for plan in plans.data or []:
            # Get course details
            course = supabase.table('courses').select('title, teacher_id').eq('id', plan['course_id']).single().execute()
            
            plan_data = {
                **plan,
                'course_title': course.data['title'] if course.data else 'Unknown Course',
                'schedule': json.loads(plan['schedule_data']) if plan['schedule_data'] else []
            }
            plans_with_courses.append(plan_data)
        
        return {"success": True, "plans": plans_with_courses}
        
    except Exception as e:
        print(f"Error fetching study plans: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/start")
async def start_study_session(session: StudySession):
    """Start a study session and track progress"""
    try:
        session_data = {
            "student_id": session.student_id,
            "course_id": session.course_id,
            "topic": session.topic,
            "planned_duration": session.planned_duration,
            "completion_status": "in_progress",
            "scheduled_date": session.scheduled_date.isoformat(),
            "difficulty_level": session.difficulty_level,
            "study_type": session.study_type,
            "ai_recommendations": json.dumps(session.ai_recommendations) if session.ai_recommendations else None,
            "started_at": datetime.now().isoformat()
        }
        
        result = supabase.table('study_sessions').insert(session_data).execute()
        
        return {
            "success": True,
            "session_id": result.data[0]['id'],
            "message": "Study session started"
        }
        
    except Exception as e:
        print(f"Error starting study session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/session/{session_id}/complete")
async def complete_study_session(session_id: str, actual_duration: int, effectiveness_rating: int):
    """Complete a study session and update analytics"""
    try:
        update_data = {
            "completion_status": "completed",
            "actual_duration": actual_duration,
            "effectiveness_rating": effectiveness_rating,
            "completed_at": datetime.now().isoformat()
        }
        
        result = supabase.table('study_sessions').update(update_data).eq('id', session_id).execute()
        
        return {
            "success": True,
            "message": "Study session completed successfully"
        }
        
    except Exception as e:
        print(f"Error completing study session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{student_id}")
async def get_study_analytics(student_id: str, days: int = 30):
    """Get comprehensive study analytics for a student"""
    try:
        # Get study sessions from the last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions = supabase.table('study_sessions').select('*').eq('student_id', student_id).gte('created_at', cutoff_date.isoformat()).execute()
        
        if not sessions.data:
            return {
                "success": True,
                "analytics": {
                    "total_study_time": 0,
                    "sessions_completed": 0,
                    "average_session_duration": 0,
                    "completion_rate": 0,
                    "productivity_score": 0,
                    "weekly_progress": [],
                    "subject_breakdown": [],
                    "recommendations": ["Start your first study session to see analytics!"]
                }
            }
        
        # Calculate analytics
        completed_sessions = [s for s in sessions.data if s['completion_status'] == 'completed']
        total_study_time = sum(s['actual_duration'] or 0 for s in completed_sessions)
        sessions_completed = len(completed_sessions)
        total_sessions = len(sessions.data)
        
        avg_duration = total_study_time / max(sessions_completed, 1)
        completion_rate = (sessions_completed / max(total_sessions, 1)) * 100
        
        # Calculate productivity score based on effectiveness ratings
        effectiveness_ratings = [s.get('effectiveness_rating', 3) for s in completed_sessions if s.get('effectiveness_rating')]
        productivity_score = (sum(effectiveness_ratings) / max(len(effectiveness_ratings), 1)) * 20  # Scale to 100
        
        # Generate weekly progress
        weekly_progress = generate_weekly_progress(sessions.data, days)
        
        # Generate subject breakdown
        subject_breakdown = generate_subject_breakdown(sessions.data)
        
        # Generate AI recommendations
        recommendations = generate_study_recommendations(sessions.data, completion_rate, productivity_score)
        
        analytics = StudyAnalytics(
            total_study_time=total_study_time,
            sessions_completed=sessions_completed,
            average_session_duration=int(avg_duration),
            completion_rate=round(completion_rate, 1),
            productivity_score=round(productivity_score, 1),
            weekly_progress=weekly_progress,
            subject_breakdown=subject_breakdown,
            recommendations=recommendations
        )
        
        return {"success": True, "analytics": analytics.dict()}
        
    except Exception as e:
        print(f"Error fetching study analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_weekly_progress(sessions: List[Dict], days: int) -> List[Dict]:
    """Generate weekly progress data"""
    weeks = days // 7
    progress = []
    
    for week in range(weeks):
        week_start = datetime.now() - timedelta(days=(weeks - week) * 7)
        week_end = week_start + timedelta(days=7)
        
        week_sessions = [
            s for s in sessions 
            if week_start <= datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')) < week_end
        ]
        
        completed = len([s for s in week_sessions if s['completion_status'] == 'completed'])
        total_time = sum(s['actual_duration'] or 0 for s in week_sessions if s['completion_status'] == 'completed')
        
        progress.append({
            'week': f"Week {week + 1}",
            'sessions': len(week_sessions),
            'completed': completed,
            'total_time': total_time
        })
    
    return progress

def generate_subject_breakdown(sessions: List[Dict]) -> List[Dict]:
    """Generate subject/course breakdown"""
    course_stats = {}
    
    for session in sessions:
        course_id = session['course_id']
        if course_id not in course_stats:
            course_stats[course_id] = {
                'course_id': course_id,
                'sessions': 0,
                'total_time': 0,
                'completed': 0
            }
        
        course_stats[course_id]['sessions'] += 1
        if session['completion_status'] == 'completed':
            course_stats[course_id]['completed'] += 1
            course_stats[course_id]['total_time'] += session['actual_duration'] or 0
    
    # Get course names
    breakdown = []
    for course_id, stats in course_stats.items():
        try:
            course = supabase.table('courses').select('title').eq('id', course_id).single().execute()
            stats['course_name'] = course.data['title'] if course.data else 'Unknown Course'
        except:
            stats['course_name'] = 'Unknown Course'
        
        breakdown.append(stats)
    
    return breakdown

def generate_study_recommendations(sessions: List[Dict], completion_rate: float, productivity_score: float) -> List[str]:
    """Generate AI-powered study recommendations"""
    recommendations = []
    
    if completion_rate < 50:
        recommendations.append("Try shorter study sessions to improve completion rate")
        recommendations.append("Set realistic daily study goals")
    
    if productivity_score < 60:
        recommendations.append("Consider changing your study environment")
        recommendations.append("Try different study techniques like Pomodoro method")
    
    if len(sessions) < 7:
        recommendations.append("Establish a consistent daily study routine")
    
    # Analyze study patterns
    study_times = [datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).hour for s in sessions]
    if study_times:
        peak_hour = max(set(study_times), key=study_times.count)
        recommendations.append(f"Your most productive time appears to be around {peak_hour}:00")
    
    if not recommendations:
        recommendations = [
            "Great job! Keep maintaining your study consistency",
            "Consider gradually increasing session duration",
            "Try exploring new study techniques to stay engaged"
        ]
    
    return recommendations[:5]  # Limit to 5 recommendations
