"""
Tests for AlignCV V2 - AI Rewriting Module
Tests Mistral 7B integration, fallback modes, and document versioning.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response
from datetime import datetime

from backend.v2.ai.rewrite_engine import (
    rewrite_resume,
    extract_keyphrases,
    _fallback_response,
    STYLE_PROMPTS
)


# ============================================
# Test Configuration
# ============================================

@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Senior Software Engineer
    
    Experience:
    - Worked on backend systems
    - Used Python and SQL
    - Fixed bugs and added features
    
    Skills: Python, SQL, JavaScript, Docker
    """


@pytest.fixture
def mock_mistral_success_response():
    """Mock successful Mistral API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": """{
                        "rewritten_text": "John Doe - Senior Software Engineer\\n\\nProfessional Experience:\\n- Architected and optimized backend systems serving 100K+ requests/day\\n- Developed scalable Python microservices with 99.9% uptime\\n- Enhanced SQL query performance by 40% through indexing optimization\\n\\nTechnical Skills: Python, SQL, JavaScript, Docker, System Architecture",
                        "improvements": [
                            "Added quantifiable metrics (100K+ requests/day, 40% performance gain)",
                            "Enhanced technical terminology and impact language",
                            "Improved ATS keyword density",
                            "Structured content for better readability"
                        ],
                        "impact_score": 88
                    }"""
                }
            }
        ]
    }


@pytest.fixture
def mock_mistral_plain_response():
    """Mock Mistral response without JSON structure."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a plain text response without JSON structure."
                }
            }
        ]
    }


# ============================================
# Test Prompt Templates
# ============================================

def test_style_prompts_exist():
    """Test that all three style prompts are defined."""
    assert "Technical" in STYLE_PROMPTS
    assert "Management" in STYLE_PROMPTS
    assert "Creative" in STYLE_PROMPTS


def test_style_prompts_have_placeholder():
    """Test that prompts have resume_text placeholder."""
    for style, prompt in STYLE_PROMPTS.items():
        assert "{resume_text}" in prompt, f"{style} prompt missing placeholder"


# ============================================
# Test Fallback Response
# ============================================

def test_fallback_response_preserves_text(sample_resume_text):
    """Test that fallback returns original text."""
    result = _fallback_response(sample_resume_text, "Technical")
    
    assert result["rewritten_text"] == sample_resume_text
    assert result["api_status"] == "fallback"
    assert result["impact_score"] == 0
    assert "API unavailable" in result["improvements"][0]


def test_fallback_response_with_error(sample_resume_text):
    """Test fallback with specific error message."""
    result = _fallback_response(sample_resume_text, "Technical", error="timeout")
    
    assert result["api_status"] == "fallback"
    assert "timeout" in result["warning"].lower()


# ============================================
# Test Rewrite Resume Function
# ============================================

@pytest.mark.asyncio
async def test_rewrite_resume_no_api_key(sample_resume_text):
    """Test rewrite with no API key configured (fallback mode)."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "your-mistral-api-key-here"
        
        result = await rewrite_resume(sample_resume_text, "Technical")
        
        assert result["api_status"] == "fallback"
        assert result["rewritten_text"] == sample_resume_text
        assert "API unavailable" in result["improvements"][0]


@pytest.mark.asyncio
async def test_rewrite_resume_success(sample_resume_text, mock_mistral_success_response):
    """Test successful rewrite with Mistral API."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            # Mock the async context manager
            mock_response = MagicMock()
            mock_response.json.return_value = mock_mistral_success_response
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            result = await rewrite_resume(sample_resume_text, "Technical")
            
            assert result["api_status"] == "success"
            assert "100K+ requests/day" in result["rewritten_text"]
            assert len(result["improvements"]) > 0
            assert result["impact_score"] == 88
            assert result["style"] == "Technical"
            assert result["latency"] >= 0


