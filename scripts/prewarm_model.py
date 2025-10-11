"""
Pre-warm script to download Sentence-BERT model before first use
Run this once to avoid waiting on first API request
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from utils.semantic_utils import get_model

if __name__ == "__main__":
    print("🔄 Downloading and loading Sentence-BERT model...")
    print("📦 Model: all-MiniLM-L6-v2 (~80MB)")
    print("⏱️ This may take 1-2 minutes on first run...\n")
    
    try:
        model = get_model()
        print("✅ Model loaded successfully!")
        print(f"📊 Model dimension: {model.get_sentence_embedding_dimension()}")
        print("\n🎉 You're all set! Subsequent requests will be fast.")
        
        # Test embedding
        print("\n🧪 Testing with sample text...")
        test_embedding = model.encode(["Hello world"], show_progress_bar=False)
        print(f"✅ Test successful! Embedding shape: {test_embedding.shape}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
