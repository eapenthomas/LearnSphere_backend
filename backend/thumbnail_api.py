"""
Thumbnail API
Handles course thumbnail serving and management
"""

import os
import requests
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_key)

# Create router
router = APIRouter(prefix="/api/thumbnails", tags=["thumbnails"])

@router.get("/course/{course_id}")
async def get_course_thumbnail(course_id: str):
    """Get course thumbnail URL or serve the image directly."""
    try:
        # Get course from database
        response = supabase.table("courses").select("thumbnail_url, title").eq("id", course_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        thumbnail_url = response.data.get("thumbnail_url")
        course_title = response.data.get("title", "Course")
        
        if not thumbnail_url:
            # Return a default placeholder image response
            return JSONResponse(
                status_code=200,
                content={
                    "thumbnail_url": None,
                    "message": "No thumbnail available",
                    "course_title": course_title
                }
            )
        
        # Check if it's a Supabase storage URL
        if "supabase.co" in thumbnail_url or "/storage/" in thumbnail_url:
            # For Supabase storage, try to serve directly
            try:
                img_response = requests.get(thumbnail_url, stream=True, timeout=10)
                img_response.raise_for_status()
                
                # Get content type from response
                content_type = img_response.headers.get('content-type', 'image/jpeg')
                
                # Stream the image data
                def generate():
                    for chunk in img_response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                
                return StreamingResponse(
                    generate(),
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                        "Content-Disposition": "inline"  # Display in browser, don't download
                    }
                )
            except Exception as stream_error:
                print(f"Failed to stream Supabase image: {stream_error}")
                # Fallback to URL
                return JSONResponse(
                    status_code=200,
                    content={"thumbnail_url": thumbnail_url}
                )
        else:
            # For external URLs (like Unsplash), return the URL directly
            return JSONResponse(
                status_code=200,
                content={"thumbnail_url": thumbnail_url}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thumbnail: {str(e)}")

@router.get("/course/{course_id}/url")
async def get_course_thumbnail_url(course_id: str):
    """Get course thumbnail URL only (for components that need the URL)."""
    try:
        # Get course from database
        response = supabase.table("courses").select("thumbnail_url").eq("id", course_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Course not found")
        
        thumbnail_url = response.data.get("thumbnail_url")
        
        if not thumbnail_url:
            raise HTTPException(status_code=404, detail="No thumbnail found for this course")
        
        return {
            "course_id": course_id,
            "thumbnail_url": thumbnail_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get thumbnail URL: {str(e)}")
