"""
Unit tests for semantic_utils module
Phase 4: Comprehensive testing for reliability
"""

import pytest
import sys
import os
import numpy as np

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.semantic_utils import (
    get_model,
    get_embeddings,
    compute_similarity,
    validate_input_text,
    extract_skills_and_keywords,
    split_into_sentences,
    identify_strengths_gaps,
    analyze_resume_jd_match,
    get_metrics,
    clear_cache,
    _hash_text
)


class TestModelLoading:
    """Test model loading and initialization"""
    
    def test_get_model(self):
        """Test that model loads successfully"""
        model = get_model()
        assert model is not None
        assert hasattr(model, 'encode')
    
    def test_model_singleton(self):
        """Test that model is loaded only once (singleton pattern)"""
        model1 = get_model()
        model2 = get_model()
        assert model1 is model2


class TestEmbeddings:
    """Test embedding generation"""
    
    def test_get_embeddings_single_text(self):
        """Test embedding generation for single text"""
        texts = ["This is a test sentence"]
        embeddings = get_embeddings(texts)
        
        assert embeddings.shape[0] == 1
        assert embeddings.shape[1] == 384  # MiniLM embedding dimension
        assert isinstance(embeddings, np.ndarray)
    
    def test_get_embeddings_multiple_texts(self):
        """Test embedding generation for multiple texts"""
        texts = ["First sentence", "Second sentence", "Third sentence"]
        embeddings = get_embeddings(texts)
        
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] == 384
    
    def test_embeddings_caching(self):
        """Test that embeddings are cached correctly"""
        clear_cache()
        
        text = "This is a cacheable sentence"
        
        # First call - should miss cache
        embeddings1 = get_embeddings([text], use_cache=True)
        
        # Second call - should hit cache
        embeddings2 = get_embeddings([text], use_cache=True)
        
        # Should be identical
        assert np.array_equal(embeddings1, embeddings2)
        
        # Check metrics
        metrics = get_metrics()
        assert metrics["cache_hits"] > 0
    
    def test_hash_consistency(self):
        """Test that same text produces same hash"""
        text = "Test text for hashing"
        hash1 = _hash_text(text)
        hash2 = _hash_text(text)
        assert hash1 == hash2


class TestSimilarity:
    """Test similarity computation"""
    
    def test_compute_similarity_identical_texts(self):
        """Test similarity of identical texts"""
        embeddings = get_embeddings(["Test sentence", "Test sentence"])
        similarity = compute_similarity(embeddings[0], embeddings[1])
        
        assert 95 <= similarity <= 100  # Should be very high
    
    def test_compute_similarity_different_texts(self):
        """Test similarity of different texts"""
        embeddings = get_embeddings([
            "Python programming language",
            "Cooking recipes and food"
        ])
        similarity = compute_similarity(embeddings[0], embeddings[1])
        
        assert 0 <= similarity <= 100
        assert similarity < 50  # Should be low
    
    def test_compute_similarity_similar_texts(self):
        """Test similarity of related texts"""
        embeddings = get_embeddings([
            "Python programming with FastAPI",
            "Software development using Python and FastAPI framework"
        ])
        similarity = compute_similarity(embeddings[0], embeddings[1])
        
        assert 60 <= similarity <= 100  # Should be relatively high


class TestValidation:
    """Test input validation"""
    
    def test_validate_empty_text(self):
        """Test validation rejects empty text"""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            validate_input_text("", "Test field")
    
    def test_validate_whitespace_only(self):
        """Test validation rejects whitespace-only text"""
        with pytest.raises(ValueError, match="whitespace"):
            validate_input_text("   \n\t   ", "Test field")
    
    def test_validate_too_short(self):
        """Test validation rejects text that's too short"""
        with pytest.raises(ValueError, match="at least 50 characters"):
            validate_input_text("Short text", "Test field", min_length=50)
    
    def test_validate_too_long(self):
        """Test validation rejects text that's too long"""
        long_text = "x" * 60000
        with pytest.raises(ValueError, match="too long"):
            validate_input_text(long_text, "Test field", max_length=50000)
    
    def test_validate_non_string(self):
        """Test validation rejects non-string input"""
        with pytest.raises(ValueError, match="must be a non-empty string"):
            validate_input_text(123, "Test field")
    
    def test_validate_valid_text(self):
        """Test validation accepts valid text"""
        valid_text = "This is a valid text with more than fifty characters to pass validation."
        # Should not raise exception
        validate_input_text(valid_text, "Test field")


class TestKeywordExtraction:
    """Test keyword and skill extraction"""
    
    def test_extract_tech_skills(self):
        """Test extraction of technical skills"""
        text = "Experience with Python, Java, JavaScript, and Docker"
        keywords = extract_skills_and_keywords(text)
        
        assert "Python" in keywords
        assert "Java" in keywords
        assert "JavaScript" in keywords
        assert "Docker" in keywords
    
    def test_extract_frameworks(self):
        """Test extraction of framework names"""
        text = "Built applications using React, Django, and FastAPI"
        keywords = extract_skills_and_keywords(text)
        
        assert "React" in keywords
        assert "Django" in keywords
        assert "FastAPI" in keywords
    
    def test_extract_databases(self):
        """Test extraction of database names"""
        text = "Experience with PostgreSQL, MongoDB, and MySQL"
        keywords = extract_skills_and_keywords(text)
        
        assert "PostgreSQL" in keywords
        assert "MongoDB" in keywords
        assert "MySQL" in keywords


