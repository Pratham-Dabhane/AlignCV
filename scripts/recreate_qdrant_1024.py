"""
Recreate Qdrant collection for 1024-dimensional Mistral embeddings
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

# Qdrant credentials
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "aligncv_jobs"

print("=" * 70)
print("Recreating Qdrant Collection for Mistral (1024-dim)")
print("=" * 70)

# Connect to Qdrant
print("\n1. Connecting to Qdrant...")
client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)
print("✅ Connected!")

# Delete old collection
print(f"\n2. Deleting old collection: {COLLECTION_NAME}")
try:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print("✅ Old collection deleted!")
except Exception as e:
    print(f"⚠️  No existing collection to delete: {e}")

# Create new collection with 1024 dimensions
print(f"\n3. Creating new collection with 1024 dimensions...")
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=1024,  # Mistral embeddings
        distance=Distance.COSINE
    )
)
print("✅ Collection created with 1024 dimensions!")

# Verify
print(f"\n4. Verifying collection...")
collection_info = client.get_collection(collection_name=COLLECTION_NAME)
print(f"   Collection: {collection_info.config.params.vectors.size}-dimensional vectors")
print(f"   Distance: {collection_info.config.params.vectors.distance}")

print("\n" + "=" * 70)
print("🎉 Qdrant collection ready for Mistral embeddings!")
print("=" * 70)
print("\nNext steps:")
print("1. Edit backend/v2/jobs/embedding_utils.py")
print("2. Re-enable Mistral in get_job_embedding() and get_resume_embedding()")
print("3. Restart the server")
print("4. Run job ingestion again")
