"""
Centralized Logging Configuration - Phase 8

Provides structured JSON logging with:
- Timestamp, module, level, message
- Request ID tracking
- User context
- Sentry integration for error tracking
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format.
    
    Format: {"timestamp": "...", "level": "...", "module": "...", "message": "...", ...}
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        
        # Base log data
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/app.log",
    enable_sentry: bool = False,
    sentry_dsn: str = None,
    environment: str = "development"
):
    """
    Configure centralized logging for the application.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_sentry: Whether to enable Sentry error tracking
        sentry_dsn: Sentry DSN for error reporting
        environment: Environment name (development, staging, production)
    """
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output (human-readable for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File handler with JSON format (structured for analysis)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Capture everything in file
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)
    
    # Sentry integration for error tracking
    if enable_sentry and sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            # Configure Sentry
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors and above as events
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                integrations=[sentry_logging],
                traces_sample_rate=0.1,  # Sample 10% of transactions
                profiles_sample_rate=0.1,  # Sample 10% of profiles
                send_default_pii=False,  # Don't send PII by default
            )
            
            root_logger.info("Sentry error tracking initialized")
            
        except ImportError:
            root_logger.warning("sentry-sdk not installed. Error tracking disabled.")
        except Exception as e:
            root_logger.error(f"Failed to initialize Sentry: {e}")
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    root_logger.info(
        f"Logging initialized: level={log_level}, file={log_file}, sentry={enable_sentry}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: int = None,
    request_id: str = None
):
    """
    Log an HTTP request with structured data.
    
    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        user_id: Optional user ID
        request_id: Optional request ID for tracing
    """
    
    extra = {
        "endpoint": f"{method} {path}",
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    
    if user_id:
        extra["user_id"] = user_id
    if request_id:
        extra["request_id"] = request_id
    
    # Determine log level based on status code
    if status_code >= 500:
        level = logging.ERROR
    elif status_code >= 400:
        level = logging.WARNING
    else:
        level = logging.INFO
    
    logger.log(
        level,
        f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
        extra=extra
    )


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: int = None
):
    """
    Log an error with context and optional Sentry reporting.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context data
        user_id: Optional user ID
    """
    
    extra = context or {}
    if user_id:
        extra["user_id"] = user_id
    
    logger.error(
        f"{type(error).__name__}: {str(error)}",
        exc_info=True,
        extra=extra
    )
    
    # Sentry will automatically capture this if configured
