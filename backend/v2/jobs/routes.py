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

from ..database import get_db, get_supabase_client
from ..models.models import User, Document, Job, JobBookmark, JobApplication
from ..config import get_settings, Settings
from ..auth.utils import decode_token
from supabase import Client
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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_supabase_client)
):
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        email = decode_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        result = db.table('users').select('*').eq('email', email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return result.data[0]
        
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
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client),
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
    logger.info(f"Job match request - User: {current_user['email']}, Resume: {request.resume_id}")
    
    # Fetch resume document
    result = db.table('documents').select('*').eq('id', request.resume_id).eq('user_id', current_user['id']).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    document = result.data[0]
    
    # Extract text from parsed_content
    extracted_text = None
    if document.get('parsed_content'):
        extracted_text = document['parsed_content'].get('text')
    
    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no extracted text"
        )
    
    # Generate resume embedding
    logger.info("Generating resume embedding...")
    resume_embedding = await get_resume_embedding(extracted_text, settings)
    
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
        resume_text=extracted_text,
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
    
    # Check bookmarks and applications (tables might not exist yet)
    try:
        bookmarks_result = db.table('bookmarks').select('job_id').eq('user_id', current_user['id']).execute()
        bookmarks = {b['job_id'] for b in bookmarks_result.data} if bookmarks_result.data else set()
    except:
        bookmarks = set()
    
    try:
        applications_result = db.table('applications').select('job_id').eq('user_id', current_user['id']).execute()
        applications = {a['job_id'] for a in applications_result.data} if applications_result.data else set()
    except:
        applications = set()
    
    # Enrich with bookmark/application status
    for job in ranked_jobs:
        job_id = job.get("job_id")
        job["is_bookmarked"] = job_id in bookmarks
        job["is_applied"] = job_id in applications
    
    logger.info(f"Returning {len(ranked_jobs)} matched jobs")
    return ranked_jobs


@router.post("/ingest", response_model=IngestJobsResponse)
async def ingest_jobs_endpoint(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """
    Ingest jobs from sources and create embeddings.
    
    Admin endpoint to populate job database.
    """
    logger.info(f"Job ingestion started by user: {current_user['email']}")
    
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
        result = db.table('jobs').select('*').eq('job_id', job_data["job_id"]).execute()
        
        if result.data:
            # Update existing job
            job_data['updated_at'] = datetime.utcnow().isoformat()
            db.table('jobs').update(job_data).eq('job_id', job_data["job_id"]).execute()
            updated_jobs += 1
            job_id_str = result.data[0]['id']
        else:
            # Create new job
            job_data['created_at'] = datetime.utcnow().isoformat()
            insert_result = db.table('jobs').insert(job_data).execute()
            new_jobs += 1
            job_id_str = insert_result.data[0]['id']
        
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
        db.table('jobs').update({'vector_id': job_data["job_id"]}).eq('id', job_id_str).execute()
        embeddings_created += 1
    
    logger.info(f"Job ingestion complete - New: {new_jobs}, Updated: {updated_jobs}, Embeddings: {embeddings_created}")
    
    return IngestJobsResponse(
        total_ingested=len(jobs_data),
        new_jobs=new_jobs,
        updated_jobs=updated_jobs,
        embeddings_created=embeddings_created
    )


@router.get("/", response_model=List[Dict])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get list of jobs with pagination."""
    try:
        query = db.table('jobs').select('*')
        
        if source:
            query = query.eq('source', source)
        
        result = query.order('created_at', desc=True).range(skip, skip + limit - 1).execute()
        jobs = result.data if result.data else []
        
        return [
            {
                "id": job['id'],
                "job_id": job['job_id'],
                "title": job['title'],
                "company": job['company'],
                "location": job.get('location'),
                "url": job.get('url'),
                "tags": job.get('tags', []),
                "salary_min": job.get('salary_min'),
                "salary_max": job.get('salary_max'),
                "employment_type": job.get('employment_type'),
                "experience_level": job.get('experience_level'),
                "created_at": job['created_at']
            }
            for job in jobs
        ]
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []


@router.post("/bookmark")
def bookmark_job(
    request: BookmarkRequest,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Bookmark a job for later review."""
    try:
        # Check if job exists (by job_id string, not UUID)
        job_result = db.table('jobs').select('*').eq('job_id', request.job_id).execute()
        
        if not job_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job = job_result.data[0]
        
        # Check if already bookmarked
        existing = db.table('bookmarks').select('*').eq('user_id', current_user['id']).eq('job_id', request.job_id).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job already bookmarked"
            )
        
        # Create bookmark with job details
        bookmark_data = {
            'user_id': current_user['id'],
            'job_id': request.job_id,
            'title': job['title'],
            'company': job['company'],
            'location': job.get('location'),
            'description': job.get('description'),
            'source_url': job.get('url'),
            'notes': request.notes
        }
        result = db.table('bookmarks').insert(bookmark_data).execute()
        
        logger.info(f"Job bookmarked - User: {current_user['id']}, Job: {request.job_id}")
        
        return {"message": "Job bookmarked successfully", "bookmark_id": result.data[0]['id']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bookmarking job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bookmark job"
        )


