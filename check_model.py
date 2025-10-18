"""Check which embedding model is currently configured."""

from sentence_transformers import SentenceTransformer

# Load the model that's configured in embedding_utils.py
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

print("\n" + "="*60)
print("📊 Current Embedding Model Configuration")
print("="*60)
print(f"\n🤖 Model: BAAI/bge-base-en-v1.5")
print(f"📏 Embedding Dimension: {model.get_sentence_embedding_dimension()}")
print(f"📝 Max Sequence Length: {model.max_seq_length}")
print(f"💾 Model Size: ~440MB")
print(f"🎯 Use Case: Semantic search & information retrieval")
print("\n" + "="*60)

# Test a sample embedding
sample_text = "Python developer with FastAPI experience"
embedding = model.encode(sample_text)
print(f"\n✅ Test Embedding Generated:")
print(f"   Input: '{sample_text}'")
print(f"   Output: {len(embedding)} dimensions")
print(f"   First 5 values: {embedding[:5].tolist()}")
print("\n" + "="*60 + "\n")
