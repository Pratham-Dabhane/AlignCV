"""
Vector Embedding Utilities - Phase 6.1

Handles text-to-vector embeddings using BGE-base-en-v1.5 (768-dim).
Upgraded from all-MiniLM-L6-v2 (384-dim) for better semantic search quality.
"""

import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer

from ..config import Settings

logger = logging.getLogger(__name__)

# Global model cache
_sentence_transformer_model: Optional[SentenceTransformer] = None


def get_sentence_transformer_model() -> SentenceTransformer:
    """
    Load and cache sentence-transformers model.
    
    Uses 'BAAI/bge-base-en-v1.5' for high-quality semantic search.
    Model size: ~440MB, Embedding dimension: 768
    Best for: Information retrieval, semantic similarity
    """
    global _sentence_transformer_model
    
    if _sentence_transformer_model is None:
        logger.info("Loading sentence-transformers model: BAAI/bge-base-en-v1.5")
        _sentence_transformer_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
        logger.info("BGE-base-en-v1.5 model loaded successfully (768-dim)")
    
    return _sentence_transformer_model


def get_local_embedding(text: str) -> List[float]:
    """
    Get embedding using local sentence-transformers model.
    
    Uses BGE-base-en-v1.5 for optimal semantic search performance.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector (768 dimensions)
    """
    try:
        model = get_sentence_transformer_model()
        embedding = model.encode(text, convert_to_numpy=True)
        logger.info(f"BGE embedding generated: {len(embedding)} dimensions")
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Local embedding error: {e}")
        raise


async def get_job_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for job description.
    
    Uses BGE-base-en-v1.5 for optimal semantic search (768 dimensions).
    
    Args:
        text: Job description text
        settings: Application settings
        
    Returns:
        Embedding vector (768 dimensions)
    """
    # Use BGE-base-en-v1.5 for high-quality semantic embeddings
    logger.info("Using BGE-base-en-v1.5 embedding model for job (768-dim)")
    return get_local_embedding(text)


async def get_resume_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for resume/CV.
    
    Uses BGE-base-en-v1.5 for optimal semantic search (768 dimensions).
    
    Args:
        text: Resume text
        settings: Application settings
        
    Returns:
        Embedding vector (768 dimensions)
    """
    # Use BGE-base-en-v1.5 for high-quality semantic embeddings
    logger.info("Using BGE-base-en-v1.5 embedding model for resume (768-dim)")
    return get_local_embedding(text)


async def get_batch_embeddings(texts: List[str], settings: Settings) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Uses local model for batch processing (faster than API calls).
    
    Args:
        texts: List of texts to embed
        settings: Application settings
        
    Returns:
        List of embedding vectors
    """
    try:
        logger.info(f"Generating batch embeddings for {len(texts)} texts")
        model = get_sentence_transformer_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        logger.info(f"Batch embeddings generated: {len(embeddings)} vectors")
        return [emb.tolist() for emb in embeddings]
    except Exception as e:
        logger.error(f"Batch embedding error: {e}")
        raise
