"""
AlignCV V2 Main Application.

Includes:
- Authentication (JWT + Google OAuth)
- Document upload and parsing
- AI-powered resume rewriting
- Job matching and notifications
- Structured logging and monitoring

V2 routes use /v2 prefix for consistency.
"""

import asyncio
import sys

# Fix for Windows + psycopg async compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db
from .logging_config import setup_logging, get_logger
from .middleware import RequestLoggingMiddleware
from .auth.routes import router as auth_router
from .documents.routes import router as documents_router
from .ai.routes import router as ai_router
from .jobs.routes import router as jobs_router
from .notifications.routes import router as notifications_router

# Security scheme for OpenAPI docs
security = HTTPBearer()

# Configure centralized logging
setup_logging(
    log_level=settings.log_level if hasattr(settings, 'log_level') else 'INFO',
    log_file='logs/app.log',
    enable_sentry=settings.sentry_dsn is not None if hasattr(settings, 'sentry_dsn') else False,
    sentry_dsn=getattr(settings, 'sentry_dsn', None),
    environment=settings.environment
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("AlignCV V2 Starting...")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Storage backend: {settings.storage_backend}")
    logger.info("AlignCV V2 ready!")
    
    yield
    
    # Shutdown
    logger.info("AlignCV V2 shutting down...")


# Create V2 app
app_v2 = FastAPI(
    title="AlignCV V2 API",
    description="Advanced resume matching with authentication and document management",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/v2/docs",
    redoc_url="/v2/redoc",
    openapi_url="/v2/openapi.json",
    swagger_ui_parameters={
        "persistAuthorization": True  # Keep authorization between page refreshes
    }
)

# Configure CORS
app_v2.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app_v2.add_middleware(RequestLoggingMiddleware)

# Include routers
app_v2.include_router(auth_router)
app_v2.include_router(documents_router)
app_v2.include_router(ai_router)
app_v2.include_router(jobs_router)
app_v2.include_router(notifications_router)

@app_v2.get("/v2/")
async def root():
    """V2 API root endpoint."""
    return {
        "message": "AlignCV V2 API",
        "version": "2.0.0",
        "docs": "/v2/docs",
        "features": [
            "JWT Authentication",
            "Google OAuth",
            "Document Upload (PDF/DOCX)",
            "NLP Extraction (Skills, Roles, Entities)",
            "Document Management",
            "AI Resume Rewriting (Mistral 7B)",
            "Job Matching & Ranking (Qdrant + Embeddings)",
            "Job Bookmarks & Applications"
        ]
    }


@app_v2.get("/v2/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.v2.app_v2:app_v2",
        host="0.0.0.0",
        port=8001,  # Use port 8001 for V2, 8000 for V1
        reload=settings.debug
    )
