"""
File storage utilities for AlignCV V2.

Supports:
- Local file storage
- Supabase Storage (cloud storage)
- AWS S3 (optional)
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class LocalStorage:
    """Local file storage handler."""
    
    def __init__(self, base_path: str = None):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory for file storage
        """
        self.base_path = base_path or settings.local_storage_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Create storage directory if it doesn't exist."""
        Path(self.base_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directory ready: {self.base_path}")
    
    def save_file(self, file_path: str, user_id: int, original_filename: str) -> str:
        """
        Save file to local storage.
        
        Args:
            file_path: Temporary file path
            user_id: User ID
            original_filename: Original filename
            
        Returns:
            Storage path (relative to base_path)
        """
        # Create user directory
        user_dir = Path(self.base_path) / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{original_filename}"
        destination = user_dir / filename
        
        # Copy file
        shutil.copy2(file_path, destination)
        logger.info(f"File saved: {destination}")
        
        # Return relative path
        return str(destination.relative_to(self.base_path))
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from local storage.
        
        Args:
            storage_path: Storage path (relative to base_path)
            
        Returns:
            True if deleted successfully
        """
        try:
            full_path = Path(self.base_path) / storage_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return False
    
    def get_file_path(self, storage_path: str) -> str:
        """
        Get full file path from storage path.
        
        Args:
            storage_path: Storage path (relative to base_path)
            
        Returns:
            Full file path
        """
        return str(Path(self.base_path) / storage_path)


class SupabaseStorage:
    """
    Supabase Storage handler using Supabase Python client.
    
    Requires Supabase project with Storage enabled.
    """
    
    def __init__(self):
        """Initialize Supabase Storage with credentials."""
        try:
            from supabase import create_client, Client
            
            if not settings.supabase_url:
                raise ValueError("SUPABASE_URL not set in .env")
            
            if not settings.supabase_service_role_key:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY not set in .env")
            
            # Initialize Supabase client with service role key (full access)
            self.client: Client = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            self.bucket_name = settings.supabase_storage_bucket
            
            # Verify bucket exists (or just log warning if we can't check)
            try:
                self.client.storage.get_bucket(self.bucket_name)
                logger.info(f"Supabase Storage initialized with bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Could not verify bucket '{self.bucket_name}': {e}")
                logger.warning(f"Please ensure bucket '{self.bucket_name}' exists in Supabase Dashboard")
                logger.info(f"Supabase Storage initialized (bucket verification skipped)")
            
        except ImportError:
            logger.error("supabase package not installed. Run: pip install supabase")
            raise
        except Exception as e:
            logger.error(f"Supabase Storage initialization failed: {str(e)}")
            raise
    
    def save_file(self, file_path: str, user_id: int, original_filename: str) -> str:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_path: Local temporary file path
            user_id: User ID
            original_filename: Original filename
            
        Returns:
            Supabase storage path
        """
        try:
            # Generate unique storage path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            storage_path = f"user_{user_id}/{timestamp}_{original_filename}"
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to Supabase Storage
            response = self.client.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "application/octet-stream"}
            )
            
            logger.info(f"File uploaded to Supabase Storage: {storage_path}")
            return storage_path
            
        except Exception as e:
            logger.error(f"Supabase Storage upload failed: {str(e)}")
            raise
    
    def delete_file(self, storage_path: str) -> bool:
        """
        Delete file from Supabase Storage.
        
        Args:
            storage_path: Supabase storage path
            
        Returns:
            True if deleted successfully
        """
        try:
            response = self.client.storage.from_(self.bucket_name).remove([storage_path])
            logger.info(f"File deleted from Supabase Storage: {storage_path}")
            return True
        except Exception as e:
            logger.error(f"Supabase Storage deletion failed: {str(e)}")
            return False
    
    def get_file_url(self, storage_path: str, expiration: int = 3600) -> Optional[str]:
        """
        Get signed URL for file download.
        
        Args:
            storage_path: Supabase storage path
            expiration: URL expiration in seconds (default 1 hour)
            
        Returns:
            Signed URL or None if file doesn't exist
        """
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=storage_path,
                expires_in=expiration
            )
            return response.get('signedURL')
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {str(e)}")
            return None
    
    def download_file(self, storage_path: str, destination_path: str) -> bool:
        """
        Download file from Supabase Storage to local path.
        
        Args:
            storage_path: Supabase storage path
            destination_path: Local destination path
            
        Returns:
            True if downloaded successfully
        """
        try:
            response = self.client.storage.from_(self.bucket_name).download(storage_path)
            
            # Write to destination
            with open(destination_path, 'wb') as f:
                f.write(response)
            
            logger.info(f"File downloaded from Supabase Storage: {storage_path} -> {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Supabase Storage download failed: {str(e)}")
            return False
    
    def get_public_url(self, storage_path: str) -> Optional[str]:
        """
        Get public URL for file (if bucket is public).
        
        Args:
            storage_path: Supabase storage path
            
        Returns:
            Public URL or None
        """
        try:
            response = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            return response
        except Exception as e:
            logger.error(f"Failed to get public URL: {str(e)}")
            return None


class S3Storage:
    """
    AWS S3 Storage handler (placeholder).
    
    Implement when S3 credentials are available.
    """
    
    def __init__(self):
        logger.warning("S3Storage not implemented yet")
        raise NotImplementedError("S3 storage coming in Phase 2")
    
    def save_file(self, file_path: str, user_id: int, original_filename: str) -> str:
        raise NotImplementedError()
    
    def delete_file(self, storage_path: str) -> bool:
        raise NotImplementedError()


def get_storage():
    """
    Get storage handler based on configuration.
    
    Returns:
        Storage handler instance
    """
    backend = settings.storage_backend.lower()
    
    if backend == "local":
        return LocalStorage()
    elif backend == "supabase":
        return SupabaseStorage()
    elif backend == "s3":
        return S3Storage()
    else:
        logger.warning(f"Unknown storage backend: {backend}, using local")
        return LocalStorage()
