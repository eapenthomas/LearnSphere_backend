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
    Fetch all students for a teacher and perform risk analysis using batched queries.
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
        courses_data = courses_res.data or []
        course_ids = [c["id"] for c in courses_data]
        course_map = {c["id"]: c["title"] for c in courses_data}
        
        if not course_ids:
            return []

        # 2. Get All Enrollments
        enrollments_res = supabase.table("enrollments").select("student_id, course_id, profiles!enrollments_student_id_fkey(full_name)").in_("course_id", course_ids).eq("status", "active").execute()
        enrollments = enrollments_res.data or []
        
        if not enrollments:
            return []

        student_ids = list(set([e["student_id"] for e in enrollments]))

        # 3. Batch Fetch All Metrics (Massive optimization: reduction in HTTP calls)
        # Quizzes & Submissions
        quizzes_res = supabase.table("quizzes").select("id, course_id").in_("course_id", course_ids).execute()
        all_q_ids = [q["id"] for q in quizzes_res.data or []]
        quiz_submissions = []
        if all_q_ids and student_ids:
            qs_res = supabase.table("quiz_submissions").select("student_id, quiz_id, score, total_marks").in_("quiz_id", all_q_ids).in_("student_id", student_ids).execute()
            quiz_submissions = qs_res.data or []

        # Assignments & Submissions
        assignments_res = supabase.table("assignments").select("id, course_id, max_score").in_("course_id", course_ids).execute()
        all_a_ids = [a["id"] for a in assignments_res.data or []]
        assign_submissions = []
        if all_a_ids and student_ids:
            asub_res = supabase.table("assignment_submissions").select("student_id, assignment_id, score").in_("assignment_id", all_a_ids).in_("student_id", student_ids).execute()
            assign_submissions = asub_res.data or []

        # Progress
        progress_res = supabase.table("course_progress").select("student_id, course_id, overall_progress_percentage").in_("course_id", course_ids).in_("student_id", student_ids).execute()
        all_progress = progress_res.data or []

        # 4. Map data for quick lookup
        qs_map = {} # (sid, cid) -> list of scores
        for q in (quizzes_res.data or []):
            qid, cid = q["id"], q["course_id"]
            for s in quiz_submissions:
                if s["quiz_id"] == qid:
                    key = (s["student_id"], cid)
                    if key not in qs_map: qs_map[key] = []
                    if s["total_marks"] > 0:
                        qs_map[key].append(s["score"] / s["total_marks"] * 100)

        as_map = {} # (sid, cid) -> list of scores
        as_counts = {} # (sid, cid) -> sub_count
        course_a_total = {} # cid -> total_assignments
        for a in (assignments_res.data or []):
            aid, cid = a["id"], a["course_id"]
            course_a_total[cid] = course_a_total.get(cid, 0) + 1
            for s in assign_submissions:
                if s["assignment_id"] == aid:
                    key = (s["student_id"], cid)
                    if key not in as_map: as_map[key] = []
                    if (a.get("max_score") or 0) > 0:
                        as_map[key].append(s["score"] / a["max_score"] * 100)
                    as_counts[key] = as_counts.get(key, 0) + 1

        prog_map = {(p["student_id"], p["course_id"]): p["overall_progress_percentage"] for p in all_progress}

        # 5. Process and Predict
        results = []
        for enrollment in enrollments:
            sid = enrollment["student_id"]
            cid = enrollment["course_id"]
            key = (sid, cid)
            
            # Aggregate from memory
            q_scores = qs_map.get(key, [])
            quiz_score = sum(q_scores) / len(q_scores) if q_scores else 65
            quiz_count = len(q_scores)

            a_scores = as_map.get(key, [])
            assign_score = sum(a_scores) / len(a_scores) if a_scores else 70
            sub_count = as_counts.get(key, 0)
            total_a = course_a_total.get(cid, 0)
            sub_rate = sub_count / total_a if total_a > 0 else 0
            
            comp_rate = prog_map.get(key, 0)

            # ML Prediction
            features = np.array([[quiz_score, assign_score, comp_rate, sub_rate, quiz_count]])
            prediction = float(performance_model.predict(features)[0])
            predicted_score = round(np.clip(prediction, 0, 100), 2)
            
            risk_level = "Low Risk"
            if predicted_score < 40: risk_level = "High Risk"
            elif predicted_score <= 60: risk_level = "Moderate Risk"
            
            results.append({
                "student_id": sid,
                "student_name": enrollment.get("profiles", {}).get("full_name", "Unknown"),
                "course_name": course_map.get(cid, "Unknown"),
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
