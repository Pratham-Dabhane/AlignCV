"""
Recreate Qdrant Collection with 768 Dimensions (BGE-base-en-v1.5)

This script:
1. Deletes the existing aligncv_jobs collection (384-dim)
2. Creates a new collection with 768 dimensions for BGE embeddings
3. Re-ingests all jobs with new BGE-base-en-v1.5 embeddings
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.v2.config import get_settings
from backend.v2.jobs.vector_store import get_qdrant_client, create_collection
from backend.v2.jobs.ingest import ingest_jobs_from_sources, MockJobScraper
from backend.v2.jobs.embedding_utils import get_job_embedding
from backend.v2.jobs.vector_store import upsert_job_vector


async def recreate_collection():
    """Recreate Qdrant collection with 768 dimensions."""
    settings = get_settings()
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    print(f"\n🔄 Phase 6.1: Upgrading to BGE-base-en-v1.5 (768-dim)\n")
    print("=" * 60)
    
    # Step 1: Delete existing collection
    try:
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if exists:
            print(f"\n🗑️  Deleting existing collection '{collection_name}'...")
            client.delete_collection(collection_name)
            print(f"✅ Collection deleted")
        else:
            print(f"\nℹ️  Collection '{collection_name}' does not exist (first time setup)")
    except Exception as e:
        print(f"⚠️  Error checking/deleting collection: {e}")
    
    # Step 2: Create new collection with 768 dimensions
    print(f"\n🏗️  Creating new collection with 768 dimensions...")
    try:
        await create_collection(settings, vector_size=768)
        print(f"✅ Collection '{collection_name}' created with 768 dimensions")
    except Exception as e:
        print(f"❌ Failed to create collection: {e}")
        return False
    
    # Step 3: Verify collection
    try:
        collection_info = client.get_collection(collection_name)
        print(f"\n📊 Collection Info:")
        print(f"   - Name: {collection_info.config.params.vectors.size}")
        print(f"   - Vector size: {collection_info.config.params.vectors.size}")
        print(f"   - Distance: {collection_info.config.params.vectors.distance}")
        print(f"   - Points count: {collection_info.points_count}")
    except Exception as e:
        print(f"⚠️  Could not verify collection: {e}")
    
    # Step 4: Re-ingest jobs with BGE embeddings
    print(f"\n📥 Re-ingesting jobs with BGE-base-en-v1.5 embeddings...")
    try:
        # Fetch jobs from mock scraper
        jobs_data = await ingest_jobs_from_sources()
        
        embeddings_created = 0
        for job_data in jobs_data:
            # Generate embedding with BGE
            job_embedding = await get_job_embedding(job_data["description"], settings)
            
            # Store in Qdrant
            await upsert_job_vector(
                job_id=job_data["job_id"],
                vector=job_embedding,
                payload={
                    "title": job_data["title"],
                    "company": job_data["company"],
                    "description": job_data["description"][:500],  # Truncate for storage
                    "url": job_data["url"],
                    "location": job_data.get("location"),
                    "tags": job_data.get("tags", []),
                },
                settings=settings
            )
            embeddings_created += 1
        
        print(f"\n✅ Ingestion Complete:")
        print(f"   - Total jobs: {len(jobs_data)}")
        print(f"   - Embeddings created: {embeddings_created}")
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Final verification
    try:
        collection_info = client.get_collection(collection_name)
        print(f"\n✅ Final Status:")
        print(f"   - Collection: {collection_name}")
        print(f"   - Vector dimension: {collection_info.config.params.vectors.size}")
        print(f"   - Total points: {collection_info.points_count}")
        print(f"   - Status: {collection_info.status}")
    except Exception as e:
        print(f"⚠️  Could not verify final status: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Phase 6.1 upgrade complete!")
    print("   BGE-base-en-v1.5 (768-dim) is now active\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(recreate_collection())
    sys.exit(0 if success else 1)
