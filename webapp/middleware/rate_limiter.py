#!/usr/bin/env python3
"""
Enhanced Rate Limiter
Per-endpoint and per-user rate limiting with Redis support
Uses memory in dev, Redis in prod
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from functools import wraps
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.config.security import (
    is_rate_limiting_enabled,
    get_rate_limit_per_minute,
    get_rate_limit_per_hour
)

# Try to import Redis (optional, falls back to memory)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RateLimiter:
    """
    Enhanced Rate Limiter
    Supports per-endpoint and per-user rate limiting
    Uses Redis in production, memory in development
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize rate limiter
        
        Args:
            redis_url: Optional Redis URL (if None, uses memory)
        """
        self.rate_limiting_enabled = is_rate_limiting_enabled()
        self.use_redis = REDIS_AVAILABLE and redis_url is not None
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Test connection
            except Exception:
                self.use_redis = False
                self.redis_client = None
        
        # Memory storage (fallback)
        self.memory_storage: Dict[str, list] = {}
    
    def _get_key(self, identifier: str, endpoint: Optional[str] = None) -> str:
        """
        Get Redis key or memory key
        
        Args:
            identifier: IP address or user ID
            endpoint: Optional endpoint name
            
        Returns:
            Key string
        """
        if endpoint:
            return f"rate_limit:{endpoint}:{identifier}"
        return f"rate_limit:{identifier}"
    
    def check_rate_limit(
        self,
        identifier: str,
        per_minute: Optional[int] = None,
        per_hour: Optional[int] = None,
        endpoint: Optional[str] = None
    ) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Check rate limit for identifier
        
        Args:
            identifier: IP address or user ID
            per_minute: Optional custom per-minute limit
            per_hour: Optional custom per-hour limit
            endpoint: Optional endpoint name for per-endpoint limiting
            
        Returns:
            Tuple of (is_allowed, error_message, headers_dict)
        """
        if not self.rate_limiting_enabled:
            return True, None, {}
        
        # Get limits
        if per_minute is None:
            per_minute = get_rate_limit_per_minute()
        if per_hour is None:
            per_hour = get_rate_limit_per_hour()
        
        key = self._get_key(identifier, endpoint)
        now = time.time()
        
        if self.use_redis:
            return self._check_redis_rate_limit(key, now, per_minute, per_hour)
        else:
            return self._check_memory_rate_limit(key, now, per_minute, per_hour)
    
    def _check_redis_rate_limit(
        self,
        key: str,
        now: float,
        per_minute: int,
        per_hour: int
    ) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """Check rate limit using Redis"""
        pipe = self.redis_client.pipeline()
        
        # Get current counts
        minute_key = f"{key}:minute"
        hour_key = f"{key}:hour"
        
        pipe.zcard(minute_key)
        pipe.zcard(hour_key)
        pipe.zremrangebyscore(minute_key, 0, now - 60)  # Remove entries older than 1 minute
        pipe.zremrangebyscore(hour_key, 0, now - 3600)  # Remove entries older than 1 hour
        pipe.zadd(minute_key, {str(now): now})
        pipe.zadd(hour_key, {str(now): now})
        pipe.expire(minute_key, 60)
        pipe.expire(hour_key, 3600)
        
        results = pipe.execute()
        minute_count = results[0]
        hour_count = results[1]
        
        # Check limits
        if minute_count >= per_minute:
            remaining = max(0, per_minute - minute_count)
            reset_time = int(now) + 60
            headers = {
                'X-RateLimit-Limit': str(per_minute),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
            return False, f"Rate limit exceeded: {per_minute} requests per minute", headers
        
        if hour_count >= per_hour:
            remaining = max(0, per_hour - hour_count)
            reset_time = int(now) + 3600
            headers = {
                'X-RateLimit-Limit': str(per_hour),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
            return False, f"Rate limit exceeded: {per_hour} requests per hour", headers
        
        # Allowed
        remaining_minute = max(0, per_minute - minute_count - 1)
        remaining_hour = max(0, per_hour - hour_count - 1)
        reset_time = int(now) + 60
        
        headers = {
            'X-RateLimit-Limit': str(per_minute),
            'X-RateLimit-Remaining': str(remaining_minute),
            'X-RateLimit-Reset': str(reset_time)
        }
        
        return True, None, headers
    
    def _check_memory_rate_limit(
        self,
        key: str,
        now: float,
        per_minute: int,
        per_hour: int
    ) -> tuple[bool, Optional[str], Dict[str, Any]]:
        """Check rate limit using memory"""
        if key not in self.memory_storage:
            self.memory_storage[key] = []
        
        # Clean old entries
        minute_ago = now - 60
        hour_ago = now - 3600
        
        self.memory_storage[key] = [
            ts for ts in self.memory_storage[key]
            if ts > hour_ago
        ]
        
        # Count requests
        recent_minute = [ts for ts in self.memory_storage[key] if ts > minute_ago]
        recent_hour = self.memory_storage[key]
        
        # Check limits
        if len(recent_minute) >= per_minute:
            remaining = max(0, per_minute - len(recent_minute))
            reset_time = int(now) + 60
            headers = {
                'X-RateLimit-Limit': str(per_minute),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
            return False, f"Rate limit exceeded: {per_minute} requests per minute", headers
        
        if len(recent_hour) >= per_hour:
            remaining = max(0, per_hour - len(recent_hour))
            reset_time = int(now) + 3600
            headers = {
                'X-RateLimit-Limit': str(per_hour),
                'X-RateLimit-Remaining': str(remaining),
                'X-RateLimit-Reset': str(reset_time)
            }
            return False, f"Rate limit exceeded: {per_hour} requests per hour", headers
        
        # Add current request
        self.memory_storage[key].append(now)
        
        # Allowed
        remaining_minute = max(0, per_minute - len(recent_minute) - 1)
        remaining_hour = max(0, per_hour - len(recent_hour) - 1)
        reset_time = int(now) + 60
        
        headers = {
            'X-RateLimit-Limit': str(per_minute),
            'X-RateLimit-Remaining': str(remaining_minute),
            'X-RateLimit-Reset': str(reset_time)
        }
        
        return True, None, headers


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(per_minute: Optional[int] = None, per_hour: Optional[int] = None, endpoint: Optional[str] = None):
    """
    Decorator for rate limiting Flask endpoints
    
    Args:
        per_minute: Optional custom per-minute limit
        per_hour: Optional custom per-hour limit
        endpoint: Optional endpoint name
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            
            # Get identifier (IP address or user ID)
            identifier = request.remote_addr
            if request.is_json and 'user_id' in request.json:
                identifier = f"user:{request.json['user_id']}"
            
            # Check rate limit
            allowed, error, headers = rate_limiter.check_rate_limit(
                identifier,
                per_minute=per_minute,
                per_hour=per_hour,
                endpoint=endpoint or f.__name__
            )
            
            if not allowed:
                response = jsonify({'error': error})
                for key, value in headers.items():
                    response.headers[key] = str(value)
                return response, 429
            
            # Call original function
            result = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(result, tuple) and len(result) == 2:
                response, status = result
                if hasattr(response, 'headers'):
                    for key, value in headers.items():
                        response.headers[key] = str(value)
                return response, status
            elif hasattr(result, 'headers'):
                for key, value in headers.items():
                    result.headers[key] = str(value)
            
            return result
        
        return decorated_function
    return decorator

