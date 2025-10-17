"""
Tests for authentication functionality in AlignCV V2.

Tests:
- User signup with email/password
- User login
- JWT token generation and validation
- Google OAuth (mocked)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.v2.app_v2 import app_v2
from backend.v2.database import Base, get_db
from backend.v2.auth.utils import hash_password, verify_password, create_access_token, verify_token


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override dependency
app_v2.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def async_client():
    """Create async test client."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(app=app_v2, base_url="http://test") as client:
        yield client
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ========================================
# Password Hashing Tests
# ========================================

def test_hash_password():
    """Test password hashing."""
    password = "SecurePassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 50  # Bcrypt hashes are long


def test_verify_password():
    """Test password verification."""
    password = "SecurePassword123!"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


# ========================================
# JWT Token Tests
# ========================================

def test_create_access_token():
    """Test JWT access token creation."""
    token = create_access_token(data={"sub": "test@example.com"})
    
    assert isinstance(token, str)
    assert len(token) > 50


def test_verify_token():
    """Test JWT token verification."""
    email = "test@example.com"
    token = create_access_token(data={"sub": email})
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == email
    assert payload["type"] == "access"


def test_verify_invalid_token():
    """Test verification of invalid token."""
    payload = verify_token("invalid_token_string")
    assert payload is None


# ========================================
# Signup Tests
# ========================================

@pytest.mark.asyncio
async def test_signup_success(async_client):
    """Test successful user signup."""
    response = await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]


@pytest.mark.asyncio
async def test_signup_duplicate_email(async_client):
    """Test signup with duplicate email."""
    # First signup
    await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    # Second signup with same email
    response = await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Another User",
            "email": "test@example.com",
            "password": "DifferentPass123!"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_invalid_email(async_client):
    """Test signup with invalid email."""
    response = await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "not_an_email",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 422  # Validation error


# ========================================
# Login Tests
# ========================================

@pytest.mark.asyncio
async def test_login_success(async_client):
    """Test successful login."""
    # First create a user
    await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    # Now login
    response = await async_client.post(
        "/v2/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    """Test login with wrong password."""
    # Create user
    await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    # Try to login with wrong password
    response = await async_client.post(
        "/v2/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPassword!"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    """Test login with non-existent user."""
    response = await async_client.post(
        "/v2/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
    )
    
    assert response.status_code == 401


# ========================================
# Token Refresh Tests
# ========================================

@pytest.mark.asyncio
async def test_refresh_token(async_client):
    """Test token refresh."""
    # Signup to get tokens
    signup_response = await async_client.post(
        "/v2/auth/signup",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    
    refresh_token = signup_response.json()["tokens"]["refresh_token"]
    
    # Refresh token
    response = await async_client.post(
        "/v2/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(async_client):
    """Test refresh with invalid token."""
    response = await async_client.post(
        "/v2/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == 401
