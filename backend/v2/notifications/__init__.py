"""
Notifications Module - Phase 7

Handles email notifications and background tasks using Celery.
"""

from .celery_app import celery_app
from .tasks import check_new_jobs, send_job_match_email, send_daily_digest
from .email_service import EmailService

__all__ = [
    "celery_app",
    "check_new_jobs",
    "send_job_match_email",
    "send_daily_digest",
    "EmailService",
]
