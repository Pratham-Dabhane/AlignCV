"""
Notifications API Routes - Phase 7

Endpoints for managing notification settings and viewing notification history.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from ..database import get_db
from ..auth.utils import decode_token
from ..models.models import User, Notification, NotificationSettings, Job
from ..config import Settings, get_settings
from .tasks import send_job_match_email

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

router = APIRouter(prefix="/v2/notifications", tags=["Notifications"])


# ============================================
# Dependencies
# ============================================

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


# ============================================
# Pydantic Schemas
# ============================================

class NotificationSettingsSchema(BaseModel):
    """Notification settings schema."""
    email_enabled: bool = True
    digest_frequency: str = Field("daily", pattern="^(daily|weekly|disabled)$")
    notify_new_matches: bool = True
    notify_application_updates: bool = True
    min_match_score: float = Field(0.85, ge=0.0, le=1.0)


class NotificationSchema(BaseModel):
    """Notification schema."""
    id: int
    type: str
    title: str
    message: str
    job_id: Optional[int] = None
    match_score: Optional[float] = None
    email_sent: bool
    is_read: bool
    created_at: datetime
    
    # Job details (if applicable)
    job_title: Optional[str] = None
    job_company: Optional[str] = None


class NotificationListResponse(BaseModel):
    """Response for listing notifications."""
    total: int
    unread: int
    notifications: List[NotificationSchema]


# ============================================
# Routes
# ============================================

@router.get("/settings", response_model=NotificationSettingsSchema)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's notification settings.
    
    Creates default settings if they don't exist.
    """
    try:
        # Check if settings exist
        result = await db.execute(
            select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            # Create default settings
            settings = NotificationSettings(
                user_id=current_user.id,
                email_enabled=1,
                digest_frequency="daily",
                notify_new_matches=1,
                notify_application_updates=1,
                min_match_score=0.85
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return NotificationSettingsSchema(
            email_enabled=bool(settings.email_enabled),
            digest_frequency=settings.digest_frequency,
            notify_new_matches=bool(settings.notify_new_matches),
            notify_application_updates=bool(settings.notify_application_updates),
            min_match_score=settings.min_match_score
        )
        
    except Exception as e:
        logger.error(f"Error fetching notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification settings"
        )


@router.put("/settings", response_model=NotificationSettingsSchema)
async def update_notification_settings(
    settings_data: NotificationSettingsSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's notification settings.
    """
    try:
        # Get existing settings
        result = await db.execute(
            select(NotificationSettings).where(NotificationSettings.user_id == current_user.id)
        )
        settings = result.scalar_one_or_none()
        
        if settings:
            # Update existing settings
            settings.email_enabled = 1 if settings_data.email_enabled else 0
            settings.digest_frequency = settings_data.digest_frequency
            settings.notify_new_matches = 1 if settings_data.notify_new_matches else 0
            settings.notify_application_updates = 1 if settings_data.notify_application_updates else 0
            settings.min_match_score = settings_data.min_match_score
            settings.updated_at = datetime.utcnow()
        else:
            # Create new settings
            settings = NotificationSettings(
                user_id=current_user.id,
                email_enabled=1 if settings_data.email_enabled else 0,
                digest_frequency=settings_data.digest_frequency,
                notify_new_matches=1 if settings_data.notify_new_matches else 0,
                notify_application_updates=1 if settings_data.notify_application_updates else 0,
                min_match_score=settings_data.min_match_score
            )
            db.add(settings)
        
        await db.commit()
        await db.refresh(settings)
        
        logger.info(f"Updated notification settings for user {current_user.email}")
        
        return settings_data
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's notifications.
    
    Query parameters:
    - unread_only: If true, only return unread notifications
    - limit: Maximum number of notifications to return
    - offset: Number of notifications to skip
    """
    try:
        # Build query
        query = select(Notification).where(Notification.user_id == current_user.id)
        
        if unread_only:
            query = query.where(Notification.is_read == 0)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        # Count total and unread
        total_result = await db.execute(
            select(Notification).where(Notification.user_id == current_user.id)
        )
        total = len(total_result.scalars().all())
        
        unread_result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == current_user.id,
                    Notification.is_read == 0
                )
            )
        )
        unread = len(unread_result.scalars().all())
        
        # Format response
        notification_list = []
        for notif in notifications:
            # Get job details if applicable
            job_title = None
            job_company = None
            if notif.job_id:
                job_result = await db.execute(select(Job).where(Job.id == notif.job_id))
                job = job_result.scalar_one_or_none()
                if job:
                    job_title = job.title
                    job_company = job.company
            
            notification_list.append(NotificationSchema(
                id=notif.id,
                type=notif.type,
                title=notif.title,
                message=notif.message,
                job_id=notif.job_id,
                match_score=notif.match_score,
                email_sent=bool(notif.email_sent),
                is_read=bool(notif.is_read),
                created_at=notif.created_at,
                job_title=job_title,
                job_company=job_company
            ))
        
        return NotificationListResponse(
            total=total,
            unread=unread,
            notifications=notification_list
        )
        
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    try:
        # Get notification
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == current_user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Mark as read
        notification.is_read = 1
        notification.read_at = datetime.utcnow()
        await db.commit()
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )


@router.post("/test")
async def test_notification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    """
    Test notification system by sending a test email.
    
    Useful for verifying SendGrid configuration.
    """
    try:
        # Get a sample job
        result = await db.execute(select(Job).limit(1))
        sample_job = result.scalar_one_or_none()
        
        if not sample_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs available for test. Ingest jobs first."
            )
        
        # Queue test email
        send_job_match_email.delay(current_user.id, [sample_job.id])
        
        logger.info(f"Test notification queued for {current_user.email}")
        
        return {
            "message": "Test notification queued successfully",
            "email": current_user.email,
            "note": "Check your email inbox (and spam folder) in a few moments"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test notification"
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification."""
    try:
        # Get notification
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == current_user.id
                )
            )
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Delete notification
        await db.delete(notification)
        await db.commit()
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )
