#!/usr/bin/env python3
"""
Security Middleware
CSRF protection, input sanitization, XSS prevention, rate limiting
Configured with dev/prod toggles
"""

import re
import html
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.config.security import (
    is_csrf_enabled,
    is_rate_limiting_enabled,
    get_rate_limit_per_minute,
    get_rate_limit_per_hour,
    is_strict_validation
)


class SecurityMiddleware:
    """
    Security Middleware
    Provides CSRF protection, input sanitization, XSS prevention, and rate limiting
    """
    
    def __init__(self):
        """Initialize security middleware"""
        self.csrf_enabled = is_csrf_enabled()
        self.rate_limiting_enabled = is_rate_limiting_enabled()
        self.strict_validation = is_strict_validation()
        
        # CSRF token storage (in production, should use Redis or database)
        self.csrf_tokens: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting storage (in production, should use Redis)
        self.rate_limits: Dict[str, list] = {}
    
    def sanitize_input(self, text: str, allow_html: bool = False) -> str:
        """
        Sanitize user input to prevent XSS attacks
        
        Args:
            text: Input text to sanitize
            allow_html: If True, allow safe HTML tags (not recommended)
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove HTML tags (Vibecode #7 compliance)
        if not allow_html:
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'<>|</>', '', text)  # Remove React fragments
            text = re.sub(r'\[ref=[^\]]+\]', '', text)  # Remove debug IDs
        
        # Escape HTML entities
        text = html.escape(text)
        
        # Remove control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        
        # Remove CSS class names that might leak (Vibecode #7)
        text = re.sub(r'\b(class|className)\s*=\s*["\'][^"\']*["\']', '', text)
        
        return text.strip()
    
    def validate_input_length(self, text: str, max_length: int = 10000, min_length: int = 0) -> tuple[bool, str]:
        """
        Validate input length
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            min_length: Minimum required length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            if min_length > 0:
                return False, f"Input must be at least {min_length} characters"
            return True, ""
        
        length = len(text)
        if length < min_length:
            return False, f"Input must be at least {min_length} characters"
        if length > max_length:
            return False, f"Input must be no more than {max_length} characters"
        
        return True, ""
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        # Remove @ if present
        username = username.lstrip('@')
        
        # Check length
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 30:
            return False, "Username must be no more than 30 characters"
        
        # Check format (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        # Check reserved usernames
        reserved = ['admin', 'administrator', 'root', 'system', 'api', 'www', 'mail', 'ftp']
        if username.lower() in reserved:
            return False, "Username is reserved"
        
        return True, ""
    
    def generate_csrf_token(self, session_id: str) -> str:
        """
        Generate CSRF token for session
        
        Args:
            session_id: Session ID
            
        Returns:
            CSRF token
        """
        if not self.csrf_enabled:
            return ""
        
        import secrets
        token = secrets.token_urlsafe(32)
        
        self.csrf_tokens[session_id] = {
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return token
    
    def verify_csrf_token(self, session_id: str, token: str) -> bool:
        """
        Verify CSRF token
        
        Args:
            session_id: Session ID
            token: CSRF token to verify
            
        Returns:
            True if valid, False otherwise
        """
        if not self.csrf_enabled:
            return True  # CSRF disabled in dev mode
        
        if session_id not in self.csrf_tokens:
            return False
        
        stored = self.csrf_tokens[session_id]
        
        # Check expiration
        expires_at = datetime.fromisoformat(stored.get("expires_at", "1970-01-01T00:00:00"))
        if expires_at < datetime.now():
            del self.csrf_tokens[session_id]
            return False
        
        # Verify token
        return stored.get("token") == token
    
    def check_rate_limit(self, identifier: str, per_minute: Optional[int] = None, per_hour: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """
        Check rate limit for identifier (IP address or user ID)
        
        Args:
            identifier: IP address or user ID
            per_minute: Optional custom per-minute limit
            per_hour: Optional custom per-hour limit
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        if not self.rate_limiting_enabled:
            return True, None
        
        now = datetime.now()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Get limits
        if per_minute is None:
            per_minute = get_rate_limit_per_minute()
        if per_hour is None:
            per_hour = get_rate_limit_per_hour()
        
        # Clean old entries
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        self.rate_limits[identifier] = [
            ts for ts in self.rate_limits[identifier]
            if datetime.fromisoformat(ts) > hour_ago
        ]
        
        # Check per-minute limit
        recent_minute = [
            ts for ts in self.rate_limits[identifier]
            if datetime.fromisoformat(ts) > minute_ago
        ]
        
        if len(recent_minute) >= per_minute:
            return False, f"Rate limit exceeded: {per_minute} requests per minute"
        
        # Check per-hour limit
        if len(self.rate_limits[identifier]) >= per_hour:
            return False, f"Rate limit exceeded: {per_hour} requests per hour"
        
        # Add current request
        self.rate_limits[identifier].append(now.isoformat())
        
        return True, None
    
    def clean_expired_tokens(self):
        """Clean expired CSRF tokens"""
        now = datetime.now()
        expired = []
        
        for session_id, token_data in self.csrf_tokens.items():
            expires_at = datetime.fromisoformat(token_data.get("expires_at", "1970-01-01T00:00:00"))
            if expires_at < now:
                expired.append(session_id)
        
        for session_id in expired:
            del self.csrf_tokens[session_id]
    
    def clean_old_rate_limits(self, hours: int = 24):
        """Clean old rate limit entries"""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()
        
        for identifier in list(self.rate_limits.keys()):
            self.rate_limits[identifier] = [
                ts for ts in self.rate_limits[identifier]
                if ts > cutoff_str
            ]
            
            # Remove empty entries
            if not self.rate_limits[identifier]:
                del self.rate_limits[identifier]


# Global middleware instance
security_middleware = SecurityMiddleware()


def require_csrf(f: Callable) -> Callable:
    """
    Decorator to require CSRF token for endpoint
    
    Args:
        f: Flask route function
        
    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_csrf_enabled():
            return f(*args, **kwargs)
        
        from flask import request, jsonify
        
        session_id = request.headers.get('X-Session-ID') or request.json.get('session_id') if request.is_json else None
        csrf_token = request.headers.get('X-CSRF-Token') or (request.json.get('csrf_token') if request.is_json else None)
        
        if not session_id or not csrf_token:
            return jsonify({'error': 'CSRF token required'}), 403
        
        if not security_middleware.verify_csrf_token(session_id, csrf_token):
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def sanitize_request_data(data: Dict[str, Any], fields_to_sanitize: Optional[list] = None) -> Dict[str, Any]:
    """
    Sanitize request data
    
    Args:
        data: Request data dictionary
        fields_to_sanitize: Optional list of field names to sanitize (if None, sanitize all string fields)
        
    Returns:
        Sanitized data dictionary
    """
    if data is None:
        return {}
    
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        if fields_to_sanitize and key not in fields_to_sanitize:
            sanitized[key] = value
            continue
        
        if isinstance(value, str):
            sanitized[key] = security_middleware.sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value, fields_to_sanitize)
        elif isinstance(value, list):
            sanitized[key] = [
                security_middleware.sanitize_input(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized

