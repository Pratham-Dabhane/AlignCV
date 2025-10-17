"""
AlignCV V2 Main Application.

Includes:
- Authentication (JWT + Google OAuth)
- Document upload and parsing
- Maintains V1 compatibility

V1 routes remain accessible at their original paths.
V2 routes use /v2 prefix.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.v2.config import settings
from backend.v2.database import init_db
from backend.v2.auth.routes import router as auth_router
from backend.v2.documents.routes import router as documents_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/v2_app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


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
    logger.info("AlignCV V2 ready! 🚀")
    
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
    openapi_url="/v2/openapi.json"
)

# Configure CORS
app_v2.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app_v2.include_router(auth_router)
app_v2.include_router(documents_router)


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
            "Document Management"
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
