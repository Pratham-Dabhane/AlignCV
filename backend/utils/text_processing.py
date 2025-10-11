"""
Text processing utilities
Future: Clean and preprocess resume and job description text
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean input text by removing extra whitespace and special characters
    
    Phase 2+: Expand with more sophisticated cleaning
    - Remove URLs
    - Normalize whitespace
    - Handle special characters
    - Lowercase conversion
    
    Args:
        text: Raw input text
        
    Returns:
        Cleaned text
    """
    # Basic cleaning for Phase 1
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    return text


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text
    
    Phase 2+: Implement keyword extraction
    - Use NLP techniques
    - Extract skills, technologies, qualifications
    
    Args:
        text: Input text
        
    Returns:
        List of extracted keywords
    """
    # Placeholder for Phase 2+
    return []


def split_into_sections(resume_text: str) -> dict:
    """
    Split resume into sections (experience, education, skills, etc.)
    
    Phase 2+: Implement section detection
    
    Args:
        resume_text: Full resume text
        
    Returns:
        Dictionary with section names as keys
    """
    # Placeholder for Phase 2+
    return {"full_text": resume_text}
