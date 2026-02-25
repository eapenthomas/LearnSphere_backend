from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/dashboard-optimized", tags=["Dashboard Optimization"])

# Initialize Supabase (reusing existing env vars)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@router.get("/student/{student_id}")
async def get_student_dashboard_consolidated(student_id: str):
    """
    Consolidated student dashboard data in massive parallel/batch fetching.
    """
    try:
        # Fetch enrollments, profiles (self), and assignments in minimal calls
        # We can use Supabase's joining feature: select('*, courses(*)')
        
        # 1. Get Enrollments with Course details and Progress
        enrollments_res = supabase.table("enrollments").select(
            "*, courses(*), course_progress(*)"
        ).eq("student_id", student_id).eq("status", "active").execute()
        enrollments = enrollments_res.data or []
        
        course_ids = [e["course_id"] for e in enrollments]
        
        # 2. Get Assignments for these courses
        assignments = []
        if course_ids:
            # Get assignments AND their submissions for this student in one join
            # Note: Supabase doesn't support complex nested filters well in one select, 
            # so we'll do 2 parallel calls for assignments and submissions if needed.
            assignments_res = supabase.table("assignments").select("*").in_("course_id", course_ids).eq("status", "active").execute()
            submissions_res = supabase.table("assignment_submissions").select("*").eq("student_id", student_id).in_("assignment_id", [a["id"] for a in assignments_res.data or []]).execute()
            
            sub_map = {s["assignment_id"]: s for s in submissions_res.data or []}
            for a in assignments_res.data or []:
                a_data = a.copy()
                sub = sub_map.get(a["id"])
                a_data["submission_status"] = sub["status"] if sub else "not_submitted"
                a_data["submission_score"] = sub["score"] if sub else None
                assignments.append(a_data)

        # 3. Calculate Stats efficiently
        enrolled_count = len(enrollments)
        total_progress = 0
        total_m_comp = 0
        total_m = 0
        
        for e in enrollments:
            prog = e.get("course_progress", [])
            # course_progress is likely a list if not maybe_single
            if isinstance(prog, list) and prog:
                p_data = prog[0]
                total_progress += p_data.get("overall_progress_percentage", 0)
                # Assume columns exist or use defaults
            elif isinstance(prog, dict):
                total_progress += prog.get("overall_progress_percentage", 0)

        avg_progress = round(total_progress / enrolled_count) if enrolled_count > 0 else 0
        
        completed_assignments = len([a for a in assignments if a["submission_status"] in ["submitted", "reviewed", "graded"]])
        assign_percentage = round((completed_assignments / len(assignments)) * 100) if assignments else 0

        # 4. Construct response
        return {
            "stats": [
                {
                    "title": "Enrolled Courses",
                    "value": str(enrolled_count),
                    "change": f"{enrolled_count} active",
                    "color": "from-blue-500 to-blue-600"
                },
                {
                    "title": "Course Progress",
                    "value": f"{avg_progress}%",
                    "change": "Overall Completion",
                    "color": "from-green-500 to-green-600"
                },
                {
                    "title": "Assignment Progress",
                    "value": f"{assign_percentage}%",
                    "change": f"{completed_assignments}/{len(assignments)} finished",
                    "color": "from-purple-500 to-purple-600"
                }
            ],
            "recent_courses": enrollments[:6], # Already contains courses(*)
            "upcoming_assignments": [a for a in assignments if a["submission_status"] == "not_submitted"][:5]
        }
    except Exception as e:
        print(f"Error in consolidated dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
