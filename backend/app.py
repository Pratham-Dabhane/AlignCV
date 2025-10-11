"""
AlignCV - Backend API
Main FastAPI application for resume and job description analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from pathlib import Path

# Import semantic utilities (Phase 2)
from utils.semantic_utils import analyze_resume_jd_match

# Create logs directory if it doesn't exist (Phase 4)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging (Phase 4: Enhanced logging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'aligncv.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AlignCV API",
    description="Semantic matching API for resumes and job descriptions",
    version="0.1.0"
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class AnalyzeRequest(BaseModel):
    """Request model for resume analysis"""
    resume_text: str = Field(..., min_length=1, description="Resume text content")
    job_description_text: str = Field(..., min_length=1, description="Job description text content")


class AnalyzeResponse(BaseModel):
    """Response model for analysis results"""
    match_score: float = Field(..., ge=0, le=100, description="Match percentage (0-100)")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    gaps: List[str] = Field(default_factory=list, description="Identified gaps")
    message: Optional[str] = Field(None, description="Status or error message")


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AlignCV API",
        "status": "running",
        "version": "0.1.0",
        "tagline": "Your Career, Aligned"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(request: AnalyzeRequest):
    """
    Analyze resume against job description
    
    Phase 2: Semantic matching with Sentence-BERT embeddings
    - Computes similarity score (0-100%)
    - Identifies strengths (matching requirements)
    - Identifies gaps (missing requirements)
    
    Args:
        request: AnalyzeRequest with resume_text and job_description_text
        
    Returns:
        AnalyzeResponse with match_score, strengths, and gaps
    """
    try:
        logger.info(f"Received analysis request - Resume length: {len(request.resume_text)}, JD length: {len(request.job_description_text)}")
        
        # Validate input lengths
        if len(request.resume_text) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Resume text is too short. Please provide at least 50 characters."
            )
        
        if len(request.job_description_text) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Job description text is too short. Please provide at least 50 characters."
            )
        
        # Phase 2: Semantic matching with embeddings
        logger.info("Starting semantic analysis...")
        result = analyze_resume_jd_match(
            resume_text=request.resume_text,
            jd_text=request.job_description_text
        )
        
        response = AnalyzeResponse(
            match_score=result["match_score"],
            strengths=result["strengths"],
            gaps=result["gaps"],
            message="Phase 2: Semantic matching complete. Score based on Sentence-BERT embeddings."
        )
        
        logger.info(f"Analysis complete - Match score: {response.match_score}%")
        return response
        
    except HTTPException:
        raise
    except ValueError as e:
        # Validation errors - return user-friendly messages
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Runtime errors from semantic analysis
        logger.error(f"Runtime error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Unexpected errors - log with full traceback
        logger.error(f"Unexpected error during analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again or contact support if the issue persists."
        )


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "0.4.0",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/metrics")
async def get_metrics():
    """
    Get performance metrics
    Phase 4: Added for monitoring and debugging
    
    Returns:
        Performance metrics including cache statistics
    """
    try:
        from utils.semantic_utils import get_metrics
        metrics = get_metrics()
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": logger.handlers[0].formatter.formatTime(logging.LogRecord(
                name="", level=0, pathname="", lineno=0,
                msg="", args=(), exc_info=None
            ))
        }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
