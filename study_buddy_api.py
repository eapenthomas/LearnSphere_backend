from fastapi import APIRouter, HTTPException, Query, Depends
from auth_middleware import get_current_user, TokenData
import os
from supabase import create_client, Client
import logging
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/study-buddy", tags=["Study Buddy"])
logger = logging.getLogger(__name__)

def get_supabase_client() -> Client:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase configuration")
    return create_client(supabase_url, supabase_key)

# ─── Requests Models ──────────────────────────────────────────────────────────

class BuddyRequestCreate(BaseModel):
    receiver_id: str
    course_id: str

class BuddyRequestAction(BaseModel):
    action: str # "accept" or "reject"

class MessageCreate(BaseModel):
    receiver_id: str
    course_id: str
    content: str

class SessionCreate(BaseModel):
    course_id: str
    topic: str
    start_time: str
    duration_minutes: int
    meeting_link: Optional[str] = None
    participant_ids: list[str] = []

# ─── Buddy Requests Endpoints ─────────────────────────────────────────────────

@router.post("/request")
async def send_buddy_request(
    data: BuddyRequestCreate,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        if data.receiver_id == current_user.user_id:
            raise HTTPException(status_code=400, detail="Cannot send request to yourself")
            
        # Check for existing request in either direction
        ex1 = supabase.table("study_buddy_requests").select("*").eq("course_id", data.course_id).eq("sender_id", current_user.user_id).eq("receiver_id", data.receiver_id).execute()
        ex2 = supabase.table("study_buddy_requests").select("*").eq("course_id", data.course_id).eq("sender_id", data.receiver_id).eq("receiver_id", current_user.user_id).execute()
        all_existing = (ex1.data or []) + (ex2.data or [])
        
        if all_existing:
            req = all_existing[0]
            if req["status"] == "pending":
                raise HTTPException(status_code=400, detail="A request is already pending between you two.")
            elif req["status"] == "accepted":
                raise HTTPException(status_code=400, detail="You are already buddies!")
            elif req["status"] == "rejected":
                # If it was rejected, we might allow a new one depending on policy, but let's just error for now.
                raise HTTPException(status_code=400, detail="A previous request was rejected.")

        res = supabase.table("study_buddy_requests").insert({
            "sender_id": current_user.user_id,
            "receiver_id": data.receiver_id,
            "course_id": data.course_id,
            "status": "pending"
        }).execute()
        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending buddy request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{request_id}/respond")
async def respond_to_request(
    request_id: str,
    action_data: BuddyRequestAction,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        if action_data.action not in ["accept", "reject"]:
            raise HTTPException(status_code=400, detail="Invalid action")
            
        req = supabase.table("study_buddy_requests").select("*").eq("id", request_id).execute()
        if not req.data:
            raise HTTPException(status_code=404, detail="Request not found")
            
        if req.data[0]["receiver_id"] != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not your request to respond to")
            
        res = supabase.table("study_buddy_requests").update({
            "status": "accepted" if action_data.action == "accept" else "rejected"
        }).eq("id", request_id).execute()
        
        return res.data[0]
    except Exception as e:
        logger.error(f"Error responding to request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections/{course_id}")
async def get_connections(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        # Get all requests involving this user in this course
        reqs1 = supabase.table("study_buddy_requests").select("id, sender_id, receiver_id, status, created_at").eq("course_id", course_id).eq("sender_id", current_user.user_id).neq("status", "rejected").execute()
        reqs2 = supabase.table("study_buddy_requests").select("id, sender_id, receiver_id, status, created_at").eq("course_id", course_id).eq("receiver_id", current_user.user_id).neq("status", "rejected").execute()
        
        all_reqs = {r["id"]: r for r in ((reqs1.data or []) + (reqs2.data or []))}.values()
        
        # We need to enrich this with profile info
        results = []
        if not all_reqs:
            return results
            
        buddy_ids = [r["sender_id"] if r["receiver_id"] == current_user.user_id else r["receiver_id"] for r in all_reqs]
        prof_res = supabase.table("profiles").select("id, full_name, profile_picture").in_("id", buddy_ids).execute()
        profiles = {p["id"]: p for p in (prof_res.data or [])}
        
        for r in all_reqs:
            other_id = r["sender_id"] if r["receiver_id"] == current_user.user_id else r["receiver_id"]
            p = profiles.get(other_id, {})
            results.append({
                "request_id": r["id"],
                "status": r["status"],
                "is_sender": r["sender_id"] == current_user.user_id,
                "buddy_id": other_id,
                "buddy_name": p.get("full_name", "Unknown"),
                "buddy_avatar": p.get("profile_picture"),
                "created_at": r["created_at"]
            })
        return results
    except Exception as e:
        logger.error(f"Error getting connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Messaging Endpoints ──────────────────────────────────────────────────────

@router.post("/message")
async def send_message(
    data: MessageCreate,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        # Verify they are actually buddies
        buddy_check = supabase.table("study_buddy_requests").select("id").eq("course_id", data.course_id).eq("status", "accepted").in_("sender_id", [current_user.user_id, data.receiver_id]).in_("receiver_id", [current_user.user_id, data.receiver_id]).execute()
        
        if not buddy_check.data:
            raise HTTPException(status_code=403, detail="You can only message accepted study buddies in this course.")
            
        res = supabase.table("buddy_messages").insert({
            "sender_id": current_user.user_id,
            "receiver_id": data.receiver_id,
            "course_id": data.course_id,
            "content": data.content
        }).execute()
        return res.data[0]
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{course_id}/{buddy_id}")
async def get_messages(
    course_id: str,
    buddy_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        # Mark messages to me as read
        supabase.table("buddy_messages").update({"is_read": True}).eq("course_id", course_id).eq("receiver_id", current_user.user_id).eq("sender_id", buddy_id).eq("is_read", False).execute()
        
        msgs1 = supabase.table("buddy_messages").select("*").eq("course_id", course_id).eq("sender_id", current_user.user_id).eq("receiver_id", buddy_id).execute()
        msgs2 = supabase.table("buddy_messages").select("*").eq("course_id", course_id).eq("sender_id", buddy_id).eq("receiver_id", current_user.user_id).execute()
        
        all_msgs = (msgs1.data or []) + (msgs2.data or [])
        all_msgs.sort(key=lambda x: x["created_at"])
        
        return all_msgs
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── Scheduling Endpoints ─────────────────────────────────────────────────────

@router.post("/session")
async def create_session(
    data: SessionCreate,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        # Create session
        session_data = {
            "course_id": data.course_id,
            "host_id": current_user.user_id,
            "topic": data.topic,
            "start_time": data.start_time,
            "duration_minutes": data.duration_minutes,
            "meeting_link": data.meeting_link
        }
        res = supabase.table("study_sessions").insert(session_data).execute()
        session_id = res.data[0]["id"]
        
        # Add participants
        participants = [{"session_id": session_id, "student_id": current_user.user_id, "status": "going"}]
        for pid in data.participant_ids:
            if pid != current_user.user_id:
                 participants.append({"session_id": session_id, "student_id": pid, "status": "maybe"})
                 
        if participants:
            supabase.table("study_session_participants").insert(participants).execute()
            
        return res.data[0]
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{course_id}")
async def get_sessions(
    course_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    supabase = get_supabase_client()
    try:
        # Get sessions where user is participant
        parts = supabase.table("study_session_participants").select("session_id, status").eq("student_id", current_user.user_id).execute()
        session_ids = [p["session_id"] for p in (parts.data or [])]
        
        if not session_ids:
            return []
            
        sessions = supabase.table("study_sessions").select("*").in_("id", session_ids).eq("course_id", course_id).eq("status", "scheduled").order("start_time").execute()
        
        # Enrich with host name
        results = []
        if sessions.data:
            host_ids = [s["host_id"] for s in sessions.data]
            hosts_res = supabase.table("profiles").select("id, full_name").in_("id", host_ids).execute()
            hosts = {h["id"]: h["full_name"] for h in (hosts_res.data or [])}
            
            for s in sessions.data:
                host_name = hosts.get(s["host_id"], "Unknown")
                status = next((p["status"] for p in parts.data if p["session_id"] == s["id"]), "maybe")
                results.append({
                    **s,
                    "host_name": host_name,
                    "my_status": status
                })
            
        return results
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
