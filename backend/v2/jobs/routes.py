"""
Job Matching API Routes - Phase 5/6

Endpoints for job discovery, matching, bookmarking, and application tracking.
"""

import logging
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field
from datetime import datetime

from ..database import get_db
from ..models.models import User, Document, Job, JobBookmark, JobApplication
from ..config import get_settings, Settings
from ..auth.utils import decode_token
from .embedding_utils import get_resume_embedding, get_job_embedding, get_batch_embeddings
from .vector_store import (
    create_collection,
    search_similar_jobs,
    upsert_job_vector,
    upsert_job_vectors_batch,
    get_collection_info
)
from .matcher import rank_jobs, filter_jobs_by_criteria
from .ingest import ingest_jobs_from_sources

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v2/jobs", tags=["Jobs"])
security = HTTPBearer()


# ========================================
# Schemas
# ========================================

class JobMatchRequest(BaseModel):
    """Request for job matching."""
    resume_id: int = Field(..., description="Document ID of the resume")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of matches to return")
    min_salary: Optional[int] = Field(None, description="Minimum salary filter")
    location: Optional[str] = Field(None, description="Location filter")
    experience_level: Optional[str] = Field(None, description="Experience level filter")
    employment_type: Optional[str] = Field(None, description="Employment type filter")


class JobMatchResponse(BaseModel):
    """Response with matched jobs."""
    job_id: str
    title: str
    company: str
    location: Optional[str]
    url: str
    description: str
    tags: List[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    employment_type: Optional[str]
    experience_level: Optional[str]
    vector_score: float
    skill_score: float
    combined_score: float
    fit_percentage: int
    matched_skills: List[str]
    gap_skills: List[str]
    is_bookmarked: bool = False
    is_applied: bool = False


class BookmarkRequest(BaseModel):
    """Request to bookmark a job."""
    job_id: int = Field(..., description="Database ID of the job")
    notes: Optional[str] = Field(None, description="Optional notes about the job")


class ApplicationRequest(BaseModel):
    """Request to mark job as applied."""
    job_id: int = Field(..., description="Database ID of the job")
    notes: Optional[str] = Field(None, description="Application notes")
    status: str = Field(default="applied", description="Application status")


class IngestJobsResponse(BaseModel):
    """Response from job ingestion."""
    total_ingested: int
    new_jobs: int
    updated_jobs: int
    embeddings_created: int


# ========================================
# Dependencies
# ========================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        email = decode_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# ========================================# ========================================
# Endpoints
# ========================================

@router.post("/match", response_model=List[JobMatchResponse])
async def match_jobs(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Match resume with jobs using vector similarity.
    
    Process:
    1. Fetch resume embedding
    2. Search Qdrant for top K similar jobs
    3. Extract matched/gap skills using SpaCy
    4. Rank by combined score (vector + skill match)
    5. Return enriched job matches
    """
    logger.info(f"Job match request - User: {current_user.email}, Resume: {request.resume_id}")
    
    # Fetch resume document
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == request.resume_id,
                Document.user_id == current_user.id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Generate resume embedding
    logger.info("Generating resume embedding...")
    resume_embedding = await get_resume_embedding(document.extracted_text, settings)
    
    # Search for similar jobs in Qdrant
    logger.info(f"Searching for top {request.top_k} matching jobs...")
    job_matches = await search_similar_jobs(
        query_vector=resume_embedding,
        top_k=request.top_k * 2,  # Get more, then filter
        settings=settings
    )
    
    if not job_matches:
        logger.warning("No job matches found")
        return []
    
    # Rank jobs with skill analysis
    logger.info("Ranking jobs with skill analysis...")
    ranked_jobs = await rank_jobs(
        resume_text=document.extracted_text,
        job_matches=job_matches,
        settings=settings
    )
    
    # Apply filters
    if any([request.min_salary, request.location, request.experience_level, request.employment_type]):
        logger.info("Applying user filters...")
        ranked_jobs = filter_jobs_by_criteria(
            jobs=ranked_jobs,
            min_salary=request.min_salary,
            location=request.location,
            experience_level=request.experience_level,
            employment_type=request.employment_type
        )
    
    # Limit to requested top_k
    ranked_jobs = ranked_jobs[:request.top_k]
    
    # Check bookmarks and applications
    job_ids_in_db = [j["job_id"] for j in ranked_jobs]
    result = await db.execute(
        select(Job).where(Job.job_id.in_(job_ids_in_db))
    )
    jobs_in_db = result.scalars().all()
    job_id_to_db_id = {j.job_id: j.id for j in jobs_in_db}
    
    # Get user's bookmarks and applications
    result = await db.execute(
        select(JobBookmark).where(JobBookmark.user_id == current_user.id)
    )
    bookmarks = {b.job_id for b in result.scalars().all()}
    
    result = await db.execute(
        select(JobApplication).where(JobApplication.user_id == current_user.id)
    )
    applications = {a.job_id for a in result.scalars().all()}
    
    # Enrich with bookmark/application status
    for job in ranked_jobs:
        db_job_id = job_id_to_db_id.get(job["job_id"])
        if db_job_id:
            job["is_bookmarked"] = db_job_id in bookmarks
            job["is_applied"] = db_job_id in applications
    
    logger.info(f"Returning {len(ranked_jobs)} matched jobs")
    return ranked_jobs


@router.post("/ingest", response_model=IngestJobsResponse)
async def ingest_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Ingest jobs from sources and create embeddings.
    
    Admin endpoint to populate job database.
    """
    logger.info(f"Job ingestion started by user: {current_user.email}")
    
    # Ensure collection exists
    await create_collection(settings)
    
    # Ingest jobs from sources
    jobs_data = await ingest_jobs_from_sources()
    
    if not jobs_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest jobs"
        )
    
    new_jobs = 0
    updated_jobs = 0
    embeddings_created = 0
    
    for job_data in jobs_data:
        # Check if job already exists
        result = await db.execute(
            select(Job).where(Job.job_id == job_data["job_id"])
        )
        existing_job = result.scalar_one_or_none()
        
        if existing_job:
            # Update existing job
            for key, value in job_data.items():
                if key != "job_id":
                    setattr(existing_job, key, value)
            updated_jobs += 1
            job_model = existing_job
        else:
            # Create new job
            job_model = Job(**job_data)
            db.add(job_model)
            new_jobs += 1
        
        await db.flush()
        
        # Generate embedding for job description
        job_embedding = await get_job_embedding(job_data["description"], settings)
        
        # Store in Qdrant
        await upsert_job_vector(
            job_id=job_data["job_id"],
            vector=job_embedding,
            payload={
                "title": job_data["title"],
                "company": job_data["company"],
                "description": job_data["description"],
                "url": job_data["url"],
                "location": job_data.get("location"),
                "tags": job_data.get("tags", []),
                "salary_min": job_data.get("salary_min"),
                "salary_max": job_data.get("salary_max"),
                "employment_type": job_data.get("employment_type"),
                "experience_level": job_data.get("experience_level"),
            },
            settings=settings
        )
        
        # Update vector_id in database
        job_model.vector_id = job_data["job_id"]
        embeddings_created += 1
    
    await db.commit()
    
    logger.info(f"Job ingestion complete - New: {new_jobs}, Updated: {updated_jobs}, Embeddings: {embeddings_created}")
    
    return IngestJobsResponse(
        total_ingested=len(jobs_data),
        new_jobs=new_jobs,
        updated_jobs=updated_jobs,
        embeddings_created=embeddings_created
    )


@router.get("/", response_model=List[Dict])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of jobs with pagination."""
    query = select(Job)
    
    if source:
        query = query.where(Job.source == source)
    
    query = query.order_by(Job.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [
        {
            "id": job.id,
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "url": job.url,
            "tags": job.tags,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "created_at": job.created_at.isoformat()
        }
        for job in jobs
    ]


@router.post("/bookmark")
async def bookmark_job(
    request: BookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bookmark a job for later review."""
    # Check if job exists
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already bookmarked
    result = await db.execute(
        select(JobBookmark).where(
            and_(
                JobBookmark.user_id == current_user.id,
                JobBookmark.job_id == request.job_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already bookmarked"
        )
    
    # Create bookmark
    bookmark = JobBookmark(
        user_id=current_user.id,
        job_id=request.job_id,
        notes=request.notes
    )
    db.add(bookmark)
    await db.commit()
    
    logger.info(f"Job bookmarked - User: {current_user.id}, Job: {request.job_id}")
    
    return {"message": "Job bookmarked successfully", "bookmark_id": bookmark.id}


@router.delete("/bookmark/{job_id}")
async def remove_bookmark(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove bookmark from a job."""
    result = await db.execute(
        select(JobBookmark).where(
            and_(
                JobBookmark.user_id == current_user.id,
                JobBookmark.job_id == job_id
            )
        )
    )
    bookmark = result.scalar_one_or_none()
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    await db.delete(bookmark)
    await db.commit()
    
    logger.info(f"Bookmark removed - User: {current_user.id}, Job: {job_id}")
    
    return {"message": "Bookmark removed successfully"}


@router.get("/bookmarks")
async def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bookmarked jobs."""
    result = await db.execute(
        select(JobBookmark).where(JobBookmark.user_id == current_user.id)
    )
    bookmarks = result.scalars().all()
    
    # Fetch job details
    job_ids = [b.job_id for b in bookmarks]
    result = await db.execute(select(Job).where(Job.id.in_(job_ids)))
    jobs = {j.id: j for j in result.scalars().all()}
    
    return [
        {
            "bookmark_id": b.id,
            "job": {
                "id": jobs[b.job_id].id,
                "title": jobs[b.job_id].title,
                "company": jobs[b.job_id].company,
                "url": jobs[b.job_id].url,
            },
            "notes": b.notes,
            "created_at": b.created_at.isoformat()
        }
        for b in bookmarks
        if b.job_id in jobs
    ]


@router.post("/apply")
async def apply_to_job(
    request: ApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a job as applied."""
    # Check if job exists
    result = await db.execute(select(Job).where(Job.id == request.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if already applied
    result = await db.execute(
        select(JobApplication).where(
            and_(
                JobApplication.user_id == current_user.id,
                JobApplication.job_id == request.job_id
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing application
        existing.status = request.status
        existing.notes = request.notes
        existing.updated_at = datetime.utcnow()
        await db.commit()
        return {"message": "Application updated successfully", "application_id": existing.id}
    
    # Create application
    application = JobApplication(
        user_id=current_user.id,
        job_id=request.job_id,
        status=request.status,
        notes=request.notes
    )
    db.add(application)
    await db.commit()
    
    logger.info(f"Job application created - User: {current_user.id}, Job: {request.job_id}")
    
    return {"message": "Job application recorded successfully", "application_id": application.id}


@router.get("/applications")
async def get_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's job applications."""
    result = await db.execute(
        select(JobApplication).where(JobApplication.user_id == current_user.id)
    )
    applications = result.scalars().all()
    
    # Fetch job details
    job_ids = [a.job_id for a in applications]
    result = await db.execute(select(Job).where(Job.id.in_(job_ids)))
    jobs = {j.id: j for j in result.scalars().all()}
    
    return [
        {
            "application_id": a.id,
            "job": {
                "id": jobs[a.job_id].id,
                "title": jobs[a.job_id].title,
                "company": jobs[a.job_id].company,
                "url": jobs[a.job_id].url,
            },
            "status": a.status,
            "applied_date": a.applied_date.isoformat(),
            "notes": a.notes,
            "created_at": a.created_at.isoformat()
        }
        for a in applications
        if a.job_id in jobs
    ]


@router.get("/stats")
async def get_stats(
    settings: Settings = Depends(get_settings)
):
    """Get vector database statistics."""
    try:
        info = await get_collection_info(settings)
        return info
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
