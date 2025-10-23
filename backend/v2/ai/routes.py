"""
AlignCV V2 - AI Rewriting Routes
API endpoints for resume rewriting with Mistral AI.
"""

import logging
import difflib
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from ..database import get_db, get_supabase_client
from ..models.models import Document, DocumentVersion, User
from ..auth.utils import verify_token
from supabase import Client
from .rewrite_engine import rewrite_resume, extract_keyphrases, tailor_resume_to_job
from ..config import settings

logger = logging.getLogger(__name__)

# Configure logging for week3_4 - create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
week3_log_handler = logging.FileHandler("logs/week3_4.log")
week3_log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(week3_log_handler)

router = APIRouter(prefix="/v2/rewrite", tags=["AI Rewriting"])

# Security scheme for JWT authentication
security = HTTPBearer()


# Schemas
class RewriteRequest(BaseModel):
    """Request schema for resume rewriting."""
    resume_id: str = Field(..., description="ID of the document to rewrite (UUID)")
    rewrite_style: str = Field(..., description="Style: Technical, Management, or Creative")


class RewriteResponse(BaseModel):
    """Response schema for resume rewriting."""
    version_id: int  # Temporary: 0 until versions table created
    resume_id: str  # UUID
    original_text: str
    rewritten_text: str
    diff_html: str
    improvements: list
    impact_score: int
    style: str
    latency: float
    api_status: str
    warning: Optional[str] = None


# Dependency: Get current user from JWT token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_supabase_client)
):
    """Extract and verify user from Bearer token."""
    token = credentials.credentials
    
    try:
        payload = verify_token(token, token_type="access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Extract email from payload
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )
    
    # Fetch user from database
    result = db.table('users').select('*').eq('email', email).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return result.data[0]


@router.post("/", response_model=RewriteResponse)
async def rewrite(
    request: RewriteRequest,
    db: Client = Depends(get_supabase_client),
    user = Depends(get_current_user)
):
    """
    Rewrite a resume document with Mistral AI.
    
    - **resume_id**: Document ID to rewrite
    - **rewrite_style**: Technical, Management, or Creative
    
    Returns rewritten version with diff and improvements.
    """
    
    logger.info(f"Rewrite request - User: {user['email']}, Document: {request.resume_id}, Style: {request.rewrite_style}")
    
    # Fetch document
    result = db.table('documents').select('*').eq('id', request.resume_id).eq('user_id', user['id']).execute()
    
    if not result.data:
        logger.warning(f"Document {request.resume_id} not found for user {user['email']}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    document = result.data[0]
    
    # Extract text from parsed_content
    extracted_text = None
    if document.get('parsed_content'):
        extracted_text = document['parsed_content'].get('text')
    
    if not extracted_text:
        logger.warning(f"Document {request.resume_id} has no extracted text")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no text content to rewrite"
        )
    
    # Call Mistral AI rewrite engine
    try:
        start_time = datetime.utcnow()
        
        rewrite_result = await rewrite_resume(
            resume_text=extracted_text,
            style=request.rewrite_style,
            timeout=30
        )
        
        # Generate diff
        diff_html = _generate_diff_html(
            extracted_text,
            rewrite_result["rewritten_text"]
        )
        
        # Extract keyphrases from rewritten text
        keyphrases = await extract_keyphrases(rewrite_result["rewritten_text"])
        
        # TODO: Save document version to Supabase when versions table is created
        # For now, just return the result without saving
        
        logger.info(
            f"Rewrite complete - "
            f"Latency: {rewrite_result['latency']}s, "
            f"Status: {rewrite_result['api_status']}, "
            f"Original: {rewrite_result['original_length']} chars, "
            f"Rewritten: {rewrite_result['rewritten_length']} chars"
        )
        
        return RewriteResponse(
            version_id=0,  # Temporary: versions not yet implemented in Supabase
            resume_id=request.resume_id,
            original_text=extracted_text,
            rewritten_text=rewrite_result["rewritten_text"],
            diff_html=diff_html,
            improvements=rewrite_result["improvements"],
            impact_score=rewrite_result["impact_score"],
            style=request.rewrite_style,
            latency=rewrite_result["latency"],
            api_status=rewrite_result["api_status"],
            warning=rewrite_result.get("warning")
        )
        
    except Exception as e:
        logger.error(f"Rewrite error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rewrite failed: {str(e)}"
        )


# TEMPORARILY DISABLED - Requires document_versions table
# Uncomment and convert these endpoints after creating document_versions table in Supabase
#
# @router.get("/versions/{resume_id}")
# async def get_rewrite_versions(
#     resume_id: int,
#     db: AsyncSession = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     """Get all rewrite versions for a document."""
#     pass
#
# @router.get("/version/{version_id}")
# async def get_version_detail(
#     version_id: int,
#     db: AsyncSession = Depends(get_db),
#     user: User = Depends(get_current_user)
# ):
#     """Get detailed view of a specific rewrite version."""
#     pass
    
    # Generate diff
    diff_html = _generate_diff_html(version.original_text, version.rewritten_text)
    
    return {
        "version_id": version.id,
        "resume_id": version.document_id,
        "original_text": version.original_text,
        "rewritten_text": version.rewritten_text,
        "diff_html": diff_html,
        "style": version.rewrite_style,
        "improvements": version.improvements,
        "impact_score": version.impact_score,
        "keyphrases": version.keyphrases,
        "api_latency": version.api_latency,
        "api_status": version.api_status,
        "created_at": version.created_at.isoformat()
    }


