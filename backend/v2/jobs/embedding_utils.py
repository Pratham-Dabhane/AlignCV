"""
Vector Embedding Utilities - Phase 5/6

Handles text-to-vector embeddings using Mistral AI or sentence-transformers fallback.
"""

import logging
from typing import List, Optional
import httpx
from sentence_transformers import SentenceTransformer

from ..config import Settings

logger = logging.getLogger(__name__)

# Global model cache
_sentence_transformer_model: Optional[SentenceTransformer] = None


def get_sentence_transformer_model() -> SentenceTransformer:
    """
    Load and cache sentence-transformers model.
    
    Uses 'all-MiniLM-L6-v2' for fast, high-quality embeddings.
    Model size: ~90MB, Embedding dimension: 384
    """
    global _sentence_transformer_model
    
    if _sentence_transformer_model is None:
        logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
        _sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    
    return _sentence_transformer_model


async def get_mistral_embedding(text: str, api_key: str) -> Optional[List[float]]:
    """
    Get embedding from Mistral AI API.
    
    Args:
        text: Text to embed
        api_key: Mistral API key
        
    Returns:
        Embedding vector or None if failed
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-embed",
                    "input": [text]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                embedding = data["data"][0]["embedding"]
                logger.info(f"Mistral embedding generated: {len(embedding)} dimensions")
                return embedding
            else:
                logger.warning(f"Mistral API error: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Mistral embedding error: {e}")
        return None


def get_local_embedding(text: str) -> List[float]:
    """
    Get embedding using local sentence-transformers model.
    
    Fallback when Mistral API is unavailable.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector (384 dimensions)
    """
    try:
        model = get_sentence_transformer_model()
        embedding = model.encode(text, convert_to_numpy=True)
        logger.info(f"Local embedding generated: {len(embedding)} dimensions")
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Local embedding error: {e}")
        raise


async def get_job_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for job description.
    
    Uses local model for consistency (384 dimensions).
    Mistral embeddings are 1024-dim, which requires different Qdrant collection setup.
    
    Args:
        text: Job description text
        settings: Application settings
        
    Returns:
        Embedding vector (384 dimensions)
    """
    # Use local model for consistent 384-dimensional embeddings
    # Note: To use Mistral (1024-dim), recreate Qdrant collection with size=1024
    logger.info("Using local embedding model for job (384-dim)")
    return get_local_embedding(text)


async def get_resume_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for resume/CV.
    
    Uses local model for consistency (384 dimensions).
    
    Args:
        text: Resume text
        settings: Application settings
        
    Returns:
        Embedding vector (384 dimensions)
    """
    # Use local model for consistent 384-dimensional embeddings
    logger.info("Using local embedding model for resume (384-dim)")
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
