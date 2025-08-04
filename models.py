from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.STUDENT

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    role: str
    full_name: str
    message: str

class ProfileSyncRequest(BaseModel):
    user_id: str
    full_name: str
    role: UserRole = UserRole.STUDENT

class PasswordUpdateRequest(BaseModel):
    user_id: str
    current_password: str
    new_password: str

class ErrorResponse(BaseModel):
    error: str
    message: str