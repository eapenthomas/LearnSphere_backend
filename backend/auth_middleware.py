"""
Authentication Middleware for LearnSphere
Handles JWT tokens, refresh tokens, and persistent login sessions
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_admin: Client = create_client(supabase_url, supabase_service_key)

# Security scheme
security = HTTPBearer(auto_error=False)

class TokenData(BaseModel):
    user_id: str
    role: str
    email: str

class RefreshTokenData(BaseModel):
    user_id: str
    token_type: str = "refresh"

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify JWT token and return token data"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        email: str = payload.get("email")
        token_type_check: str = payload.get("type")
        
        if user_id is None or role is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        if token_type_check != token_type:
            raise HTTPException(status_code=401, detail=f"Invalid token type. Expected {token_type}")
        
        return TokenData(user_id=user_id, role=role, email=email)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> TokenData:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    return verify_token(token, "access")

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[TokenData]:
    """Get current user from JWT token (optional)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return verify_token(token, "access")
    except HTTPException:
        return None

def get_current_teacher(user: TokenData = Depends(get_current_user)) -> TokenData:
    """Ensure current user is a teacher"""
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user

def get_current_student(user: TokenData = Depends(get_current_user)) -> TokenData:
    """Ensure current user is a student"""
    if user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return user

def get_current_admin(user: TokenData = Depends(get_current_user)) -> TokenData:
    """Ensure current user is an admin"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def get_current_user_from_cookie(request: Request) -> Optional[TokenData]:
    """Get current user from HTTP-only cookie"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    
    try:
        return verify_token(access_token, "access")
    except HTTPException:
        return None

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HTTP-only authentication cookies"""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to False for localhost development
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to False for localhost development
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def clear_auth_cookies(response: Response):
    """Clear authentication cookies"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

def refresh_access_token(refresh_token: str) -> str:
    """Refresh access token using refresh token"""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        token_type: str = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token type")
        
        # Get fresh user data from database
        user_response = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()
        if not user_response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = user_response.data[0]
        
        # Check if user is still active
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="User account is disabled")
        
        # Create new access token
        token_data = {
            "user_id": user["id"],
            "role": user.get("role", "student"),
            "email": user.get("email", ""),
            "full_name": user.get("full_name", "")
        }
        
        return create_access_token(token_data)
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

def create_tokens_for_user(user_data: Dict[str, Any]) -> tuple[str, str]:
    """Create both access and refresh tokens for a user"""
    token_data = {
        "user_id": user_data["id"],
        "role": user_data.get("role", "student"),
        "email": user_data.get("email", ""),
        "full_name": user_data.get("full_name", "")
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"user_id": user_data["id"]})
    
    return access_token, refresh_token