def _generate_diff_html(original: str, rewritten: str) -> str:
    """
    Generate HTML diff between original and rewritten text.
    Uses Python's difflib to highlight changes.
    """
    original_lines = original.splitlines()
    rewritten_lines = rewritten.splitlines()
    
    diff = difflib.unified_diff(
        original_lines,
        rewritten_lines,
        lineterm='',
        n=0  # No context lines
    )
    
    html_lines = []
    html_lines.append('<div class="diff-viewer">')
    html_lines.append('<div class="diff-original"><h4>Original</h4>')
    
    for line in original_lines:
        html_lines.append(f'<p>{line}</p>')
    
    html_lines.append('</div>')
    html_lines.append('<div class="diff-rewritten"><h4>Rewritten</h4>')
    
    for line in rewritten_lines:
        html_lines.append(f'<p>{line}</p>')
    
    html_lines.append('</div>')
    html_lines.append('</div>')
    
    return '\n'.join(html_lines)


# ============================================================================
# PHASE 9: RESUME TAILORING TO JOB DESCRIPTION
# ============================================================================

class TailorResumeRequest(BaseModel):
    """Request schema for resume tailoring to specific job."""
    resume_id: str = Field(..., description="ID of the document to tailor (UUID)")
    job_description: str = Field(..., min_length=50, description="Target job description")
    tailoring_level: str = Field(
        default="moderate",
        description="Tailoring aggressiveness: conservative, moderate, or aggressive"
    )


class TailorResumeResponse(BaseModel):
    """Response schema for tailored resume."""
    tailored_resume: str
    original_resume: str
    match_score: int = Field(..., ge=0, le=100)
    missing_skills: list
    keyword_suggestions: list
    changes_made: list
    priority_improvements: list
    tailoring_level: str
    latency: float
    api_status: str
    warning: Optional[str] = None


@router.post("/tailor-to-job", response_model=TailorResumeResponse)
async def tailor_resume_to_job_endpoint(
    request: TailorResumeRequest,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    **PHASE 9: Resume Tailoring**
    
    Tailor a resume to match a specific job description using AI analysis.
    
    This powerful feature:
    - Analyzes gaps between your resume and job requirements
    - Identifies missing skills and keywords
    - Generates a tailored version optimized for the target role
    - Provides specific improvement suggestions
    - Shows before/after comparison
    
    **Tailoring Levels**:
    - `conservative`: Minimal changes, maintains authenticity
    - `moderate`: Balanced optimization (recommended)
    - `aggressive`: Comprehensive restructuring for maximum match
    
    **Example Use Case**:
    ```
    User finds dream job posting → Pastes job description → 
    Gets tailored resume highlighting relevant experience → 
    Increases interview chances by 50%+
    ```
    
    Args:
        resume_id: ID of the resume to tailor
        job_description: Full text of the target job posting
        tailoring_level: How aggressive to optimize (default: moderate)
        
    Returns:
        TailorResumeResponse with tailored resume and analysis
    """
    try:
        logger.info(f"Tailoring request - User: {current_user['email']}, Resume ID: {request.resume_id}, Level: {request.tailoring_level}")
        
        # Validate tailoring level
        valid_levels = ["conservative", "moderate", "aggressive"]
        if request.tailoring_level not in valid_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tailoring level. Must be one of: {', '.join(valid_levels)}"
            )
        
        # Fetch the document
        result = db.table('documents').select('*').eq('id', request.resume_id).eq('user_id', current_user['id']).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or you don't have permission to access it"
            )
        
        document = result.data[0]
        
        # Extract text from parsed_content
        extracted_text = None
        if document.get('parsed_content'):
            extracted_text = document['parsed_content'].get('text')
        
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no extracted text. Please upload a valid resume."
            )
        
        # Call AI tailoring service
        logger.info("Calling AI tailoring service...")
        result = await tailor_resume_to_job(
            resume_text=extracted_text,
            job_description=request.job_description,
            tailoring_level=request.tailoring_level
        )
        
        # Log the result
        logger.info(
            f"Tailoring complete - Match score: {result['match_score']}%, "
            f"Missing skills: {len(result['missing_skills'])}, "
            f"Changes: {len(result['changes_made'])}"
        )
        
        # Return response
        return TailorResumeResponse(
            tailored_resume=result["tailored_resume"],
            original_resume=result["original_resume"],
            match_score=result["match_score"],
            missing_skills=result["missing_skills"],
            keyword_suggestions=result["keyword_suggestions"],
            changes_made=result["changes_made"],
            priority_improvements=result["priority_improvements"],
            tailoring_level=result["tailoring_level"],
            latency=result["latency"],
            api_status=result["api_status"],
            warning=result.get("warning")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume tailoring error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume tailoring failed: {str(e)}"
        )
