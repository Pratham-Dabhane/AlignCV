"""
AlignCV - Backend API
Main FastAPI application for resume and job description analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    
    Phase 1: Returns dummy data
    Phase 2+: Will integrate semantic matching, gap analysis, and checklist generation
    
    Args:
        request: AnalyzeRequest with resume_text and job_description_text
        
    Returns:
        AnalyzeResponse with match_score, strengths, and gaps
    """
    try:
        logger.info(f"Received analysis request - Resume length: {len(request.resume_text)}, JD length: {len(request.job_description_text)}")
        
        # Phase 1: Return dummy data
        # TODO Phase 2: Implement semantic matching with embeddings
        # TODO Phase 3: Implement gap analysis
        # TODO Phase 4: Generate actionable checklist
        
        response = AnalyzeResponse(
            match_score=0.0,
            strengths=[],
            gaps=[],
            message="Phase 1: Dummy response. Semantic matching coming in Phase 2."
        )
        
        logger.info(f"Analysis complete - Match score: {response.match_score}")
        return response
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_version": "0.1.0",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
