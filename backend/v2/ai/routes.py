"""
AlignCV V2 - AI Rewriting Routes
API endpoints for resume rewriting with Mistral AI.
"""

import logging
import difflib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from ..database import get_db
from ..models.models import Document, DocumentVersion, User
from ..auth.utils import verify_token
from .rewrite_engine import rewrite_resume, extract_keyphrases
from ..config import settings

logger = logging.getLogger(__name__)

# Configure logging for week3_4
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
    resume_id: int = Field(..., description="ID of the document to rewrite")
    rewrite_style: str = Field(..., description="Style: Technical, Management, or Creative")


class RewriteResponse(BaseModel):
    """Response schema for resume rewriting."""
    version_id: int
    resume_id: int
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
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
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
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/", response_model=RewriteResponse)
async def rewrite(
    request: RewriteRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Rewrite a resume document with Mistral AI.
    
    - **resume_id**: Document ID to rewrite
    - **rewrite_style**: Technical, Management, or Creative
    
    Returns rewritten version with diff and improvements.
    """
    
    logger.info(f"Rewrite request - User: {user.email}, Document: {request.resume_id}, Style: {request.rewrite_style}")
    
    # Fetch document
    result = await db.execute(
        select(Document).where(
            Document.id == request.resume_id,
            Document.user_id == user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        logger.warning(f"Document {request.resume_id} not found for user {user.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    if not document.extracted_text:
        logger.warning(f"Document {request.resume_id} has no extracted text")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no text content to rewrite"
        )
    
    # Call Mistral AI rewrite engine
    try:
        start_time = datetime.utcnow()
        
        rewrite_result = await rewrite_resume(
            resume_text=document.extracted_text,
            style=request.rewrite_style,
            timeout=30
        )
        
        # Generate diff
        diff_html = _generate_diff_html(
            document.extracted_text,
            rewrite_result["rewritten_text"]
        )
        
        # Extract keyphrases from rewritten text
        keyphrases = await extract_keyphrases(rewrite_result["rewritten_text"])
        
        # Create document version
        version = DocumentVersion(
            document_id=document.id,
            user_id=user.id,
            original_text=document.extracted_text,
            rewritten_text=rewrite_result["rewritten_text"],
            rewrite_style=request.rewrite_style,
            improvements=rewrite_result["improvements"],
            impact_score=rewrite_result["impact_score"],
            keyphrases=keyphrases,
            api_latency=rewrite_result["latency"],
            api_status=rewrite_result["api_status"]
        )
        
        db.add(version)
        await db.commit()
        await db.refresh(version)
        
        logger.info(
            f"Rewrite complete - Version: {version.id}, "
            f"Latency: {rewrite_result['latency']}s, "
            f"Status: {rewrite_result['api_status']}, "
            f"Original: {rewrite_result['original_length']} chars, "
            f"Rewritten: {rewrite_result['rewritten_length']} chars"
        )
        
        return RewriteResponse(
            version_id=version.id,
            resume_id=document.id,
            original_text=document.extracted_text,
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


@router.get("/versions/{resume_id}")
async def get_rewrite_versions(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get all rewrite versions for a document.
    
    - **resume_id**: Document ID
    
    Returns list of all versions with metadata.
    """
    
    # Verify document ownership
    result = await db.execute(
        select(Document).where(
            Document.id == resume_id,
            Document.user_id == user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    # Fetch all versions
    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == resume_id)
        .order_by(DocumentVersion.created_at.desc())
    )
    versions = result.scalars().all()
    
    logger.info(f"Retrieved {len(versions)} versions for document {resume_id}")
    
    return {
        "resume_id": resume_id,
        "versions": [
            {
                "version_id": v.id,
                "style": v.rewrite_style,
                "impact_score": v.impact_score,
                "improvements": v.improvements,
                "keyphrases": v.keyphrases,
                "created_at": v.created_at.isoformat(),
                "api_status": v.api_status
            }
            for v in versions
        ]
    }


@router.get("/version/{version_id}")
async def get_version_detail(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get detailed view of a specific rewrite version.
    
    - **version_id**: Version ID
    
    Returns full version with original and rewritten text.
    """
    
    # Fetch version
    result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.id == version_id,
            DocumentVersion.user_id == user.id
        )
    )
    version = result.scalar_one_or_none()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found or access denied"
        )
    
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
