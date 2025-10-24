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
import traceback

# Fix for Windows + psycopg async compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print("🚀 Starting AlignCV V2 application...", file=sys.stderr)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer
    from contextlib import asynccontextmanager

    print("✅ FastAPI imports successful", file=sys.stderr)

    from .config import settings
    print(f"✅ Config loaded - Environment: {settings.environment}", file=sys.stderr)
    
    from .database import init_db
    print("✅ Database module imported", file=sys.stderr)
    
    from .logging_config import setup_logging, get_logger
    from .middleware import RequestLoggingMiddleware
    print("✅ Logging and middleware imported", file=sys.stderr)
    
    from .auth.routes import router as auth_router
    print("✅ Auth routes imported", file=sys.stderr)
    
    from .documents.routes import router as documents_router
    print("✅ Documents routes imported", file=sys.stderr)
    
    from .ai.routes import router as ai_router
    print("✅ AI routes imported", file=sys.stderr)
    
    from .jobs.routes import router as jobs_router
    print("✅ Jobs routes imported", file=sys.stderr)
    
    from .notifications.routes import router as notifications_router
    print("✅ Notifications routes imported", file=sys.stderr)
    
except Exception as e:
    print(f"❌ STARTUP ERROR during imports: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

# Security scheme for OpenAPI docs
security = HTTPBearer()

print("🔄 Configuring logging...", file=sys.stderr)

# Configure centralized logging
try:
    setup_logging(
        log_level=settings.log_level if hasattr(settings, 'log_level') else 'INFO',
        log_file='logs/app.log',
        enable_sentry=settings.sentry_dsn is not None if hasattr(settings, 'sentry_dsn') else False,
        sentry_dsn=getattr(settings, 'sentry_dsn', None),
        environment=settings.environment
    )
    print("✅ Logging configured", file=sys.stderr)
except Exception as e:
    print(f"❌ Logging setup failed: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

logger = get_logger(__name__)

print("✅ Logger instance created", file=sys.stderr)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    print("🔄 Lifespan startup begin", file=sys.stderr)
    # Startup
    logger.info("=" * 60)
    logger.info("AlignCV V2 Starting...")
    logger.info("=" * 60)
    
    # Initialize database
    print("🔄 Attempting database initialization...", file=sys.stderr)
    logger.info("Initializing database...")
    try:
        await init_db()
        print("✅ Database initialized", file=sys.stderr)
        logger.info("Database initialized successfully")
    except Exception as e:
        print(f"❌ Database init failed: {e}", file=sys.stderr)
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Storage backend: {settings.storage_backend}")
    logger.info("AlignCV V2 ready!")
    
    print("✅ Lifespan startup complete", file=sys.stderr)
    
    yield
    
    # Shutdown
    logger.info("AlignCV V2 shutting down...")
    print("🔄 Lifespan shutdown", file=sys.stderr)


print("🔄 Creating FastAPI app...", file=sys.stderr)

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

print("✅ Middleware configured", file=sys.stderr)

# Include routers
app_v2.include_router(auth_router)
app_v2.include_router(documents_router)
app_v2.include_router(ai_router)
app_v2.include_router(jobs_router)
app_v2.include_router(notifications_router)

print("✅ All routers included", file=sys.stderr)
print("🎉 FastAPI app created successfully!", file=sys.stderr)

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
