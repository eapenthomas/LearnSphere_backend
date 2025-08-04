import os
import asyncio
from auth import AuthService
from models import RegisterRequest, LoginRequest, UserRole

# Test the registration functionality
async def test_registration():
    print("Testing registration functionality...")

    # Test data - using a unique email for testing
    import uuid
    test_email = f"test_{str(uuid.uuid4())[:8]}@example.com"

    test_user = RegisterRequest(
        email=test_email,
        password="testpassword123",
        full_name="Test User",
        role=UserRole.STUDENT
    )

    try:
        result = await AuthService.register_user(test_user)
        print(f"✅ Registration successful: {result.message}")
        print(f"User ID: {result.user_id}")
        print(f"Email: {test_email}")
        print(f"Role: {result.role}")
        print(f"Full Name: {result.full_name}")
        return result, test_email
    except Exception as e:
        print(f"❌ Registration failed: {str(e)}")
        return None, None

# Test the login functionality
async def test_login(email):
    print("\nTesting login functionality...")

    # Test data
    test_credentials = LoginRequest(
        email=email,
        password="testpassword123"
    )

    try:
        result = await AuthService.login_user(test_credentials)
        print(f"✅ Login successful: {result.message}")
        print(f"User ID: {result.user_id}")
        print(f"Role: {result.role}")
        print(f"Full Name: {result.full_name}")
        return result
    except Exception as e:
        print(f"❌ Login failed: {str(e)}")
        return None

# Test password hashing
def test_password_hashing():
    print("\nTesting password hashing...")
    
    test_password = "mypassword123"
    
    # Hash password
    salt, hashed = AuthService.hash_password(test_password)
    print(f"✅ Password hashed successfully")
    print(f"Salt: {salt[:10]}...")
    print(f"Hash: {hashed[:20]}...")
    
    # Verify password
    is_valid = AuthService.verify_password(test_password, salt, hashed)
    print(f"✅ Password verification: {'Success' if is_valid else 'Failed'}")
    
    # Test wrong password
    is_invalid = AuthService.verify_password("wrongpassword", salt, hashed)
    print(f"✅ Wrong password test: {'Success' if not is_invalid else 'Failed'}")
    
    return True

async def main():
    print("🔧 LearnSphere Authentication Test")
    print("=" * 50)
    
    # Check environment variables
    print("Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not set")
    else:
        print(f"✅ SUPABASE_URL: {supabase_url[:20]}...")
    
    if not supabase_anon_key:
        print("❌ SUPABASE_ANON_KEY not set")
    else:
        print(f"✅ SUPABASE_ANON_KEY: {supabase_anon_key[:20]}...")
    
    if not supabase_service_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not set")
    else:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {supabase_service_key[:20]}...")
    
    print("\n" + "=" * 50)
    
    # Test password hashing
    test_password_hashing()
    
    print("\n" + "=" * 50)
    
    # Test registration
    registration_result, test_email = await test_registration()

    if registration_result and test_email:
        # Test login with the same email used for registration
        await test_login(test_email)
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 