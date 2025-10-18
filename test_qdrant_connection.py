"""
Quick test to verify Qdrant connection
"""
import asyncio
from backend.v2.config import get_settings
from backend.v2.jobs.vector_store import get_qdrant_client, create_collection

async def test_connection():
    print("=" * 60)
    print("Testing Qdrant Connection")
    print("=" * 60)
    
    settings = get_settings()
    
    print(f"\n1. Configuration:")
    print(f"   URL: {settings.qdrant_url}")
    print(f"   API Key: {'✓ Set' if settings.qdrant_api_key else '✗ Missing'}")
    print(f"   Collection: {settings.qdrant_collection_name}")
    
    print(f"\n2. Connecting to Qdrant...")
    try:
        client = get_qdrant_client(settings)
        print("   ✅ Client initialized successfully!")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False
    
    print(f"\n3. Creating collection '{settings.qdrant_collection_name}'...")
    try:
        await create_collection(settings, vector_size=384)
        print(f"   ✅ Collection ready!")
    except Exception as e:
        print(f"   ⚠️  Collection operation: {e}")
        # This might be OK if collection already exists
    
    print(f"\n4. Checking connection health...")
    try:
        collections = client.get_collections()
        print(f"   ✅ Connection working!")
        print(f"   📊 Total collections: {len(collections.collections)}")
        
        # List collections
        for col in collections.collections:
            print(f"      - {col.name}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Qdrant is connected and ready!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if not result:
        print("\n❌ Connection test failed. Check your credentials.")
    else:
        print("\n✅ All systems go! Ready to ingest jobs.")
