#!/usr/bin/env python3
"""
Security Tests
"""

import unittest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'webapp'))

from webapp.config.security import (
    get_security_config,
    is_auth_required,
    is_csrf_enabled,
    is_rate_limiting_enabled,
    DEV_MODE,
    PROD_MODE
)
from webapp.middleware.security import security_middleware


class TestSecurity(unittest.TestCase):
    """Test Security Configuration"""
    
    def setUp(self):
        """Set up test environment"""
        # Ensure dev mode
        os.environ['DEV_MODE'] = 'true'
        os.environ['PROD_MODE'] = 'false'
    
    def test_dev_mode_default(self):
        """Test that dev mode is default"""
        config = get_security_config()
        self.assertFalse(config.get('auth_required', True))
        self.assertFalse(config.get('csrf_protection', True))
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        dirty_input = "<script>alert('xss')</script>Hello"
        clean = security_middleware.sanitize_input(dirty_input)
        self.assertNotIn('<script>', clean)
        self.assertIn('Hello', clean)
    
    def test_username_validation(self):
        """Test username validation"""
        is_valid, error = security_middleware.validate_username("valid_username")
        self.assertTrue(is_valid)
        
        is_valid, error = security_middleware.validate_username("ab")
        self.assertFalse(is_valid)
        
        is_valid, error = security_middleware.validate_username("admin")
        self.assertFalse(is_valid)  # Reserved username


if __name__ == '__main__':
    unittest.main()

