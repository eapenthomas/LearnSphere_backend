"""
Peer Study Matchmaker API
Pairs students within a course based on complementary quiz/assignment performance vectors.
Algorithm: complementarity = 0.6 × joint_coverage + 0.4 × profile_diversity
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from auth_middleware import get_current_user, TokenData
import os
from supabase import create_client, Client
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import cluster_utils

def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase configuration")
    return create_client(supabase_url, supabase_key)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/peer-match", tags=["Peer Match"])


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _complementarity(vA: np.ndarray, vB: np.ndarray) -> float:
    """
    Score how complementary two skill vectors are (0–1, higher = better match).
    - coverage  : how well they together cover all topics
    - diversity : how different their profiles are (1 - cosine_sim)
    """
    coverage = float(np.mean(np.maximum(vA, vB)))
    dot = float(np.dot(vA, vB))
    normA = float(np.linalg.norm(vA))
    normB = float(np.linalg.norm(vB))
    if normA == 0 or normB == 0:
        diversity = 1.0
    else:
        diversity = 1.0 - dot / (normA * normB)
    return round(0.6 * coverage + 0.4 * diversity, 4)


def _label_skills(vector: np.ndarray, labels: list[str], threshold_strong=0.7, threshold_weak=0.4) -> dict:
    """Partition topic labels into strong / average / weak."""
    strong = [labels[i] for i, v in enumerate(vector) if v >= threshold_strong]
    weak   = [labels[i] for i, v in enumerate(vector) if v <= threshold_weak and v > 0]
    return {"strong": strong, "weak": weak}


# ─── Student's enrolled courses (helper for frontend dropdown) ────────────────

@router.get("/courses/{student_id}")
async def get_student_courses_for_match(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    """Return enrolled courses for the peer-match course picker."""
    supabase = get_supabase_client()
    try:
        # Step 1: get enrolled course IDs
        enroll_res = supabase.table("enrollments").select("course_id").eq("student_id", student_id).eq("status", "active").execute()
        course_ids = list({e["course_id"] for e in (enroll_res.data or [])})
        if not course_ids:
            return []

        # Step 2: get course titles
        courses_res = supabase.table("courses").select("id, title").in_("id", course_ids).execute()
        courses = [{"id": c["id"], "title": c.get("title", "Unknown")} for c in (courses_res.data or [])]
        return courses
    except Exception as e:
        logger.error(f"Error fetching courses for peer match: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch courses")


# ─── Main endpoint ────────────────────────────────────────────────────────────
@router.get("/{course_id}")
async def get_peer_matches(
    course_id: str,
    student_id: str = Query(...),
    top_n: int = Query(3, ge=1, le=10),
    current_user: TokenData = Depends(get_current_user),
):
    """
    Returns the top-N most complementary study partners for `student_id`
    within `course_id`, ranked by complementarity score.
    """
    supabase = get_supabase_client()

    try:
        # ── 1. Enrolled students in this course ──────────────────────────────
        enroll_res = supabase.table("enrollments").select("student_id").eq("course_id", course_id).eq("status", "active").execute()
        enrolled_ids = list({e["student_id"] for e in (enroll_res.data or [])})

        if student_id not in enrolled_ids:
            raise HTTPException(status_code=403, detail="You are not enrolled in this course.")
        if len(enrolled_ids) < 2:
            return {"matches": [], "message": "Not enough students enrolled to find matches."}

        # ── 2. Quizzes in this course ─────────────────────────────────────────
        quiz_res = supabase.table("quizzes").select("id, title").eq("course_id", course_id).execute()
        quizzes  = quiz_res.data or []

        # ── 3. Assignments in this course ────────────────────────────────────
        assign_res = supabase.table("assignments").select("id, title, max_score").eq("course_id", course_id).eq("status", "active").execute()
        assignments = assign_res.data or []

        if not quizzes and not assignments:
            return {"matches": [], "message": "No quizzes or assignments found in this course yet."}

        # ── 4. Build dimension labels ─────────────────────────────────────────
        quiz_labels   = [f"Quiz: {q['title']}" for q in quizzes]
        assign_labels = [f"Assignment: {a['title']}" for a in assignments]
        all_labels    = quiz_labels + assign_labels
        n_dims        = len(all_labels)

        # ── 5. Fetch all quiz submissions for this course ─────────────────────
        quiz_ids = [q["id"] for q in quizzes]
        if quiz_ids:
            qs_res = supabase.table("quiz_submissions").select("student_id, quiz_id, score, total_marks").in_("quiz_id", quiz_ids).execute()
            quiz_subs = qs_res.data or []
        else:
            quiz_subs = []

        # ── 6. Fetch all assignment submissions for this course ───────────────
        assign_ids = [a["id"] for a in assignments]
        if assign_ids:
            as_res = supabase.table("assignment_submissions").select("student_id, assignment_id, score").in_("assignment_id", assign_ids).execute()
            asgn_subs = as_res.data or []
        else:
            asgn_subs = []

        # ── 7. Build score matrix  student_id → np.array[n_dims] ─────────────
        def empty_vec():
            return np.zeros(n_dims, dtype=float)

        student_vecs: dict[str, np.ndarray] = {sid: empty_vec() for sid in enrolled_ids}

        # Fill quiz scores (col 0 … len(quizzes)-1)
        quiz_idx = {q["id"]: i for i, q in enumerate(quizzes)}
        for sub in quiz_subs:
            sid  = sub["student_id"]
            qidx = quiz_idx.get(sub["quiz_id"])
            if sid in student_vecs and qidx is not None and sub["total_marks"]:
                student_vecs[sid][qidx] = (sub["score"] or 0) / sub["total_marks"]

        # Fill assignment scores (col len(quizzes) … n_dims-1)
        assign_idx = {a["id"]: len(quizzes) + i for i, a in enumerate(assignments)}
        for sub in asgn_subs:
            sid  = sub["student_id"]
            aidx = assign_idx.get(sub["assignment_id"])
            asgn = next((a for a in assignments if a["id"] == sub["assignment_id"]), None)
            if sid in student_vecs and aidx is not None and asgn and asgn["max_score"] and sub["score"] is not None:
                student_vecs[sid][aidx] = sub["score"] / asgn["max_score"]

        # ── 8. Compute complementarity for the requesting student ─────────────
        vMe = student_vecs.get(student_id, empty_vec())
        my_skills = _label_skills(vMe, all_labels)
        
        # Determine cluster for requesting student
        # We need their aggegated features. Since we have vMe, we can compute averages if we know which are quizzes vs assignments
        # To avoid re-fetching, we can approximate avg straight from valid scores in vMe
        my_q_scores = [vMe[i] for i in range(len(quizzes)) if vMe[i] > 0]
        my_a_scores = [vMe[len(quizzes)+i] for i in range(len(assignments)) if vMe[len(quizzes)+i] > 0]
        
        my_avg_q = float(np.mean(my_q_scores)) if my_q_scores else 0.0
        my_avg_a = float(np.mean(my_a_scores)) if my_a_scores else 0.0
        my_comp_rate = len(my_a_scores) / len(assignments) if assignments else 0.0
        
        my_extended_features = cluster_utils.build_extended_features(vMe, my_avg_q, my_comp_rate, my_avg_a)
        # But wait, our cluster model is trained ONLY on [avg_q, avg_a, comp_rate]!
        my_cluster_features = np.array([my_avg_q, my_avg_a, my_comp_rate])
        my_cluster_id = cluster_utils.predict_cluster(my_cluster_features)

        candidates = []
        for sid, vec in student_vecs.items():
            if sid == student_id:
                continue
            
            # Peer's features
            peer_q = [vec[i] for i in range(len(quizzes)) if vec[i] > 0]
            peer_a = [vec[len(quizzes)+i] for i in range(len(assignments)) if vec[len(quizzes)+i] > 0]
            peer_avg_q = float(np.mean(peer_q)) if peer_q else 0.0
            peer_avg_a = float(np.mean(peer_a)) if peer_a else 0.0
            peer_comp_rate = len(peer_a) / len(assignments) if assignments else 0.0
            
            peer_cluster_features = np.array([peer_avg_q, peer_avg_a, peer_comp_rate])
            peer_cluster_id = cluster_utils.predict_cluster(peer_cluster_features)
            
            # Base score
            score = _complementarity(vMe, vec)
            
            # Cross-cluster bonus (encourage pairing students from different profiles)
            if my_cluster_id != -1 and peer_cluster_id != -1 and my_cluster_id != peer_cluster_id:
                score += 0.05
                
            candidates.append((sid, score, vec, peer_cluster_id))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:top_n]

        # ── 9. Fetch profile names and details for matched students ─────────────
        top_ids = [c[0] for c in top]
        profiles_res = supabase.table("profiles").select("id, full_name, email, profile_picture").in_("id", top_ids).execute()
        profile_map  = {p["id"]: p for p in (profiles_res.data or [])}

        # ── 10. Build response ────────────────────────────────────────────────
        matches = []
        for sid, score, vec, peer_c_id in top:
            prof   = profile_map.get(sid, {})
            skills = _label_skills(vec, all_labels)
            # Topics where they can help me (they're strong, I'm weak)
            can_help_me = [
                lbl for i, lbl in enumerate(all_labels)
                if vec[i] >= 0.65 and vMe[i] <= 0.45
            ]
            # Topics I can help them (I'm strong, they're weak)
            i_help_them = [
                lbl for i, lbl in enumerate(all_labels)
                if vMe[i] >= 0.65 and vec[i] <= 0.45
            ]
            first_name = (prof.get("full_name") or "Student").split()[0]
            matches.append({
                "student_id":       sid,
                "name":             first_name,
                "full_name":        prof.get("full_name") or "Student",
                "email":            prof.get("email") or "",
                "bio":              "",
                "avatar_url":       prof.get("profile_picture"),
                "compatibility_pct": min(100, round(score * 100)),
                "their_strengths":  skills["strong"],
                "their_weaknesses": skills["weak"],
                "can_help_me":      can_help_me,
                "i_help_them":      i_help_them,
                "peer_cluster":     peer_c_id,
                "cluster_name":     cluster_utils.cluster_name(peer_c_id, 3) if peer_c_id != -1 else ""
            })

        return {
            "my_strengths": my_skills["strong"],
            "my_weaknesses": my_skills["weak"],
            "my_cluster": my_cluster_id,
            "my_cluster_name": cluster_utils.cluster_name(my_cluster_id, 3) if my_cluster_id != -1 else "",
            "matches": matches,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Peer match error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to compute peer matches")



