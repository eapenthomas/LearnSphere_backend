from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from auth_middleware import get_current_user

load_dotenv()

# Initialize Supabase client with service role key to bypass RLS
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/forum", tags=["forum"])

# Pydantic models
class CreateQuestionRequest(BaseModel):
    title: str
    content: str
    course_id: Optional[str] = None
    tags: Optional[List[str]] = []

class CreateAnswerRequest(BaseModel):
    question_id: str
    content: str

class ForumQuestion(BaseModel):
    id: str
    title: str
    content: str
    course_id: Optional[str]
    course_name: Optional[str]
    student_id: str
    student_name: str
    tags: List[str]
    answer_count: int
    is_resolved: bool
    created_at: datetime
    updated_at: datetime

class ForumAnswer(BaseModel):
    id: str
    question_id: str
    content: str
    teacher_id: str
    teacher_name: str
    is_accepted: bool
    created_at: datetime
    updated_at: datetime

class QuestionWithAnswers(BaseModel):
    question: ForumQuestion
    answers: List[ForumAnswer]

# Create forum tables if they don't exist
async def create_forum_tables():
    """Create forum tables in Supabase"""
    try:
        # Create forum_questions table
        supabase.table('forum_questions').select('id').limit(1).execute()
    except:
        # Table doesn't exist, create it
        print("Creating forum tables...")
        # Note: In production, these should be created via Supabase dashboard or migration scripts

@router.on_event("startup")
async def startup_event():
    await create_forum_tables()

