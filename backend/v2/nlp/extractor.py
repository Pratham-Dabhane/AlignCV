"""
NLP utilities for extracting skills, roles, and entities from documents.

Uses SpaCy for Named Entity Recognition and pattern matching.
"""

import logging
import spacy
from typing import List, Dict, Set
from functools import lru_cache

from ..config import settings

logger = logging.getLogger(__name__)

# Common skill keywords to extract
SKILL_KEYWORDS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php",
    "swift", "kotlin", "go", "rust", "scala", "r", "matlab",
    
    # Web Technologies
    "html", "css", "react", "angular", "vue", "node.js", "express",
    "django", "flask", "fastapi", "spring boot", "asp.net",
    
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "dynamodb", "cassandra", "oracle", "sqlite",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "gitlab ci",
    "github actions", "terraform", "ansible", "ci/cd",
    
    # Data Science & ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
    "pandas", "numpy", "matplotlib", "jupyter", "data analysis",
    
    # Tools & Frameworks
    "git", "jira", "agile", "scrum", "rest api", "graphql", "microservices",
    "oauth", "jwt", "redis", "rabbitmq", "kafka",
}

# Common job roles
JOB_ROLES = {
    "software engineer", "backend developer", "frontend developer",
    "full stack developer", "data scientist", "machine learning engineer",
    "devops engineer", "cloud engineer", "data engineer", "qa engineer",
    "product manager", "project manager", "tech lead", "architect",
}


@lru_cache(maxsize=1)
def load_spacy_model():
    """
    Load SpaCy model (cached).
    
    Returns:
        spacy.Language: Loaded SpaCy model
    """
    try:
        logger.info(f"Loading SpaCy model: {settings.spacy_model}")
        nlp = spacy.load(settings.spacy_model)
        logger.info("SpaCy model loaded successfully")
        return nlp
    except OSError:
        logger.error(f"SpaCy model not found: {settings.spacy_model}")
        logger.info("Please run: python -m spacy download en_core_web_sm")
        raise


def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from text.
    
    Args:
        text: Input text (resume or job description)
        
    Returns:
        List of extracted skills
    """
    text_lower = text.lower()
    found_skills = set()
    
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found_skills.add(skill.title())
    
    return sorted(list(found_skills))


def extract_roles(text: str) -> List[str]:
    """
    Extract job roles/titles from text.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted roles
    """
    text_lower = text.lower()
    found_roles = set()
    
    for role in JOB_ROLES:
        if role in text_lower:
            found_roles.add(role.title())
    
    return sorted(list(found_roles))


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities using SpaCy NER.
    
    Args:
        text: Input text
        
    Returns:
        Dict with entity types as keys and lists of entities as values
    """
    try:
        nlp = load_spacy_model()
        doc = nlp(text[:100000])  # Limit to 100k chars for performance
        
        entities = {}
        for ent in doc.ents:
            entity_type = ent.label_
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append(ent.text)
        
        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    except Exception as e:
        logger.error(f"Entity extraction failed: {str(e)}")
        return {}


def extract_all(text: str) -> Dict[str, any]:
    """
    Extract all information from text.
    
    Args:
        text: Input text
        
    Returns:
        Dict with skills, roles, and entities
    """
    return {
        "skills": extract_skills(text),
        "roles": extract_roles(text),
        "entities": extract_entities(text)
    }
