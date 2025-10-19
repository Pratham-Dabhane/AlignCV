"""
Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ========================================
# Request Schemas
# ========================================

class SignupRequest(BaseModel):
    """User signup with email and password."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class LoginRequest(BaseModel):
    """User login with email and password."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class GoogleAuthRequest(BaseModel):
    """Google OAuth authentication."""
    token: str = Field(..., description="Google ID token from frontend")


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


# ========================================
# Response Schemas
# ========================================

class UserResponse(BaseModel):
    """User information response."""
    id: str  # UUID from Supabase
    name: str
    email: str
    google_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=900, description="Access token expiration in seconds")


class AuthResponse(BaseModel):
    """Complete authentication response with user and tokens."""
    user: UserResponse
    tokens: TokenResponse
    message: str = "Authentication successful"


# ========================================
# Error Schemas
# ========================================

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
