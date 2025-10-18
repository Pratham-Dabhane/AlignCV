"""
Quick Test Script for Phase 5/6 - Job Matching Engine

Tests the job matching system without full database setup.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.v2.config import settings
from backend.v2.jobs.embedding_utils import get_local_embedding, get_batch_embeddings
from backend.v2.jobs.matcher import extract_skills, calculate_skill_match
from backend.v2.jobs.ingest import MockJobScraper


async def test_embeddings():
    """Test embedding generation."""
    print("=" * 60)
    print("Testing Embedding Generation")
    print("=" * 60)
    
    # Test single embedding
    print("\n1. Single Embedding Test...")
    text = "Senior Python developer with FastAPI and PostgreSQL experience"
    embedding = get_local_embedding(text)
    print(f"   ✅ Generated embedding with {len(embedding)} dimensions")
    assert len(embedding) == 384, "Expected 384 dimensions"
    
    # Test batch embeddings
    print("\n2. Batch Embedding Test...")
    texts = [
        "Machine Learning Engineer with TensorFlow",
        "Frontend Developer with React and TypeScript",
        "DevOps Engineer with Kubernetes and AWS"
    ]
    embeddings = await get_batch_embeddings(texts, settings)
    print(f"   ✅ Generated {len(embeddings)} embeddings")
    assert len(embeddings) == 3, "Expected 3 embeddings"
    
    print("\n✅ Embedding tests passed!\n")


def test_skill_extraction():
    """Test skill extraction with SpaCy."""
    print("=" * 60)
    print("Testing Skill Extraction")
    print("=" * 60)
    
    resume_text = """
    Senior Software Engineer with 5 years of experience.
    Expert in Python, FastAPI, PostgreSQL, Docker, and Kubernetes.
    Built scalable APIs and microservices on AWS.
    Strong knowledge of machine learning and NLP.
    """
    
    print("\n1. Extracting Skills from Resume...")
    skills = extract_skills(resume_text, settings)
    print(f"   ✅ Extracted {len(skills)} skills")
    print(f"   Skills: {skills[:10]}...")
    
    job_description = """
    Looking for a Senior Python Engineer.
    Requirements: Python, FastAPI, PostgreSQL, Redis, AWS.
    Experience with Docker and Kubernetes preferred.
    """
    
    print("\n2. Extracting Skills from Job Description...")
    job_skills = extract_skills(job_description, settings)
    print(f"   ✅ Extracted {len(job_skills)} skills")
    print(f"   Skills: {job_skills[:10]}...")
    
    print("\n3. Calculating Skill Match...")
    match_result = calculate_skill_match(skills, job_skills)
    print(f"   ✅ Match Percentage: {match_result['match_percentage']}%")
    print(f"   ✅ Matched Skills: {match_result['matched_skills'][:5]}")
    print(f"   ✅ Gap Skills: {match_result['gap_skills'][:5]}")
    
    print("\n✅ Skill extraction tests passed!\n")


async def test_job_ingestion():
    """Test job ingestion."""
    print("=" * 60)
    print("Testing Job Ingestion")
    print("=" * 60)
    
    print("\n1. Running MockJobScraper...")
    scraper = MockJobScraper()
    jobs = await scraper.scrape()
    
    print(f"   ✅ Scraped {len(jobs)} jobs")
    
    print("\n2. Sample Jobs:")
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n   Job {i}:")
        print(f"   Title: {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Salary: ${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}")
        print(f"   Tags: {', '.join(job.get('tags', []))}")
    
    print("\n✅ Job ingestion tests passed!\n")


def test_matching_algorithm():
    """Test the complete matching algorithm."""
    print("=" * 60)
    print("Testing Job Matching Algorithm")
    print("=" * 60)
    
    resume_text = """
    Experienced Python developer with 3 years of backend development.
    Skills: Python, FastAPI, PostgreSQL, Docker, REST APIs.
    Built microservices and worked with AWS.
    """
    
    job_description_1 = """
    Senior Python Developer needed.
    Requirements: Python, FastAPI, PostgreSQL, Kubernetes, AWS.
    Build scalable backend systems.
    """
    
    job_description_2 = """
    Frontend Developer wanted.
    Requirements: React, TypeScript, JavaScript, CSS, HTML.
    Build responsive web applications.
    """
    
    print("\n1. Extracting Resume Skills...")
    resume_skills = extract_skills(resume_text, settings)
    print(f"   ✅ Resume has {len(resume_skills)} skills")
    
    print("\n2. Matching with Job 1 (Backend - Good Fit)...")
    job1_skills = extract_skills(job_description_1, settings)
    match1 = calculate_skill_match(resume_skills, job1_skills)
    print(f"   ✅ Match: {match1['match_percentage']}%")
    print(f"   ✅ Matched: {match1['matched_skills'][:5]}")
    print(f"   ✅ Gaps: {match1['gap_skills'][:5]}")
    
    print("\n3. Matching with Job 2 (Frontend - Poor Fit)...")
    job2_skills = extract_skills(job_description_2, settings)
    match2 = calculate_skill_match(resume_skills, job2_skills)
    print(f"   ✅ Match: {match2['match_percentage']}%")
    print(f"   ✅ Matched: {match2['matched_skills'][:5]}")
    print(f"   ✅ Gaps: {match2['gap_skills'][:5]}")
    
    print("\n4. Verification...")
    assert match1['match_percentage'] > match2['match_percentage'], \
        "Backend job should match better than frontend job"
    print(f"   ✅ Backend match ({match1['match_percentage']}%) > Frontend match ({match2['match_percentage']}%)")
    
    print("\n✅ Matching algorithm tests passed!\n")


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AlignCV Phase 5/6 - Job Matching Quick Test")
    print("=" * 60 + "\n")
    
    try:
        # Test embeddings
        await test_embeddings()
        
        # Test skill extraction
        test_skill_extraction()
        
        # Test job ingestion
        await test_job_ingestion()
        
        # Test matching algorithm
        test_matching_algorithm()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nPhase 5/6 is working correctly!")
        print("\nNext Steps:")
        print("1. Setup Qdrant (cloud or local Docker)")
        print("2. Add QDRANT_URL and QDRANT_API_KEY to .env")
        print("3. Run: uvicorn backend.v2.app_v2:app_v2 --reload --port 8001")
        print("4. Visit: http://localhost:8001/v2/docs")
        print("5. Try POST /v2/jobs/ingest to load mock jobs")
        print("6. Try POST /v2/jobs/match to match your resume")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
