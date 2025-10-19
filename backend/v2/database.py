"""
Database connection and session management for AlignCV V2.

Uses Supabase client for database operations (bypasses IPv6 connection issues).
"""

from supabase import create_client, Client
from typing import Optional
from .config import settings

# Global Supabase client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
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
        client = get_supabase_client()
        # Test connection by checking if we can access storage
        client.storage.list_buckets()
        return True
    except Exception as e:
        raise Exception(f"Failed to connect to Supabase: {e}")
