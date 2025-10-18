"""
Mistral-enabled version of embedding_utils.py

To use this:
1. Run: python scripts/recreate_qdrant_1024.py
2. Replace backend/v2/jobs/embedding_utils.py with this file
3. Restart server
"""

# Copy this code to replace get_job_embedding() and get_resume_embedding()

async def get_job_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for job description.
    
    Tries Mistral AI first (1024-dim), falls back to local model (384-dim).
    
    Args:
        text: Job description text
        settings: Application settings
        
    Returns:
        Embedding vector
    """
    # Try Mistral first if API key is available
    if settings.mistral_api_key:
        logger.info("Attempting Mistral AI embedding for job (1024-dim)")
        embedding = await get_mistral_embedding(text, settings.mistral_api_key)
        if embedding:
            logger.info(f"✅ Mistral embedding: {len(embedding)} dimensions")
            return embedding
        logger.warning("Mistral failed, falling back to local model")
    
    # Fallback to local model
    logger.info("Using local embedding model for job (384-dim)")
    return get_local_embedding(text)


async def get_resume_embedding(text: str, settings: Settings) -> List[float]:
    """
    Generate embedding for resume/CV.
    
    Tries Mistral AI first (1024-dim), falls back to local model (384-dim).
    
    Args:
        text: Resume text
        settings: Application settings
        
    Returns:
        Embedding vector
    """
    # Try Mistral first if API key is available
    if settings.mistral_api_key:
        logger.info("Attempting Mistral AI embedding for resume (1024-dim)")
        embedding = await get_mistral_embedding(text, settings.mistral_api_key)
        if embedding:
            logger.info(f"✅ Mistral embedding: {len(embedding)} dimensions")
            return embedding
        logger.warning("Mistral failed, falling back to local model")
    
    # Fallback to local model
    logger.info("Using local embedding model for resume (384-dim)")
    return get_local_embedding(text)
