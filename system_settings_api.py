"""
System Settings API
Manages system-wide configuration settings including AI feature toggles
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from auth_middleware import get_current_admin, TokenData

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_service_key)

router = APIRouter(prefix="/api/admin/settings", tags=["system-settings"])

# Pydantic models
class SystemSettings(BaseModel):
    general: Dict[str, Any] = {}
    email: Dict[str, Any] = {}
    ai: Dict[str, Any] = {}
    security: Dict[str, Any] = {}
    notifications: Dict[str, Any] = {}
    database: Dict[str, Any] = {}

class SettingUpdate(BaseModel):
    category: str
    settings: Dict[str, Any]

class AIFeatureStatus(BaseModel):
    notes_summarizer: bool
    ai_quiz_generation: bool
    ai_tutor: bool

@router.get("/", response_model=SystemSettings)
async def get_system_settings(
    current_admin: TokenData = Depends(get_current_admin)
):
    """Get all system settings"""
    try:
        # Get all settings from database
        response = supabase.table("system_settings").select("*").execute()
        
        if not response.data:
            # Return default settings if none exist
            return SystemSettings()
        
        # Organize settings by category
        settings = {
            "general": {},
            "email": {},
            "ai": {},
            "security": {},
            "notifications": {},
            "database": {}
        }
        
        for setting in response.data:
            category = setting.get("category", "general")
            key = setting.get("setting_key", "")
            value = setting.get("setting_value", "")
            setting_type = setting.get("setting_type", "string")
            
            # Convert value based on type
            if setting_type == "boolean":
                converted_value = value.lower() == "true"
            elif setting_type == "number":
                try:
                    converted_value = float(value) if "." in value else int(value)
                except ValueError:
                    converted_value = value
            else:
                converted_value = value
            
            if category in settings:
                settings[category][key] = converted_value
        
        return SystemSettings(**settings)
        
    except Exception as e:
        print(f"Error fetching system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system settings")

@router.put("/", response_model=Dict[str, str])
async def update_system_settings(
    settings: SystemSettings,
    current_admin: TokenData = Depends(get_current_admin)
):
    """Update system settings"""
    try:
        # Convert settings to database format
        settings_to_update = []
        
        for category, category_settings in settings.dict().items():
            for key, value in category_settings.items():
                # Determine setting type
                if isinstance(value, bool):
                    setting_type = "boolean"
                    setting_value = str(value).lower()
                elif isinstance(value, (int, float)):
                    setting_type = "number"
                    setting_value = str(value)
                else:
                    setting_type = "string"
                    setting_value = str(value)
                
                settings_to_update.append({
                    "category": category,
                    "setting_key": key,
                    "setting_value": setting_value,
                    "setting_type": setting_type,
                    "description": f"{category.title()} setting for {key}",
                    "is_encrypted": False,
                    "is_public": False
                })
        
        # Upsert all settings
        for setting in settings_to_update:
            supabase.table("system_settings").upsert(setting).execute()
        
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        print(f"Error updating system settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system settings")

@router.get("/ai-features", response_model=AIFeatureStatus)
async def get_ai_feature_status():
    """Get AI feature status (public endpoint for frontend checks)"""
    try:
        response = supabase.table("system_settings").select("*").eq("category", "ai").execute()
        
        if not response.data:
            # Return default enabled status
            return AIFeatureStatus(
                notes_summarizer=True,
                ai_quiz_generation=True,
                ai_tutor=True
            )
        
        # Extract AI feature settings
        ai_settings = {}
        for setting in response.data:
            key = setting.get("setting_key", "")
            value = setting.get("setting_value", "true")
            setting_type = setting.get("setting_type", "boolean")
            
            if setting_type == "boolean":
                ai_settings[key] = value.lower() == "true"
            else:
                ai_settings[key] = value
        
        return AIFeatureStatus(
            notes_summarizer=ai_settings.get("content_summarization", True),
            ai_quiz_generation=ai_settings.get("quiz_generation", True),
            ai_tutor=ai_settings.get("chatbot", True)
        )
        
    except Exception as e:
        print(f"Error fetching AI feature status: {e}")
        # Return default enabled status on error
        return AIFeatureStatus(
            notes_summarizer=True,
            ai_quiz_generation=True,
            ai_tutor=True
        )

@router.put("/ai-features", response_model=Dict[str, str])
async def update_ai_features(
    features: AIFeatureStatus,
    current_admin: TokenData = Depends(get_current_admin)
):
    """Update AI feature toggles"""
    try:
        # Map frontend names to database keys
        feature_mapping = {
            "notes_summarizer": "content_summarization",
            "ai_quiz_generation": "quiz_generation", 
            "ai_tutor": "chatbot"
        }
        
        for frontend_key, db_key in feature_mapping.items():
            value = getattr(features, frontend_key)
            
            # Upsert the setting
            supabase.table("system_settings").upsert({
                "category": "ai",
                "setting_key": db_key,
                "setting_value": str(value).lower(),
                "setting_type": "boolean",
                "description": f"Enable/disable {frontend_key}",
                "is_encrypted": False,
                "is_public": False
            }).execute()
        
        return {"message": "AI features updated successfully"}
        
    except Exception as e:
        print(f"Error updating AI features: {e}")
        raise HTTPException(status_code=500, detail="Failed to update AI features")

@router.post("/initialize-defaults")
async def initialize_default_settings(
    current_admin: TokenData = Depends(get_current_admin)
):
    """Initialize default system settings"""
    try:
        default_settings = [
            # General Settings
            {"category": "general", "setting_key": "site_name", "setting_value": "LearnSphere", "setting_type": "string", "description": "Site name", "is_encrypted": False, "is_public": True},
            {"category": "general", "setting_key": "site_description", "setting_value": "Advanced Learning Management System", "setting_type": "string", "description": "Site description", "is_encrypted": False, "is_public": True},
            {"category": "general", "setting_key": "maintenance_mode", "setting_value": "false", "setting_type": "boolean", "description": "Maintenance mode", "is_encrypted": False, "is_public": False},
            {"category": "general", "setting_key": "registration_enabled", "setting_value": "true", "setting_type": "boolean", "description": "Allow user registration", "is_encrypted": False, "is_public": False},
            {"category": "general", "setting_key": "max_file_upload_size", "setting_value": "50", "setting_type": "number", "description": "Max file upload size in MB", "is_encrypted": False, "is_public": False},
            {"category": "general", "setting_key": "session_timeout", "setting_value": "30", "setting_type": "number", "description": "Session timeout in minutes", "is_encrypted": False, "is_public": False},
            
            # AI Settings
            {"category": "ai", "setting_key": "openai_api_key", "setting_value": "", "setting_type": "string", "description": "OpenAI API key", "is_encrypted": True, "is_public": False},
            {"category": "ai", "setting_key": "deepseek_api_key", "setting_value": "", "setting_type": "string", "description": "DeepSeek API key", "is_encrypted": True, "is_public": False},
            {"category": "ai", "setting_key": "default_model", "setting_value": "gpt-3.5-turbo", "setting_type": "string", "description": "Default AI model", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "quiz_generation", "setting_value": "true", "setting_type": "boolean", "description": "Enable AI quiz generation", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "content_summarization", "setting_value": "true", "setting_type": "boolean", "description": "Enable AI content summarization", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "auto_grading", "setting_value": "false", "setting_type": "boolean", "description": "Enable AI auto-grading", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "chatbot", "setting_value": "true", "setting_type": "boolean", "description": "Enable AI chatbot", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "max_tokens_per_request", "setting_value": "4000", "setting_type": "number", "description": "Maximum tokens per AI request", "is_encrypted": False, "is_public": False},
            {"category": "ai", "setting_key": "daily_token_limit", "setting_value": "100000", "setting_type": "number", "description": "Daily token usage limit", "is_encrypted": False, "is_public": False},
            
            # Email Settings
            {"category": "email", "setting_key": "smtp_enabled", "setting_value": "true", "setting_type": "boolean", "description": "Enable SMTP email service", "is_encrypted": False, "is_public": False},
            {"category": "email", "setting_key": "smtp_host", "setting_value": "smtp.gmail.com", "setting_type": "string", "description": "SMTP host", "is_encrypted": False, "is_public": False},
            {"category": "email", "setting_key": "smtp_port", "setting_value": "587", "setting_type": "number", "description": "SMTP port", "is_encrypted": False, "is_public": False},
            {"category": "email", "setting_key": "smtp_username", "setting_value": "", "setting_type": "string", "description": "SMTP username", "is_encrypted": True, "is_public": False},
            {"category": "email", "setting_key": "smtp_password", "setting_value": "", "setting_type": "string", "description": "SMTP password", "is_encrypted": True, "is_public": False},
            {"category": "email", "setting_key": "from_email", "setting_value": "noreply@learnsphere.com", "setting_type": "string", "description": "From email address", "is_encrypted": False, "is_public": False},
            {"category": "email", "setting_key": "from_name", "setting_value": "LearnSphere", "setting_type": "string", "description": "From name", "is_encrypted": False, "is_public": False},
            
            # Security Settings
            {"category": "security", "setting_key": "password_min_length", "setting_value": "8", "setting_type": "number", "description": "Minimum password length", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "require_special_chars", "setting_value": "true", "setting_type": "boolean", "description": "Require special characters in passwords", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "require_numbers", "setting_value": "true", "setting_type": "boolean", "description": "Require numbers in passwords", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "require_uppercase", "setting_value": "true", "setting_type": "boolean", "description": "Require uppercase letters in passwords", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "session_security", "setting_value": "high", "setting_type": "string", "description": "Session security level", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "two_factor_enabled", "setting_value": "false", "setting_type": "boolean", "description": "Enable two-factor authentication", "is_encrypted": False, "is_public": False},
            {"category": "security", "setting_key": "ip_whitelisting", "setting_value": "false", "setting_type": "boolean", "description": "Enable IP whitelisting", "is_encrypted": False, "is_public": False},
            
            # Notification Settings
            {"category": "notifications", "setting_key": "email_notifications", "setting_value": "true", "setting_type": "boolean", "description": "Enable email notifications", "is_encrypted": False, "is_public": False},
            {"category": "notifications", "setting_key": "push_notifications", "setting_value": "false", "setting_type": "boolean", "description": "Enable push notifications", "is_encrypted": False, "is_public": False},
            {"category": "notifications", "setting_key": "sms_notifications", "setting_value": "false", "setting_type": "boolean", "description": "Enable SMS notifications", "is_encrypted": False, "is_public": False},
            {"category": "notifications", "setting_key": "deadline_reminders", "setting_value": "true", "setting_type": "boolean", "description": "Enable deadline reminders", "is_encrypted": False, "is_public": False},
            {"category": "notifications", "setting_key": "grade_notifications", "setting_value": "true", "setting_type": "boolean", "description": "Enable grade notifications", "is_encrypted": False, "is_public": False},
            {"category": "notifications", "setting_key": "forum_notifications", "setting_value": "true", "setting_type": "boolean", "description": "Enable forum notifications", "is_encrypted": False, "is_public": False},
            
            # Database Settings
            {"category": "database", "setting_key": "backup_frequency", "setting_value": "daily", "setting_type": "string", "description": "Backup frequency", "is_encrypted": False, "is_public": False},
            {"category": "database", "setting_key": "retention_period", "setting_value": "30", "setting_type": "number", "description": "Data retention period in days", "is_encrypted": False, "is_public": False},
            {"category": "database", "setting_key": "auto_cleanup", "setting_value": "true", "setting_type": "boolean", "description": "Enable automatic cleanup", "is_encrypted": False, "is_public": False},
            {"category": "database", "setting_key": "compression_enabled", "setting_value": "true", "setting_type": "boolean", "description": "Enable data compression", "is_encrypted": False, "is_public": False},
        ]
        
        # Insert default settings
        for setting in default_settings:
            supabase.table("system_settings").upsert(setting).execute()
        
        return {"message": "Default settings initialized successfully"}
        
    except Exception as e:
        print(f"Error initializing default settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize default settings")
