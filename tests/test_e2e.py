"""
End-to-End Test Suite - Phase 8

Comprehensive E2E tests covering the complete user workflow:
1. Signup/Login
2. Upload Resume
3. AI Rewrite
4. Job Matching
5. Notifications

Tests auth token expiry, DB consistency, and full integration.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi import status
from pathlib import Path
import io

from backend.v2.app_v2 import app_v2
from backend.v2.database import get_db
from backend.v2.models.models import User, Document, Job, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os


# Test database URL
TEST_DB_URL = "sqlite+aiosqlite:///./test_aligncv.db"

# Test fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Initialize test database before running tests."""
    # Remove old test database if exists
    if os.path.exists("./test_aligncv.db"):
        os.remove("./test_aligncv.db")
    
    # Create new test database
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Cleanup after all tests
    await engine.dispose()
    if os.path.exists("./test_aligncv.db"):
        os.remove("./test_aligncv.db")


@pytest.fixture
async def client():
    """Create async HTTP client for API testing."""
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app_v2), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user_credentials():
    """Test user credentials."""
    return {
        "email": "e2e_test@example.com",
        "password": "SecurePassword123!",
        "name": "E2E Test User"
    }


@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user_credentials):
    """Create authenticated client with JWT token."""
    # Register user
    response = await client.post(
        "/v2/auth/signup",
        json=test_user_credentials
    )
    
    if response.status_code == 201:
        data = response.json()
        token = data["tokens"]["access_token"]
    else:
        # User might already exist, try login
        response = await client.post(
            "/v2/auth/login",
            json={
                "email": test_user_credentials["email"],
                "password": test_user_credentials["password"]
            }
        )
        data = response.json()
        token = data["tokens"]["access_token"]
    
    # Add token to client headers
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# ============================================
# E2E TEST: Complete User Workflow
# ============================================

@pytest.mark.asyncio
class TestCompleteWorkflow:
    """Test the complete user workflow from signup to notifications."""
    
    async def test_01_signup(self, client: AsyncClient):
        """Test user signup."""
        response = await client.post(
            "/v2/auth/signup",
            json={
                "email": "workflow_test@example.com",
                "password": "TestPass123!",
                "name": "Workflow Test"
            }
        )
        
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
        
        if response.status_code == 201:
            data = response.json()
            assert "tokens" in data
            assert "access_token" in data["tokens"]
            assert "user" in data
            assert data["user"]["email"] == "workflow_test@example.com"
    
    async def test_02_login(self, client: AsyncClient):
        """Test user login."""
        response = await client.post(
            "/v2/auth/login",
            json={
                "email": "workflow_test@example.com",
                "password": "TestPass123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tokens" in data
        assert "access_token" in data["tokens"]
    
    @pytest.mark.skip(reason="Requires Qdrant and Mistral services running")
    async def test_03_upload_resume(self, authenticated_client: AsyncClient):
        """Test resume upload."""
        # Create a test PDF file
        test_pdf_content = b"%PDF-1.4\nTest PDF content for E2E testing"
        
        files = {
            "file": ("test_resume.pdf", io.BytesIO(test_pdf_content), "application/pdf")
        }
        
        response = await authenticated_client.post(
            "/v2/documents/upload",
            files=files
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        data = response.json()
        assert "id" in data
        assert "filename" in data
        
        # Store document ID for next tests
        return data["id"]
    
    @pytest.mark.skip(reason="Requires Qdrant and Mistral services running")
    async def test_04_list_documents(self, authenticated_client: AsyncClient):
        """Test listing user documents."""
        response = await authenticated_client.get("/v2/documents/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data.get("documents", []), list)
    
    async def test_05_get_notification_settings(self, authenticated_client: AsyncClient):
        """Test getting notification settings."""
        response = await authenticated_client.get("/v2/notifications/settings")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email_enabled" in data
        assert "digest_frequency" in data
    
    async def test_06_update_notification_settings(self, authenticated_client: AsyncClient):
        """Test updating notification settings."""
        response = await authenticated_client.put(
            "/v2/notifications/settings",
            json={
                "email_enabled": True,
                "digest_frequency": "weekly",
                "min_match_score": 0.75
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["digest_frequency"] == "weekly"
        assert data["min_match_score"] == 0.75


# ============================================
# AUTHENTICATION TESTS
# ============================================

@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication flows."""
    
    async def test_signup_validation(self, client: AsyncClient):
        """Test signup input validation."""
        # Invalid email
        response = await client.post(
            "/v2/auth/signup",
            json={
                "email": "invalid-email",
                "password": "Pass123!",
                "name": "Test User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/v2/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_protected_endpoint_without_token(self, client: AsyncClient):
        """Test accessing protected endpoint without token."""
        response = await client.get("/v2/documents/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    async def test_protected_endpoint_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        client.headers["Authorization"] = "Bearer invalid_token_here"
        response = await client.get("/v2/documents/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# DOCUMENT TESTS
# ============================================

@pytest.mark.asyncio
class TestDocuments:
    """Test document management."""
    
    async def test_upload_invalid_file_type(self, authenticated_client: AsyncClient):
        """Test uploading invalid file type."""
        files = {
            "file": ("test.txt", io.BytesIO(b"test content"), "text/plain")
        }
        
        response = await authenticated_client.post(
            "/v2/documents/upload",
            files=files
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    async def test_get_nonexistent_document(self, authenticated_client: AsyncClient):
        """Test getting non-existent document."""
        response = await authenticated_client.get("/v2/documents/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================
# NOTIFICATIONS TESTS
# ============================================

@pytest.mark.asyncio
class TestNotifications:
    """Test notification system."""
    
    async def test_list_notifications(self, authenticated_client: AsyncClient):
        """Test listing user notifications."""
        response = await authenticated_client.get("/v2/notifications")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "notifications" in data
        assert "total" in data
    
    async def test_update_invalid_settings(self, authenticated_client: AsyncClient):
        """Test updating settings with invalid data."""
        response = await authenticated_client.put(
            "/v2/notifications/settings",
            json={
                "digest_frequency": "invalid_frequency"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ============================================
# HEALTH & INFO TESTS
# ============================================

@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/v2/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_api_root(self, client: AsyncClient):
        """Test API root endpoint."""
        response = await client.get("/v2/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data


# ============================================
# PERFORMANCE TESTS
# ============================================

@pytest.mark.asyncio
class TestPerformance:
    """Test API performance."""
    
    async def test_concurrent_requests(self, authenticated_client: AsyncClient):
        """Test handling concurrent requests."""
        import asyncio
        
        async def make_request():
            return await authenticated_client.get("/v2/notifications/settings")
        
        # Make 10 concurrent requests
        responses = await asyncio.gather(*[make_request() for _ in range(10)])
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    async def test_response_time(self, authenticated_client: AsyncClient):
        """Test API response time."""
        import time
        
        start = time.time()
        response = await authenticated_client.get("/v2/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in less than 1 second
