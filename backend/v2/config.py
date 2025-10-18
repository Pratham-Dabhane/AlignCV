"""
Configuration management for AlignCV V2.

Loads environment variables using Pydantic Settings.
All sensitive credentials are loaded from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses .env file for local development.
    For production, set environment variables directly.
    """
    
    # ========================================
    # Database
    # ========================================
    database_url: str
    
    # ========================================
    # JWT Authentication
    # ========================================
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7
    
    # ========================================
    # Google OAuth2
    # ========================================
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str = "http://localhost:8000/v2/auth/google/callback"
    
    # ========================================
    # Firebase Storage
    # ========================================
    firebase_api_key: Optional[str] = None
    firebase_auth_domain: Optional[str] = None
    firebase_project_id: Optional[str] = None
    firebase_storage_bucket: Optional[str] = None
    firebase_messaging_sender_id: Optional[str] = None
    firebase_app_id: Optional[str] = None
    firebase_service_account_path: Optional[str] = None
    
    # ========================================
    # Mistral AI
    # ========================================
    mistral_api_key: Optional[str] = None
    mistral_model: str = "mistral-small-latest"
    
    # ========================================
    # Qdrant Vector DB
    # ========================================
    qdrant_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None
    qdrant_collection_name: str = "aligncv_jobs"
    
    # ========================================
    # SendGrid Email
    # ========================================
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: str = "noreply@aligncv.com"
    sendgrid_from_name: str = "AlignCV"
    
    # ========================================
    # Redis & Celery (Phase 7)
    # ========================================
    redis_url: Optional[str] = None
    upstash_redis_rest_url: Optional[str] = None
    upstash_redis_rest_token: Optional[str] = None
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # ========================================
    # Logging & Monitoring (Phase 8)
    # ========================================
    log_level: str = "INFO"
    sentry_dsn: Optional[str] = None  # Sentry error tracking
    sentry_environment: Optional[str] = None
    
    # ========================================
    # File Storage
    # ========================================
    storage_backend: str = "local"  # 'local', 'firebase', or 's3'
    local_storage_path: str = "./storage/uploads"
    max_file_size_mb: int = 5
    
    # ========================================
    # Application
    # ========================================
    environment: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:8501,http://localhost:8502"
    
    # ========================================
    # NLP
    # ========================================
    spacy_model: str = "en_core_web_sm"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings loaded from environment
    """
    return Settings()


# Convenience export
settings = get_settings()
