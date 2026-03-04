import os
import sys
import numpy as np

# Add the backend directory to path so we can import modules if needed
sys.path.append("d:/Learn_Sphere/backend")

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("d:/Learn_Sphere/backend/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

def _complementarity(vA: np.ndarray, vB: np.ndarray) -> float:
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
    strong = [labels[i] for i, v in enumerate(vector) if v >= threshold_strong]
    weak   = [labels[i] for i, v in enumerate(vector) if v <= threshold_weak and v > 0]
    return {"strong": strong, "weak": weak}

try:
    # Get course
    courses = supabase.table("courses").select("id, title").ilike("title", "%Advanced React%").execute()
    if not courses.data:
        print("Course not found")
        sys.exit(1)
        
    course_id = courses.data[0]["id"]
    print(f"Course: {courses.data[0]['title']} ({course_id})")

    # Get enrollments
    enrollments = supabase.table("enrollments").select("student_id").eq("course_id", course_id).eq("status", "active").execute()
    enrolled_ids = [e["student_id"] for e in enrollments.data]
    print(f"Enrolled students: {len(enrolled_ids)}")
    
    if len(enrolled_ids) < 2:
        print("Not enough students")
        sys.exit(1)

    # Pick a student to be the requester
    student_id = enrolled_ids[0]
    print(f"Requester Student ID: {student_id}")

    quizzes = supabase.table("quizzes").select("id, title").eq("course_id", course_id).execute().data
    assignments = supabase.table("assignments").select("id, title, max_score").eq("course_id", course_id).eq("status", "active").execute().data
    
    quiz_labels   = [f"Quiz: {q['title']}" for q in quizzes]
    assign_labels = [f"Assignment: {a['title']}" for a in assignments]
    all_labels    = quiz_labels + assign_labels
    
    quiz_ids = [q["id"] for q in quizzes]
    quiz_subs = []
    if quiz_ids:
        quiz_subs = supabase.table("quiz_submissions").select("student_id, quiz_id, score, total_marks").in_("quiz_id", quiz_ids).execute().data
        
    assign_ids = [a["id"] for a in assignments]
    asgn_subs = []
    if assign_ids:
        asgn_subs = supabase.table("assignment_submissions").select("student_id, assignment_id, score").in_("assignment_id", assign_ids).execute().data

    n_dims = len(all_labels)
    student_vecs = {sid: np.zeros(n_dims, dtype=float) for sid in enrolled_ids}

    # Quiz loop
    quiz_idx = {q["id"]: i for i, q in enumerate(quizzes)}
    for sub in quiz_subs:
        sid = sub["student_id"]
        qidx = quiz_idx.get(sub["quiz_id"])
        if sid in student_vecs and qidx is not None and sub["total_marks"]:
            student_vecs[sid][qidx] = (sub["score"] or 0) / sub["total_marks"]

    # Assgn loop
    assign_idx = {a["id"]: len(quizzes) + i for i, a in enumerate(assignments)}
    for sub in asgn_subs:
        sid = sub["student_id"]
        aidx = assign_idx.get(sub["assignment_id"])
        asgn = next((a for a in assignments if a["id"] == sub["assignment_id"]), None)
        if sid in student_vecs and aidx is not None and asgn and asgn["max_score"] and sub["score"] is not None:
            student_vecs[sid][aidx] = sub["score"] / asgn["max_score"]

    print("Vectors built.")

    # Compute complementarity
    vMe = student_vecs.get(student_id, np.zeros(n_dims, dtype=float))
    my_skills = _label_skills(vMe, all_labels)

    candidates = []
    for sid, vec in student_vecs.items():
        if sid == student_id:
            continue
        score = _complementarity(vMe, vec)
        candidates.append((sid, score, vec))
        
    print("Complementarity computed.")

    candidates.sort(key=lambda x: x[1], reverse=True)
    top = candidates[:3]

    top_ids = [c[0] for c in top]
    profiles_res = supabase.table("profiles").select("id, full_name, email, bio, avatar_url").in_("id", top_ids).execute()
    profile_map  = {p["id"]: p for p in (profiles_res.data or [])}
    print("Profiles mapped.")
    
    matches = []
    for sid, score, vec in top:
        prof   = profile_map.get(sid, {})
        skills = _label_skills(vec, all_labels)
        can_help_me = [
            lbl for i, lbl in enumerate(all_labels)
            if vec[i] >= 0.65 and vMe[i] <= 0.45
        ]
        i_help_them = [
            lbl for i, lbl in enumerate(all_labels)
            if vMe[i] >= 0.65 and vec[i] <= 0.45
        ]
        first_name = (prof.get("full_name") or "Student").split()[0]
        matches.append({
            "student_id":       sid,
            "name":             first_name,
        })
        
    print(matches)
    print("SUCCESS: No crash occurred!")

except Exception as e:
    import traceback
    traceback.print_exc()
