from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
import joblib
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

# Model Path
MODEL_PATH = os.path.join(os.path.dirname(__file__), "performance_model.pkl")

# Global variable for the model
performance_model = None

def load_model():
    """Load the ML model once at startup."""
    global performance_model
    try:
        if os.path.exists(MODEL_PATH):
            performance_model = joblib.load(MODEL_PATH)
            logger.info(f"✅ ML Model loaded successfully from {MODEL_PATH}")
        else:
            logger.warning(f"⚠️  ML Model file not found at {MODEL_PATH}. Predictions will be unavailable.")
    except Exception as e:
        logger.error(f"❌ Error loading ML model: {e}")
        performance_model = None

# Initial load
load_model()

class PredictionRequest(BaseModel):
    avg_quiz_score: float = Field(..., ge=0, le=100)
    avg_assignment_score: float = Field(..., ge=0, le=100)
    completion_rate: float = Field(..., ge=0, le=100)
    assignment_submission_rate: float = Field(..., ge=0, le=1)
    quiz_attempt_count: int = Field(..., ge=0)

class PredictionResponse(BaseModel):
    predicted_score: float
    risk_level: str

@router.post("/predict-performance", response_model=PredictionResponse)
async def predict_performance(data: PredictionRequest):
    """
    Predict student course performance using the trained Linear Regression model.
    """
    if performance_model is None:
        raise HTTPException(
            status_code=503, 
            detail="Machine Learning model is not loaded on the server."
        )

    try:
        # Prepare feature array in the exact order model was trained on:
        # ['avg_quiz_score', 'avg_assignment_score', 'completion_rate', 'assignment_submission_rate', 'quiz_attempt_count']
        features = np.array([[
            data.avg_quiz_score,
            data.avg_assignment_score,
            data.completion_rate,
            data.assignment_submission_rate,
            data.quiz_attempt_count
        ]])

        # Predict
        prediction = performance_model.predict(features)[0]
        
        # Round and clip for sanity
        predicted_score = round(float(np.clip(prediction, 0, 100)), 2)

        # Risk Classification logic
        if predicted_score < 40:
            risk_level = "High Risk"
        elif 40 <= predicted_score <= 60:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Low Risk"

        return {
            "predicted_score": predicted_score,
            "risk_level": risk_level
        }

    except Exception as e:
        logger.error(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail="Error processing prediction request.")

@router.get("/teacher/risk-analysis/{teacher_id}")
async def get_teacher_risk_analysis(teacher_id: str):
    """
    Fetch all students for a teacher and perform risk analysis on each.
    """
    if performance_model is None:
        raise HTTPException(status_code=503, detail="ML model not available")

    try:
        from supabase import create_client, Client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key)

        # 1. Get Teacher's Courses
        courses_res = supabase.table("courses").select("id, title").eq("teacher_id", teacher_id).execute()
        courses = courses_res.data or []
        course_ids = [c["id"] for c in courses]
        
        if not course_ids:
            return []

        # 2. Get All Enrollments for these courses
        enrollments_res = supabase.table("enrollments").select("student_id, course_id, profiles!enrollments_student_id_fkey(full_name)").in_("course_id", course_ids).execute()
        enrollments = enrollments_res.data or []
        
        if not enrollments:
            return []

        results = []
        
        # 3. Process each student-course pair (Simplified for performance)
        for enrollment in enrollments:
            student_id = enrollment["student_id"]
            course_id = enrollment["course_id"]
            student_name = enrollment.get("profiles", {}).get("full_name", "Unknown Student")
            
            # Fetch features
            quizzes_res = supabase.table("quizzes").select("id").eq("course_id", course_id).execute()
            q_ids = [q["id"] for q in quizzes_res.data or []]
            
            quiz_score = 65  # Default
            quiz_count = 0
            if q_ids:
                qs_res = supabase.table("quiz_submissions").select("score, total_marks").eq("student_id", student_id).in_("quiz_id", q_ids).execute()
                qs_data = qs_res.data or []
                quiz_count = len(qs_data)
                if quiz_count > 0:
                    quiz_score = sum((q["score"] / q["total_marks"] * 100) for q in qs_data if q["total_marks"] > 0) / quiz_count

            assign_res = supabase.table("assignments").select("id, max_score").eq("course_id", course_id).execute()
            a_ids = [a["id"] for a in assign_res.data or []]
            
            assign_score = 70
            sub_rate = 0
            if a_ids:
                asub_res = supabase.table("assignment_submissions").select("score, assignment_id").eq("student_id", student_id).in_("assignment_id", a_ids).execute()
                asub_data = asub_res.data or []
                sub_rate = len(asub_data) / len(a_ids)
                if asub_data:
                    max_map = {a["id"]: a["max_score"] for a in assign_res.data or []}
                    assign_score = sum((s["score"] / max_map.get(s["assignment_id"], 100) * 100) for s in asub_data if max_map.get(s["assignment_id"], 0) > 0) / len(asub_data)

            prog_res = supabase.table("course_progress").select("overall_progress_percentage").eq("student_id", student_id).eq("course_id", course_id).maybe_single().execute()
            comp_rate = prog_res.data["overall_progress_percentage"] if prog_res.data else 0

            # 4. Predict
            features = np.array([[quiz_score, assign_score, comp_rate, sub_rate, quiz_count]])
            prediction = float(performance_model.predict(features)[0])
            predicted_score = round(np.clip(prediction, 0, 100), 2)
            
            risk_level = "Low Risk"
            if predicted_score < 40: risk_level = "High Risk"
            elif predicted_score <= 60: risk_level = "Moderate Risk"
            
            results.append({
                "student_id": student_id,
                "student_name": student_name,
                "course_name": next((c["title"] for c in courses if c["id"] == course_id), "Unknown"),
                "predicted_score": predicted_score,
                "risk_level": risk_level,
                "metrics": {
                    "quiz_score": round(quiz_score, 1),
                    "assign_score": round(assign_score, 1),
                    "comp_rate": comp_rate
                }
            })

        results.sort(key=lambda x: x["predicted_score"])
        return results

    except Exception as e:
        logger.error(f"Teacher Risk Analysis Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
