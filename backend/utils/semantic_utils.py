"""
Semantic utilities for resume and job description matching
Phase 2: Sentence-BERT embeddings and similarity computation
Phase 4: Optimization with caching and enhanced error handling
"""

import re
import numpy as np
from typing import List, Tuple, Dict, Optional
from sentence_transformers import SentenceTransformer, util
import logging
import hashlib
from functools import lru_cache
import time

# Initialize logger
logger = logging.getLogger(__name__)

# Load pre-trained model (lazy loading for efficiency)
_model = None

# Cache for embeddings (stores text hash -> embedding)
_embedding_cache: Dict[str, np.ndarray] = {}

# Performance metrics
_metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "total_processing_time": 0.0
}


def get_model():
    """
    Get or initialize the Sentence-BERT model
    Using 'all-MiniLM-L6-v2' - fast, efficient, good quality
    Free, ~80MB model
    """
    global _model
    if _model is None:
        logger.info("Loading Sentence-BERT model: all-MiniLM-L6-v2")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    return _model


def _hash_text(text: str) -> str:
    """Generate hash for text to use as cache key"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def get_embeddings(texts: List[str], use_cache: bool = True) -> np.ndarray:
    """
    Generate embeddings for a list of texts using Sentence-BERT
    Phase 4: Added caching for repeated job descriptions
    
    Args:
        texts: List of text strings to encode
        use_cache: Whether to use embedding cache (default: True)
        
    Returns:
        numpy array of embeddings (shape: [len(texts), embedding_dim])
    """
    try:
        start_time = time.time()
        model = get_model()
        embeddings_list = []
        
        for text in texts:
            text_hash = _hash_text(text)
            
            # Check cache
            if use_cache and text_hash in _embedding_cache:
                embeddings_list.append(_embedding_cache[text_hash])
                _metrics["cache_hits"] += 1
                logger.debug(f"Cache hit for text (hash: {text_hash[:8]}...)")
            else:
                # Generate new embedding
                embedding = model.encode([text], convert_to_tensor=False, show_progress_bar=False)[0]
                embeddings_list.append(embedding)
                _metrics["cache_misses"] += 1
                
                # Store in cache
                if use_cache:
                    _embedding_cache[text_hash] = embedding
                    logger.debug(f"Cached embedding (hash: {text_hash[:8]}...)")
        
        embeddings = np.array(embeddings_list)
        elapsed_time = time.time() - start_time
        
        logger.info(f"Generated embeddings for {len(texts)} texts in {elapsed_time:.2f}s (cache hits: {_metrics['cache_hits']}, misses: {_metrics['cache_misses']})")
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        raise ValueError(f"Failed to generate embeddings: {str(e)}")


def compute_similarity(resume_embedding: np.ndarray, jd_embedding: np.ndarray) -> float:
    """
    Compute cosine similarity between resume and job description embeddings
    
    Args:
        resume_embedding: Resume embedding vector
        jd_embedding: Job description embedding vector
        
    Returns:
        Similarity score from 0-100 (percentage)
    """
    try:
        # Compute cosine similarity
        similarity = util.cos_sim(resume_embedding, jd_embedding).item()
        
        # Convert from [-1, 1] to [0, 100]
        # Cosine similarity is typically [0, 1] for text, so we scale to percentage
        score = max(0, min(100, similarity * 100))
        
        logger.info(f"Computed similarity score: {score:.2f}%")
        return round(score, 2)
    except Exception as e:
        logger.error(f"Error computing similarity: {str(e)}")
        raise


def extract_skills_and_keywords(text: str) -> List[str]:
    """
    Extract potential skills and keywords from text
    Simple extraction based on common patterns
    
    Args:
        text: Input text (resume or job description)
        
    Returns:
        List of extracted keywords/skills
    """
    # Common tech skills and keywords (expandable)
    skill_patterns = [
        r'\b(?:Python|Java|JavaScript|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|TypeScript)\b',
        r'\b(?:React|Angular|Vue|Django|Flask|FastAPI|Spring|Node\.js|Express)\b',
        r'\b(?:SQL|MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQLite)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|CI/CD|Git)\b',
        r'\b(?:Machine Learning|AI|Data Science|NLP|Computer Vision)\b',
        r'\b(?:Agile|Scrum|REST API|GraphQL|Microservices)\b',
        r'\b(?:Leadership|Communication|Problem Solving|Team Work)\b'
    ]
    
    keywords = []
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend(matches)
    
    # Remove duplicates and return
    return list(set(keywords))


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences for granular analysis
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    return sentences


def identify_strengths_gaps(resume_text: str, jd_text: str) -> Tuple[List[str], List[str]]:
    """
    Identify strengths (matches) and gaps (missing) between resume and JD
    
    Uses semantic similarity at sentence level to find:
    - Strengths: Resume sentences that match JD requirements
    - Gaps: JD requirements not covered in resume
    
    Args:
        resume_text: Full resume text
        jd_text: Full job description text
        
    Returns:
        Tuple of (strengths, gaps) as lists of strings
    """
    try:
        logger.info("Identifying strengths and gaps")
        
        # Extract keywords first (simple rule-based)
        resume_keywords = set(extract_skills_and_keywords(resume_text))
        jd_keywords = set(extract_skills_and_keywords(jd_text))
        
        # Find matching and missing keywords
        matching_keywords = resume_keywords.intersection(jd_keywords)
        missing_keywords = jd_keywords - resume_keywords
        
        # Split JD into requirements (sentences)
        jd_sentences = split_into_sentences(jd_text)
        resume_sentences = split_into_sentences(resume_text)
        
        if not jd_sentences or not resume_sentences:
            logger.warning("No valid sentences found for analysis")
            return (
                [f"Matching skills: {', '.join(list(matching_keywords)[:5])}" if matching_keywords else "Basic qualifications met"],
                [f"Missing skills: {', '.join(list(missing_keywords)[:5])}" if missing_keywords else "Consider adding more specific details"]
            )
        
        # Get embeddings for all sentences
        model = get_model()
        jd_embeddings = model.encode(jd_sentences, convert_to_tensor=True)
        resume_embeddings = model.encode(resume_sentences, convert_to_tensor=True)
        
        # Find matches: for each JD sentence, find best matching resume sentence
        strengths = []
        gaps = []
        
        similarity_threshold = 0.5  # Threshold for considering a match
        
        for idx, jd_sent in enumerate(jd_sentences[:10]):  # Limit to top 10 requirements
            # Compute similarity with all resume sentences
            similarities = util.cos_sim(jd_embeddings[idx], resume_embeddings)[0]
            max_similarity = similarities.max().item()
            
            if max_similarity > similarity_threshold:
                # Found a match - this is a strength
                best_match_idx = similarities.argmax().item()
                strengths.append({
                    "requirement": jd_sent[:100],  # Truncate long sentences
                    "match": resume_sentences[best_match_idx][:100],
                    "score": max_similarity
                })
            else:
                # No good match - this is a gap
                gaps.append({
                    "requirement": jd_sent[:100],
                    "score": max_similarity
                })
        
        # Sort by score and format
        strengths.sort(key=lambda x: x["score"], reverse=True)
        gaps.sort(key=lambda x: x["score"])
        
        # Format for output (top 5 each)
        strength_texts = [f"✓ {s['requirement']}" for s in strengths[:5]]
        gap_texts = [f"⚠ {g['requirement']}" for g in gaps[:5]]
        
        # Add keyword-based insights if available
        if matching_keywords:
            strength_texts.insert(0, f"✓ Matching skills: {', '.join(list(matching_keywords)[:5])}")
        if missing_keywords:
            gap_texts.insert(0, f"⚠ Missing skills: {', '.join(list(missing_keywords)[:5])}")
        
        logger.info(f"Found {len(strength_texts)} strengths and {len(gap_texts)} gaps")
        
        return (
            strength_texts[:5] if strength_texts else ["Your resume shows basic qualifications"],
            gap_texts[:5] if gap_texts else ["Consider adding more specific details to match requirements"]
        )
        
    except Exception as e:
        logger.error(f"Error in identify_strengths_gaps: {str(e)}")
        # Fallback to simple keyword matching
        resume_keywords = set(extract_skills_and_keywords(resume_text))
        jd_keywords = set(extract_skills_and_keywords(jd_text))
        
        matching = resume_keywords.intersection(jd_keywords)
        missing = jd_keywords - resume_keywords
        
        return (
            [f"Matching skills: {', '.join(list(matching)[:5])}" if matching else "Basic qualifications present"],
            [f"Missing skills: {', '.join(list(missing)[:5])}" if missing else "Consider adding more details"]
        )


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from PDF or DOCX files
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text as string
    """
    try:
        if file_path.lower().endswith('.pdf'):
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                logger.info(f"Extracted {len(text)} characters from PDF")
                return text
                
        elif file_path.lower().endswith('.docx'):
            import docx
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text
            
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
            
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}")
        raise


