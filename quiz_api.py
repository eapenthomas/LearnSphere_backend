from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])

# Pydantic models
class QuizOption(BaseModel):
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    question_text: str
    question_type: str = "mcq"
    options: Optional[List[QuizOption]] = None
    correct_answer: Optional[str] = None
    marks: int = 1

class CreateQuizRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    course_id: str
    instructions: Optional[str] = ""
    duration_minutes: Optional[int] = 60
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    questions: List[QuizQuestion]

class UpdateQuizRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    course_id: Optional[str] = None
    instructions: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[str] = None
    questions: Optional[List[QuizQuestion]] = None

@router.get("/teacher/{teacher_id}")
async def get_teacher_quizzes(teacher_id: str):
    """Get all quizzes created by a specific teacher"""
    try:
        # Get quizzes with course information
        response = supabase.table('quizzes').select('''
            *,
            courses!quizzes_course_id_fkey (
                id,
                title,
                code
            )
        ''').eq('teacher_id', teacher_id).order('created_at', desc=True).execute()
        
        # Get question counts for each quiz
        quizzes = response.data
        for quiz in quizzes:
            question_count_response = supabase.table('quiz_questions').select('id').eq('quiz_id', quiz['id']).execute()
            quiz['question_count'] = len(question_count_response.data)
            
            # Get submission count
            submission_count_response = supabase.table('quiz_submissions').select('id').eq('quiz_id', quiz['id']).execute()
            quiz['submission_count'] = len(submission_count_response.data)
        
        return {
            "success": True,
            "data": quizzes
        }
        
    except Exception as e:
        print(f"Error fetching teacher quizzes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_quiz(request: CreateQuizRequest, teacher_id: str):
    """Create a new quiz with questions"""
    try:
        # Calculate total marks
        total_marks = sum(q.marks for q in request.questions)
        
        # Create quiz
        quiz_data = {
            'title': request.title,
            'description': request.description,
            'course_id': request.course_id,
            'teacher_id': teacher_id,
            'instructions': request.instructions,
            'total_marks': total_marks,
            'duration_minutes': request.duration_minutes,
            'start_time': request.start_time,
            'end_time': request.end_time,
            'status': 'draft'
        }
        
        quiz_response = supabase.table('quizzes').insert(quiz_data).execute()
        quiz_id = quiz_response.data[0]['id']
        
        # Create questions
        for index, question in enumerate(request.questions):
            question_data = {
                'quiz_id': quiz_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'marks': question.marks,
                'order_index': index
            }
            
            if question.question_type == 'mcq' and question.options:
                question_data['options'] = [opt.dict() for opt in question.options]
            elif question.question_type in ['true_false', 'short_answer']:
                question_data['correct_answer'] = question.correct_answer
            
            supabase.table('quiz_questions').insert(question_data).execute()
        
        return {
            "success": True,
            "message": "Quiz created successfully",
            "data": {"quiz_id": quiz_id}
        }
        
    except Exception as e:
        print(f"Error creating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quiz_id}")
async def get_quiz_details(quiz_id: str):
    """Get detailed quiz information including questions"""
    try:
        # Get quiz details
        quiz_response = supabase.table('quizzes').select('''
            *,
            courses!quizzes_course_id_fkey (
                id,
                title,
                code
            )
        ''').eq('id', quiz_id).single().execute()
        
        # Get questions
        questions_response = supabase.table('quiz_questions').select('*').eq('quiz_id', quiz_id).order('order_index').execute()
        
        quiz_data = quiz_response.data
        quiz_data['questions'] = questions_response.data
        
        return {
            "success": True,
            "data": quiz_data
        }
        
    except Exception as e:
        print(f"Error fetching quiz details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{quiz_id}")
async def update_quiz(quiz_id: str, request: UpdateQuizRequest):
    """Update quiz details and questions"""
    try:
        # Update quiz basic info
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.course_id is not None:
            update_data['course_id'] = request.course_id
        if request.instructions is not None:
            update_data['instructions'] = request.instructions
        if request.duration_minutes is not None:
            update_data['duration_minutes'] = request.duration_minutes
        if request.start_time is not None:
            update_data['start_time'] = request.start_time
        if request.end_time is not None:
            update_data['end_time'] = request.end_time
        if request.status is not None:
            update_data['status'] = request.status
        
        if update_data:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            supabase.table('quizzes').update(update_data).eq('id', quiz_id).execute()
        
        # Update questions if provided
        if request.questions is not None:
            # Delete existing questions
            supabase.table('quiz_questions').delete().eq('quiz_id', quiz_id).execute()
            
            # Calculate new total marks
            total_marks = sum(q.marks for q in request.questions)
            supabase.table('quizzes').update({'total_marks': total_marks}).eq('id', quiz_id).execute()
            
            # Insert new questions
            for index, question in enumerate(request.questions):
                question_data = {
                    'quiz_id': quiz_id,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'marks': question.marks,
                    'order_index': index
                }
                
                if question.question_type == 'mcq' and question.options:
                    question_data['options'] = [opt.dict() for opt in question.options]
                elif question.question_type in ['true_false', 'short_answer']:
                    question_data['correct_answer'] = question.correct_answer
                
                supabase.table('quiz_questions').insert(question_data).execute()
        
        return {
            "success": True,
            "message": "Quiz updated successfully"
        }
        
    except Exception as e:
        print(f"Error updating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: str):
    """Delete a quiz and all associated data"""
    try:
        # Delete quiz (cascade will handle questions and submissions)
        supabase.table('quizzes').delete().eq('id', quiz_id).execute()
        
        return {
            "success": True,
            "message": "Quiz deleted successfully"
        }
        
    except Exception as e:
        print(f"Error deleting quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{quiz_id}/submissions")
async def get_quiz_submissions(quiz_id: str):
    """Get all submissions for a specific quiz"""
    try:
        response = supabase.table('quiz_submissions').select('''
            *,
            profiles!quiz_submissions_student_id_fkey (
                id,
                full_name,
                email
            )
        ''').eq('quiz_id', quiz_id).order('submitted_at', desc=True).execute()
        
        return {
            "success": True,
            "data": response.data
        }
        
    except Exception as e:
        print(f"Error fetching quiz submissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/submission/{submission_id}")
async def get_submission_details(submission_id: str):
    """Get detailed submission data including answers for a specific submission"""
    try:
        # Get submission details
        submission_response = supabase.table('quiz_submissions').select('*').eq('id', submission_id).single().execute()
        
        if not submission_response.data:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        submission = submission_response.data
        
        # Get quiz details
        quiz_response = supabase.table('quizzes').select('*').eq('id', submission['quiz_id']).single().execute()
        
        quiz = quiz_response.data if quiz_response.data else {}
        
        # Get student details
        student_response = supabase.table('profiles').select('id, full_name, email').eq('id', submission['student_id']).single().execute()
        student = student_response.data if student_response.data else {}
        
        # Get course details if quiz has course_id
        course = {}
        if quiz.get('course_id'):
            course_response = supabase.table('courses').select('id, title, code').eq('id', quiz['course_id']).single().execute()
            course = course_response.data if course_response.data else {}
        
        # Get quiz questions to match with student answers
        questions_response = supabase.table('quiz_questions').select('*').eq('quiz_id', submission['quiz_id']).order('order_index').execute()
        questions = {q['id']: q for q in questions_response.data} if questions_response.data else {}
        
        # Format the answers data from the JSONB answers column
        answers = []
        student_answers = submission.get('answers', [])
        
        for student_answer in student_answers:
            question_id = student_answer.get('question_id')
            question = questions.get(question_id, {})
            
            # Determine if answer is correct based on question type
            student_answer_text = student_answer.get('answer', '')
            is_correct = False
            
            if question.get('question_type') == 'mcq':
                # For MCQ, check if student answer matches any correct option
                options = question.get('options', [])
                for option in options:
                    if option.get('is_correct', False) and option.get('text') == student_answer_text:
                        is_correct = True
                        break
            else:
                # For other types, compare with correct_answer field
                correct_answer = question.get('correct_answer', '')
                if student_answer_text.lower().strip() == correct_answer.lower().strip():
                    is_correct = True
            
            formatted_answer = {
                'question_id': question_id,
                'question_text': question.get('question_text', ''),
                'question_type': question.get('question_type', ''),
                'student_answer': student_answer_text,
                'correct_answer': question.get('correct_answer', ''),
                'is_correct': is_correct,
                'marks': question.get('marks', 0) if is_correct else 0,
                'options': question.get('options', []),
                'order_index': question.get('order_index', 0)
            }
            answers.append(formatted_answer)
        
        # Sort answers by order_index
        answers.sort(key=lambda x: x['order_index'])
        
        # Combine all data
        result = {
            'id': submission['id'],
            'quiz_id': submission['quiz_id'],
            'student_id': submission['student_id'],
            'score': submission['score'],
            'total_marks': submission['total_marks'],
            'time_taken_minutes': submission.get('time_taken_minutes', 0),
            'submitted_at': submission['submitted_at'],
            'student': student,
            'quiz': {
                **quiz,
                'courses': course
            },
            'answers': answers
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching submission details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/courses/{teacher_id}")
async def get_teacher_courses(teacher_id: str):
    """Get courses taught by a specific teacher for quiz creation"""
    try:
        response = supabase.table('courses').select('id, title, code, description').eq('teacher_id', teacher_id).order('title').execute()

        return {
            "success": True,
            "data": response.data
        }

    except Exception as e:
        print(f"Error fetching teacher courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Student quiz endpoints
@router.get("/student/{student_id}/available")
async def get_student_available_quizzes(student_id: str):
    """Get available quizzes for a student from their enrolled courses"""
    try:
        # Get student's enrolled courses from the enrollments table
        enrolled_courses_response = supabase.table('enrollments').select('course_id').eq('student_id', student_id).eq('status', 'active').execute()

        if not enrolled_courses_response.data:
            return {
                "success": True,
                "data": []
            }

        course_ids = [enrollment['course_id'] for enrollment in enrolled_courses_response.data]

        # Get published quizzes from enrolled courses
        quizzes_response = supabase.table('quizzes').select('''
            *,
            courses!quizzes_course_id_fkey (
                id,
                title,
                code
            )
        ''').in_('course_id', course_ids).eq('status', 'published').order('created_at', desc=True).execute()

        # Check which quizzes the student has already submitted
        quiz_ids = [quiz['id'] for quiz in quizzes_response.data]
        if quiz_ids:
            submissions_response = supabase.table('quiz_submissions').select('quiz_id').eq('student_id', student_id).in_('quiz_id', quiz_ids).execute()
            submitted_quiz_ids = [sub['quiz_id'] for sub in submissions_response.data]
        else:
            submitted_quiz_ids = []

        # Add submission status, question count, and time-based access to each quiz
        from datetime import datetime, timezone
        current_time = datetime.now(timezone.utc)

        for quiz in quizzes_response.data:
            quiz['is_submitted'] = quiz['id'] in submitted_quiz_ids

            # Get question count for this quiz
            questions_count_response = supabase.table('quiz_questions').select('id').eq('quiz_id', quiz['id']).execute()
            quiz['questions'] = questions_count_response.data  # Add questions array for count
            quiz['question_count'] = len(questions_count_response.data)

            # Add time-based access control
            quiz['is_accessible'] = True
            quiz['access_message'] = ''

            if quiz['start_time']:
                try:
                    start_time_str = quiz['start_time']
                    if start_time_str.endswith('Z'):
                        start_time_str = start_time_str[:-1] + '+00:00'
                    start_time = datetime.fromisoformat(start_time_str)
                    if start_time.tzinfo is None:
                        start_time = start_time.replace(tzinfo=timezone.utc)

                    if current_time < start_time:
                        quiz['is_accessible'] = False
                        quiz['access_message'] = f"Quiz opens on {start_time.strftime('%Y-%m-%d at %H:%M')}"
                except Exception as e:
                    print(f"Error parsing start_time: {e}")

            if quiz['end_time']:
                try:
                    end_time_str = quiz['end_time']
                    if end_time_str.endswith('Z'):
                        end_time_str = end_time_str[:-1] + '+00:00'
                    end_time = datetime.fromisoformat(end_time_str)
                    if end_time.tzinfo is None:
                        end_time = end_time.replace(tzinfo=timezone.utc)

                    if current_time > end_time:
                        quiz['is_accessible'] = False
                        quiz['access_message'] = f"Quiz closed on {end_time.strftime('%Y-%m-%d at %H:%M')}"
                except Exception as e:
                    print(f"Error parsing end_time: {e}")

        return {
            "success": True,
            "data": quizzes_response.data
        }

    except Exception as e:
        print(f"Error fetching student quizzes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{quiz_id}/take")
async def get_quiz_for_student(quiz_id: str, student_id: str):
    """Get quiz details for student to take (without correct answers)"""
    try:
        # Get quiz details
        quiz_response = supabase.table('quizzes').select('''
            *,
            courses!quizzes_course_id_fkey (
                id,
                title,
                code
            )
        ''').eq('id', quiz_id).eq('status', 'published').single().execute()

        # Check if student is enrolled in the course
        enrollment_check = supabase.table('enrollments').select('id').eq('student_id', student_id).eq('course_id', quiz_response.data['course_id']).eq('status', 'active').execute()

        if not enrollment_check.data:
            raise HTTPException(status_code=403, detail="Student not enrolled in this course")

        # Check time-based access
        from datetime import datetime, timezone
        current_time = datetime.now(timezone.utc)
        quiz_data = quiz_response.data

        if quiz_data['start_time']:
            try:
                start_time_str = quiz_data['start_time']
                if start_time_str.endswith('Z'):
                    start_time_str = start_time_str[:-1] + '+00:00'
                start_time = datetime.fromisoformat(start_time_str)
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)

                if current_time < start_time:
                    raise HTTPException(status_code=403, detail=f"Quiz not yet available. Opens on {start_time.strftime('%Y-%m-%d at %H:%M')}")
            except Exception as e:
                print(f"Error parsing start_time in take quiz: {e}")

        if quiz_data['end_time']:
            try:
                end_time_str = quiz_data['end_time']
                if end_time_str.endswith('Z'):
                    end_time_str = end_time_str[:-1] + '+00:00'
                end_time = datetime.fromisoformat(end_time_str)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)

                if current_time > end_time:
                    raise HTTPException(status_code=403, detail=f"Quiz has expired. Closed on {end_time.strftime('%Y-%m-%d at %H:%M')}")
            except Exception as e:
                print(f"Error parsing end_time in take quiz: {e}")

        # Check if student has already submitted
        submission_check = supabase.table('quiz_submissions').select('id').eq('quiz_id', quiz_id).eq('student_id', student_id).execute()

        if submission_check.data:
            raise HTTPException(status_code=400, detail="Quiz already submitted")

        # Get questions without correct answers
        questions_response = supabase.table('quiz_questions').select('id, question_text, question_type, options, marks, order_index').eq('quiz_id', quiz_id).order('order_index').execute()

        # Remove correct answers from options (options are stored as simple strings, not objects)
        # No need to remove is_correct since options are stored as plain text arrays

        quiz_data = quiz_response.data
        quiz_data['questions'] = questions_response.data

        return {
            "success": True,
            "data": quiz_data
        }

    except Exception as e:
        print(f"Error fetching quiz for student: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class SubmitQuizRequest(BaseModel):
    quiz_id: str
    student_id: str
    answers: List[Dict[str, Any]]  # [{"question_id": "uuid", "answer": "selected_option_or_text"}]
    time_taken_minutes: Optional[int] = None

@router.post("/submit")
async def submit_quiz(request: SubmitQuizRequest):
    """Submit quiz answers and calculate score"""
    try:
        # Get quiz and questions with correct answers
        quiz_response = supabase.table('quizzes').select('*').eq('id', request.quiz_id).single().execute()
        questions_response = supabase.table('quiz_questions').select('*').eq('quiz_id', request.quiz_id).execute()

        # Check if already submitted
        existing_submission = supabase.table('quiz_submissions').select('id').eq('quiz_id', request.quiz_id).eq('student_id', request.student_id).execute()

        if existing_submission.data:
            raise HTTPException(status_code=400, detail="Quiz already submitted")

        # Calculate score
        total_score = 0
        total_marks = quiz_response.data['total_marks']

        # Create a map of question_id to correct answer
        questions_map = {q['id']: q for q in questions_response.data}

        for answer in request.answers:
            question_id = answer['question_id']
            student_answer = answer['answer']

            if question_id in questions_map:
                question = questions_map[question_id]
                is_correct = False

                if question['question_type'] == 'mcq':
                    # Find the correct option
                    for option in question['options']:
                        if option['is_correct'] and option['text'] == student_answer:
                            is_correct = True
                            break
                elif question['question_type'] in ['true_false', 'short_answer']:
                    is_correct = str(student_answer).lower().strip() == str(question['correct_answer']).lower().strip()

                if is_correct:
                    total_score += question['marks']

        # Save submission
        submission_data = {
            'quiz_id': request.quiz_id,
            'student_id': request.student_id,
            'answers': request.answers,
            'score': total_score,
            'total_marks': total_marks,
            'time_taken_minutes': request.time_taken_minutes
        }

        submission_response = supabase.table('quiz_submissions').insert(submission_data).execute()

        return {
            "success": True,
            "message": "Quiz submitted successfully",
            "data": {
                "score": total_score,
                "total_marks": total_marks,
                "percentage": round((total_score / total_marks) * 100, 1) if total_marks > 0 else 0
            }
        }

    except Exception as e:
        print(f"Error submitting quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enrollment endpoints for testing
@router.post("/enroll-student")
async def enroll_student_in_course(student_id: str, course_id: str):
    """Enroll a student in a course (for testing purposes)"""
    try:
        enrollment_data = {
            'student_id': student_id,
            'course_id': course_id,
            'status': 'active'
        }

        response = supabase.table('enrollments').insert(enrollment_data).execute()

        return {
            "success": True,
            "message": "Student enrolled successfully",
            "data": response.data
        }

    except Exception as e:
        print(f"Error enrolling student: {e}")
        raise HTTPException(status_code=500, detail=str(e))
