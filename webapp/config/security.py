#!/usr/bin/env python3
"""
Security Configuration System
Environment-based security flags for dev/prod modes
All security features can be toggled based on environment
"""

import os
from typing import Dict, Any

# Environment detection
DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
PROD_MODE = os.getenv('PROD_MODE', 'false').lower() == 'true'

# Default to dev mode if neither is explicitly set
if not PROD_MODE:
    DEV_MODE = True

# Security configuration based on environment
if DEV_MODE:
    # Development mode: Relaxed security for easier development
    SECURITY_CONFIG: Dict[str, Any] = {
        "auth_required": False,
        "rate_limiting_enabled": True,  # Keep basic rate limiting even in dev
        "csrf_protection": False,
        "encryption_enabled": False,
        "session_secure": False,
        "password_min_length": 0,  # No password requirement in dev
        "two_factor_required": False,
        "rate_limit_per_minute": 1000,  # Higher limit in dev
        "rate_limit_per_hour": 10000,
        "strict_input_validation": False,
        "require_https": False,
        "security_headers_enabled": False,
        "bot_detection_strict": False,
        "content_moderation_strict": False
    }
elif PROD_MODE:
    # Production mode: Full security enabled
    SECURITY_CONFIG: Dict[str, Any] = {
        "auth_required": True,
        "rate_limiting_enabled": True,
        "csrf_protection": True,
        "encryption_enabled": True,
        "session_secure": True,
        "password_min_length": 12,
        "two_factor_required": False,  # Optional, can enable later
        "rate_limit_per_minute": 100,
        "rate_limit_per_hour": 1000,
        "strict_input_validation": True,
        "require_https": True,
        "security_headers_enabled": True,
        "bot_detection_strict": True,
        "content_moderation_strict": True
    }
else:
    # Fallback to dev mode
    SECURITY_CONFIG = {
        "auth_required": False,
        "rate_limiting_enabled": True,
        "csrf_protection": False,
        "encryption_enabled": False,
        "session_secure": False,
        "password_min_length": 0,
        "two_factor_required": False,
        "rate_limit_per_minute": 1000,
        "rate_limit_per_hour": 10000,
        "strict_input_validation": False,
        "require_https": False,
        "security_headers_enabled": False,
        "bot_detection_strict": False,
        "content_moderation_strict": False
    }


def get_security_config() -> Dict[str, Any]:
    """Get current security configuration"""
    return SECURITY_CONFIG.copy()


def is_auth_required() -> bool:
    """Check if authentication is required"""
    return SECURITY_CONFIG.get("auth_required", False)


def is_csrf_enabled() -> bool:
    """Check if CSRF protection is enabled"""
    return SECURITY_CONFIG.get("csrf_protection", False)


def is_rate_limiting_enabled() -> bool:
    """Check if rate limiting is enabled"""
    return SECURITY_CONFIG.get("rate_limiting_enabled", True)


def get_rate_limit_per_minute() -> int:
    """Get rate limit per minute"""
    return SECURITY_CONFIG.get("rate_limit_per_minute", 100)


def get_rate_limit_per_hour() -> int:
    """Get rate limit per hour"""
    return SECURITY_CONFIG.get("rate_limit_per_hour", 1000)


def is_strict_validation() -> bool:
    """Check if strict input validation is enabled"""
    return SECURITY_CONFIG.get("strict_input_validation", False)


def is_https_required() -> bool:
    """Check if HTTPS is required"""
    return SECURITY_CONFIG.get("require_https", False)


def is_security_headers_enabled() -> bool:
    """Check if security headers are enabled"""
    return SECURITY_CONFIG.get("security_headers_enabled", False)


def get_password_min_length() -> int:
    """Get minimum password length"""
    return SECURITY_CONFIG.get("password_min_length", 0)


def is_bot_detection_strict() -> bool:
    """Check if bot detection should be strict"""
    return SECURITY_CONFIG.get("bot_detection_strict", False)


def is_content_moderation_strict() -> bool:
    """Check if content moderation should be strict"""
    return SECURITY_CONFIG.get("content_moderation_strict", False)


# Export current mode for logging/debugging
CURRENT_MODE = "DEV" if DEV_MODE else ("PROD" if PROD_MODE else "DEV")