class TestSentenceSplitting:
    """Test sentence splitting"""
    
    def test_split_basic_sentences(self):
        """Test splitting basic sentences"""
        text = "First sentence. Second sentence. Third sentence."
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
    
    def test_split_filters_short_sentences(self):
        """Test that very short fragments are filtered out"""
        text = "Hello. This is a proper sentence with enough words."
        sentences = split_into_sentences(text)
        
        # "Hello" should be filtered (< 10 chars)
        assert len(sentences) == 1


class TestStrengthsGaps:
    """Test strengths and gaps identification"""
    
    def test_identify_matching_keywords(self):
        """Test identification of matching skills"""
        resume = "Software Engineer with Python, Docker, and PostgreSQL experience"
        jd = "Looking for engineer with Python, Docker, and database skills"
        
        strengths, gaps = identify_strengths_gaps(resume, jd)
        
        assert len(strengths) > 0
        # Should identify matching skills
        assert any("Python" in str(s) or "Docker" in str(s) for s in strengths)
    
    def test_identify_missing_requirements(self):
        """Test identification of gaps"""
        resume = "Experience with Python and basic web development"
        jd = "Required: Python, Docker, Kubernetes, AWS, and microservices expertise"
        
        strengths, gaps = identify_strengths_gaps(resume, jd)
        
        # Should have Python as strength
        assert len(strengths) > 0
        
        # Should identify missing skills as gaps
        assert len(gaps) > 0


class TestFullAnalysis:
    """Test complete analysis workflow"""
    
    def test_analyze_valid_inputs(self):
        """Test analysis with valid resume and job description"""
        resume = """
        John Doe - Software Engineer
        
        Experience:
        - 5 years developing Python applications with FastAPI
        - Built REST APIs and microservices with Docker
        - Database experience with PostgreSQL and MongoDB
        - Agile/Scrum methodologies
        
        Skills: Python, FastAPI, Docker, PostgreSQL, Git
        """
        
        jd = """
        Software Engineer Position
        
        Requirements:
        - 3+ years Python development
        - Experience with FastAPI or Flask
        - REST API knowledge
        - Database experience (SQL/NoSQL)
        - Docker containerization
        """
        
        result = analyze_resume_jd_match(resume, jd)
        
        assert "match_score" in result
        assert "strengths" in result
        assert "gaps" in result
        assert "processing_time" in result
        assert "metadata" in result
        
        assert 0 <= result["match_score"] <= 100
        assert result["match_score"] > 50  # Should be decent match
        assert isinstance(result["strengths"], list)
        assert isinstance(result["gaps"], list)
    
    def test_analyze_empty_resume(self):
        """Test analysis rejects empty resume"""
        with pytest.raises(ValueError, match="Resume"):
            analyze_resume_jd_match("", "Valid job description" * 10)
    
    def test_analyze_empty_jd(self):
        """Test analysis rejects empty job description"""
        with pytest.raises(ValueError, match="Job description"):
            analyze_resume_jd_match("Valid resume text" * 10, "")
    
    def test_analyze_short_inputs(self):
        """Test analysis rejects inputs that are too short"""
        with pytest.raises(ValueError, match="at least 50 characters"):
            analyze_resume_jd_match("Too short", "Also too short")
    
    def test_analyze_performance_tracking(self):
        """Test that performance metrics are tracked"""
        resume = "Software Engineer with Python and FastAPI experience. " * 10
        jd = "Looking for Python developer with FastAPI knowledge. " * 10
        
        clear_cache()
        initial_metrics = get_metrics()
        
        result = analyze_resume_jd_match(resume, jd)
        
        new_metrics = get_metrics()
        assert new_metrics["total_requests"] > initial_metrics["total_requests"]
        assert result["processing_time"] > 0


class TestMetrics:
    """Test metrics and monitoring"""
    
    def test_get_metrics_structure(self):
        """Test metrics return expected structure"""
        metrics = get_metrics()
        
        assert "total_requests" in metrics
        assert "cache_hits" in metrics
        assert "cache_misses" in metrics
        assert "total_processing_time" in metrics
        assert "cache_size" in metrics
        assert "cache_hit_rate" in metrics
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Generate some embeddings to populate cache
        get_embeddings(["Test 1", "Test 2"], use_cache=True)
        
        metrics_before = get_metrics()
        assert metrics_before["cache_size"] > 0
        
        clear_cache()
        
        metrics_after = get_metrics()
        assert metrics_after["cache_size"] == 0


# Performance and stress tests
class TestPerformance:
    """Test performance under load"""
    
    def test_analyze_large_resume(self):
        """Test analysis with large resume (max size)"""
        resume = "Software Engineer Experience: " * 1000  # ~30k chars
        jd = "Looking for Software Engineer with relevant experience " * 20
        
        result = analyze_resume_jd_match(resume, jd)
        
        assert result["processing_time"] < 10  # Should complete within 10 seconds
    
    def test_multiple_analyses_with_caching(self):
        """Test that caching improves performance"""
        resume1 = "Python developer with FastAPI experience " * 10
        resume2 = "Java developer with Spring Boot experience " * 10
        jd = "Software engineer position requiring programming skills " * 10
        
        # First analysis
        result1 = analyze_resume_jd_match(resume1, jd)
        time1 = result1["processing_time"]
        
        # Second analysis with same JD (should use cache)
        result2 = analyze_resume_jd_match(resume2, jd)
        time2 = result2["processing_time"]
        
        # Second should be faster or similar (cache helps)
        assert time2 <= time1 * 1.5  # Allow some variance


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
