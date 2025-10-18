"""
Job Matching Engine - Phase 5/6

Matches resumes with jobs using vector similarity and skill extraction.
"""

import logging
from typing import List, Dict, Any
import spacy
from collections import Counter

from ..config import Settings

logger = logging.getLogger(__name__)

# Global SpaCy model cache
_spacy_model = None


def get_spacy_model(settings: Settings):
    """Load and cache SpaCy model."""
    global _spacy_model
    
    if _spacy_model is None:
        logger.info(f"Loading SpaCy model: {settings.spacy_model}")
        _spacy_model = spacy.load(settings.spacy_model)
        logger.info("SpaCy model loaded successfully")
    
    return _spacy_model


def extract_skills(text: str, settings: Settings) -> List[str]:
    """
    Extract skills and keyphrases from text using SpaCy.
    
    Args:
        text: Job description or resume text
        settings: Application settings
        
    Returns:
        List of extracted skills/keyphrases
    """
    try:
        nlp = get_spacy_model(settings)
        doc = nlp(text.lower())
        
        skills = []
        
        # Extract noun chunks (technical terms, tools, frameworks)
        for chunk in doc.noun_chunks:
            # Filter out generic terms
            if len(chunk.text) > 2 and not chunk.root.is_stop:
                skills.append(chunk.text.strip())
        
        # Extract named entities (organizations, products, technologies)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE"]:
                skills.append(ent.text.strip())
        
        # Extract potential technical skills (words with specific patterns)
        for token in doc:
            # Look for capitalized words, tech terms, etc.
            if (token.is_alpha and 
                (token.text.isupper() or 
                 token.text in ["python", "java", "javascript", "sql", "aws", "docker", "kubernetes"])):
                skills.append(token.text)
        
        # Count frequency and return unique skills
        skill_counts = Counter(skills)
        top_skills = [skill for skill, count in skill_counts.most_common(50)]
        
        logger.info(f"Extracted {len(top_skills)} skills from text")
        return top_skills
        
    except Exception as e:
        logger.error(f"Skill extraction error: {e}")
        return []


def calculate_skill_match(
    resume_skills: List[str],
    job_skills: List[str]
) -> Dict[str, Any]:
    """
    Calculate skill match between resume and job.
    
    Args:
        resume_skills: Skills from resume
        job_skills: Skills from job description
        
    Returns:
        Dictionary with matched skills, gap skills, and match percentage
    """
    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)
    
    matched_skills = list(resume_set.intersection(job_set))
    gap_skills = list(job_set.difference(resume_set))
    
    # Calculate match percentage
    if len(job_set) > 0:
        match_percentage = (len(matched_skills) / len(job_set)) * 100
    else:
        match_percentage = 0
    
    return {
        "matched_skills": matched_skills[:10],  # Top 10 matches
        "gap_skills": gap_skills[:10],  # Top 10 gaps
        "match_percentage": round(match_percentage, 2),
        "total_matched": len(matched_skills),
        "total_required": len(job_set)
    }


async def rank_jobs(
    resume_text: str,
    job_matches: List[Dict[str, Any]],
    settings: Settings
) -> List[Dict[str, Any]]:
    """
    Rank and enrich job matches with skill analysis.
    
    Args:
        resume_text: Full resume text
        job_matches: Jobs from vector search (with scores)
        settings: Application settings
        
    Returns:
        Ranked jobs with skill match analysis
    """
    logger.info(f"Ranking {len(job_matches)} job matches")
    
    # Extract skills from resume
    resume_skills = extract_skills(resume_text, settings)
    
    ranked_jobs = []
    
    for match in job_matches:
        job_description = match["payload"].get("description", "")
        
        # Extract skills from job description
        job_skills = extract_skills(job_description, settings)
        
        # Calculate skill match
        skill_analysis = calculate_skill_match(resume_skills, job_skills)
        
        # Combine vector similarity score with skill match
        vector_score = match["score"] * 100  # Convert to percentage
        skill_score = skill_analysis["match_percentage"]
        
        # Weighted combined score (70% vector, 30% skill match)
        combined_score = (vector_score * 0.7) + (skill_score * 0.3)
        
        ranked_job = {
            "job_id": match["job_id"],
            "title": match["payload"].get("title", ""),
            "company": match["payload"].get("company", ""),
            "location": match["payload"].get("location", ""),
            "url": match["payload"].get("url", ""),
            "description": job_description[:500] + "...",  # Truncate for response
            "tags": match["payload"].get("tags", []),
            "salary_min": match["payload"].get("salary_min"),
            "salary_max": match["payload"].get("salary_max"),
            "employment_type": match["payload"].get("employment_type"),
            "experience_level": match["payload"].get("experience_level"),
            "vector_score": round(vector_score, 2),
            "skill_score": round(skill_score, 2),
            "combined_score": round(combined_score, 2),
            "matched_skills": skill_analysis["matched_skills"],
            "gap_skills": skill_analysis["gap_skills"],
            "fit_percentage": round(combined_score, 0)  # For progress bar
        }
        
        ranked_jobs.append(ranked_job)
    
    # Sort by combined score (descending)
    ranked_jobs.sort(key=lambda x: x["combined_score"], reverse=True)
    
    logger.info(f"Ranked jobs with scores ranging from {ranked_jobs[0]['combined_score']} to {ranked_jobs[-1]['combined_score']}")
    
    return ranked_jobs


def filter_jobs_by_criteria(
    jobs: List[Dict[str, Any]],
    min_salary: int = None,
    location: str = None,
    experience_level: str = None,
    employment_type: str = None
) -> List[Dict[str, Any]]:
    """
    Filter jobs by user criteria.
    
    Args:
        jobs: List of job matches
        min_salary: Minimum salary requirement
        location: Preferred location
        experience_level: entry, mid, senior
        employment_type: full-time, part-time, contract, internship
        
    Returns:
        Filtered job list
    """
    filtered = jobs
    
    if min_salary:
        filtered = [j for j in filtered if j.get("salary_max", 0) >= min_salary]
    
    if location:
        location_lower = location.lower()
        filtered = [
            j for j in filtered 
            if j.get("location") and location_lower in j["location"].lower()
        ]
    
    if experience_level:
        filtered = [
            j for j in filtered 
            if j.get("experience_level") == experience_level
        ]
    
    if employment_type:
        filtered = [
            j for j in filtered 
            if j.get("employment_type") == employment_type
        ]
    
    logger.info(f"Filtered to {len(filtered)} jobs from {len(jobs)}")
    return filtered
