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

import asyncio

@router.get("/student/{student_id}")
async def get_student_dashboard_consolidated(student_id: str):
    """
    Consolidated student dashboard data in massive parallel/batch fetching.
    """
    try:
        # 1. Get Enrollments with Course details
        enrollments_res = await asyncio.to_thread(
            lambda: supabase.table("enrollments").select("*, courses(*)").eq("student_id", student_id).eq("status", "active").execute()
        )
        enrollments = enrollments_res.data or []
        
        course_ids = [e["course_id"] for e in enrollments]
        
        # 1.5 Fetch course progress, assignments, and submissions concurrently
        assignments = []
        progress_map = {}
        sub_map = {}
        
        if course_ids:
            # We can fetch everything we need for this student in parallel
            def fetch_progress():
                return supabase.table("course_progress").select("*").eq("student_id", student_id).in_("course_id", course_ids).execute()
                
            def fetch_assignments():
                return supabase.table("assignments").select("*").in_("course_id", course_ids).eq("status", "active").execute()
                
            def fetch_submissions():
                return supabase.table("assignment_submissions").select("*").eq("student_id", student_id).execute()
                
            # Run in parallel
            p_res, a_res, s_res = await asyncio.gather(
                asyncio.to_thread(fetch_progress),
                asyncio.to_thread(fetch_assignments),
                asyncio.to_thread(fetch_submissions)
            )
            
            progress_map = {p["course_id"]: p for p in (p_res.data if p_res else [])}
            sub_map = {s["assignment_id"]: s for s in (s_res.data if s_res else [])}
            
            for a in a_res.data or []:
                a_data = a.copy()
                sub = sub_map.get(a["id"])
                a_data["submission_status"] = sub["status"] if sub else "not_submitted"
                a_data["submission_score"] = sub["score"] if sub else None
                assignments.append(a_data)

        for e in enrollments:
            e["course_progress"] = progress_map.get(e["course_id"])

        # 3. Calculate Stats efficiently
        enrolled_count = len(enrollments)
        total_progress = 0
        total_m_comp = 0
        total_m = 0
        
        for e in enrollments:
            prog = e.get("course_progress")
            if prog:
                total_progress += prog.get("overall_progress_percentage", 0)

        avg_progress = round(total_progress / enrolled_count) if enrolled_count > 0 else 0
        
        completed_assignments = len([a for a in assignments if a["submission_status"] in ["submitted", "reviewed", "graded"]])
        assign_percentage = round((completed_assignments / len(assignments)) * 100) if assignments else 0

        # Format recent courses
        formatted_courses = []
        for e in enrollments[:6]:
            c = e.get("courses") or {}
            prog_data = e.get("course_progress")
            prog = prog_data.get("overall_progress_percentage", 0) if prog_data else 0
            
            formatted_courses.append({
                "id": c.get("id", e.get("course_id")),
                "title": c.get("title", "Unknown Course"),
                "instructor": "Course Teacher",
                "nextLesson": "Continue Learning",
                "progress": prog
            })

        # Format upcoming assignments
        formatted_assignments = []
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        course_dict = {e.get("course_id"): (e.get("courses") or {}).get("title", "Unknown Course") for e in enrollments}

        raw_assignments = [a for a in assignments if a["submission_status"] == "not_submitted"]
        for a in raw_assignments[:5]:
            due_date_str = a.get("due_date")
            days_until = 0
            formatted_date = "No Due Date"
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    days_until = max(0, (due_date - now).days)
                    formatted_date = due_date.strftime("%b %d")
                except:
                    pass
                    
            formatted_assignments.append({
                "id": a["id"],
                "title": a.get("title", "Assignment"),
                "type": "assignment",
                "daysUntil": days_until,
                "dueDate": formatted_date,
                "course": course_dict.get(a.get("course_id"), "Unknown Course")
            })

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
            "recent_courses": formatted_courses,
            "upcoming_assignments": formatted_assignments
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in consolidated dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
