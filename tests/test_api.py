"""
Backend API tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns service info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AlignCV API"
    assert data["status"] == "running"
    assert "tagline" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_analyze_endpoint_success():
    """Test analyze endpoint with valid input (Phase 2: Real semantic matching)"""
    payload = {
        "resume_text": "Software Engineer with 5 years experience in Python and FastAPI. Built REST APIs and microservices. Experience with PostgreSQL, Docker, and Kubernetes. Strong problem-solving skills and Agile methodology.",
        "job_description_text": "Looking for a Software Engineer with Python experience, REST API knowledge, and familiarity with databases and containerization tools."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert "strengths" in data
    assert "gaps" in data
    assert 0 <= data["match_score"] <= 100  # Score should be in valid range
    assert isinstance(data["strengths"], list)
    assert isinstance(data["gaps"], list)


def test_analyze_endpoint_missing_fields():
    """Test analyze endpoint with missing fields"""
    payload = {
        "resume_text": "Some resume text"
        # Missing job_description_text
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_empty_text():
    """Test analyze endpoint with empty text"""
    payload = {
        "resume_text": "",
        "job_description_text": "Job description"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_short_text():
    """Test analyze endpoint with text that's too short"""
    payload = {
        "resume_text": "Too short",
        "job_description_text": "This is a job description that needs to be at least 50 characters long."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 400  # Bad request


def test_analyze_semantic_matching():
    """Test that semantic matching returns reasonable results"""
    payload = {
        "resume_text": """
        John Doe - Senior Python Developer
        
        Experience:
        - 5 years developing web applications with Python, Django, and FastAPI
        - Built RESTful APIs serving 1M+ requests per day
        - Worked with PostgreSQL and Redis for data storage and caching
        - Implemented CI/CD pipelines with Docker and Kubernetes
        - Led team of 3 developers in Agile environment
        
        Skills: Python, FastAPI, Django, PostgreSQL, Docker, Kubernetes, REST APIs
        """,
        "job_description_text": """
        We are looking for a Senior Python Developer to join our team.
        
        Requirements:
        - 3+ years Python development experience
        - Experience with FastAPI or Flask
        - Knowledge of REST API design
        - Database experience (PostgreSQL preferred)
        - Containerization experience with Docker
        - Agile methodology experience
        """
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Should have a decent match score for this good alignment
    assert data["match_score"] >= 50, f"Expected match score >= 50, got {data['match_score']}"
    
    # Should have identified some strengths
    assert len(data["strengths"]) > 0, "Should identify at least one strength"
    
    # May or may not have gaps depending on analysis
    assert isinstance(data["gaps"], list)
