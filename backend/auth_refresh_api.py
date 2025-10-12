"""
Authentication Refresh API for LearnSphere
Handles token refresh and persistent login sessions
"""

import os
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

from auth_middleware import (
    refresh_access_token, 
    create_tokens_for_user, 
    set_auth_cookies, 
    clear_auth_cookies,
    get_current_user_from_cookie,
    TokenData
)

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/auth", tags=["auth-refresh"])

class RefreshResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    role: str
    full_name: str

class LogoutResponse(BaseModel):
    success: bool
    message: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_tokens(request: RefreshTokenRequest):
    """Refresh access token using refresh token from request body"""
    try:
        import jwt
        import hashlib
        from datetime import datetime, timedelta
        
        jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        refresh_token = request.refresh_token
        
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token provided")
        
        # Verify refresh token in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        response = supabase_admin.table('refresh_tokens').select('*').eq('token_hash', token_hash).eq('is_revoked', False).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        token_record = response.data
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_record['expires_at'].replace('Z', '+00:00'))
        if expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")
        
        # Get user data
        user_response = supabase_admin.table('profiles').select('*').eq('id', token_record['user_id']).single().execute()
        
        if not user_response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = user_response.data
        
        # Generate new access token
        access_token_data = {
            "user_id": user['id'],
            "email": user['email'],
            "role": user['role'],
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }
        access_token = jwt.encode(access_token_data, jwt_secret, algorithm="HS256")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user['id'],
            "role": user['role'],
            "full_name": user.get('full_name', ''),
            "approval_status": user.get('approval_status', 'approved'),
            "is_active": user.get('is_active', True)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response):
    """Logout user and clear cookies"""
    try:
        clear_auth_cookies(response)
        
        return LogoutResponse(
            success=True,
            message="Logged out successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(user: TokenData = Depends(get_current_user_from_cookie)):
    """Get current user information from cookie"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Get fresh user data from database
        user_response = supabase_admin.table("profiles").select("*").eq("id", user.user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        
        return {
            "success": True,
            "user_id": user_data["id"],
            "email": user_data.get("email", ""),
            "full_name": user_data.get("full_name", ""),
            "role": user_data.get("role", "student"),
            "is_active": user_data.get("is_active", True),
            "approval_status": user_data.get("approval_status", "approved")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")