@router.delete("/bookmark/{job_id}")
def remove_bookmark(
    job_id: str,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Remove bookmark from a job."""
    try:
        result = db.table('bookmarks').select('*').eq('user_id', current_user['id']).eq('job_id', job_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bookmark not found"
            )
        
        db.table('bookmarks').delete().eq('user_id', current_user['id']).eq('job_id', job_id).execute()
        
        logger.info(f"Bookmark removed - User: {current_user['id']}, Job: {job_id}")
        
        return {"message": "Bookmark removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing bookmark: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove bookmark"
        )


@router.get("/bookmarks")
def get_bookmarks(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get user's bookmarked jobs."""
    try:
        result = db.table('bookmarks').select('*').eq('user_id', current_user['id']).execute()
        bookmarks = result.data
        
        return bookmarks
    except Exception as e:
        logger.error(f"Error fetching bookmarks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookmarks"
        )


@router.post("/apply")
def apply_to_job(
    request: ApplicationRequest,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Mark a job as applied."""
    try:
        # Check if job exists
        job_result = db.table('jobs').select('*').eq('job_id', request.job_id).execute()
        
        if not job_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job = job_result.data[0]
        
        # Check if already applied
        existing = db.table('applications').select('*').eq('user_id', current_user['id']).eq('job_id', request.job_id).execute()
        
        if existing.data:
            # Update existing application
            update_data = {
                'status': request.status,
                'notes': request.notes,
                'updated_at': datetime.utcnow().isoformat()
            }
            db.table('applications').update(update_data).eq('user_id', current_user['id']).eq('job_id', request.job_id).execute()
            return {"message": "Application updated successfully", "application_id": existing.data[0]['id']}
        
        # Create application with job details
        application_data = {
            'user_id': current_user['id'],
            'job_id': request.job_id,
            'title': job['title'],
            'company': job['company'],
            'location': job.get('location'),
            'description': job.get('description'),
            'source_url': job.get('url'),
            'status': request.status,
            'notes': request.notes,
            'applied_date': datetime.utcnow().date().isoformat()
        }
        result = db.table('applications').insert(application_data).execute()
        
        logger.info(f"Job application created - User: {current_user['id']}, Job: {request.job_id}")
        
        return {"message": "Job application recorded successfully", "application_id": result.data[0]['id']}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying to job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record job application"
        )


@router.get("/applications")
def get_applications(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Get user's job applications."""
    try:
        result = db.table('applications').select('*').eq('user_id', current_user['id']).execute()
        applications = result.data
        
        return applications
    except Exception as e:
        logger.error(f"Error fetching applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )


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
