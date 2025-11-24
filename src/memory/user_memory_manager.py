#!/usr/bin/env python3
"""
User Memory Manager - Combines UserManager and MemoryManager
Provides per-user memory isolation with simple session-based identification
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .user_manager import UserManager
from .memory_manager import MemoryManager


class UserMemoryManager:
    """Manages memory per user with session-based identification"""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize user memory manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.user_manager = UserManager(base_dir=base_dir)
        
        # Per-user memory managers (cached)
        self.user_memory_managers: Dict[str, MemoryManager] = {}
    
    def get_memory_manager(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> tuple[MemoryManager, Dict[str, Any]]:
        """
        Get or create memory manager for a user
        
        Args:
            user_id: Optional user ID
            session_id: Optional session ID
        
        Returns:
            Tuple of (MemoryManager, user_data)
        """
        # Get or create user
        user_data = self.user_manager.get_or_create_user(user_id=user_id, session_id=session_id)
        user_id = user_data["user_id"]
        
        # Get or create memory manager for this user
        if user_id not in self.user_memory_managers:
            self.user_memory_managers[user_id] = MemoryManager(
                base_dir=self.base_dir,
                user_dir=user_data["user_dir"]
            )
        
        return self.user_memory_managers[user_id], user_data
    
    def store_interaction(self, user_input: str, assistant_output: str, 
                         user_id: Optional[str] = None, session_id: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """
        Store interaction for a user
        
        Args:
            user_input: User's message
            assistant_output: Assistant's response
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Optional metadata
        """
        memory_manager, user_data = self.get_memory_manager(user_id=user_id, session_id=session_id)
        
        # Add user info to metadata
        if metadata is None:
            metadata = {}
        metadata["user_id"] = user_data["user_id"]
        metadata["session_id"] = user_data["session_id"]
        
        memory_manager.store_interaction(user_input, assistant_output, metadata)
    
    def retrieve_context(self, query: str, user_id: Optional[str] = None, 
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve memory context for a user
        
        Args:
            query: Query string
            user_id: Optional user ID
            session_id: Optional session ID
        
        Returns:
            Dictionary with memory context
        """
        memory_manager, user_data = self.get_memory_manager(user_id=user_id, session_id=session_id)
        context = memory_manager.retrieve_context(query)
        context["user_id"] = user_data["user_id"]
        context["session_id"] = user_data["session_id"]
        return context
    
    def export_user_data(self, user_id: Optional[str] = None, 
                        session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all user data for download
        
        Args:
            user_id: Optional user ID
            session_id: Optional session ID
        
        Returns:
            Dictionary with all user data
        """
        memory_manager, user_data = self.get_memory_manager(user_id=user_id, session_id=session_id)
        
        # Get user export from user manager
        user_export = self.user_manager.export_user_data(user_data["user_id"])
        
        # Add conversation data
        user_export["conversation_data"] = memory_manager.export_conversation_data()
        
        return user_export
    
    def get_user_data(self, user_id: Optional[str] = None, 
                     session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user data (for frontend)
        
        Args:
            user_id: Optional user ID
            session_id: Optional session ID
        
        Returns:
            Dictionary with user data (user_id, session_id, etc.)
        """
        _, user_data = self.get_memory_manager(user_id=user_id, session_id=session_id)
        return user_data

