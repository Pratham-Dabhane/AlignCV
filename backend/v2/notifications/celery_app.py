"""
Celery Application Configuration - Phase 7

Configures Celery with Upstash Redis as the broker and result backend.
"""

import logging
import ssl
from celery import Celery
from celery.schedules import crontab
from ..config import get_settings

logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create Celery app
celery_app = Celery("aligncv")

# Configure Celery with Upstash Redis
# Upstash Redis uses standard Redis protocol with authentication
if settings.redis_url and not settings.redis_url.startswith("redis://default:${"):
    # Use configured Redis URL if it's valid
    redis_url = settings.redis_url
elif settings.upstash_redis_rest_url and settings.upstash_redis_rest_token:
    # Construct Redis URL from Upstash credentials
    # Upstash REST URL format: https://hostname.upstash.io
    # Redis URL format: rediss://default:TOKEN@hostname.upstash.io:6379
    redis_host = settings.upstash_redis_rest_url.replace('https://', '').replace('http://', '').strip('/')
    redis_url = f"rediss://default:{settings.upstash_redis_rest_token}@{redis_host}:6379"
else:
    logger.warning("No Redis URL configured. Celery tasks will fail!")
    redis_url = "redis://localhost:6379"  # Fallback (will fail if Redis not running locally)

logger.info(f"Configuring Celery with broker: {redis_url.split('@')[0]}@***")

# SSL options for Upstash Redis (rediss://)
redis_backend_use_ssl = {
    'ssl_cert_reqs': ssl.CERT_NONE  # Accept self-signed certificates from Upstash
}

celery_app.conf.update(
    # Broker settings (Upstash Redis)
    broker_url=redis_url,
    broker_use_ssl=redis_backend_use_ssl if redis_url.startswith('rediss://') else None,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Result backend (Upstash Redis)
    result_backend=redis_url,
    redis_backend_use_ssl=redis_backend_use_ssl if redis_url.startswith('rediss://') else None,
    result_expires=3600,  # Results expire after 1 hour
    
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "backend.v2.notifications.tasks.check_new_jobs": {"queue": "notifications"},
        "backend.v2.notifications.tasks.send_job_match_email": {"queue": "emails"},
        "backend.v2.notifications.tasks.send_daily_digest": {"queue": "emails"},
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        "check-new-jobs-daily": {
            "task": "backend.v2.notifications.tasks.check_new_jobs",
            "schedule": crontab(hour=9, minute=0),  # Every day at 9 AM UTC
        },
        "send-weekly-digests": {
            "task": "backend.v2.notifications.tasks.send_daily_digest",
            "schedule": crontab(day_of_week=1, hour=9, minute=0),  # Every Monday at 9 AM UTC
        },
    },
)

# Auto-discover tasks from this module
celery_app.autodiscover_tasks(["backend.v2.notifications"])

logger.info("Celery app configured successfully")
