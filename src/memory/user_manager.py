#!/usr/bin/env python3
"""
User Manager - Simple user identification without authentication
Uses session IDs for user identification
Supports browser localStorage and local file storage
"""

import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class UserManager:
    """Manages user identification and per-user memory isolation"""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize user manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.users_dir = self.base_dir / "data" / "users"
        self.users_dir.mkdir(parents=True, exist_ok=True)
        
        # Active sessions (in-memory)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_or_create_user(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get or create a user session
        
        Args:
            user_id: Optional user ID (if provided, use it)
            session_id: Optional session ID (if provided, use it)
        
        Returns:
            Dictionary with user_id, session_id, and user_dir
        """
        # If user_id provided, use it
        if user_id:
            user_dir = self.users_dir / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Create or load user info
            user_info = self._load_user_info(user_id)
            
            return {
                "user_id": user_id,
                "session_id": session_id or str(uuid.uuid4()),
                "user_dir": user_dir,
                "created_at": user_info.get("created_at", datetime.now().isoformat()),
                "last_seen": datetime.now().isoformat()
            }
        
        # If session_id provided, try to find existing user
        if session_id:
            # Check active sessions
            if session_id in self.active_sessions:
                user_data = self.active_sessions[session_id]
                user_data["last_seen"] = datetime.now().isoformat()
                return user_data
            
            # Try to find user by session
            user_id = self._find_user_by_session(session_id)
            if user_id:
                user_dir = self.users_dir / user_id
                user_info = self._load_user_info(user_id)
                user_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "user_dir": user_dir,
                    "created_at": user_info.get("created_at", datetime.now().isoformat()),
                    "last_seen": datetime.now().isoformat()
                }
                self.active_sessions[session_id] = user_data
                return user_data
        
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        session_id = session_id or str(uuid.uuid4())
        user_dir = self.users_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        user_info = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
        
        # Save user info
        self._save_user_info(user_id, user_info)
        
        user_data = {
            "user_id": user_id,
            "session_id": session_id,
            "user_dir": user_dir,
            "created_at": user_info["created_at"],
            "last_seen": user_info["last_seen"]
        }
        
        # Store in active sessions
        self.active_sessions[session_id] = user_data
        
        return user_data
    
    def _load_user_info(self, user_id: str) -> Dict[str, Any]:
        """Load user info from disk"""
        user_info_file = self.users_dir / user_id / "user_info.json"
        if user_info_file.exists():
            try:
                with open(user_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat()
        }
    
    def _save_user_info(self, user_id: str, user_info: Dict[str, Any]):
        """Save user info to disk"""
        user_info_file = self.users_dir / user_id / "user_info.json"
        try:
            with open(user_info_file, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save user info: {e}")
    
    def _find_user_by_session(self, session_id: str) -> Optional[str]:
        """Find user ID by session ID (search all users)"""
        if not self.users_dir.exists():
            return None
        
        for user_dir in self.users_dir.iterdir():
            if user_dir.is_dir():
                user_info_file = user_dir / "user_info.json"
                if user_info_file.exists():
                    try:
                        with open(user_info_file, 'r', encoding='utf-8') as f:
                            user_info = json.load(f)
                            if user_info.get("session_id") == session_id:
                                return user_info.get("user_id")
                    except Exception:
                        continue
        
        return None
    
    def get_user_dir(self, user_id: str) -> Path:
        """Get user directory path"""
        return self.users_dir / user_id
    
    def list_users(self) -> list[Dict[str, Any]]:
        """List all users"""
        users = []
        if not self.users_dir.exists():
            return users
        
        for user_dir in self.users_dir.iterdir():
            if user_dir.is_dir():
                user_info = self._load_user_info(user_dir.name)
                users.append(user_info)
        
        return users
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for download
        
        Args:
            user_id: User ID to export
        
        Returns:
            Dictionary with all user data
        """
        user_dir = self.users_dir / user_id
        
        export_data = {
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "user_info": self._load_user_info(user_id),
            "memory": {},
            "conversations": []
        }
        
        # Export memory files
        memory_files = {
            "ephemeral": user_dir / "state" / "ephemeral_context.json",
            "structured": user_dir / "memory" / "structured_memory.json",
            "vector": user_dir / "vectors" / "memory_index.json"
        }
        
        for key, file_path in memory_files.items():
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        export_data["memory"][key] = json.load(f)
                except Exception:
                    pass
        
        # Export conversations (if stored separately)
        conversations_file = user_dir / "conversations.json"
        if conversations_file.exists():
            try:
                with open(conversations_file, 'r', encoding='utf-8') as f:
                    export_data["conversations"] = json.load(f)
            except Exception:
                pass
        
        return export_data

