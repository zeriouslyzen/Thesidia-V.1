#!/usr/bin/env python3
"""
Session Manager
Secure session management with expiration and rotation
Configured but disabled in dev mode
"""

import secrets
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from config.security import is_auth_required, SECURITY_CONFIG


class SessionManager:
    """
    Session Manager
    Manages user sessions with expiration, rotation, and concurrent session limits
    In dev mode: Uses simple session IDs
    In prod mode: Full session management with security
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize session manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.auth_required = is_auth_required()
        self.session_secure = SECURITY_CONFIG.get("session_secure", False)
        
        # Session storage
        self.sessions_file = self.base_dir / "data" / "auth" / "sessions.json"
        # Try to create directory, but handle read-only filesystem (e.g., Vercel)
        try:
            self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot create data directory (read-only filesystem): {e}")
            print("Using in-memory session storage (not persistent)")
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._load_sessions()
        
        # Session configuration
        self.session_expiration_hours = 24 * 7  # 7 days default
        self.max_concurrent_sessions = 5  # Max 5 concurrent sessions per user
    
    def _load_sessions(self):
        """Load sessions from disk"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
            except Exception:
                self.sessions = {}
        else:
            self.sessions = {}
        
        # Clean expired sessions
        self._clean_expired_sessions()
    
    def _save_sessions(self):
        """Save sessions to disk"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save sessions: {e}")
    
    def _clean_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = []
        
        for session_id, session_data in self.sessions.items():
            expires_at = datetime.fromisoformat(session_data.get("expires_at", "1970-01-01T00:00:00"))
            if expires_at < now:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
        
        if expired:
            self._save_sessions()
    
    def create_session(self, user_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """
        Create a new session
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Session ID
        """
        # In dev mode, use simple session IDs
        if not self.auth_required:
            return secrets.token_urlsafe(32)
        
        # Check concurrent session limit
        user_sessions = [s for s in self.sessions.values() if s.get("user_id") == user_id]
        if len(user_sessions) >= self.max_concurrent_sessions:
            # Remove oldest session
            oldest = min(user_sessions, key=lambda s: datetime.fromisoformat(s.get("created_at", "1970-01-01T00:00:00")))
            for sid, data in self.sessions.items():
                if data == oldest:
                    del self.sessions[sid]
                    break
        
        # Create new session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self.session_expiration_hours)
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_activity": datetime.now().isoformat(),
            "ip_address": ip_address,
            "user_agent": user_agent,
            "rotated": False
        }
        
        self._save_sessions()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data dictionary or None
        """
        # In dev mode, always return valid session
        if not self.auth_required:
            return {"session_id": session_id, "valid": True}
        
        if session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        # Check expiration
        expires_at = datetime.fromisoformat(session_data.get("expires_at", "1970-01-01T00:00:00"))
        if expires_at < datetime.now():
            del self.sessions[session_id]
            self._save_sessions()
            return None
        
        # Update last activity
        session_data["last_activity"] = datetime.now().isoformat()
        self._save_sessions()
        
        return session_data
    
    def rotate_session(self, old_session_id: str, user_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Optional[str]:
        """
        Rotate session (create new session, invalidate old)
        
        Args:
            old_session_id: Old session ID
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            New session ID or None
        """
        # In dev mode, just create new session
        if not self.auth_required:
            return secrets.token_urlsafe(32)
        
        # Verify old session
        old_session = self.get_session(old_session_id)
        if not old_session or old_session.get("user_id") != user_id:
            return None
        
        # Create new session
        new_session_id = self.create_session(user_id, ip_address, user_agent)
        
        # Mark old session as rotated
        if old_session_id in self.sessions:
            self.sessions[old_session_id]["rotated"] = True
            self.sessions[old_session_id]["rotated_to"] = new_session_id
            self._save_sessions()
        
        return new_session_id
    
    def invalidate_session(self, session_id: str):
        """
        Invalidate a session
        
        Args:
            session_id: Session ID to invalidate
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
    
    def invalidate_user_sessions(self, user_id: str, keep_current: Optional[str] = None):
        """
        Invalidate all sessions for a user
        
        Args:
            user_id: User ID
            keep_current: Optional session ID to keep active
        """
        to_remove = []
        for session_id, session_data in self.sessions.items():
            if session_data.get("user_id") == user_id:
                if keep_current and session_id == keep_current:
                    continue
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]
        
        if to_remove:
            self._save_sessions()
    
    def get_user_sessions(self, user_id: str) -> list[Dict[str, Any]]:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of session data dictionaries
        """
        user_sessions = []
        for session_data in self.sessions.values():
            if session_data.get("user_id") == user_id:
                # Check if expired
                expires_at = datetime.fromisoformat(session_data.get("expires_at", "1970-01-01T00:00:00"))
                if expires_at >= datetime.now():
                    user_sessions.append(session_data)
        
        return user_sessions
    
    def is_session_valid(self, session_id: str) -> bool:
        """
        Check if session is valid
        
        Args:
            session_id: Session ID
            
        Returns:
            True if valid, False otherwise
        """
        # In dev mode, always valid
        if not self.auth_required:
            return True
        
        session = self.get_session(session_id)
        return session is not None