@router.post("/questions", response_model=dict)
async def create_question(request: CreateQuestionRequest, student_id: str = Query(...)):
    """Create a new forum question"""
    try:
        # Check if forum tables exist
        try:
            test_query = supabase.table('forum_questions').select('id').limit(1).execute()
        except Exception as table_error:
            if 'does not exist' in str(table_error):
                raise HTTPException(status_code=503, detail="Forum system is not yet set up. Please contact administrator to create forum tables.")
            else:
                raise table_error

        # Get student info
        student_response = supabase.table('profiles').select('full_name').eq('id', student_id).single().execute()
        if not student_response.data:
            raise HTTPException(status_code=404, detail="Student not found")

        # Get course info if course_id is provided
        course_name = None
        if request.course_id:
            course_response = supabase.table('courses').select('title').eq('id', request.course_id).single().execute()
            if course_response.data:
                course_name = course_response.data['title']

        # Create question
        question_data = {
            'title': request.title,
            'content': request.content,
            'course_id': request.course_id,
            'student_id': student_id,
            'tags': request.tags,
            'is_resolved': False,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

        # Use service role to bypass RLS for forum operations
        response = supabase.table('forum_questions').insert(question_data).execute()

        return {
            "success": True,
            "message": "Question posted successfully",
            "data": response.data[0]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating question: {e}")
        if 'does not exist' in str(e) or 'relation' in str(e):
            raise HTTPException(status_code=503, detail="Forum system is not yet set up. Please contact administrator to create forum tables.")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions", response_model=List[ForumQuestion])
async def get_questions(
    course_id: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get forum questions with filters and role-based access control"""
    try:
        # Check if forum tables exist
        try:
            test_query = supabase.table('forum_questions').select('id').limit(1).execute()
        except Exception as table_error:
            if 'does not exist' in str(table_error):
                # Return empty list if tables don't exist yet
                return []
            else:
                raise table_error

        query = supabase.table('forum_questions').select('*')

        # Apply role-based access control
        user_role = current_user.role
        user_id = current_user.user_id
        
        if user_role == 'teacher':
            # Teachers can only see questions from their own courses
            teacher_courses_response = supabase.table('courses').select('id').eq('teacher_id', user_id).execute()
            teacher_course_ids = [course['id'] for course in teacher_courses_response.data]
            
            if not teacher_course_ids:
                # Teacher has no courses, return empty list
                return []
            
            # Filter questions by teacher's courses
            query = query.in_('course_id', teacher_course_ids)
        elif user_role == 'student':
            # Students can see questions from courses they're enrolled in
            student_enrollments_response = supabase.table('enrollments').select('course_id').eq('student_id', user_id).eq('status', 'active').execute()
            student_course_ids = [enrollment['course_id'] for enrollment in student_enrollments_response.data]
            
            if not student_course_ids:
                # Student is not enrolled in any courses, return empty list
                return []
            
            # Filter questions by student's enrolled courses
            query = query.in_('course_id', student_course_ids)
        
        # Apply additional filters
        if course_id:
            query = query.eq('course_id', course_id)
        if student_id:
            query = query.eq('student_id', student_id)
        if resolved is not None:
            query = query.eq('is_resolved', resolved)

        # Apply pagination and ordering
        query = query.order('created_at', desc=True).range(offset, offset + limit - 1)

        response = query.execute()

        # Get answer counts for each question
        questions = []
        for question in response.data:
            # Count answers for this question
            try:
                answer_count_response = supabase.table('forum_answers').select('id').eq('question_id', question['id']).execute()
                answer_count = len(answer_count_response.data)
            except:
                answer_count = 0

            # Get student name separately
            student_name = 'Unknown Student'
            if question.get('student_id'):
                try:
                    student_response = supabase.table('profiles').select('full_name').eq('id', question['student_id']).execute()
                    if student_response.data:
                        student_name = student_response.data[0]['full_name']
                except:
                    pass

            # Get course name separately
            course_name = None
            if question.get('course_id'):
                try:
                    course_response = supabase.table('courses').select('title').eq('id', question['course_id']).execute()
                    if course_response.data:
                        course_name = course_response.data[0]['title']
                except:
                    pass

            questions.append(ForumQuestion(
                id=question['id'],
                title=question['title'],
                content=question['content'],
                course_id=question['course_id'],
                course_name=course_name,
                student_id=question['student_id'],
                student_name=student_name,
                tags=question.get('tags', []),
                answer_count=answer_count,
                is_resolved=question['is_resolved'],
                created_at=datetime.fromisoformat(question['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(question['updated_at'].replace('Z', '+00:00'))
            ))

        return questions

    except Exception as e:
        print(f"Error fetching questions: {e}")
        # Return empty list instead of error if tables don't exist
        if 'does not exist' in str(e) or 'relation' in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}", response_model=QuestionWithAnswers)
async def get_question_with_answers(question_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific question with all its answers"""
    try:
        # Get question details
        question_response = supabase.table('forum_questions').select('*').eq('id', question_id).single().execute()
        
        if not question_response.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question_data = question_response.data
        
        # Check access control - user must have access to this question's course
        user_role = current_user.role
        user_id = current_user.user_id
        question_course_id = question_data.get('course_id')
        
        if user_role == 'teacher':
            # Teachers can only access questions from their own courses
            teacher_courses_response = supabase.table('courses').select('id').eq('teacher_id', user_id).execute()
            teacher_course_ids = [course['id'] for course in teacher_courses_response.data]
            
            if question_course_id not in teacher_course_ids:
                raise HTTPException(status_code=403, detail="Access denied: You can only view questions from your own courses")
        elif user_role == 'student':
            # Students can only access questions from courses they're enrolled in
            student_enrollments_response = supabase.table('enrollments').select('course_id').eq('student_id', user_id).eq('status', 'active').execute()
            student_course_ids = [enrollment['course_id'] for enrollment in student_enrollments_response.data]
            
            if question_course_id not in student_course_ids:
                raise HTTPException(status_code=403, detail="Access denied: You can only view questions from courses you're enrolled in")
        
        # Get answers
        answers_response = supabase.table('forum_answers').select('*').eq('question_id', question_id).order('created_at').execute()
        
        # Count answers
        answer_count = len(answers_response.data)
        
        # Get student name separately
        student_name = 'Unknown Student'
        if question_data.get('student_id'):
            try:
                student_response = supabase.table('profiles').select('full_name').eq('id', question_data['student_id']).execute()
                if student_response.data:
                    student_name = student_response.data[0]['full_name']
            except:
                pass

        # Get course name separately
        course_name = None
        if question_data.get('course_id'):
            try:
                course_response = supabase.table('courses').select('title').eq('id', question_data['course_id']).execute()
                if course_response.data:
                    course_name = course_response.data[0]['title']
            except:
                pass
        
        # Build question object
        question = ForumQuestion(
            id=question_data['id'],
            title=question_data['title'],
            content=question_data['content'],
            course_id=question_data['course_id'],
            course_name=course_name,
            student_id=question_data['student_id'],
            student_name=student_name,
            tags=question_data.get('tags', []),
            answer_count=answer_count,
            is_resolved=question_data['is_resolved'],
            created_at=datetime.fromisoformat(question_data['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(question_data['updated_at'].replace('Z', '+00:00'))
        )
        
        # Build answers list
        answers = []
        for answer_data in answers_response.data:
            # Get teacher name separately
            teacher_name = 'Unknown Teacher'
            if answer_data.get('teacher_id'):
                try:
                    teacher_response = supabase.table('profiles').select('full_name').eq('id', answer_data['teacher_id']).execute()
                    if teacher_response.data:
                        teacher_name = teacher_response.data[0]['full_name']
                except:
                    pass

            answers.append(ForumAnswer(
                id=answer_data['id'],
                question_id=answer_data['question_id'],
                content=answer_data['content'],
                teacher_id=answer_data['teacher_id'],
                teacher_name=teacher_name,
                is_accepted=answer_data.get('is_accepted', False),
                created_at=datetime.fromisoformat(answer_data['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(answer_data['updated_at'].replace('Z', '+00:00'))
            ))
        
        return QuestionWithAnswers(question=question, answers=answers)
        
    except Exception as e:
        print(f"Error fetching question with answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answers", response_model=dict)
async def create_answer(request: CreateAnswerRequest, teacher_id: str = Query(...)):
    """Create an answer to a forum question"""
    try:
        # Verify teacher exists
        teacher_response = supabase.table('profiles').select('full_name, role').eq('id', teacher_id).single().execute()
        if not teacher_response.data or teacher_response.data['role'] != 'teacher':
            raise HTTPException(status_code=403, detail="Only teachers can answer questions")
        
        # Verify question exists
        question_response = supabase.table('forum_questions').select('id').eq('id', request.question_id).single().execute()
        if not question_response.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Create answer
        answer_data = {
            'question_id': request.question_id,
            'content': request.content,
            'teacher_id': teacher_id,
            'is_accepted': False,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        response = supabase.table('forum_answers').insert(answer_data).execute()
        
        return {
            "success": True,
            "message": "Answer posted successfully",
            "data": response.data[0]
        }
        
    except Exception as e:
        print(f"Error creating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/questions/{question_id}/resolve")
async def resolve_question(question_id: str, student_id: str = Query(...)):
    """Mark a question as resolved"""
    try:
        # Verify the student owns the question
        question_response = supabase.table('forum_questions').select('student_id').eq('id', question_id).single().execute()
        if not question_response.data:
            raise HTTPException(status_code=404, detail="Question not found")
        
        if question_response.data['student_id'] != student_id:
            raise HTTPException(status_code=403, detail="Only the question author can resolve it")
        
        # Update question status
        update_response = supabase.table('forum_questions').update({
            'is_resolved': True,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', question_id).execute()
        
        return {
            "success": True,
            "message": "Question marked as resolved"
        }
        
    except Exception as e:
        print(f"Error resolving question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/answers/{answer_id}/accept")
async def accept_answer(answer_id: str, student_id: str = Query(...)):
    """Accept an answer as the best answer"""
    try:
        # Get answer and question info
        answer_response = supabase.table('forum_answers').select('question_id').eq('id', answer_id).single().execute()
        if not answer_response.data:
            raise HTTPException(status_code=404, detail="Answer not found")
        
        question_id = answer_response.data['question_id']
        
        # Verify the student owns the question
        question_response = supabase.table('forum_questions').select('student_id').eq('id', question_id).single().execute()
        if not question_response.data or question_response.data['student_id'] != student_id:
            raise HTTPException(status_code=403, detail="Only the question author can accept answers")
        
        # Unaccept all other answers for this question
        supabase.table('forum_answers').update({'is_accepted': False}).eq('question_id', question_id).execute()
        
        # Accept this answer
        supabase.table('forum_answers').update({
            'is_accepted': True,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', answer_id).execute()
        
        # Mark question as resolved
        supabase.table('forum_questions').update({
            'is_resolved': True,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', question_id).execute()
        
        return {
            "success": True,
            "message": "Answer accepted successfully"
        }
        
    except Exception as e:
        print(f"Error accepting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
