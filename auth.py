import os
import hashlib
import secrets
from supabase import create_client, Client
from fastapi import HTTPException, APIRouter
from dotenv import load_dotenv
from models import RegisterRequest, LoginRequest, AuthResponse, ProfileSyncRequest, UserRole, PasswordUpdateRequest, ForgotPasswordRequest, VerifyOTPRequest, ForgotPasswordResponse, EmailCheckRequest, EmailCheckResponse
from email_service import email_service
from datetime import datetime, timedelta, timezone

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_anon_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_anon_key)

# Use anon key for admin operations if service role key is not available
if supabase_service_key and not supabase_service_key.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"):
    print("⚠️  Service role key appears invalid, using anon key for admin operations")
    supabase_admin: Client = create_client(supabase_url, supabase_anon_key)
elif supabase_service_key:
    try:
        supabase_admin: Client = create_client(supabase_url, supabase_service_key)
        print("✅ Using service role key for admin operations")
    except Exception as e:
        print(f"⚠️  Service role key failed, using anon key: {e}")
        supabase_admin: Client = create_client(supabase_url, supabase_anon_key)
else:
    print("⚠️  Service role key not found, using anon key for admin operations")
    supabase_admin: Client = create_client(supabase_url, supabase_anon_key)


class AuthService:
    
    @staticmethod
    async def store_refresh_token(user_id: str, refresh_token: str):
        """Store refresh token in database"""
        try:
            import hashlib
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            # Store in database
            supabase_admin.table('refresh_tokens').insert({
                'user_id': user_id,
                'token_hash': token_hash,
                'expires_at': (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            }).execute()
        except Exception as e:
            print(f"Error storing refresh token: {e}")

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

            # Get the created profile to check approval status
            created_profile = profile_response.data[0]

            # If this is a teacher, manually create the approval request
            if request.role.value == "teacher":
                try:
                    # Create teacher approval request manually
                    approval_request_data = {
                        "teacher_id": user_id,
                        "status": "pending"
                    }

                    approval_response = supabase_admin.table("teacher_approval_requests").insert(approval_request_data).execute()

                    if not approval_response.data:
                        print(f"Warning: Failed to create approval request for teacher {user_id}")

                    # Try to send email notification (optional)
                    try:
                        email_data = {
                            "recipient_email": "eapentkadamapuzha@gmail.com",
                            "subject": "New Teacher Registration Request",
                            "body": f"A new teacher has registered and is awaiting approval. Teacher: {request.full_name} ({request.email})",
                            "notification_type": "teacher_registration"
                        }
                        supabase_admin.table("email_notifications").insert(email_data).execute()
                    except Exception as email_error:
                        print(f"Warning: Failed to create email notification: {email_error}")

                except Exception as approval_error:
                    print(f"Warning: Failed to create approval request: {approval_error}")
                    # Don't fail the registration if approval request creation fails

            # Determine message based on role
            if request.role.value == "teacher":
                message = "Teacher registration successful! Your account is pending admin approval. You will receive an email notification once approved."
            else:
                message = "User registered successfully. You can now login with your email and password."

            return AuthResponse(
                access_token="",  # No token for manual registration
                user_id=user_id,
                role=request.role.value,
                full_name=request.full_name,
                message=message,
                approval_status=created_profile.get("approval_status", "approved"),
                is_active=created_profile.get("is_active", True)
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

            # Check if user account is active
            if not profile.get("is_active", True):
                raise HTTPException(
                    status_code=403,
                    detail="Your account has been disabled. Please contact support for assistance."
                )

            # Check teacher approval status
            if profile.get("role") == "teacher" and profile.get("approval_status") != "approved":
                raise HTTPException(
                    status_code=403,
                    detail="Your teacher account is pending approval. Please wait for admin approval."
                )

            # Generate JWT tokens for persistent login
            import jwt
            from datetime import datetime, timedelta, timezone, timezone
            
            jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
            
            # Generate access token (short-lived)
            access_token_data = {
                "user_id": user_id,
                "email": profile.get("email"),
                "role": profile.get("role", "student"),
                "type": "access",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=120)  # 2 hours as configured
            }
            access_token = jwt.encode(access_token_data, jwt_secret, algorithm="HS256")
            
            # Generate refresh token (long-lived)
            refresh_token_data = {
                "user_id": user_id,
                "email": profile.get("email"),
                "type": "refresh",
                "exp": datetime.now(timezone.utc) + timedelta(days=7)  # 7 days
            }
            refresh_token = jwt.encode(refresh_token_data, jwt_secret, algorithm="HS256")
            
            # Store refresh token in database
            try:
                await AuthService.store_refresh_token(user_id, refresh_token)
                print(f"✅ Refresh token stored for user {user_id}")
            except Exception as e:
                print(f"❌ Failed to store refresh token: {str(e)}")

            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user_id=user_id,
                role=profile.get("role", "student"),
                full_name=profile.get("full_name", request.email.split("@")[0]),
                message="Login successful",
                approval_status=profile.get("approval_status", "approved"),
                is_active=profile.get("is_active", True)
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
            # Get frontend URL from environment variable
            frontend_url = os.environ.get('FRONTEND_URL', 'https://learn-sphere-frontend-black.vercel.app')
            
            auth_response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": f"{frontend_url}/auth/callback"
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

                # Check if user account is active
                if not profile.get("is_active", True):
                    raise HTTPException(
                        status_code=403,
                        detail="Your account has been disabled. Please contact support for assistance."
                    )

                # Check teacher approval status
                if profile.get("role") == "teacher" and profile.get("approval_status") != "approved":
                    raise HTTPException(
                        status_code=403,
                        detail="Your teacher account is pending approval. Please wait for admin approval."
                    )

                return AuthResponse(
                    access_token=auth_response.session.access_token,
                    user_id=user_id,
                    role=profile["role"],
                    full_name=profile["full_name"],
                    message="Google login successful",
                    approval_status=profile.get("approval_status", "approved"),
                    is_active=profile.get("is_active", True)
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

    @staticmethod
    async def update_password(request: PasswordUpdateRequest) -> AuthResponse:
        try:
            # Get user profile
            profile_response = supabase_admin.table("profiles").select("*").eq("id", request.user_id).execute()

            if not profile_response.data:
                raise HTTPException(status_code=404, detail="User not found")

            profile = profile_response.data[0]

            # Check if password fields exist
            if not profile.get("password_salt") or not profile.get("password_hash"):
                raise HTTPException(status_code=400, detail="Account not set up for password login")

            # Verify current password
            if not AuthService.verify_password(request.current_password, profile["password_salt"], profile["password_hash"]):
                raise HTTPException(status_code=400, detail="Current password is incorrect")

            # Check if new password is different from current
            if AuthService.verify_password(request.new_password, profile["password_salt"], profile["password_hash"]):
                raise HTTPException(status_code=400, detail="New password must be different from current password")

            # Hash new password
            salt, hashed_password = AuthService.hash_password(request.new_password)

            # Update password in database
            update_response = supabase_admin.table("profiles").update({
                "password_salt": salt,
                "password_hash": hashed_password
            }).eq("id", request.user_id).execute()

            if not update_response.data:
                raise HTTPException(status_code=500, detail="Failed to update password")

            return AuthResponse(
                access_token="",
                user_id=request.user_id,
                role=profile.get("role", "student"),
                full_name=profile.get("full_name", "User"),
                message="Password updated successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password update failed: {str(e)}")

    @staticmethod
    async def check_email_availability(request: EmailCheckRequest) -> EmailCheckResponse:
        try:
            # Get all profiles to check if email exists
            all_profiles = supabase_admin.table("profiles").select("email").execute()

            # Check if email already exists (case-insensitive)
            email_exists = False
            for profile in all_profiles.data or []:
                if profile.get("email") and profile.get("email").lower() == request.email.lower():
                    email_exists = True
                    break

            return EmailCheckResponse(
                email=request.email,
                exists=email_exists,
                message="Email is already registered" if email_exists else "Email is available"
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Email check failed: {str(e)}")

    @staticmethod
    async def forgot_password(request: ForgotPasswordRequest) -> ForgotPasswordResponse:
        try:
            # Check if user exists
            all_profiles = supabase_admin.table("profiles").select("*").execute()

            profile = None
            for p in all_profiles.data or []:
                if p.get("email") and p.get("email").lower() == request.email.lower():
                    profile = p
                    break

            if not profile:
                # For security, don't reveal if email exists or not
                return ForgotPasswordResponse(
                    message="If an account with this email exists, you will receive a password reset code.",
                    email=request.email
                )

            # Check if account is set up for password login
            if not profile.get("password_salt") or not profile.get("password_hash"):
                raise HTTPException(status_code=400, detail="This account is not set up for password login. Please use Google login or contact support.")

            # Generate OTP
            otp_code = email_service.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=10)  # OTP expires in 10 minutes

            # Store OTP in database
            otp_data = {
                "email": request.email.lower(),
                "otp_code": otp_code,
                "expires_at": expires_at.isoformat(),
                "is_used": False
            }

            otp_response = supabase_admin.table("password_reset_otps").insert(otp_data).execute()

            if not otp_response.data:
                raise HTTPException(status_code=500, detail="Failed to generate password reset code")

            # Send OTP email
            user_name = profile.get("full_name", "User")
            email_sent = email_service.send_otp_email(request.email, otp_code, user_name)

            if not email_sent and email_service.is_configured():
                # If email service is configured but sending failed
                raise HTTPException(status_code=500, detail="Failed to send password reset email")

            return ForgotPasswordResponse(
                message="If an account with this email exists, you will receive a password reset code.",
                email=request.email
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password reset request failed: {str(e)}")

    @staticmethod
    async def verify_otp_and_reset_password(request: VerifyOTPRequest) -> AuthResponse:
        try:
            # Find valid OTP
            otp_response = supabase_admin.table("password_reset_otps").select("*").eq("email", request.email.lower()).eq("otp_code", request.otp_code).eq("is_used", False).execute()

            if not otp_response.data:
                raise HTTPException(status_code=400, detail="Invalid or expired verification code")

            otp_record = otp_response.data[0]

            # Check if OTP is expired
            expires_at = datetime.fromisoformat(otp_record["expires_at"].replace('Z', '+00:00'))
            if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
                raise HTTPException(status_code=400, detail="Verification code has expired")

            # Find user profile
            all_profiles = supabase_admin.table("profiles").select("*").execute()

            profile = None
            for p in all_profiles.data or []:
                if p.get("email") and p.get("email").lower() == request.email.lower():
                    profile = p
                    break

            if not profile:
                raise HTTPException(status_code=404, detail="User not found")

            # Hash new password
            salt, hashed_password = AuthService.hash_password(request.new_password)

            # Update password in database
            update_response = supabase_admin.table("profiles").update({
                "password_salt": salt,
                "password_hash": hashed_password
            }).eq("id", profile["id"]).execute()

            if not update_response.data:
                raise HTTPException(status_code=500, detail="Failed to update password")

            # Mark OTP as used
            supabase_admin.table("password_reset_otps").update({
                "is_used": True,
                "used_at": datetime.utcnow().isoformat()
            }).eq("id", otp_record["id"]).execute()

            return AuthResponse(
                access_token="",
                user_id=profile["id"],
                role=profile.get("role", "student"),
                full_name=profile.get("full_name", "User"),
                message="Password reset successfully"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password reset failed: {str(e)}")

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


# Create FastAPI router
router = APIRouter()

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    return await AuthService.register_user(request)

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user"""
    return await AuthService.login_user(request)

@router.post("/profile-sync", response_model=AuthResponse)
async def sync_profile(request: ProfileSyncRequest):
    """Sync user profile"""
    return await AuthService.sync_profile(request)

@router.post("/update-password")
async def update_password(request: PasswordUpdateRequest):
    """Update user password"""
    return await AuthService.update_password(request)

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email"""
    return await AuthService.forgot_password(request)

@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP for password reset"""
    return await AuthService.verify_otp(request)

@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email(request: EmailCheckRequest):
    """Check if email exists"""
    return await AuthService.check_email_availability(request)