@pytest.mark.asyncio
async def test_rewrite_resume_invalid_style(sample_resume_text):
    """Test rewrite with invalid style (should default to Technical)."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "your-mistral-api-key-here"
        
        result = await rewrite_resume(sample_resume_text, "InvalidStyle")
        
        assert result["style"] == "Technical"  # Should default
        assert result["api_status"] == "fallback"


@pytest.mark.asyncio
async def test_rewrite_resume_timeout():
    """Test rewrite with API timeout."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            from httpx import TimeoutException
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=TimeoutException("Timeout")
            )
            
            result = await rewrite_resume("test text", "Technical", timeout=1)
            
            assert result["api_status"] == "fallback"
            assert "timeout" in result["warning"].lower()


@pytest.mark.asyncio
async def test_rewrite_resume_http_error():
    """Test rewrite with HTTP error from API."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            from httpx import HTTPStatusError, Request
            
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            
            mock_request = MagicMock(spec=Request)
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=HTTPStatusError(
                    "Unauthorized",
                    request=mock_request,
                    response=mock_response
                )
            )
            
            result = await rewrite_resume("test text", "Technical")
            
            assert result["api_status"] == "fallback"
            assert "401" in result["warning"]


@pytest.mark.asyncio
async def test_rewrite_resume_plain_text_response(sample_resume_text, mock_mistral_plain_response):
    """Test rewrite when Mistral returns plain text instead of JSON."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_mistral_plain_response
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            result = await rewrite_resume(sample_resume_text, "Technical")
            
            assert result["api_status"] == "success"
            assert result["rewritten_text"] == "This is a plain text response without JSON structure."
            assert result["impact_score"] == 75  # Default score


# ============================================
# Test Keyphrase Extraction
# ============================================

@pytest.mark.asyncio
async def test_extract_keyphrases(sample_resume_text):
    """Test keyphrase extraction from resume text."""
    keyphrases = await extract_keyphrases(sample_resume_text, max_phrases=5)
    
    assert isinstance(keyphrases, list)
    assert len(keyphrases) <= 5
    # Should extract some technical terms
    assert any("python" in phrase.lower() or "software" in phrase.lower() for phrase in keyphrases)


@pytest.mark.asyncio
async def test_extract_keyphrases_empty_text():
    """Test keyphrase extraction with empty text."""
    keyphrases = await extract_keyphrases("", max_phrases=10)
    
    assert isinstance(keyphrases, list)
    assert len(keyphrases) == 0


@pytest.mark.asyncio
async def test_extract_keyphrases_error_handling():
    """Test keyphrase extraction error handling."""
    with patch("backend.v2.ai.rewrite_engine.load_spacy_model", side_effect=Exception("Model error")):
        keyphrases = await extract_keyphrases("test text")
        
        assert keyphrases == []


# ============================================
# Test Different Styles
# ============================================

@pytest.mark.asyncio
async def test_technical_style_prompt():
    """Test that Technical style uses correct prompt."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"rewritten_text": "test", "improvements": [], "impact_score": 80}'}}]
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await rewrite_resume("test", "Technical")
            
            # Check that the API was called
            call_args = mock_post.call_args
            assert "technical skills" in call_args[1]["json"]["messages"][0]["content"].lower()


@pytest.mark.asyncio
async def test_management_style_prompt():
    """Test that Management style uses correct prompt."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"rewritten_text": "test", "improvements": [], "impact_score": 80}'}}]
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await rewrite_resume("test", "Management")
            
            # Check that the API was called with Management prompt
            call_args = mock_post.call_args
            assert "leadership" in call_args[1]["json"]["messages"][0]["content"].lower()


@pytest.mark.asyncio
async def test_creative_style_prompt():
    """Test that Creative style uses correct prompt."""
    with patch("backend.v2.ai.rewrite_engine.settings") as mock_settings:
        mock_settings.mistral_api_key = "test_api_key"
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": '{"rewritten_text": "test", "improvements": [], "impact_score": 80}'}}]
            }
            mock_response.raise_for_status = MagicMock()
            
            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await rewrite_resume("test", "Creative")
            
            # Check that the API was called with Creative prompt
            call_args = mock_post.call_args
            assert "creative" in call_args[1]["json"]["messages"][0]["content"].lower()
