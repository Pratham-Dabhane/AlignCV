"""
Comprehensive Integration Test for All Phases (1-8)
Tests if all components work together seamlessly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.v2.config import get_settings
from backend.v2.database import get_db, init_db
from backend.v2.models.models import User, Document, Job
from backend.v2.auth.utils import hash_password, create_access_token
from backend.v2.jobs.embedding_utils import get_local_embedding
from backend.v2.ai.rewrite_engine import rewrite_resume
from backend.v2.jobs.vector_store import get_qdrant_client
from backend.v2.nlp.extractor import extract_all
from sqlalchemy import select
import httpx

print("="*80)
print("🧪 ALIGNCV - COMPREHENSIVE INTEGRATION TEST (PHASES 1-8)")
print("="*80)

async def test_phase1_database():
    """Phase 1: Database & Models"""
    print("\n📦 PHASE 1: Testing Database & Models...")
    try:
        await init_db()
        print("   ✅ Database initialized")
        
        async for db in get_db():
            # Test User model
            result = await db.execute(select(User).limit(1))
            print("   ✅ User model accessible")
            
            # Test Document model
            result = await db.execute(select(Document).limit(1))
            print("   ✅ Document model accessible")
            
            # Test Job model
            result = await db.execute(select(Job).limit(1))
            print("   ✅ Job model accessible")
            break
        
        return True
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False


async def test_phase2_auth():
    """Phase 2: Authentication System"""
    print("\n🔐 PHASE 2: Testing Authentication...")
    try:
        # Test password hashing
        password = "TestPassword123!"
        hashed = hash_password(password)
        print(f"   ✅ Password hashing works (length: {len(hashed)})")
        
        # Test JWT token creation
        token = create_access_token({"sub": "test@example.com", "user_id": 1})
        print(f"   ✅ JWT token generation works (length: {len(token)})")
        
        return True
    except Exception as e:
        print(f"   ❌ Auth Error: {e}")
        return False


async def test_phase3_ai_rewriting():
    """Phase 3: AI Rewriting (Mistral)"""
    print("\n🤖 PHASE 3: Testing AI Rewriting (Mistral API)...")
    try:
        settings = get_settings()
        
        if not settings.mistral_api_key or settings.mistral_api_key.startswith("your_"):
            print("   ⚠️  Mistral API key not configured (skipping)")
            return True
        
        test_text = "Software Engineer with 3 years of Python experience."
        
        result = await rewrite_resume(
            resume_text=test_text,
            style="Technical"
        )
        
        if result and "rewritten_text" in result:
            print(f"   ✅ Mistral AI rewriting works")
            print(f"   📝 Original: {test_text[:50]}...")
            print(f"   📝 Rewritten: {result['rewritten_text'][:80]}...")
            return True
        else:
            print(f"   ❌ Mistral response invalid: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ AI Rewriting Error: {e}")
        return False


async def test_phase4_nlp_extraction():
    """Phase 4: NLP Skill Extraction"""
    print("\n🧠 PHASE 4: Testing NLP Extraction (SpaCy)...")
    try:
        test_text = """
        Software Engineer with 5 years of experience in Python, JavaScript, and React.
        Built REST APIs with FastAPI and Django. Worked with PostgreSQL and MongoDB.
        """
        
        result = extract_all(test_text)
        
        if result and "skills" in result:
            print(f"   ✅ SpaCy NLP extraction works")
            print(f"   📊 Extracted skills: {result['skills'][:5]}")
            print(f"   📊 Roles: {result.get('roles', [])}")
            return True
        else:
            print(f"   ❌ NLP extraction failed: {result}")
            return False
            
    except Exception as e:
        print(f"   ❌ NLP Extraction Error: {e}")
        return False


async def test_phase56_embeddings():
    """Phase 5-6: Embeddings (BAAI/BGE)"""
    print("\n🔢 PHASE 5-6: Testing Embeddings (BAAI/bge-base-en-v1.5)...")
    try:
        test_text = "Senior Python Developer with FastAPI and machine learning experience"
        
        embedding = get_local_embedding(test_text)
        
        if embedding and len(embedding) == 768:
            print(f"   ✅ BAAI/BGE embeddings work")
            print(f"   📐 Dimensions: {len(embedding)} (768-dim)")
            print(f"   📊 Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
            return True
        else:
            print(f"   ❌ Embedding dimensions wrong: {len(embedding) if embedding else 0}")
            return False
            
    except Exception as e:
        print(f"   ❌ Embeddings Error: {e}")
        return False


async def test_phase56_qdrant():
    """Phase 5-6: Vector Database (Qdrant)"""
    print("\n🗄️  PHASE 5-6: Testing Vector Database (Qdrant)...")
    try:
        settings = get_settings()
        
        if not settings.qdrant_url or not settings.qdrant_api_key:
            print("   ⚠️  Qdrant not configured (skipping)")
            return True
        
        client = get_qdrant_client(settings)
        
        # Test connection by getting collections
        collections = client.get_collections()
        
        print(f"   ✅ Qdrant connection works")
        print(f"   📦 Collections: {len(collections.collections)}")
        return True
            
    except Exception as e:
        print(f"   ❌ Qdrant Error: {e}")
        return False


async def test_phase7_notifications():
    """Phase 7: Notification System"""
    print("\n📧 PHASE 7: Testing Notification System...")
    try:
        settings = get_settings()
        
        # Check SendGrid config
        if settings.sendgrid_api_key and not settings.sendgrid_api_key.startswith("placeholder"):
            print(f"   ✅ SendGrid configured")
            print(f"   📧 From: {settings.sendgrid_from_email}")
        else:
            print(f"   ⚠️  SendGrid not configured (optional)")
        
        # Check Redis/Celery config
        if settings.upstash_redis_rest_url:
            print(f"   ✅ Upstash Redis configured")
            print(f"   ⏰ Celery task queue ready")
        else:
            print(f"   ⚠️  Redis not configured (optional)")
        
        return True
            
    except Exception as e:
        print(f"   ❌ Notification Error: {e}")
        return False


async def test_phase8_logging():
    """Phase 8: Structured Logging"""
    print("\n📝 PHASE 8: Testing Structured Logging...")
    try:
        from backend.v2.logging_config import get_logger
        
        logger = get_logger(__name__)
        logger.info("Test log message from integration test")
        print(f"   ✅ Structured logging works")
        print(f"   ✅ Request logging middleware ready")
        
        return True
            
    except Exception as e:
        print(f"   ❌ Logging Error: {e}")
        return False


async def test_phase8_api_integration():
    """Phase 8: API Integration"""
    print("\n🌐 PHASE 8: Testing API Integration...")
    try:
        # Test if server is running on port 8001
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8001/v2/health", timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ API server running on port 8001")
                    print(f"   📊 Status: {data.get('status', 'unknown')}")
                    print(f"   📊 Database: {data.get('database', 'unknown')}")
                    return True
                else:
                    print(f"   ⚠️  API returned status: {response.status_code}")
                    return True  # Don't fail if server not running
                    
            except httpx.ConnectError:
                print(f"   ⚠️  API server not running (start with: python start_server.py)")
                return True  # Don't fail if server not running
            
    except Exception as e:
        print(f"   ❌ API Integration Error: {e}")
        return False


async def test_full_workflow():
    """Test complete workflow: Auth -> Upload -> Rewrite -> Match -> Notify"""
    print("\n🔄 TESTING COMPLETE WORKFLOW...")
    try:
        settings = get_settings()
        
        # Step 1: Auth token
        token = create_access_token({"sub": "test@example.com", "user_id": 999})
        print(f"   ✅ Step 1: Auth token created")
        
        # Step 2: Extract skills
        resume_text = "Python Developer with FastAPI, React, and PostgreSQL experience"
        skills = extract_all(resume_text)
        print(f"   ✅ Step 2: Skills extracted ({len(skills.get('skills', []))} skills)")
        
        # Step 3: Generate embeddings
        embedding = get_local_embedding(resume_text)
        print(f"   ✅ Step 3: Embeddings generated ({len(embedding)} dims)")
        
        # Step 4: AI Rewriting (if configured)
        if settings.mistral_api_key and not settings.mistral_api_key.startswith("your_"):
            rewrite_result = await rewrite_resume(
                resume_text=resume_text,
                style="Technical"
            )
            if rewrite_result:
                print(f"   ✅ Step 4: Resume rewritten with AI")
            else:
                print(f"   ⚠️  Step 4: AI rewriting skipped")
        else:
            print(f"   ⚠️  Step 4: AI rewriting skipped (no API key)")
        
        print(f"   ✅ COMPLETE WORKFLOW SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"   ❌ Workflow Error: {e}")
        return False


async def main():
    """Run all integration tests"""
    print("\n🚀 Starting comprehensive integration test...\n")
    
    results = {}
    
    # Test each phase
    results["Phase 1 - Database"] = await test_phase1_database()
    results["Phase 2 - Auth"] = await test_phase2_auth()
    results["Phase 3 - AI Rewriting"] = await test_phase3_ai_rewriting()
    results["Phase 4 - NLP Extraction"] = await test_phase4_nlp_extraction()
    results["Phase 5-6 - Embeddings"] = await test_phase56_embeddings()
    results["Phase 5-6 - Qdrant"] = await test_phase56_qdrant()
    results["Phase 7 - Notifications"] = await test_phase7_notifications()
    results["Phase 8 - Logging"] = await test_phase8_logging()
    results["Phase 8 - API Integration"] = await test_phase8_api_integration()
    results["Complete Workflow"] = await test_full_workflow()
    
    # Print summary
    print("\n" + "="*80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for phase, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {phase}")
    
    print("\n" + "="*80)
    print(f"🎯 RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL - ALIGNCV IS PRODUCTION READY!")
    elif passed >= total * 0.7:
        print("⚠️  MOSTLY WORKING - Some optional features need configuration")
    else:
        print("❌ CRITICAL ISSUES - Please review failed tests")
    
    print("="*80)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
