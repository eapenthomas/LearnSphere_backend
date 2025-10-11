"""
AI-Powered Quiz Generator API
Generates quiz questions from uploaded PDF/DOCX files using OpenAI/DeepSeek API
"""

import os
import uuid
import tempfile
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import PyPDF2
import docx
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Initialize OpenAI client lazily to avoid startup delays
client = None
MODEL_NAME = None

def get_openai_client():
    """Get OpenAI client lazily"""
    global client, MODEL_NAME
    
    if client is None:
        summary_key = os.getenv("SUMMARY_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_OPENAI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            client = OpenAI(api_key=openai_key)
            MODEL_NAME = "gpt-4o-mini"
            print("Using OpenAI API for quiz generation")
        elif summary_key:
            client = OpenAI(api_key=summary_key)
            MODEL_NAME = "gpt-3.5-turbo"
            print("Using OpenAI API for quiz generation")
        elif deepseek_key:
            # Use DeepSeek API as fallback
            client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com"
            )
            MODEL_NAME = "deepseek-chat"
            print("Using DeepSeek API for quiz generation")
        else:
            print("Warning: No API key found for quiz generation")
    
    return client

router = APIRouter(prefix="/api/quiz-generator", tags=["quiz-generator"])

# Pydantic models
class QuizQuestion(BaseModel):
    question: str
    question_type: str  # 'multiple_choice', 'true_false', 'short_answer'
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"  # easy, medium, hard

class GeneratedQuiz(BaseModel):
    title: str
    description: str
    questions: List[QuizQuestion]
    total_questions: int
    estimated_time: int  # in minutes

