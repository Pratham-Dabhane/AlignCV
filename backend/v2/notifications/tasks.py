"""
Celery Tasks - Phase 7

Background tasks for job matching and email notifications.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .celery_app import celery_app
from .email_service import EmailService
from ..config import get_settings
from ..models.models import User, Job, Notification, NotificationSettings, Document
from ..jobs.embedding_utils import get_resume_embedding
from ..jobs.matcher import rank_jobs
from ..jobs.vector_store import search_similar_jobs, get_qdrant_client

logger = logging.getLogger(__name__)


# Create async database session for Celery tasks
settings = get_settings()
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="backend.v2.notifications.tasks.check_new_jobs")
def check_new_jobs():
    """
    Periodic task to check for new job matches.
    
    Runs daily at 9 AM UTC.
    For each user with notifications enabled:
    1. Get their latest resume
    2. Search for new jobs (created in last 24 hours)
    3. If match score > threshold, create notification and queue email
    """
    import asyncio
    return asyncio.run(_check_new_jobs_async())


async def _check_new_jobs_async():
    """Async implementation of check_new_jobs."""
    logger.info("Starting check_new_jobs task")
    
    async with AsyncSessionLocal() as db:
        try:
            # Get all users with notifications enabled
            result = await db.execute(
                select(User, NotificationSettings).join(
                    NotificationSettings,
                    User.id == NotificationSettings.user_id
                ).where(
                    and_(
                        NotificationSettings.email_enabled == 1,
                        NotificationSettings.notify_new_matches == 1
                    )
                )
            )
            users_with_settings = result.all()
            
            logger.info(f"Found {len(users_with_settings)} users with notifications enabled")
            
            notifications_created = 0
            emails_queued = 0
            
            for user, settings_obj in users_with_settings:
                try:
                    # Get user's latest resume
                    doc_result = await db.execute(
                        select(Document).where(
                            Document.user_id == user.id
                        ).order_by(Document.created_at.desc()).limit(1)
                    )
                    latest_doc = doc_result.scalar_one_or_none()
                    
                    if not latest_doc or not latest_doc.parsed_text:
                        logger.info(f"User {user.email} has no resume, skipping")
                        continue
                    
                    # Get jobs created in last 24 hours
                    yesterday = datetime.utcnow() - timedelta(days=1)
                    jobs_result = await db.execute(
                        select(Job).where(Job.created_at >= yesterday)
                    )
                    new_jobs = jobs_result.scalars().all()
                    
                    if not new_jobs:
                        logger.info("No new jobs in last 24 hours")
                        continue
                    
                    logger.info(f"Checking {len(new_jobs)} new jobs for user {user.email}")
                    
                    # Generate resume embedding
                    resume_embedding = await get_resume_embedding(latest_doc.parsed_text, get_settings())
                    
                    # Search for matching jobs
                    qdrant_client = get_qdrant_client(get_settings())
                    search_results = await search_similar_jobs(
                        query_vector=resume_embedding,
                        settings=get_settings(),
                        limit=20
                    )
                    
                    # Rank jobs using skill matching
                    skills = latest_doc.skills if latest_doc.skills else []
                    ranked_jobs = await rank_jobs(
                        jobs_data=search_results,
                        user_skills=skills,
                        settings=get_settings()
                    )
                    
                    # Filter by threshold and new jobs only
                    new_job_ids = {job.job_id for job in new_jobs}
                    high_matches = [
                        job for job in ranked_jobs
                        if job.get("combined_score", 0) >= settings_obj.min_match_score
                        and job.get("job_id") in new_job_ids
                    ]
                    
                    if high_matches:
                        logger.info(f"Found {len(high_matches)} high-quality matches for {user.email}")
                        
                        # Create notification record
                        for match in high_matches[:5]:  # Top 5 matches
                            notification = Notification(
                                user_id=user.id,
                                type="job_match",
                                title=f"New match: {match.get('title', 'Untitled')}",
                                message=f"{match.get('company', 'Unknown')} is hiring! {int(match.get('combined_score', 0) * 100)}% match",
                                job_id=match.get("id"),
                                match_score=match.get("combined_score"),
                                email_sent=0
                            )
                            db.add(notification)
                            notifications_created += 1
                        
                        await db.commit()
                        
                        # Queue email task
                        send_job_match_email.delay(user.id, [job.get("id") for job in high_matches[:5]])
                        emails_queued += 1
                    else:
                        logger.info(f"No high-quality matches for {user.email}")
                        
                except Exception as e:
                    logger.error(f"Error processing user {user.email}: {e}")
                    await db.rollback()
                    continue
            
            logger.info(f"check_new_jobs complete: {notifications_created} notifications, {emails_queued} emails queued")
            return {
                "notifications_created": notifications_created,
                "emails_queued": emails_queued
            }
            
        except Exception as e:
            logger.error(f"check_new_jobs failed: {e}")
            return {"error": str(e)}


@celery_app.task(name="backend.v2.notifications.tasks.send_job_match_email")
def send_job_match_email(user_id: int, job_ids: List[int]):
    """
    Send job match notification email to user.
    
    Args:
        user_id: User ID
        job_ids: List of job IDs that matched
    """
    import asyncio
    return asyncio.run(_send_job_match_email_async(user_id, job_ids))


async def _send_job_match_email_async(user_id: int, job_ids: List[int]):
    """Async implementation of send_job_match_email."""
    logger.info(f"Sending job match email to user {user_id} for {len(job_ids)} jobs")
    
    async with AsyncSessionLocal() as db:
        try:
            # Get user
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found")
                return {"success": False, "error": "User not found"}
            
            # Get jobs
            jobs_result = await db.execute(select(Job).where(Job.id.in_(job_ids)))
            jobs = jobs_result.scalars().all()
            
            if not jobs:
                logger.error(f"No jobs found for IDs: {job_ids}")
                return {"success": False, "error": "Jobs not found"}
            
            # Prepare job data for email
            job_matches = []
            for job in jobs:
                job_matches.append({
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "url": job.url,
                    "salary_min": job.salary_min,
                    "salary_max": job.salary_max,
                    "combined_score": 0.85,  # Placeholder, should come from notification
                })
            
            # Send email
            email_service = EmailService()
            success = await email_service.send_job_match_notification(
                to_email=user.email,
                user_name=user.name,
                job_matches=job_matches
            )
            
            if success:
                # Update notification records
                await db.execute(
                    f"UPDATE notifications SET email_sent = 1, email_sent_at = '{datetime.utcnow().isoformat()}' "
                    f"WHERE user_id = {user_id} AND job_id IN ({','.join(map(str, job_ids))}) AND email_sent = 0"
                )
                await db.commit()
                
                logger.info(f"Email sent successfully to {user.email}")
                return {"success": True, "user_email": user.email}
            else:
                logger.error(f"Failed to send email to {user.email}")
                return {"success": False, "error": "Email sending failed"}
                
        except Exception as e:
            logger.error(f"send_job_match_email failed: {e}")
            return {"success": False, "error": str(e)}


@celery_app.task(name="backend.v2.notifications.tasks.send_daily_digest")
def send_daily_digest():
    """
    Send daily/weekly digest emails.
    
    Runs daily for daily digest users, weekly for weekly digest users.
    """
    import asyncio
    return asyncio.run(_send_daily_digest_async())


async def _send_daily_digest_async():
    """Async implementation of send_daily_digest."""
    logger.info("Starting send_daily_digest task")
    
    async with AsyncSessionLocal() as db:
        try:
            # Determine digest type based on day of week
            is_monday = datetime.utcnow().weekday() == 0
            digest_frequency = "weekly" if is_monday else "daily"
            
            # Get users with appropriate digest settings
            result = await db.execute(
                select(User, NotificationSettings).join(
                    NotificationSettings,
                    User.id == NotificationSettings.user_id
                ).where(
                    and_(
                        NotificationSettings.email_enabled == 1,
                        NotificationSettings.digest_frequency == digest_frequency
                    )
                )
            )
            users_with_settings = result.all()
            
            logger.info(f"Found {len(users_with_settings)} users for {digest_frequency} digest")
            
            emails_sent = 0
            
            for user, settings_obj in users_with_settings:
                try:
                    # Calculate summary stats
                    days_back = 7 if digest_frequency == "weekly" else 1
                    start_date = datetime.utcnow() - timedelta(days=days_back)
                    
                    # Count new jobs
                    jobs_result = await db.execute(
                        select(Job).where(Job.created_at >= start_date)
                    )
                    new_jobs_count = len(jobs_result.scalars().all())
                    
                    # Count new matches (notifications)
                    notif_result = await db.execute(
                        select(Notification).where(
                            and_(
                                Notification.user_id == user.id,
                                Notification.created_at >= start_date,
                                Notification.type == "job_match"
                            )
                        )
                    )
                    new_matches_count = len(notif_result.scalars().all())
                    
                    summary = {
                        "new_jobs": new_jobs_count,
                        "new_matches": new_matches_count,
                        "applications": 0,  # Could add application count
                    }
                    
                    # Send digest email
                    email_service = EmailService()
                    success = await email_service.send_digest_email(
                        to_email=user.email,
                        user_name=user.name,
                        digest_type=digest_frequency,
                        summary=summary
                    )
                    
                    if success:
                        emails_sent += 1
                        
                except Exception as e:
                    logger.error(f"Error sending digest to {user.email}: {e}")
                    continue
            
            logger.info(f"send_daily_digest complete: {emails_sent} emails sent")
            return {"emails_sent": emails_sent, "digest_type": digest_frequency}
            
        except Exception as e:
            logger.error(f"send_daily_digest failed: {e}")
            return {"error": str(e)}