def validate_input_text(text: str, field_name: str, min_length: int = 50, max_length: int = 50000) -> None:
    """
    Validate input text with comprehensive checks
    Phase 4: Enhanced validation with detailed error messages
    
    Args:
        text: Input text to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum required length
        max_length: Maximum allowed length
        
    Raises:
        ValueError: If validation fails
    """
    if not text or not isinstance(text, str):
        raise ValueError(f"{field_name} must be a non-empty string")
    
    text = text.strip()
    
    if not text:
        raise ValueError(f"{field_name} cannot be empty or contain only whitespace")
    
    if len(text) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters (currently {len(text)})")
    
    if len(text) > max_length:
        raise ValueError(f"{field_name} is too long. Maximum {max_length} characters (currently {len(text)})")
    
    # Check for meaningful content (not just special characters)
    alphanumeric_count = sum(c.isalnum() for c in text)
    if alphanumeric_count < min_length * 0.5:
        raise ValueError(f"{field_name} does not contain enough meaningful content")


def get_metrics() -> Dict:
    """
    Get performance metrics for monitoring
    Phase 4: Added for analytics and debugging
    
    Returns:
        Dictionary with performance metrics
    """
    return {
        **_metrics,
        "cache_size": len(_embedding_cache),
        "cache_hit_rate": (_metrics["cache_hits"] / max(1, _metrics["cache_hits"] + _metrics["cache_misses"])) * 100
    }