class QuizGenerationRequest(BaseModel):
    num_questions: int
    difficulty: str = "medium"
    question_types: List[str] = ["multiple_choice", "true_false", "short_answer"]
    course_id: str
    teacher_id: str

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file with comprehensive encoding handling and fallback methods"""
    
    # Method 1: Try pdfplumber first (preferred)
    try:
        import pdfplumber
        import io
        text_parts = []
        
        print(f"Processing PDF file with pdfplumber: {file_path}")
        
        with pdfplumber.open(file_path) as pdf:
            print(f"PDF has {len(pdf.pages)} pages")
            
            for i, page in enumerate(pdf.pages):
                try:
                    print(f"Processing page {i+1}...")
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Multiple encoding strategies to handle problematic characters
                        try:
                            # Strategy 1: Direct UTF-8 encoding with error handling
                            cleaned_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                        except Exception:
                            try:
                                # Strategy 2: Replace problematic characters
                                cleaned_text = page_text.encode('utf-8', errors='replace').decode('utf-8')
                            except Exception:
                                # Strategy 3: Use ASCII fallback
                                cleaned_text = page_text.encode('ascii', errors='ignore').decode('ascii')
                        
                        # Additional cleanup for common problematic characters
                        cleaned_text = cleaned_text.replace('\ufffd', '')  # Remove replacement characters
                        cleaned_text = cleaned_text.replace('\udfc1', '')  # Remove the specific problematic character
                        
                        if cleaned_text.strip():
                            text_parts.append(cleaned_text.strip())
                            print(f"Page {i+1}: Extracted {len(cleaned_text)} characters")
                        else:
                            print(f"Page {i+1}: No readable text found")
                    else:
                        print(f"Page {i+1}: No text extracted")
                        
                except Exception as page_error:
                    print(f"Warning: Failed to extract text from page {i+1}: {str(page_error)}")
                    continue
        
        if text_parts:
            final_text = "\n".join(text_parts).strip()
            print(f"Successfully extracted {len(final_text)} total characters from PDF using pdfplumber")
            return final_text
            
    except Exception as e:
        print(f"pdfplumber failed: {str(e)}")
    
    # Method 2: Fallback to PyPDF2
    try:
        print(f"Trying PyPDF2 fallback for: {file_path}")
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        # Clean the text with multiple strategies
                        try:
                            cleaned_text = page_text.encode('utf-8', errors='ignore').decode('utf-8')
                        except Exception:
                            cleaned_text = page_text.encode('ascii', errors='ignore').decode('ascii')
                        
                        # Remove problematic characters
                        cleaned_text = cleaned_text.replace('\ufffd', '')
                        cleaned_text = cleaned_text.replace('\udfc1', '')
                        
                        if cleaned_text.strip():
                            text_parts.append(cleaned_text.strip())
                            print(f"PyPDF2 Page {i+1}: Extracted {len(cleaned_text)} characters")
                            
                except Exception as page_error:
                    print(f"PyPDF2 Warning: Failed to extract text from page {i+1}: {str(page_error)}")
                    continue
        
        if text_parts:
            final_text = "\n".join(text_parts).strip()
            print(f"Successfully extracted {len(final_text)} total characters from PDF using PyPDF2")
            return final_text
            
    except Exception as e:
        print(f"PyPDF2 also failed: {str(e)}")
    
    # If both methods fail
    raise HTTPException(
        status_code=400, 
        detail="Unable to extract text from PDF. The file may be corrupted, password-protected, or contain only images. Please try with a different PDF file."
    )

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def generate_quiz_with_ai(content: str, num_questions: int, difficulty: str, question_types: List[str]) -> List[QuizQuestion]:
    """Generate quiz questions using OpenAI API"""
    try:
        # Prepare the prompt
        types_str = ", ".join(question_types)
        
        prompt = f"""
        Based on the following educational content, generate {num_questions} quiz questions with {difficulty} difficulty level.
        
        Question types to include: {types_str}
        
        For each question, provide:
        1. The question text
        2. Question type (multiple_choice, true_false, or short_answer)
        3. For multiple choice: 4 options (A, B, C, D)
        4. The correct answer
        5. A brief explanation
        6. Difficulty level
        
        Format the response as a JSON array with this structure:
        [
            {{
                "question": "Question text here",
                "question_type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "Brief explanation",
                "difficulty": "{difficulty}"
            }}
        ]
        
        Content to analyze:
        {content[:4000]}  # Limit content to avoid token limits
        
        Make sure questions are educational, clear, and test understanding of the key concepts.
        """
        
        # Get client lazily
        openai_client = get_openai_client()
        if not openai_client:
            raise HTTPException(status_code=500, detail="Quiz generation service not available")
        
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator specializing in generating high-quality quiz questions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse the response
        content_text = response.choices[0].message.content.strip()
        
        # Extract JSON from the response
        json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
        if json_match:
            questions_data = json.loads(json_match.group())
        else:
            # Fallback: try to parse the entire response as JSON
            questions_data = json.loads(content_text)
        
        questions = []
        for q_data in questions_data:
            question = QuizQuestion(
                question=q_data.get("question", ""),
                question_type=q_data.get("question_type", "multiple_choice"),
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer", ""),
                explanation=q_data.get("explanation"),
                difficulty=q_data.get("difficulty", difficulty)
            )
            questions.append(question)
        
        return questions[:num_questions]  # Ensure we don't exceed requested number
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing AI response: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions with AI: {str(e)}")

@router.post("/generate", response_model=GeneratedQuiz)
async def generate_quiz_from_file(
    file: UploadFile = File(...),
    num_questions: int = Form(10),
    difficulty: str = Form("medium"),
    question_types: str = Form("multiple_choice,true_false,short_answer"),
    course_id: str = Form(...),
    teacher_id: str = Form(...)
):
    """Generate quiz questions from uploaded PDF/DOCX file"""
    try:
        # Initialize OpenAI client
        openai_client = get_openai_client()
        
        # Check if API client is configured
        if not openai_client or not MODEL_NAME:
            raise HTTPException(
                status_code=400, 
                detail="AI service not configured. Please set OPENAI_API_KEY, SUMMARY_API_KEY, or DEEPSEEK_OPENAI_API_KEY in environment variables."
            )
        
        print(f"Quiz generation request: {file.filename}, {num_questions} questions, {difficulty} difficulty")
        # Validate file type
        allowed_types = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and DOCX files are supported."
            )
        
        # Validate parameters
        if num_questions < 1 or num_questions > 50:
            raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 50")
        
        if difficulty not in ["easy", "medium", "hard"]:
            raise HTTPException(status_code=400, detail="Difficulty must be 'easy', 'medium', or 'hard'")
        
        # Parse question types
        question_types_list = [t.strip() for t in question_types.split(",")]
        valid_types = ["multiple_choice", "true_false", "short_answer"]
        question_types_list = [t for t in question_types_list if t in valid_types]
        
        if not question_types_list:
            question_types_list = ["multiple_choice"]
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text based on file type
            print(f"Extracting text from {file.content_type} file...")
            if file.content_type == "application/pdf":
                extracted_text = extract_text_from_pdf(temp_file_path)
            else:  # DOCX
                extracted_text = extract_text_from_docx(temp_file_path)
            
            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="No text could be extracted from the file. Please ensure the file contains readable text.")
            
            print(f"Successfully extracted {len(extracted_text)} characters from file")
            
            # Generate questions using AI
            questions = generate_quiz_with_ai(extracted_text, num_questions, difficulty, question_types_list)
            
            if not questions:
                raise HTTPException(status_code=500, detail="Failed to generate questions")
            
            # Calculate estimated time (2 minutes per question on average)
            estimated_time = len(questions) * 2
            
            # Create quiz title from filename
            quiz_title = f"AI Generated Quiz - {file.filename.split('.')[0]}"
            
            generated_quiz = GeneratedQuiz(
                title=quiz_title,
                description=f"Auto-generated quiz with {len(questions)} questions from uploaded document",
                questions=questions,
                total_questions=len(questions),
                estimated_time=estimated_time
            )
            
            return generated_quiz
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")

class SaveQuizRequest(BaseModel):
    title: str
    description: str
    questions: List[QuizQuestion]
    total_questions: int
    estimated_time: int
    course_id: str
    teacher_id: str
    instructions: Optional[str] = ""
    start_time: Optional[str] = None
    end_time: Optional[str] = None

@router.post("/save-generated-quiz")
async def save_generated_quiz(request: SaveQuizRequest):
    """Save the generated quiz to the database"""
    try:
        # Create quiz in database
        quiz_id = str(uuid.uuid4())

        quiz_insert_data = {
            'id': quiz_id,
            'title': request.title,
            'description': request.description,
            'course_id': request.course_id,
            'teacher_id': request.teacher_id,
            'duration_minutes': request.estimated_time,
            'total_marks': len(request.questions),
            'status': 'published',
            'instructions': request.instructions or '',
            'start_time': request.start_time if request.start_time else None,
            'end_time': request.end_time if request.end_time else None
        }
        
        quiz_response = supabase.table('quizzes').insert(quiz_insert_data).execute()
        
        if not quiz_response.data:
            raise HTTPException(status_code=500, detail="Failed to create quiz")
        
        # Insert questions
        for i, question in enumerate(request.questions):
            question_id = str(uuid.uuid4())

            # Map question types to database format
            question_type_mapping = {
                'multiple_choice': 'mcq',
                'true_false': 'true_false',
                'short_answer': 'short_answer'
            }

            db_question_type = question_type_mapping.get(question.question_type, question.question_type)

            question_data = {
                'id': question_id,
                'quiz_id': quiz_id,
                'question_text': question.question,
                'question_type': db_question_type,
                'marks': 1,
                'order_index': i + 1
            }

            # Handle options and correct answers based on question type
            if db_question_type == 'mcq' and question.options:
                # For MCQ, store options as JSONB array of objects
                options_data = []
                for idx, option in enumerate(question.options):
                    options_data.append({
                        'text': option,
                        'is_correct': option == question.correct_answer
                    })
                question_data['options'] = options_data
            else:
                # For true_false and short_answer, store correct answer directly
                question_data['correct_answer'] = question.correct_answer

            supabase.table('quiz_questions').insert(question_data).execute()

        return {
            "success": True,
            "message": "Quiz saved successfully",
            "quiz_id": quiz_id,
            "total_questions": len(request.questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving quiz: {str(e)}")
