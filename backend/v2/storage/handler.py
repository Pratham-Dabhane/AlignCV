"""
File storage utilities for AlignCV V2.

Supports:
- Local file storage
- Firebase Storage (optional)
- AWS S3 (optional)
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.v2.config import settings

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


class FirebaseStorage:
    """
    Firebase Storage handler (placeholder).
    
    Implement when Firebase credentials are available.
    """
    
    def __init__(self):
        logger.warning("FirebaseStorage not implemented yet")
        raise NotImplementedError("Firebase storage coming in Phase 2")
    
    def save_file(self, file_path: str, user_id: int, original_filename: str) -> str:
        raise NotImplementedError()
    
    def delete_file(self, storage_path: str) -> bool:
        raise NotImplementedError()


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
    elif backend == "firebase":
        return FirebaseStorage()
    elif backend == "s3":
        return S3Storage()
    else:
        logger.warning(f"Unknown storage backend: {backend}, using local")
        return LocalStorage()
