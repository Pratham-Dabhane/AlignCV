"""
Simple test to check BGE embedding generation
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.v2.config import get_settings
from backend.v2.jobs.embedding_utils import get_job_embedding, get_resume_embedding


async def test_bge():
    """Test BGE embedding generation."""
    settings = get_settings()
    
    print("\n🧪 Testing BGE-base-en-v1.5 Embeddings\n")
    print("=" * 60)
    
    # Test job embedding
    print("\n📋 Test 1: Job Description Embedding")
    job_text = "Senior Software Engineer with 5+ years Python and FastAPI experience"
    print(f"Input: {job_text[:50]}...")
    
    try:
        job_embedding = await get_job_embedding(job_text, settings)
        print(f"✅ Embedding generated: {len(job_embedding)} dimensions")
        print(f"   First 5 values: {job_embedding[:5]}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test resume embedding
    print("\n👤 Test 2: Resume Text Embedding")
    resume_text = "Experienced software developer skilled in Python, machine learning, and cloud technologies"
    print(f"Input: {resume_text[:50]}...")
    
    try:
        resume_embedding = await get_resume_embedding(resume_text, settings)
        print(f"✅ Embedding generated: {len(resume_embedding)} dimensions")
        print(f"   First 5 values: {resume_embedding[:5]}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! BGE embeddings working correctly\n")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_bge())
    sys.exit(0 if success else 1)
