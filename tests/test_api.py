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
    """Test analyze endpoint with valid input"""
    payload = {
        "resume_text": "Software Engineer with 5 years experience in Python and FastAPI",
        "job_description_text": "Looking for a Software Engineer with Python experience"
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "match_score" in data
    assert "strengths" in data
    assert "gaps" in data
    assert data["match_score"] == 0.0  # Phase 1 dummy data


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
