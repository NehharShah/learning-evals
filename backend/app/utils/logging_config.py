"""
Logging configuration for the LLM Evaluation Tool
Provides structured logging with different formats and levels
"""

import logging
import logging.config
import sys
from typing import Dict, Any
import json
from datetime import datetime

from app.config import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON
        """
        log_obj = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "exc_info", "exc_text",
                "stack_info", "getMessage"
            ]:
                log_obj[key] = value
        
        return json.dumps(log_obj, default=str)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for console output
    """
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors
        """
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        
        return super().format(record)


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment settings
    """
    # Choose formatter based on settings
    if settings.log_format.lower() == "json":
        formatter_class = "app.utils.logging_config.JSONFormatter"
        format_string = ""  # JSON formatter doesn't use format string
    else:
        formatter_class = "app.utils.logging_config.ColoredFormatter"
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                "format": format_string,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            # Our application loggers
            "app": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # FastAPI and related loggers
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "WARNING",  # Reduce noise from access logs
                "handlers": ["console"],
                "propagate": False,
            },
            # OpenAI logger
            "openai": {
                "level": "WARNING",  # Reduce noise from OpenAI library
                "handlers": ["console"],
                "propagate": False,
            },
            # Rate limiting logger
            "slowapi": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console"],
        },
    }
    
    # Add file logging in production
    if settings.environment == "production":
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level,
            "formatter": "default",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }
        
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    return config


def setup_logging():
    """
    Set up logging configuration for the application
    """
    # Create logs directory if it doesn't exist (for production)
    if settings.environment == "production":
        import os
        os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    # Set up some initial logging
    logger = logging.getLogger("app.startup")
    logger.info("Logging system initialized")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Log format: {settings.log_format}")
    logger.info(f"Environment: {settings.environment}")
    
    # Log any important security settings
    if settings.debug:
        logger.warning("Debug mode is enabled - not recommended for production")
    
    # Reduce noise from verbose libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class SecurityLogger:
    """
    Specialized logger for security events
    """
    
    def __init__(self):
        self.logger = logging.getLogger("app.security")
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "info"):
        """
        Log a security event with structured data
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Event severity (debug, info, warning, error, critical)
        """
        log_data = {
            "security_event": event_type,
            "severity": severity,
            **details
        }
        
        level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(level, f"Security event: {event_type}", extra=log_data)
    
    def log_suspicious_activity(self, activity: str, client_ip: str, details: Dict[str, Any] = None):
        """
        Log suspicious activity
        """
        self.log_security_event(
            "suspicious_activity",
            {
                "activity": activity,
                "client_ip": client_ip,
                **(details or {})
            },
            "warning"
        )
    
    def log_blocked_request(self, reason: str, client_ip: str, details: Dict[str, Any] = None):
        """
        Log blocked request
        """
        self.log_security_event(
            "blocked_request",
            {
                "reason": reason,
                "client_ip": client_ip,
                **(details or {})
            },
            "warning"
        )
    
    def log_rate_limit_exceeded(self, client_ip: str, endpoint: str, details: Dict[str, Any] = None):
        """
        Log rate limit violation
        """
        self.log_security_event(
            "rate_limit_exceeded",
            {
                "client_ip": client_ip,
                "endpoint": endpoint,
                **(details or {})
            },
            "warning"
        )


# Create global security logger instance
security_logger = SecurityLogger() 