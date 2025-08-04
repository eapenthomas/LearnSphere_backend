import os
import hashlib
import secrets
from supabase import create_client, Client
from fastapi import HTTPException
from dotenv import load_dotenv
from models import RegisterRequest, LoginRequest, AuthResponse, ProfileSyncRequest, UserRole

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_anon_key or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_anon_key)
supabase_admin: Client = create_client(supabase_url, supabase_service_key)


class AuthService:

    @staticmethod
    def hash_password(password: str) -> tuple[str, str]:
        """Hash password with salt for secure storage"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return salt, hash_obj.hex()

    @staticmethod
    def verify_password(password: str, salt: str, hashed_password: str) -> bool:
        """Verify password against stored hash"""
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hash_obj.hex() == hashed_password

    @staticmethod
    async def register_user(request: RegisterRequest) -> AuthResponse:
        try:
            # Check if user already exists by email (need to check all records since email is not indexed yet)
            all_profiles = supabase_admin.table("profiles").select("id, email").execute()

            # Check if email already exists
            for profile in all_profiles.data or []:
                if profile.get("email") and profile.get("email").lower() == request.email.lower():
                    raise HTTPException(status_code=400, detail="Email already registered")

            # Generate custom user ID (bypassing Supabase Auth for now)
            import uuid
            user_id = str(uuid.uuid4())
            print(f"Generated custom UUID for registration: {user_id}")

            # Hash password for our custom storage
            salt, hashed_password = AuthService.hash_password(request.password)

            # Insert into profiles table with password
            profile_data = {
                "id": user_id,
                "email": request.email,
                "full_name": request.full_name,
                "role": request.role.value,
                "password_salt": salt,
                "password_hash": hashed_password
            }

            profile_response = supabase_admin.table("profiles").insert(profile_data).execute()

            if not profile_response.data:
                raise HTTPException(status_code=500, detail="Failed to create user profile")

            return AuthResponse(
                access_token="",  # No token for manual registration
                user_id=user_id,
                role=request.role.value,
                full_name=request.full_name,
                message="User registered successfully. You can now login with your email and password."
            )

        except HTTPException:
            raise
        except Exception as e:
            err_str = str(e).lower()
            if "duplicate key" in err_str or "already registered" in err_str:
                raise HTTPException(status_code=400, detail="Email already registered")
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

    @staticmethod
    async def login_user(request: LoginRequest) -> AuthResponse:
        try:
            # Get all profiles and find by email (since email might not be indexed yet)
            all_profiles = supabase_admin.table("profiles").select("*").execute()

            profile = None
            for p in all_profiles.data or []:
                if p.get("email") == request.email:
                    profile = p
                    break

            if not profile:
                raise HTTPException(status_code=400, detail="Invalid email or password")

            user_id = profile["id"]

            # Check if password fields exist (for backward compatibility)
            if not profile.get("password_salt") or not profile.get("password_hash"):
                raise HTTPException(status_code=400, detail="Account not set up for password login. Please use Google login or contact support.")

            # Verify password
            if not AuthService.verify_password(request.password, profile["password_salt"], profile["password_hash"]):
                raise HTTPException(status_code=400, detail="Invalid email or password")

            return AuthResponse(
                access_token="",  # No token for manual login
                user_id=user_id,
                role=profile.get("role", "student"),
                full_name=profile.get("full_name", request.email.split("@")[0]),
                message="Login successful"
            )

        except HTTPException:
            raise
        except Exception as e:
            err_str = str(e).lower()
            if "invalid" in err_str or "credentials" in err_str:
                raise HTTPException(status_code=400, detail="Invalid email or password")
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

    @staticmethod
    async def get_google_oauth_url() -> dict:
        try:
            auth_response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": "http://localhost:3000/auth/callback"
                }
            })
            return {"url": auth_response.url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")

    @staticmethod
    async def handle_google_callback(code: str, state: str) -> AuthResponse:
        try:
            auth_response = supabase.auth.exchange_code_for_session(code)
            if not getattr(auth_response, "user", None):
                raise HTTPException(status_code=400, detail="Invalid OAuth callback")

            user_id = auth_response.user.id
            email = auth_response.user.email

            profile_response = supabase_admin.table("profiles").select("*").eq("id", user_id).execute()

            if not profile_response.data:
                profile_data = {
                    "id": user_id,
                    "full_name": auth_response.user.user_metadata.get("full_name", email.split("@")[0]),
                    "role": "student"
                }
                supabase_admin.table("profiles").insert(profile_data).execute()
                return AuthResponse(
                    access_token=auth_response.session.access_token,
                    user_id=user_id,
                    role="student",
                    full_name=profile_data["full_name"],
                    message="Google login successful - new user"
                )
            else:
                profile = profile_response.data[0]
                return AuthResponse(
                    access_token=auth_response.session.access_token,
                    user_id=user_id,
                    role=profile["role"],
                    full_name=profile["full_name"],
                    message="Google login successful"
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

    @staticmethod
    async def sync_profile(request: ProfileSyncRequest) -> AuthResponse:
        try:
            profile_response = supabase_admin.table("profiles").select("*").eq("id", request.user_id).execute()

            if profile_response.data:
                supabase_admin.table("profiles").update({
                    "full_name": request.full_name,
                    "role": request.role.value
                }).eq("id", request.user_id).execute()
            else:
                profile_data = {
                    "id": request.user_id,
                    "full_name": request.full_name,
                    "role": request.role.value
                }
                supabase_admin.table("profiles").insert(profile_data).execute()

            return AuthResponse(
                access_token="",
                user_id=request.user_id,
                role=request.role.value,
                full_name=request.full_name,
                message="Profile synced successfully"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Profile sync failed: {str(e)}")
