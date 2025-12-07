#!/usr/bin/env python3
"""
Authentication Manager
JWT token generation/validation, password hashing
Configured but disabled in dev mode
"""

import os
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import json
import sys

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory.user_manager import UserManager
from webapp.config.security import is_auth_required, get_password_min_length

# JWT secret key (in production, should be from environment variable)
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


class AuthManager:
    """
    Authentication Manager
    In dev mode: Bypassed, uses existing UserManager
    In prod mode: Full authentication with JWT tokens and password hashing
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize authentication manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.user_manager = UserManager(base_dir=base_dir)
        self.auth_required = is_auth_required()
        
        # Password storage (in production, should be encrypted)
        self.passwords_file = self.base_dir / "data" / "auth" / "passwords.json"
        # Try to create directory, but handle read-only filesystem (e.g., Vercel)
        try:
            self.passwords_file.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot create data directory (read-only filesystem): {e}")
            print("Using in-memory password storage (not persistent)")
        self._load_passwords()
    
    def _load_passwords(self):
        """Load password hashes from disk"""
        if self.passwords_file.exists():
            try:
                with open(self.passwords_file, 'r', encoding='utf-8') as f:
                    self.passwords = json.load(f)
            except Exception:
                self.passwords = {}
        else:
            self.passwords = {}
    
    def _save_passwords(self):
        """Save password hashes to disk"""
        try:
            with open(self.passwords_file, 'w', encoding='utf-8') as f:
                json.dump(self.passwords, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save passwords: {e}")
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        if not password:
            return ""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed: Hashed password
            
        Returns:
            True if password matches
        """
        if not password or not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        min_length = get_password_min_length()
        
        if min_length == 0:
            # No password requirement in dev mode
            return True, ""
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        # Check for common password patterns
        if password.isdigit():
            return False, "Password must contain letters"
        
        if password.isalpha():
            return False, "Password must contain numbers or special characters"
        
        return True, ""
    
    def register_user(self, username: str, password: str, email: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new user
        
        Args:
            username: Username (without @)
            password: Plain text password
            email: Optional email address
            
        Returns:
            Dictionary with user_id, session_id, and token (if auth enabled)
        """
        # In dev mode, bypass authentication
        if not self.auth_required:
            return self.user_manager.get_or_create_user()
        
        # Validate password
        is_valid, error = self.validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        
        # Check if username already exists
        if self._username_exists(username):
            raise ValueError("Username already exists")
        
        # Create user
        user_data = self.user_manager.get_or_create_user()
        user_id = user_data["user_id"]
        
        # Hash and store password
        hashed = self.hash_password(password)
        self.passwords[user_id] = {
            "username": username,
            "password_hash": hashed,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        self._save_passwords()
        
        # Update user info with username
        user_info = self.user_manager._load_user_info(user_id)
        user_info["username"] = username
        if email:
            user_info["email"] = email
        self.user_manager._save_user_info(user_id, user_info)
        
        # Generate JWT token
        token = self.generate_token(user_id)
        
        return {
            "user_id": user_id,
            "session_id": user_data["session_id"],
            "username": username,
            "token": token
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Dictionary with user_id, session_id, and token, or None if invalid
        """
        # In dev mode, bypass authentication
        if not self.auth_required:
            return self.user_manager.get_or_create_user()
        
        # Find user by username
        user_id = self._find_user_by_username(username)
        if not user_id:
            return None
        
        # Verify password
        if user_id not in self.passwords:
            return None
        
        stored = self.passwords[user_id]
        if not self.verify_password(password, stored["password_hash"]):
            return None
        
        # Get or create user session
        user_data = self.user_manager.get_or_create_user(user_id=user_id)
        
        # Generate JWT token
        token = self.generate_token(user_id)
        
        return {
            "user_id": user_id,
            "session_id": user_data["session_id"],
            "username": username,
            "token": token
        }
    
    def generate_token(self, user_id: str) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        # In dev mode, allow password changes without verification
        if not self.auth_required:
            return True
        
        if user_id not in self.passwords:
            return False
        
        # Verify old password
        stored = self.passwords[user_id]
        if not self.verify_password(old_password, stored["password_hash"]):
            return False
        
        # Validate new password
        is_valid, error = self.validate_password_strength(new_password)
        if not is_valid:
            raise ValueError(error)
        
        # Update password
        self.passwords[user_id]["password_hash"] = self.hash_password(new_password)
        self.passwords[user_id]["password_changed_at"] = datetime.now().isoformat()
        self._save_passwords()
        
        return True
    
    def _username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        for user_id, data in self.passwords.items():
            if data.get("username") == username:
                return True
        return False
    
    def _find_user_by_username(self, username: str) -> Optional[str]:
        """Find user ID by username"""
        for user_id, data in self.passwords.items():
            if data.get("username") == username:
                return user_id
        return None
    
    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from JWT token
        
        Args:
            token: JWT token
            
        Returns:
            User data dictionary or None
        """
        # In dev mode, bypass token verification
        if not self.auth_required:
            return self.user_manager.get_or_create_user()
        
        payload = self.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        return self.user_manager.get_or_create_user(user_id=user_id)
    
    def get_or_create_user(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get or create user (wrapper for UserManager)
        In dev mode: Works as normal
        In prod mode: Requires authentication
        
        Args:
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            User data dictionary
        """
        # In dev mode, use existing UserManager
        if not self.auth_required:
            return self.user_manager.get_or_create_user(user_id=user_id, session_id=session_id)
        
        # In prod mode, require authentication
        # This method should only be called after authentication
        return self.user_manager.get_or_create_user(user_id=user_id, session_id=session_id)

