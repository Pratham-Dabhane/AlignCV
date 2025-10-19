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

from ..database import get_db, get_supabase_client
from ..auth.utils import decode_token
from ..models.models import User, Notification, NotificationSettings, Job
from ..config import Settings, get_settings
from supabase import Client
from .tasks import send_job_match_email

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

router = APIRouter(prefix="/v2/notifications", tags=["Notifications"])


# ============================================
# Dependencies
# ============================================

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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return result.data[0]
        
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
    id: str  # UUID
    type: str
    title: str
    message: str
    job_id: Optional[str] = None  # UUID
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
def get_notification_settings(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    Get user's notification settings.
    
    Creates default settings if they don't exist.
    """
    try:
        # Check if settings exist
        result = db.table('notification_settings').select('*').eq('user_id', current_user['id']).execute()
        
        if not result.data:
            # Create default settings
            new_settings = {
                'user_id': current_user['id'],
                'email_enabled': True,
                'digest_frequency': 'daily',
                'notify_new_matches': True,
                'notify_application_updates': True,
                'min_match_score': 0.85
            }
            result = db.table('notification_settings').insert(new_settings).execute()
            settings = result.data[0]
        else:
            settings = result.data[0]
        
        return NotificationSettingsSchema(
            email_enabled=settings['email_enabled'],
            digest_frequency=settings['digest_frequency'],
            notify_new_matches=settings['notify_new_matches'],
            notify_application_updates=settings['notify_application_updates'],
            min_match_score=settings['min_match_score']
        )
        
    except Exception as e:
        logger.error(f"Error fetching notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification settings"
        )


@router.put("/settings", response_model=NotificationSettingsSchema)
def update_notification_settings(
    settings_data: NotificationSettingsSchema,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """
    Update user's notification settings.
    """
    try:
        # Get existing settings
        result = db.table('notification_settings').select('*').eq('user_id', current_user['id']).execute()
        
        update_data = {
            'email_enabled': settings_data.email_enabled,
            'digest_frequency': settings_data.digest_frequency,
            'notify_new_matches': settings_data.notify_new_matches,
            'notify_application_updates': settings_data.notify_application_updates,
            'min_match_score': settings_data.min_match_score,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if result.data:
            # Update existing settings
            db.table('notification_settings').update(update_data).eq('user_id', current_user['id']).execute()
        else:
            # Create new settings
            update_data['user_id'] = current_user['id']
            db.table('notification_settings').insert(update_data).execute()
        
        logger.info(f"Updated notification settings for user {current_user['email']}")
        
        return settings_data
        
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
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
        query = db.table('notifications').select('*').eq('user_id', current_user['id'])
        
        if unread_only:
            query = query.eq('is_read', False)
        
        # Execute query with ordering and pagination
        result = query.order('created_at', desc=True).range(offset, offset + limit - 1).execute()
        notifications = result.data if result.data else []
        
        # Count total
        total_result = db.table('notifications').select('id', count='exact').eq('user_id', current_user['id']).execute()
        total = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
        
        # Count unread
        unread_result = db.table('notifications').select('id', count='exact').eq('user_id', current_user['id']).eq('is_read', False).execute()
        unread = unread_result.count if hasattr(unread_result, 'count') else len(unread_result.data)
        
        # Format response
        notification_list = []
        for notif in notifications:
            # Get job details if applicable (jobs table doesn't exist yet, so skip)
            job_title = None
            job_company = None
            
            notification_list.append(NotificationSchema(
                id=notif['id'],
                type=notif['type'],
                title=notif['title'],
                message=notif['message'],
                job_id=notif.get('job_id'),
                match_score=notif.get('match_score'),
                email_sent=notif.get('email_sent', False),
                is_read=notif.get('is_read', False),
                created_at=notif['created_at'],
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
def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Mark notification as read."""
    try:
        # Get notification
        result = db.table('notifications').select('*').eq('id', notification_id).eq('user_id', current_user['id']).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Mark as read
        db.table('notifications').update({
            'is_read': True,
            'read_at': datetime.utcnow().isoformat()
        }).eq('id', notification_id).execute()
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification"
        )


@router.post("/test")
def test_notification(
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client),
    settings: Settings = Depends(get_settings)
):
    """
    Test notification system by sending a test email.
    
    Useful for verifying SendGrid configuration.
    """
    try:
        # Get a sample job (jobs table might not exist yet)
        result = db.table('jobs').select('*').limit(1).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs available for test. Ingest jobs first."
            )
        
        sample_job = result.data[0]
        
        # Queue test email
        send_job_match_email.delay(current_user['id'], [sample_job['id']])
        
        logger.info(f"Test notification queued for {current_user['email']}")
        
        return {
            "message": "Test notification queued successfully",
            "email": current_user['email'],
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
def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user),
    db: Client = Depends(get_supabase_client)
):
    """Delete a notification."""
    try:
        # Get notification
        result = db.table('notifications').select('*').eq('id', notification_id).eq('user_id', current_user['id']).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Delete notification
        db.table('notifications').delete().eq('id', notification_id).execute()
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )
