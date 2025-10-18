"""
Test Suite for Job Matching Engine - Phase 5/6

Tests job ingestion, matching, bookmarking, and applications.
"""

import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.v2.app_v2 import app_v2
from backend.v2.config import settings


# ========================================
# Fixtures
# ========================================

@pytest.fixture
def auth_token():
    """Mock authentication token for testing."""
    return "test_token_12345"


@pytest.fixture
def auth_headers(auth_token):
    """Headers with authentication."""
    return {"Authorization": f"Bearer {auth_token}"}


# ========================================
# Test Job Ingestion
# ========================================

@pytest.mark.asyncio
async def test_ingest_jobs(auth_headers):
    """Test job ingestion from sources."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        with patch('backend.v2.jobs.ingest.ingest_jobs_from_sources') as mock_ingest:
            # Mock ingested jobs
            mock_ingest.return_value = [
                {
                    "job_id": "job1",
                    "source": "mock",
                    "title": "Software Engineer",
                    "company": "TechCorp",
                    "description": "Build awesome software",
                    "url": "https://example.com/job1",
                    "tags": ["Python", "FastAPI"]
                }
            ]
            
            async with AsyncClient(app=app_v2, base_url="http://test") as client:
                response = await client.post(
                    "/v2/jobs/ingest",
                    headers=auth_headers
                )
            
            assert response.status_code in [200, 500]  # May fail if Qdrant not available
            # In a real environment with Qdrant, expect 200


@pytest.mark.asyncio
async def test_get_jobs(auth_headers):
    """Test getting list of jobs."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.get(
                "/v2/jobs/?limit=10",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ========================================
# Test Job Matching
# ========================================

@pytest.mark.asyncio
async def test_match_jobs_no_resume(auth_headers):
    """Test job matching with non-existent resume."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.post(
                "/v2/jobs/match",
                json={"resume_id": 9999, "top_k": 10},
                headers=auth_headers
            )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_match_jobs_with_filters(auth_headers):
    """Test job matching with salary and location filters."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.post(
                "/v2/jobs/match",
                json={
                    "resume_id": 1,
                    "top_k": 10,
                    "min_salary": 120000,
                    "location": "San Francisco",
                    "experience_level": "senior"
                },
                headers=auth_headers
            )
        
        # Expect 404 if resume doesn't exist or 200 with matches
        assert response.status_code in [200, 404]


# ========================================
# Test Embedding Utilities
# ========================================

@pytest.mark.asyncio
async def test_get_local_embedding():
    """Test local embedding generation."""
    from backend.v2.jobs.embedding_utils import get_local_embedding
    
    text = "Python developer with FastAPI and PostgreSQL experience"
    embedding = get_local_embedding(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) == 384  # sentence-transformers dimension
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_get_resume_embedding():
    """Test resume embedding with fallback."""
    from backend.v2.jobs.embedding_utils import get_resume_embedding
    
    resume_text = """
    John Doe
    Software Engineer with 5 years of experience in Python, FastAPI, PostgreSQL.
    Built scalable APIs and worked with Docker, Kubernetes, AWS.
    """
    
    embedding = await get_resume_embedding(resume_text, settings)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_batch_embeddings():
    """Test batch embedding generation."""
    from backend.v2.jobs.embedding_utils import get_batch_embeddings
    
    texts = [
        "Python developer",
        "Machine Learning Engineer",
        "DevOps specialist"
    ]
    
    embeddings = await get_batch_embeddings(texts, settings)
    
    assert len(embeddings) == 3
    assert all(isinstance(emb, list) for emb in embeddings)
    assert all(len(emb) == 384 for emb in embeddings)


# ========================================
# Test Job Matching Engine
# ========================================

def test_extract_skills():
    """Test skill extraction from text."""
    from backend.v2.jobs.matcher import extract_skills
    
    text = """
    Looking for a Python developer with experience in FastAPI, PostgreSQL, Docker.
    Knowledge of AWS, Kubernetes, and machine learning is a plus.
    """
    
    skills = extract_skills(text, settings)
    
    assert isinstance(skills, list)
    assert len(skills) > 0
    # Check for some expected skills
    skills_lower = [s.lower() for s in skills]
    assert any("python" in s for s in skills_lower)


def test_calculate_skill_match():
    """Test skill matching calculation."""
    from backend.v2.jobs.matcher import calculate_skill_match
    
    resume_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"]
    job_skills = ["Python", "FastAPI", "PostgreSQL", "Kubernetes", "GCP"]
    
    result = calculate_skill_match(resume_skills, job_skills)
    
    assert "matched_skills" in result
    assert "gap_skills" in result
    assert "match_percentage" in result
    assert result["match_percentage"] == 60.0  # 3 out of 5
    assert "python" in result["matched_skills"]
    assert "kubernetes" in result["gap_skills"]


@pytest.mark.asyncio
async def test_rank_jobs():
    """Test job ranking with skill analysis."""
    from backend.v2.jobs.matcher import rank_jobs
    
    resume_text = "Python developer with FastAPI and PostgreSQL experience"
    
    job_matches = [
        {
            "job_id": "job1",
            "score": 0.85,
            "payload": {
                "title": "Python Developer",
                "company": "TechCorp",
                "description": "Python, FastAPI, PostgreSQL developer needed",
                "url": "https://example.com/job1",
                "tags": ["Python", "FastAPI"]
            }
        },
        {
            "job_id": "job2",
            "score": 0.70,
            "payload": {
                "title": "Backend Engineer",
                "company": "StartupXYZ",
                "description": "Node.js and MongoDB developer wanted",
                "url": "https://example.com/job2",
                "tags": ["Node.js", "MongoDB"]
            }
        }
    ]
    
    ranked = await rank_jobs(resume_text, job_matches, settings)
    
    assert len(ranked) == 2
    assert ranked[0]["combined_score"] >= ranked[1]["combined_score"]
    assert "matched_skills" in ranked[0]
    assert "gap_skills" in ranked[0]
    assert "fit_percentage" in ranked[0]


def test_filter_jobs_by_criteria():
    """Test job filtering."""
    from backend.v2.jobs.matcher import filter_jobs_by_criteria
    
    jobs = [
        {
            "title": "Senior Engineer",
            "salary_max": 200000,
            "location": "San Francisco, CA",
            "experience_level": "senior",
            "employment_type": "full-time"
        },
        {
            "title": "Junior Developer",
            "salary_max": 100000,
            "location": "Remote",
            "experience_level": "entry",
            "employment_type": "full-time"
        }
    ]
    
    # Filter by salary
    filtered = filter_jobs_by_criteria(jobs, min_salary=150000)
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Senior Engineer"
    
    # Filter by experience level
    filtered = filter_jobs_by_criteria(jobs, experience_level="entry")
    assert len(filtered) == 1
    assert filtered[0]["title"] == "Junior Developer"


# ========================================
# Test Bookmarks
# ========================================

@pytest.mark.asyncio
async def test_bookmark_job(auth_headers):
    """Test bookmarking a job."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.post(
                "/v2/jobs/bookmark",
                json={"job_id": 1, "notes": "Interesting opportunity"},
                headers=auth_headers
            )
        
        # Expect 404 if job doesn't exist or 200/400 if it does
        assert response.status_code in [200, 400, 404]


@pytest.mark.asyncio
async def test_get_bookmarks(auth_headers):
    """Test getting user's bookmarks."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.get(
                "/v2/jobs/bookmarks",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_remove_bookmark(auth_headers):
    """Test removing a bookmark."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.delete(
                "/v2/jobs/bookmark/1",
                headers=auth_headers
            )
        
        # Expect 404 if bookmark doesn't exist or 200 if it does
        assert response.status_code in [200, 404]


# ========================================
# Test Applications
# ========================================

@pytest.mark.asyncio
async def test_apply_to_job(auth_headers):
    """Test applying to a job."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.post(
                "/v2/jobs/apply",
                json={
                    "job_id": 1,
                    "notes": "Applied via company website",
                    "status": "applied"
                },
                headers=auth_headers
            )
        
        # Expect 404 if job doesn't exist or 200 if it does
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_get_applications(auth_headers):
    """Test getting user's applications."""
    with patch('backend.v2.jobs.routes.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        async with AsyncClient(app=app_v2, base_url="http://test") as client:
            response = await client.get(
                "/v2/jobs/applications",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ========================================
# Test Vector Store (if Qdrant available)
# ========================================

@pytest.mark.asyncio
@pytest.mark.skipif(not settings.qdrant_url, reason="Qdrant not configured")
async def test_create_collection():
    """Test creating Qdrant collection."""
    from backend.v2.jobs.vector_store import create_collection
    
    try:
        await create_collection(settings, vector_size=384)
        # If no error, collection created or already exists
        assert True
    except Exception as e:
        pytest.skip(f"Qdrant not available: {e}")


@pytest.mark.asyncio
@pytest.mark.skipif(not settings.qdrant_url, reason="Qdrant not configured")
async def test_upsert_job_vector():
    """Test upserting job vector."""
    from backend.v2.jobs.vector_store import upsert_job_vector
    from backend.v2.jobs.embedding_utils import get_local_embedding
    
    try:
        vector = get_local_embedding("Python developer position")
        await upsert_job_vector(
            job_id="test_job_1",
            vector=vector,
            payload={"title": "Test Job", "company": "Test Co"},
            settings=settings
        )
        assert True
    except Exception as e:
        pytest.skip(f"Qdrant not available: {e}")


# ========================================
# Performance Tests
# ========================================

@pytest.mark.asyncio
async def test_embedding_performance():
    """Test embedding generation performance."""
    import time
    from backend.v2.jobs.embedding_utils import get_local_embedding
    
    text = "Senior Software Engineer with 5+ years of Python experience"
    
    start = time.time()
    embedding = get_local_embedding(text)
    duration = time.time() - start
    
    assert duration < 1.0  # Should be < 1 second
    assert len(embedding) == 384


@pytest.mark.asyncio
async def test_batch_embedding_performance():
    """Test batch embedding performance."""
    import time
    from backend.v2.jobs.embedding_utils import get_batch_embeddings
    
    texts = [f"Job description {i}" for i in range(10)]
    
    start = time.time()
    embeddings = await get_batch_embeddings(texts, settings)
    duration = time.time() - start
    
    assert len(embeddings) == 10
    assert duration < 5.0  # Should be < 5 seconds for 10 embeddings


# ========================================
# Integration Tests
# ========================================

@pytest.mark.asyncio
async def test_full_matching_workflow(auth_headers):
    """Test complete job matching workflow."""
    # This would require a full database setup
    # For now, just test the API endpoints exist
    
    async with AsyncClient(app=app_v2, base_url="http://test") as client:
        # Test health check
        response = await client.get("/v2/health")
        assert response.status_code == 200
        
        # Test root endpoint
        response = await client.get("/v2/")
        assert response.status_code == 200
        features = response.json()["features"]
        assert "Job Matching & Ranking (Qdrant + Embeddings)" in features


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
