"""
Qdrant Vector Store Integration - Phase 5/6

Manages vector database operations for job matching.
"""

import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

from ..config import Settings

logger = logging.getLogger(__name__)

# Global client cache
_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client(settings: Settings) -> QdrantClient:
    """
    Initialize and cache Qdrant client.
    
    Supports both cloud and local Docker instances.
    
    Args:
        settings: Application settings with Qdrant configuration
        
    Returns:
        Configured Qdrant client
    """
    global _qdrant_client
    
    if _qdrant_client is None:
        if settings.qdrant_url and settings.qdrant_api_key:
            # Cloud instance
            logger.info(f"Connecting to Qdrant Cloud: {settings.qdrant_url}")
            _qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
        elif settings.qdrant_url:
            # Local instance (no API key)
            logger.info(f"Connecting to local Qdrant: {settings.qdrant_url}")
            _qdrant_client = QdrantClient(url=settings.qdrant_url)
        else:
            # In-memory instance for testing
            logger.warning("Using in-memory Qdrant (testing only)")
            _qdrant_client = QdrantClient(":memory:")
        
        logger.info("Qdrant client initialized successfully")
    
    return _qdrant_client


async def create_collection(settings: Settings, vector_size: int = 384):
    """
    Create Qdrant collection for job embeddings.
    
    Args:
        settings: Application settings
        vector_size: Embedding dimension (384 for sentence-transformers, 1024 for Mistral)
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if exists:
            logger.info(f"Collection '{collection_name}' already exists")
            return
        
        # Create collection
        logger.info(f"Creating collection '{collection_name}' with vector size {vector_size}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Collection '{collection_name}' created successfully")
        
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise


async def upsert_job_vector(
    job_id: str,
    vector: List[float],
    payload: Dict[str, Any],
    settings: Settings
):
    """
    Insert or update job vector in Qdrant.
    
    Args:
        job_id: Unique job identifier
        vector: Embedding vector
        payload: Job metadata (title, company, description, etc.)
        settings: Application settings
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        # Convert hex string job_id to integer for Qdrant
        # Qdrant requires point IDs to be integers or UUIDs
        point_id = int(job_id, 16) if isinstance(job_id, str) else job_id
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                **payload,
                "job_id": job_id  # Keep original job_id in payload for reference
            }
        )
        
        client.upsert(
            collection_name=collection_name,
            points=[point]
        )
        
        logger.info(f"Upserted job vector: {job_id} (point_id: {point_id})")
        
    except Exception as e:
        logger.error(f"Error upserting job vector: {e}")
        raise


async def upsert_job_vectors_batch(
    vectors_data: List[Dict[str, Any]],
    settings: Settings
):
    """
    Batch insert/update job vectors.
    
    Args:
        vectors_data: List of dicts with 'id', 'vector', and 'payload'
        settings: Application settings
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        points = [
            PointStruct(
                id=int(data["id"], 16) if isinstance(data["id"], str) else data["id"],
                vector=data["vector"],
                payload={
                    **data["payload"],
                    "job_id": data["id"]  # Keep original job_id in payload
                }
            )
            for data in vectors_data
        ]
        
        client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        logger.info(f"Batch upserted {len(points)} job vectors")
        
    except Exception as e:
        logger.error(f"Error batch upserting job vectors: {e}")
        raise


async def search_similar_jobs(
    query_vector: List[float],
    top_k: int,
    settings: Settings,
    filter_conditions: Optional[Filter] = None
) -> List[Dict[str, Any]]:
    """
    Search for similar jobs using vector similarity.
    
    Args:
        query_vector: Resume embedding vector
        top_k: Number of results to return
        settings: Application settings
        filter_conditions: Optional filters (e.g., location, company)
        
    Returns:
        List of matching jobs with scores
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=filter_conditions
        )
        
        matches = [
            {
                "job_id": result.payload.get("job_id", str(result.id)),  # Use job_id from payload
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
        
        logger.info(f"Found {len(matches)} similar jobs")
        return matches
        
    except Exception as e:
        logger.error(f"Error searching similar jobs: {e}")
        raise


async def delete_job_vector(job_id: str, settings: Settings):
    """
    Delete job vector from Qdrant.
    
    Args:
        job_id: Job identifier (hex string)
        settings: Application settings
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        # Convert hex string to integer for Qdrant point ID
        point_id = int(job_id, 16) if isinstance(job_id, str) else job_id
        
        client.delete(
            collection_name=collection_name,
            points_selector=[point_id]
        )
        logger.info(f"Deleted job vector: {job_id} (point_id: {point_id})")
        
    except Exception as e:
        logger.error(f"Error deleting job vector: {e}")
        raise


async def get_collection_info(settings: Settings) -> Dict[str, Any]:
    """
    Get collection statistics and info.
    
    Args:
        settings: Application settings
        
    Returns:
        Collection information
    """
    client = get_qdrant_client(settings)
    collection_name = settings.qdrant_collection_name
    
    try:
        info = client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
            "config": {
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance
            }
        }
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        raise
