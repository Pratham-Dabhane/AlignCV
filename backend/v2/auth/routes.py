"""
Authentication routes for AlignCV V2.

Endpoints:
- POST /v2/auth/signup - Register with email/password
- POST /v2/auth/login - Login with email/password
- POST /v2/auth/google - Google OAuth login
- POST /v2/auth/refresh - Refresh access token
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ..database import get_db
from .schemas import (
    SignupRequest, LoginRequest, GoogleAuthRequest,
    RefreshTokenRequest, AuthResponse, TokenResponse, UserResponse, ErrorResponse
)
from .utils import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token
)
from ..config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v2/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    request: SignupRequest,
    db: Client = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    Args:
        request: User registration data (name, email, password)
        db: Supabase client
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 400 if email already exists
    """
    logger.info(f"Signup attempt for email: {request.email}")
    
    # Check if user already exists
    result = db.table('users').select('*').eq('email', request.email).execute()
    
    if result.data:
        logger.warning(f"Signup failed: Email already registered - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create new user
    user_data = {
        'name': request.name,
        'email': request.email,
        'password_hash': password_hash
    }
    
    result = db.table('users').insert(user_data).execute()
    new_user = result.data[0]
    
    logger.info(f"User created successfully: {new_user['id']} - {new_user['email']}")
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user['email']})
    refresh_token = create_refresh_token(data={"sub": new_user['email']})
    
    return AuthResponse(
        user=UserResponse(**new_user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        ),
        message="User registered successfully"
    )



@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    db: Client = Depends(get_db)
):
    """
    Login with email and password.
    
    Args:
        request: Login credentials (email, password)
        db: Supabase client
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    logger.info(f"Login attempt for email: {request.email}")
    
    # Find user by email
    result = db.table('users').select('*').eq('email', request.email).execute()
    user = result.data[0] if result.data else None
    
    if not user or not user.get('password_hash'):
        logger.warning(f"Login failed: User not found - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user['password_hash']):
        logger.warning(f"Login failed: Invalid password - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"Login successful: {user['id']} - {user['email']}")
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user['email']})
    refresh_token = create_refresh_token(data={"sub": user['email']})
    
    return AuthResponse(
        user=UserResponse(**user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        ),
        message="Login successful"
    )


@router.post("/google", response_model=AuthResponse)
def google_auth(
    request: GoogleAuthRequest,
    db: Client = Depends(get_db)
):
    """
    Authenticate with Google OAuth2.
    
    **TEMPORARILY DISABLED** - Use email/password signup/login instead.
    
    Args:
        request: Google ID token from frontend
        db: Supabase client
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    logger.info("Google OAuth authentication attempt")
    
    # Temporarily disabled - return error
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth temporarily disabled. Please use email/password signup/login."
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Client = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token
        db: Database session
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    logger.info("Token refresh attempt")
    
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if not payload:
        logger.warning("Token refresh failed: Invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = payload.get("sub")
    
    # Verify user still exists
    result = db.table('users').select('*').eq('email', email).execute()
    user = result.data[0] if result.data else None
    
    if not user:
        logger.warning(f"Token refresh failed: User not found - {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"Token refreshed for user: {user['id']} - {user['email']}")
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )
