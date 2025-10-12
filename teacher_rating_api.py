"""
Teacher Rating API
Allows students to rate teachers and view ratings
"""

import os
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

router = APIRouter(prefix="/api/teacher-ratings", tags=["teacher-ratings"])

class TeacherRatingRequest(BaseModel):
    teacher_id: str
    student_id: str
    course_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    review: Optional[str] = None

class TeacherRatingResponse(BaseModel):
    id: str
    teacher_id: str
    student_id: str
    course_id: str
    rating: int
    review: Optional[str]
    student_name: str
    course_title: str
    created_at: datetime
    updated_at: datetime

class TeacherRatingSummary(BaseModel):
    teacher_id: str
    teacher_name: str
    average_rating: float
    total_ratings: int
    rating_distribution: Dict[str, int]  # {"5": 10, "4": 5, "3": 2, "2": 1, "1": 0}

@router.post("/", response_model=Dict[str, Any])
async def create_or_update_rating(rating_request: TeacherRatingRequest):
    """Create or update a teacher rating by a student"""
    try:
        # Check if student is enrolled in the course
        enrollment_response = supabase.table('enrollments').select('id').eq('student_id', rating_request.student_id).eq('course_id', rating_request.course_id).eq('status', 'active').execute()
        
        if not enrollment_response.data:
            raise HTTPException(status_code=403, detail="Student is not enrolled in this course")
        
        # Check if rating already exists
        existing_rating = supabase.table('teacher_ratings').select('id').eq('teacher_id', rating_request.teacher_id).eq('student_id', rating_request.student_id).eq('course_id', rating_request.course_id).execute()
        
        rating_data = {
            'teacher_id': rating_request.teacher_id,
            'student_id': rating_request.student_id,
            'course_id': rating_request.course_id,
            'rating': rating_request.rating,
            'review': rating_request.review,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        
        if existing_rating.data:
            # Update existing rating
            response = supabase.table('teacher_ratings').update(rating_data).eq('id', existing_rating.data[0]['id']).execute()
            message = "Rating updated successfully"
        else:
            # Create new rating
            rating_data['created_at'] = datetime.now(timezone.utc).isoformat()
            response = supabase.table('teacher_ratings').insert(rating_data).execute()
            message = "Rating created successfully"
        
        if response.data:
            return {"message": message, "rating_id": response.data[0]['id'] if response.data else None}
        else:
            raise HTTPException(status_code=500, detail="Failed to save rating")
            
    except Exception as e:
        print(f"Error creating/updating teacher rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/{teacher_id}", response_model=List[TeacherRatingResponse])
async def get_teacher_ratings(teacher_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get all ratings for a specific teacher"""
    try:
        response = supabase.table('teacher_ratings').select('''
            *,
            profiles!teacher_ratings_student_id_fkey(full_name),
            courses(title)
        ''').eq('teacher_id', teacher_id).order('created_at', desc=True).limit(limit).execute()

        ratings = []
        for rating in response.data:
            ratings.append(TeacherRatingResponse(
                id=rating['id'],
                teacher_id=rating['teacher_id'],
                student_id=rating['student_id'],
                course_id=rating['course_id'],
                rating=rating['rating'],
                review=rating['review'],
                student_name=rating['profiles']['full_name'] if rating.get('profiles') else 'Anonymous',
                course_title=rating['courses']['title'] if rating.get('courses') else 'Unknown Course',
                created_at=datetime.fromisoformat(rating['created_at'].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(rating['updated_at'].replace('Z', '+00:00'))
            ))

        return ratings

    except Exception as e:
        print(f"Error fetching teacher ratings: {e}")
        # If table doesn't exist, return empty list instead of error
        if "does not exist" in str(e):
            return []
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/{teacher_id}/summary", response_model=TeacherRatingSummary)
async def get_teacher_rating_summary(teacher_id: str):
    """Get rating summary for a teacher"""
    try:
        # Get teacher info
        teacher_response = supabase.table('profiles').select('full_name').eq('id', teacher_id).execute()
        teacher_name = teacher_response.data[0]['full_name'] if teacher_response.data else 'Unknown Teacher'
        
        # Get all ratings for teacher
        ratings_response = supabase.table('teacher_ratings').select('rating').eq('teacher_id', teacher_id).execute()
        
        if not ratings_response.data:
            return TeacherRatingSummary(
                teacher_id=teacher_id,
                teacher_name=teacher_name,
                average_rating=0.0,
                total_ratings=0,
                rating_distribution={"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
            )
        
        ratings = [r['rating'] for r in ratings_response.data]
        average_rating = sum(ratings) / len(ratings)
        total_ratings = len(ratings)
        
        # Calculate rating distribution
        rating_distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for rating in ratings:
            rating_distribution[str(rating)] += 1
        
        return TeacherRatingSummary(
            teacher_id=teacher_id,
            teacher_name=teacher_name,
            average_rating=round(average_rating, 1),
            total_ratings=total_ratings,
            rating_distribution=rating_distribution
        )
        
    except Exception as e:
        print(f"Error fetching teacher rating summary: {e}")
        # If table doesn't exist, return default summary
        if "does not exist" in str(e):
            return TeacherRatingSummary(
                teacher_id=teacher_id,
                teacher_name=teacher_name if 'teacher_name' in locals() else 'Unknown Teacher',
                average_rating=0.0,
                total_ratings=0,
                rating_distribution={"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/{student_id}/rating/{teacher_id}/{course_id}")
async def get_student_rating_for_teacher(student_id: str, teacher_id: str, course_id: str):
    """Get a student's rating for a specific teacher in a specific course"""
    try:
        response = supabase.table('teacher_ratings').select('*').eq('student_id', student_id).eq('teacher_id', teacher_id).eq('course_id', course_id).execute()
        
        if response.data:
            rating = response.data[0]
            return {
                "rating": rating['rating'],
                "review": rating['review'],
                "created_at": rating['created_at'],
                "updated_at": rating['updated_at']
            }
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching student rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{rating_id}")
async def delete_rating(rating_id: str, student_id: str = Query(...)):
    """Delete a rating (only by the student who created it)"""
    try:
        # Verify the rating belongs to the student
        rating_response = supabase.table('teacher_ratings').select('student_id').eq('id', rating_id).execute()
        
        if not rating_response.data:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        if rating_response.data[0]['student_id'] != student_id:
            raise HTTPException(status_code=403, detail="You can only delete your own ratings")
        
        # Delete the rating
        response = supabase.table('teacher_ratings').delete().eq('id', rating_id).execute()
        
        if response.data:
            return {"message": "Rating deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete rating")
            
    except Exception as e:
        print(f"Error deleting rating: {e}")
        raise HTTPException(status_code=500, detail=str(e))
