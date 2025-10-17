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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ..database import Base, get_db
from ..models.models import User
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
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email and password.
    
    Args:
        request: Signup credentials (name, email, password)
        db: Database session
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 400 if email already exists
    """
    logger.info(f"Signup attempt for email: {request.email}")
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"Signup failed: Email already registered - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create new user
    new_user = User(
        name=request.name,
        email=request.email,
        password_hash=password_hash
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"User created successfully: {new_user.id} - {new_user.email}")
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.email})
    
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        ),
        message="User registered successfully"
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Args:
        request: Login credentials (email, password)
        db: Database session
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    logger.info(f"Login attempt for email: {request.email}")
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        logger.warning(f"Login failed: User not found - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        logger.warning(f"Login failed: Invalid password - {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"Login successful: {user.id} - {user.email}")
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60
        ),
        message="Login successful"
    )


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate with Google OAuth2.
    
    Args:
        request: Google ID token from frontend
        db: Database session
        
    Returns:
        AuthResponse: User info and JWT tokens
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    logger.info("Google OAuth authentication attempt")
    
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            request.token,
            google_requests.Request(),
            settings.google_client_id
        )
        
        # Extract user info
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        
        logger.info(f"Google token verified for: {email}")
        
        # Check if user exists
        result = await db.execute(
            select(User).where(
                (User.google_id == google_id) | (User.email == email)
            )
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = google_id
                await db.commit()
                await db.refresh(user)
            logger.info(f"Existing user logged in: {user.id} - {user.email}")
        else:
            # Create new user
            user = User(
                name=name,
                email=email,
                google_id=google_id
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New user created via Google: {user.id} - {user.email}")
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.jwt_access_token_expire_minutes * 60
            ),
            message="Google authentication successful"
        )
        
    except ValueError as e:
        logger.error(f"Google token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
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
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Token refresh failed: User not found - {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"Token refreshed for user: {user.id} - {user.email}")
    
    # Generate new tokens
    access_token = create_access_token(data={"sub": email})
    new_refresh_token = create_refresh_token(data={"sub": email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60
    )
