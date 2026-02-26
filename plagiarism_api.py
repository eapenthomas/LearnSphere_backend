"""
plagiarism_api.py — Hybrid Plagiarism Detection API for LearnSphere.
Stage 1: TF-IDF structural similarity (local, fast)
Stage 2: OpenAI embedding semantic similarity (called only if Stage 1 >= 0.4)
"""

import os
import json
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from datetime import datetime, timezone
from supabase import create_client, Client

from text_utils import extract_text, preprocess_text
from tfidf_utils import compute_tfidf_similarity
from embedding_utils import generate_embedding, find_best_semantic_match
from auth_middleware import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plagiarism", tags=["Plagiarism"])

# ---------------------------------------------------------------------------
# Supabase client
# ---------------------------------------------------------------------------
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase configuration missing")
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Risk classification helpers
# ---------------------------------------------------------------------------
STAGE1_THRESHOLD = 0.4       # below this → Low Risk, skip OpenAI
SEM_HIGH_THRESHOLD = 0.8     # semantic >= 0.8  → High
SEM_MOD_THRESHOLD = 0.6      # semantic 0.6-0.8 → Moderate


def classify_risk(structural: float, semantic: Optional[float]) -> str:
    if structural < STAGE1_THRESHOLD:
        return "Low"
    if semantic is None:
        # Fallback: Stage 2 failed, use structural
        return "Moderate" if structural >= 0.6 else "Low"
    if semantic >= SEM_HIGH_THRESHOLD:
        return "High"
    if semantic >= SEM_MOD_THRESHOLD:
        return "Moderate"
    return "Low"


def risk_to_status(risk: str) -> str:
    mapping = {
        "High": "Flagged for Review",
        "Moderate": "Needs Manual Review",
        "Low": "Accepted",
    }
    return mapping.get(risk, "Accepted")


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------
@router.post("/check")
async def check_plagiarism(
    assignment_id: str = Form(...),
    submission_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Two-stage hybrid plagiarism check.
    - Stage 1: TF-IDF structural similarity (always runs, no API cost)
    - Stage 2: OpenAI semantic similarity (only if Stage 1 >= 0.4)
    """
    supabase = get_supabase()

    # ------------------------------------------------------------------
    # 1. Extract text from uploaded file
    # ------------------------------------------------------------------
    file_bytes = await file.read()
    raw_text = extract_text(file_bytes, file.filename or "submission")
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from the uploaded file.")

    processed_text = preprocess_text(raw_text)

    # ------------------------------------------------------------------
    # 2. Fetch existing submissions for the same assignment (excluding this one)
    # ------------------------------------------------------------------
    existing_res = supabase.table("assignment_submissions").select(
        "id, student_id, embedding"
    ).eq("assignment_id", assignment_id).neq("id", submission_id).execute()

    existing_subs = existing_res.data or []
    existing_texts_raw: list[str] = []

    # We need existing submission text. Since we stored embeddings, use them for Stage 2.
    # For Stage 1, we need text — fetch file URLs and extract on-the-fly (best effort).
    # Strategy: retrieve stored processed text from a separate query if available,
    # otherwise use partial text from DB or skip non-embedded ones.

    # For TF-IDF we try to get submission file_url processed texts
    sub_texts_res = supabase.table("assignment_submissions").select(
        "id, student_id, submission_text"
    ).eq("assignment_id", assignment_id).neq("id", submission_id).execute()

    sub_text_map = {
        s["id"]: s.get("submission_text", "") or ""
        for s in (sub_texts_res.data or [])
    }
    existing_texts_raw = [sub_text_map.get(s["id"], "") for s in existing_subs]

    # ------------------------------------------------------------------
    # 3. Stage 1 — TF-IDF Structural Similarity
    # ------------------------------------------------------------------
    structural_score, best_structural_idx = compute_tfidf_similarity(
        processed_text, [preprocess_text(t) for t in existing_texts_raw]
    )
    logger.info(f"Stage 1 structural similarity: {structural_score}")

    matched_student_id: Optional[str] = None
    semantic_score: Optional[float] = None

    if structural_score < STAGE1_THRESHOLD:
        # Low risk — skip OpenAI entirely
        risk_level = "Low"
        action_taken = risk_to_status(risk_level)
        logger.info("Stage 1 score below threshold. Skipping Stage 2.")
    else:
        # ------------------------------------------------------------------
        # 4. Stage 2 — OpenAI Semantic Similarity
        # ------------------------------------------------------------------
        logger.info("Stage 1 score >= threshold. Running Stage 2 (OpenAI).")
        new_embedding = generate_embedding(processed_text)

        if new_embedding:
            # Store embedding in DB for the current submission
            supabase.table("assignment_submissions").update(
                {"embedding": new_embedding}
            ).eq("id", submission_id).execute()

            # Also store processed text for future TF-IDF comparisons
            supabase.table("assignment_submissions").update(
                {"submission_text": processed_text[:50000]}  # cap at 50k chars
            ).eq("id", submission_id).execute()

            # Compare against subs that have stored embeddings
            semantic_score, matched_student_id = find_best_semantic_match(
                new_embedding, existing_subs
            )
            # If structural match index found, prefer that student_id
            if best_structural_idx >= 0 and best_structural_idx < len(existing_subs):
                matched_student_id = existing_subs[best_structural_idx].get("student_id")

        else:
            # OpenAI failed — fall back to structural result
            logger.warning("OpenAI embedding generation failed. Using structural fallback.")

        risk_level = classify_risk(structural_score, semantic_score)
        action_taken = risk_to_status(risk_level)

    # ------------------------------------------------------------------
    # 5. Update submission record with plagiarism result
    # ------------------------------------------------------------------
    update_payload = {
        "plagiarism_risk": risk_level,
        "plagiarism_similarity": semantic_score if semantic_score is not None else structural_score,
        "plagiarism_status": action_taken,
    }
    if matched_student_id:
        update_payload["plagiarism_matched_student_id"] = matched_student_id

    supabase.table("assignment_submissions").update(update_payload).eq("id", submission_id).execute()

    # ------------------------------------------------------------------
    # 6. Take action based on risk
    # ------------------------------------------------------------------
    if risk_level == "High":
        # Notify the teacher
        _notify_teacher_flagged(supabase, assignment_id, submission_id, current_user.user_id, semantic_score or structural_score)

    return {
        "structural_similarity": structural_score,
        "semantic_similarity": semantic_score,
        "matched_student_id": matched_student_id,
        "risk_level": risk_level,
        "action_taken": action_taken,
    }


# ---------------------------------------------------------------------------
# Teacher notification helper
# ---------------------------------------------------------------------------
def _notify_teacher_flagged(
    supabase: Client,
    assignment_id: str,
    submission_id: str,
    student_id: str,
    similarity: float,
):
    """Insert a notification for the teacher when a submission is flagged."""
    try:
        # Get assignment + teacher info
        assign_res = supabase.table("assignments").select(
            "title, course_id, courses(teacher_id)"
        ).eq("id", assignment_id).single().execute()

        if not assign_res.data:
            return

        assign = assign_res.data
        teacher_id = assign.get("courses", {}).get("teacher_id")
        assign_title = assign.get("title", "Assignment")

        if not teacher_id:
            return

        # Get student name
        student_res = supabase.table("profiles").select("full_name").eq("id", student_id).single().execute()
        student_name = student_res.data.get("full_name", "A student") if student_res.data else "A student"

        notification = {
            "user_id": teacher_id,
            "title": f"🚨 Plagiarism Alert: {assign_title}",
            "message": f"{student_name}'s submission was flagged with {round(similarity * 100)}% similarity. Please review.",
            "type": "plagiarism_alert",
            "is_read": False,
            "data": {
                "assignment_id": assignment_id,
                "submission_id": submission_id,
                "student_id": student_id,
                "similarity": round(similarity, 4),
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        supabase.table("notifications").insert(notification).execute()
        logger.info(f"Teacher {teacher_id} notified of plagiarism flag.")

    except Exception as e:
        logger.error(f"Failed to notify teacher: {e}")


# ---------------------------------------------------------------------------
# Teacher — get flagged submissions
# ---------------------------------------------------------------------------
@router.get("/flagged/{teacher_id}")
async def get_flagged_submissions(
    teacher_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Get all flagged/moderate plagiarism submissions for a teacher's courses."""
    supabase = get_supabase()
    try:
        # Get teacher's courses
        courses_res = supabase.table("courses").select("id").eq("teacher_id", teacher_id).execute()
        course_ids = [c["id"] for c in courses_res.data or []]
        if not course_ids:
            return []

        # Get assignments for those courses
        assign_res = supabase.table("assignments").select("id, title, course_id").in_("course_id", course_ids).execute()
        assign_ids = [a["id"] for a in assign_res.data or []]
        assign_map = {a["id"]: a for a in (assign_res.data or [])}

        if not assign_ids:
            return []

        # Get flagged submissions
        subs_res = supabase.table("assignment_submissions").select(
            "id, assignment_id, student_id, plagiarism_risk, plagiarism_similarity, plagiarism_status, plagiarism_matched_student_id, submitted_at"
        ).in_("assignment_id", assign_ids).in_(
            "plagiarism_risk", ["High", "Moderate"]
        ).execute()

        results = []
        for sub in (subs_res.data or []):
            assign_info = assign_map.get(sub["assignment_id"], {})
            # Get student name
            student_res = supabase.table("profiles").select("full_name, email").eq(
                "id", sub["student_id"]
            ).execute()
            student = student_res.data[0] if student_res.data else {}

            results.append({
                "submission_id": sub["id"],
                "student_id": sub["student_id"],
                "student_name": student.get("full_name", "Unknown"),
                "assignment_id": sub["assignment_id"],
                "assignment_title": assign_info.get("title", "Unknown"),
                "course_id": assign_info.get("course_id"),
                "plagiarism_risk": sub["plagiarism_risk"],
                "plagiarism_similarity": sub["plagiarism_similarity"],
                "plagiarism_status": sub["plagiarism_status"],
                "submitted_at": sub["submitted_at"],
            })

        results.sort(key=lambda x: x["plagiarism_similarity"] or 0, reverse=True)
        return results

    except Exception as e:
        logger.error(f"Error fetching flagged submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch flagged submissions")


# ---------------------------------------------------------------------------
# Teacher — approve / reject submission
# ---------------------------------------------------------------------------
@router.post("/review/{submission_id}")
async def review_submission(
    submission_id: str,
    action: str = Form(...),    # "approve" or "reject"
    remark: str = Form(""),
    current_user: TokenData = Depends(get_current_user),
):
    """Teacher approves or rejects a flagged submission."""
    supabase = get_supabase()
    try:
        if action not in ("approve", "reject"):
            raise HTTPException(status_code=400, detail="action must be 'approve' or 'reject'")

        new_status = "Approved by Teacher" if action == "approve" else "Rejected by Teacher"
        update = {"plagiarism_status": new_status}
        if remark:
            update["teacher_remark"] = remark

        supabase.table("assignment_submissions").update(update).eq("id", submission_id).execute()
        return {"message": f"Submission {action}d successfully.", "status": new_status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Review action error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update submission")
