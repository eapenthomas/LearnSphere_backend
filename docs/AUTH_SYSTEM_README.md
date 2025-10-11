# 🔐 Authentication System - LearnSphere

A comprehensive authentication system with multi-role support, secure JWT tokens, and password management features.

## 🌟 Overview

The LearnSphere authentication system provides secure user registration, login, and role-based access control. It supports three user roles (Student, Teacher, Admin) with different permission levels and includes features like password reset, email verification, and teacher approval workflow.

## ✨ Features

### 🔑 **Core Authentication**
- **Secure Registration** - Email-based user registration
- **JWT Login** - Token-based authentication
- **Password Reset** - Email-based password recovery
- **Role-Based Access** - Different permissions for each role
- **Session Management** - Secure token handling

### 👥 **Multi-Role Support**
- **Students** - Default role, immediate access
- **Teachers** - Requires admin approval
- **Administrators** - Full system access

### 🛡️ **Security Features**
- **Password Hashing** - PBKDF2 with salt
- **JWT Tokens** - Secure session tokens
- **Email Verification** - Account verification
- **Rate Limiting** - Brute force protection
- **Input Validation** - Comprehensive data validation

## 🏗️ Architecture

### Frontend Components

#### **Authentication Pages**
```
frontend/src/pages/auth/
├── Login.jsx           # Login form and logic
├── Register.jsx        # Registration form
├── ForgotPassword.jsx  # Password reset request
└── ResetPassword.jsx   # Password reset form
```

#### **Authentication Context**
```javascript
// frontend/src/context/AuthContext.jsx
const AuthContext = {
  user: null,           // Current user object
  login: () => {},      // Login function
  logout: () => {},     // Logout function
  register: () => {},   // Registration function
  isLoading: false      // Loading state
}
```

### Backend Components

#### **Authentication Module**
```
backend/
├── auth.py             # Authentication service
├── models.py           # User models and validation
└── main.py            # Auth endpoints
```

#### **Key Files**
- **`auth.py`** - Core authentication logic
- **`models.py`** - Pydantic models for validation
- **`email_service.py`** - Email notifications

## 🔧 Implementation Details

### Frontend Implementation

#### **Login Component**
```jsx
// frontend/src/pages/auth/Login.jsx
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const { login, isLoading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(formData.email, formData.password);
      // Redirect handled by AuthContext
    } catch (error) {
      toast.error('Login failed');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

#### **Registration Component**
```jsx
// frontend/src/pages/auth/Register.jsx
const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'student'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        toast.success('Registration successful!');
        navigate('/login');
      }
    } catch (error) {
      toast.error('Registration failed');
    }
  };
};
```

#### **Auth Context Provider**
```jsx
// frontend/src/context/AuthContext.jsx
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (email, password) => {
    const response = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setUser(data.user);
      return data;
    }
    throw new Error('Login failed');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Backend Implementation

#### **Authentication Service**
```python
# backend/auth.py
class AuthService:
    @staticmethod
    async def register_user(request: RegisterRequest) -> AuthResponse:
        # Check if email exists
        existing_user = await check_email_exists(request.email)
        if existing_user:
            raise HTTPException(400, "Email already registered")
        
        # Hash password
        password_hash = hash_password(request.password)
        
        # Create user profile
        user_data = {
            "email": request.email,
            "password_hash": password_hash,
            "full_name": request.full_name,
            "role": request.role,
            "status": "pending" if request.role == "teacher" else "active"
        }
        
        # Insert into database
        result = supabase.table("profiles").insert(user_data).execute()
        
        # Send welcome email
        await send_welcome_email(request.email, request.full_name)
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            user=result.data[0]
        )

    @staticmethod
    async def login_user(request: LoginRequest) -> AuthResponse:
        # Find user by email
        user = await get_user_by_email(request.email)
        if not user:
            raise HTTPException(401, "Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(401, "Invalid credentials")
        
        # Check account status
        if user.status != "active":
            raise HTTPException(403, "Account not activated")
        
        # Generate JWT token
        token = create_jwt_token(user.id, user.role)
        
        return AuthResponse(
            success=True,
            access_token=token,
            user=user
        )
```

#### **Password Management**
```python
# backend/auth.py
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> tuple[str, str]:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return hash_obj.hex(), salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        hash_obj = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return hash_obj.hex() == hashed_password
```

## 🔗 API Endpoints

### **Authentication Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | User registration | No |
| POST | `/login` | User login | No |
| POST | `/forgot-password` | Request password reset | No |
| POST | `/verify-otp-reset` | Verify OTP and reset password | No |
| POST | `/update-password` | Update user password | Yes |
| POST | `/sync-profile` | Sync user profile | Yes |
| POST | `/check-email` | Check email availability | No |

### **Request/Response Examples**

#### **Registration Request**
```json
POST /register
{
  "email": "student@example.com",
  "password": "securePassword123",
  "full_name": "John Doe",
  "role": "student"
}
```

#### **Registration Response**
```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "id": "uuid-here",
    "email": "student@example.com",
    "full_name": "John Doe",
    "role": "student",
    "status": "active"
  }
}
```

#### **Login Request**
```json
POST /login
{
  "email": "student@example.com",
  "password": "securePassword123"
}
```

#### **Login Response**
```json
{
  "success": true,
  "access_token": "jwt-token-here",
  "user": {
    "id": "uuid-here",
    "email": "student@example.com",
    "full_name": "John Doe",
    "role": "student"
  }
}
```

## 🛡️ Security Considerations

### **Password Security**
- **PBKDF2 Hashing** - Industry-standard password hashing
- **Salt Generation** - Unique salt for each password
- **Minimum Requirements** - Password complexity validation
- **Rate Limiting** - Prevent brute force attacks

### **JWT Token Security**
- **Short Expiration** - Tokens expire after reasonable time
- **Secure Storage** - Tokens stored securely in localStorage
- **Token Validation** - Server-side token verification
- **Role Verification** - Role-based access control

### **Input Validation**
- **Email Validation** - Proper email format checking
- **Password Strength** - Minimum length and complexity
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - Input sanitization

## 🔄 User Workflows

### **Student Registration Flow**
1. User fills registration form
2. System validates input data
3. Password is hashed and stored
4. User profile created with "active" status
5. Welcome email sent
6. User can immediately login

### **Teacher Registration Flow**
1. Teacher fills registration form
2. System validates input data
3. Password is hashed and stored
4. User profile created with "pending" status
5. Admin approval request created
6. Email sent to admins for approval
7. Teacher must wait for approval to login

### **Password Reset Flow**
1. User requests password reset
2. OTP generated and sent via email
3. User enters OTP and new password
4. System verifies OTP
5. Password updated in database
6. Confirmation email sent

## 🧪 Testing

### **Frontend Testing**
```bash
# Run authentication tests
npm test -- --testPathPattern=auth
```

### **Backend Testing**
```bash
# Test authentication endpoints
python -m pytest tests/test_auth.py
```

## 🚀 Deployment Considerations

### **Environment Variables**
```env
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
PASSWORD_SALT_ROUNDS=100000
```

### **Security Headers**
- CORS configuration
- HTTPS enforcement
- Secure cookie settings
- Content Security Policy

## 📝 Best Practices

1. **Always validate input** on both frontend and backend
2. **Use HTTPS** in production
3. **Implement rate limiting** for auth endpoints
4. **Log authentication events** for security monitoring
5. **Regular security audits** of authentication code
6. **Keep dependencies updated** for security patches

---

**🔒 Security is our top priority in LearnSphere's authentication system**
