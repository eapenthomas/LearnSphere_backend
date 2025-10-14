"""
Google Authentication Service - Complete Rewrite
Handles Google OAuth login and signup with robust error handling
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import os
from backend.models import AuthResponse
from backend.auth import supabase, supabase_admin

router = APIRouter()


class GoogleAuthURL(BaseModel):
    url: str


@router.get("/google/url", response_model=GoogleAuthURL)
async def get_google_auth_url():
    """
    Generate Google OAuth URL for authentication
    
    Returns:
        GoogleAuthURL: Object containing the OAuth URL
    """
    try:
        # Get frontend URL from environment
        frontend_url = os.environ.get('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')
        
        print(f"🔗 Generating Google OAuth URL")
        print(f"📍 Redirect URL: {frontend_url}/auth/callback")
        
        # Generate OAuth URL using Supabase
        auth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": f"{frontend_url}/auth/callback",
                "query_params": {
                    "access_type": "offline",
                    "prompt": "consent"
                }
            }
        })
        
        if not auth_response or not hasattr(auth_response, 'url'):
            raise Exception("Failed to generate OAuth URL from Supabase")
        
        print(f"✅ OAuth URL generated successfully")
        return GoogleAuthURL(url=auth_response.url)
        
    except Exception as e:
        print(f"❌ Error generating Google OAuth URL: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate Google OAuth URL: {str(e)}"
        )


@router.post("/google/callback", response_model=AuthResponse)
async def handle_google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(None, description="Optional state parameter")
):
    """
    Handle Google OAuth callback and authenticate user
    
    Args:
        code: Authorization code from Google OAuth
        state: Optional state parameter for security
        
    Returns:
        AuthResponse: User authentication data including access token
    """
    try:
        print(f"🔄 Processing Google OAuth callback")
        print(f"📝 Authorization code received: {code[:20]}...")
        
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Exchange authorization code for session
        print(f"🔄 Exchanging code for session...")
        auth_response = supabase.auth.exchange_code_for_session(code)
        
        # Validate response
        if not auth_response or not hasattr(auth_response, 'user') or not auth_response.user:
            print("❌ Invalid OAuth response - no user data")
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth callback - no user data received from Google"
            )
        
        if not hasattr(auth_response, 'session') or not auth_response.session:
            print("❌ Invalid OAuth response - no session data")
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth callback - no session data received"
            )
        
        # Extract user information
        user_id = auth_response.user.id
        email = auth_response.user.email
        access_token = auth_response.session.access_token
        
        if not email:
            print("❌ No email in OAuth response")
            raise HTTPException(
                status_code=400,
                detail="No email found in Google account"
            )
        
        print(f"✅ OAuth successful for: {email}")
        print(f"👤 User ID: {user_id}")
        
        # Extract full name from metadata
        user_metadata = auth_response.user.user_metadata or {}
        full_name = (
            user_metadata.get("full_name") or
            user_metadata.get("name") or
            user_metadata.get("display_name") or
            email.split("@")[0]
        )
        
        print(f"👤 Full name extracted: {full_name}")
        
        # Check if profile exists in database
        print(f"🔍 Checking for existing profile...")
        profile_response = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()
        
        if not profile_response.data or len(profile_response.data) == 0:
            # Create new profile for Google user
            print(f"📝 Creating new profile for Google user: {email}")
            
            profile_data = {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "role": "student",  # Default role
                "approval_status": "approved",
                "is_active": True
            }
            
            try:
                insert_response = supabase_admin.table("profiles").insert(profile_data).execute()
                
                if insert_response.data and len(insert_response.data) > 0:
                    print(f"✅ Profile created successfully for {email}")
                else:
                    print(f"⚠️ Profile insert returned no data, but no error")
                
            except Exception as create_error:
                print(f"❌ Error creating profile: {create_error}")
                # Continue anyway - profile might have been created by trigger
            
            # Return response for new user
            return AuthResponse(
                access_token=access_token,
                user_id=user_id,
                role="student",
                full_name=full_name,
                email=email,
                message="Google login successful - Welcome to LearnSphere!",
                approval_status="approved",
                is_active=True
            )
            
        else:
            # Profile exists - validate and return
            profile = profile_response.data[0]
            print(f"✅ Found existing profile for {email}")
            print(f"👤 Role: {profile.get('role')}")
            print(f"📊 Status: Active={profile.get('is_active')}, Approval={profile.get('approval_status')}")
            
            # Check if account is active
            if not profile.get("is_active", True):
                print(f"❌ Account disabled for {email}")
                raise HTTPException(
                    status_code=403,
                    detail="Your account has been disabled. Please contact support for assistance."
                )
            
            # Check teacher approval status
            user_role = profile.get("role", "student")
            approval_status = profile.get("approval_status", "approved")
            
            if user_role == "teacher" and approval_status != "approved":
                print(f"⏳ Teacher account pending approval: {email}")
                # Return response but indicate pending status
                return AuthResponse(
                    access_token=access_token,
                    user_id=user_id,
                    role=user_role,
                    full_name=profile.get("full_name", full_name),
                    email=email,
                    message="Google login successful - Teacher approval pending",
                    approval_status=approval_status,
                    is_active=True
                )
            
            # Update profile with latest Google data if needed
            update_data = {}
            if profile.get("full_name") != full_name and full_name != email.split("@")[0]:
                update_data["full_name"] = full_name
            if profile.get("email") != email:
                update_data["email"] = email
            
            if update_data:
                try:
                    supabase_admin.table("profiles").update(update_data).eq("id", user_id).execute()
                    print(f"✅ Profile updated for {email}")
                except Exception as update_error:
                    print(f"⚠️ Profile update failed (non-critical): {update_error}")
            
            # Return successful response
            print(f"✅ Google login successful for {email}")
            return AuthResponse(
                access_token=access_token,
                user_id=user_id,
                role=user_role,
                full_name=profile.get("full_name", full_name),
                email=email,
                message="Google login successful - Welcome back!",
                approval_status=approval_status,
                is_active=profile.get("is_active", True)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error in Google callback: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Google authentication failed: {str(e)}"
        )