def clear_cache() -> None:
    """
    Clear the embedding cache
    Phase 4: Useful for testing and memory management
    """
    global _embedding_cache
    _embedding_cache.clear()
    logger.info("Embedding cache cleared")


def analyze_resume_jd_match(resume_text: str, jd_text: str) -> Dict:
    """
    Complete analysis of resume and job description match
    Main function that orchestrates all semantic matching
    Phase 4: Enhanced error handling and performance tracking
    
    Args:
        resume_text: Resume text content
        jd_text: Job description text content
        
    Returns:
        Dictionary with match_score, strengths, gaps, processing_time
        
    Raises:
        ValueError: If input validation fails
        RuntimeError: If semantic analysis fails
    """
    start_time = time.time()
    
    try:
        logger.info("Starting semantic analysis")
        _metrics["total_requests"] += 1
        
        # Validate inputs with detailed error messages
        validate_input_text(resume_text, "Resume text", min_length=50, max_length=50000)
        validate_input_text(jd_text, "Job description text", min_length=50, max_length=50000)
        
        # Get embeddings for full texts (with caching)
        embeddings = get_embeddings([resume_text, jd_text], use_cache=True)
        resume_embedding = embeddings[0]
        jd_embedding = embeddings[1]
        
        # Compute overall similarity
        match_score = compute_similarity(resume_embedding, jd_embedding)
        
        # Identify strengths and gaps
        strengths, gaps = identify_strengths_gaps(resume_text, jd_text)
        
        processing_time = time.time() - start_time
        _metrics["total_processing_time"] += processing_time
        
        result = {
            "match_score": match_score,
            "strengths": strengths,
            "gaps": gaps,
            "processing_time": round(processing_time, 2),
            "metadata": {
                "resume_length": len(resume_text),
                "jd_length": len(jd_text),
                "cache_used": True
            }
        }
        
        logger.info(f"Analysis complete - Score: {match_score}%, Strengths: {len(strengths)}, Gaps: {len(gaps)}, Time: {processing_time:.2f}s")
        return result
        
    except ValueError as e:
        # Validation errors - user-friendly messages
        logger.warning(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        # Unexpected errors - log and re-raise
        logger.error(f"Unexpected error in analyze_resume_jd_match: {str(e)}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {str(e)}")
