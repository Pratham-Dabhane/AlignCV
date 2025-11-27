"""
Database connection and session management for AlignCV V2.

Uses Supabase client for database operations (bypasses IPv6 connection issues).
"""

import logging
from supabase import create_client, Client
from typing import Optional
from .config import settings

logger = logging.getLogger(__name__)

# Global Supabase client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        # Log configuration (without exposing full keys)
        supabase_url = settings.supabase_url
        has_key = bool(settings.supabase_service_role_key)
        
        logger.info(f"🔗 Connecting to Supabase...")
        logger.info(f"   URL configured: {bool(supabase_url)}")
        logger.info(f"   Service role key configured: {has_key}")
        
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is not set!")
        if not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is not set!")
        
        logger.info(f"   Connecting to: {supabase_url[:30]}...")
        
        _supabase_client = create_client(
            supabase_url,
            settings.supabase_service_role_key
        )
        logger.info("✅ Supabase client created successfully")
    return _supabase_client

# For backward compatibility, keep these but they won't be used
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

engine = None  # Not used with Supabase client
AsyncSessionLocal = None  # Not used with Supabase client

# Base class for models (kept for compatibility)
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get Supabase client.
    
    Returns:
        Client: Supabase client
        
    Example:
        @router.get("/users")
        def get_users(db: Client = Depends(get_db)):
            ...
    """
    return get_supabase_client()


async def init_db():
    """
    Initialize database connection.
    
    Verifies Supabase connection is working.
    """
    try:
        logger.info("🔄 Initializing Supabase connection...")
        client = get_supabase_client()
        
        logger.info("🧪 Testing Supabase connection with storage.list_buckets()...")
        # Test connection by checking if we can access storage
        buckets = client.storage.list_buckets()
        logger.info(f"✅ Supabase connection successful! Found {len(buckets)} storage buckets")
        
        return True
    except ValueError as e:
        # Configuration error
        logger.error(f"❌ Supabase configuration error: {e}")
        logger.error("💡 Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in Render environment variables")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error("💡 Check that your Supabase URL and service role key are correct")
        raise Exception(f"Failed to connect to Supabase: {e}")
