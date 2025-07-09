"""
Security middleware for the LLM Evaluation Tool
Provides request validation, security headers, and basic protection
"""

import time
import json
from typing import Dict, List, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware providing:
    - Security headers
    - Request validation
    - Basic request logging
    - Size limits enforcement
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.start_time = time.time()
        
        # Track request patterns for basic anomaly detection
        self.request_patterns: Dict[str, List[float]] = {}
        self.max_pattern_history = 100
    
    async def dispatch(self, request: Request, call_next):
        """
        Process each request through security checks
        """
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        
        try:
            # Pre-request security checks
            await self.validate_request_size(request)
            await self.validate_request_headers(request)
            
            # Log request
            self.log_request(request, client_ip)
            
            # Process request
            response = await call_next(request)
            
            # Post-request processing
            response = self.add_security_headers(response)
            
            # Log response
            processing_time = time.time() - start_time
            self.log_response(request, response, processing_time, client_ip)
            
            return response
            
        except HTTPException as e:
            logger.warning(f"Security middleware blocked request from {client_ip}: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "error": "Security violation"}
            )
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal security error"}
            )
    
    def get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request
        Handles proxy headers for accurate IP detection
        """
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    async def validate_request_size(self, request: Request):
        """
        Validate request size to prevent oversized payloads
        """
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                # Set a reasonable limit for API requests (10MB)
                max_size = 10 * 1024 * 1024  # 10MB
                
                if size > max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Request too large. Maximum size: {max_size / (1024 * 1024):.1f}MB"
                    )
            except ValueError:
                # Invalid content-length header
                pass
    
    async def validate_request_headers(self, request: Request):
        """
        Validate request headers for security issues
        """
        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = [
            "scanner", "bot", "crawler", "scraper", "hack", "test",
            "sqlmap", "nikto", "nmap", "masscan"
        ]
        
        for suspicious in suspicious_agents:
            if suspicious in user_agent:
                logger.warning(f"Suspicious user agent detected: {user_agent}")
                # Don't block, just log for now
                break
        
        # Validate content-type for POST requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if content_type and not any(allowed in content_type.lower() for allowed in [
                "application/json", "multipart/form-data", "application/x-www-form-urlencoded"
            ]):
                logger.warning(f"Unusual content-type: {content_type}")
        
        # Check for potential header injection
        for header_name, header_value in request.headers.items():
            if any(char in header_value for char in ['\n', '\r', '\0']):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid characters in headers"
                )
    
    def add_security_headers(self, response: Response) -> Response:
        """
        Add security headers to the response
        """
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Server": "LLM-Eval-API",  # Hide actual server information
        }
        
        # Only add HSTS in production with HTTPS
        if settings.environment == "production":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response
    
    def log_request(self, request: Request, client_ip: str):
        """
        Log incoming requests for monitoring
        """
        # Basic request logging
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_length": request.headers.get("content-length", "0"),
            "timestamp": time.time()
        }
        
        # Log at different levels based on request type
        if request.url.path.startswith("/api/v1/evaluate"):
            logger.info(f"Evaluation request from {client_ip}: {request.method} {request.url.path}")
        elif request.url.path.startswith("/api/v1/upload"):
            logger.info(f"Upload request from {client_ip}: {request.method} {request.url.path}")
        else:
            logger.debug(f"Request from {client_ip}: {request.method} {request.url.path}")
        
        # Track request patterns for anomaly detection
        self.track_request_pattern(client_ip)
    
    def log_response(self, request: Request, response: Response, processing_time: float, client_ip: str):
        """
        Log response information
        """
        # Log slow requests
        if processing_time > 5.0:  # 5 seconds
            logger.warning(
                f"Slow request from {client_ip}: {request.method} {request.url.path} "
                f"took {processing_time:.2f}s"
            )
        
        # Log error responses
        if response.status_code >= 400:
            if response.status_code >= 500:
                logger.error(
                    f"Server error for {client_ip}: {request.method} {request.url.path} "
                    f"returned {response.status_code}"
                )
            else:
                logger.warning(
                    f"Client error for {client_ip}: {request.method} {request.url.path} "
                    f"returned {response.status_code}"
                )
    
    def track_request_pattern(self, client_ip: str):
        """
        Track request patterns for basic anomaly detection
        """
        current_time = time.time()
        
        if client_ip not in self.request_patterns:
            self.request_patterns[client_ip] = []
        
        # Add current request timestamp
        self.request_patterns[client_ip].append(current_time)
        
        # Keep only recent requests (last hour)
        hour_ago = current_time - 3600
        self.request_patterns[client_ip] = [
            timestamp for timestamp in self.request_patterns[client_ip]
            if timestamp > hour_ago
        ]
        
        # Limit history size
        if len(self.request_patterns[client_ip]) > self.max_pattern_history:
            self.request_patterns[client_ip] = self.request_patterns[client_ip][-self.max_pattern_history:]
        
        # Check for rapid requests (potential abuse)
        recent_requests = [
            timestamp for timestamp in self.request_patterns[client_ip]
            if timestamp > current_time - 60  # Last minute
        ]
        
        if len(recent_requests) > 30:  # More than 30 requests per minute
            logger.warning(
                f"High request rate from {client_ip}: {len(recent_requests)} requests in the last minute"
            )
        
        # Check for very rapid requests (potential DDoS)
        very_recent = [
            timestamp for timestamp in self.request_patterns[client_ip]
            if timestamp > current_time - 10  # Last 10 seconds
        ]
        
        if len(very_recent) > 20:  # More than 20 requests in 10 seconds
            logger.error(
                f"Potential DDoS from {client_ip}: {len(very_recent)} requests in 10 seconds"
            )
    
    def get_security_stats(self) -> Dict:
        """
        Get security statistics for monitoring
        """
        current_time = time.time()
        hour_ago = current_time - 3600
        
        active_ips = len([
            ip for ip, timestamps in self.request_patterns.items()
            if any(timestamp > hour_ago for timestamp in timestamps)
        ])
        
        total_requests = sum(
            len([timestamp for timestamp in timestamps if timestamp > hour_ago])
            for timestamps in self.request_patterns.values()
        )
        
        return {
            "active_ips_last_hour": active_ips,
            "total_requests_last_hour": total_requests,
            "uptime_seconds": current_time - self.start_time,
            "tracked_ips": len(self.request_patterns)
        } 