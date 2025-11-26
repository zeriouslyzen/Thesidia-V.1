#!/usr/bin/env python3
"""
Social Media Database Schema
Defines data models and schema for posts, profiles, social graph
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import uuid


class PostSchema:
    """Post data model and validation"""
    
    @staticmethod
    def create_post(
        author_id: str,
        content: str,
        media: Optional[list] = None,
        tags: Optional[list] = None,
        visibility: str = "public"
    ) -> Dict[str, Any]:
        """
        Create a new post data structure
        
        Args:
            author_id: User ID of post author
            content: Post text content
            media: Optional list of media items
            tags: Optional list of tags
            visibility: Post visibility (public, followers, private)
            
        Returns:
            Post data dictionary
        """
        post_id = f"post_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        return {
            "id": post_id,
            "author_id": author_id,
            "content": content,
            "media": media or [],
            "created_at": now,
            "updated_at": now,
            "interactions": {
                "likes": 0,
                "comments": 0,
                "reposts": 0,
                "views": 0
            },
            "ai_score": 0.0,  # Will be calculated
            "tags": tags or [],
            "visibility": visibility,
            "moderation_status": "pending"  # Will be set after moderation
        }
    
    @staticmethod
    def validate_post(post: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate post data structure
        
        Args:
            post: Post data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["id", "author_id", "content", "created_at"]
        for field in required_fields:
            if field not in post:
                return False, f"Missing required field: {field}"
        
        if not post.get("content") or len(post["content"].strip()) == 0:
            return False, "Post content cannot be empty"
        
        if len(post["content"]) > 10000:
            return False, "Post content exceeds maximum length (10000 characters)"
        
        if post.get("visibility") not in ["public", "followers", "private"]:
            return False, "Invalid visibility setting"
        
        return True, None


class ProfileSchema:
    """User profile data model"""
    
    @staticmethod
    def create_profile(user_id: str, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user profile
        
        Args:
            user_id: User ID
            username: Optional username
            
        Returns:
            Profile data dictionary
        """
        now = datetime.now().isoformat()
        
        return {
            "user_id": user_id,
            "username": username or f"user_{user_id[:8]}",
            "display_name": "",
            "bio": "",
            "avatar_url": "",
            "banner_url": "",
            "location": "",
            "website": "",
            "stats": {
                "posts": 0,
                "followers": 0,
                "following": 0
            },
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def validate_profile(profile: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate profile data structure
        
        Args:
            profile: Profile data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "user_id" not in profile:
            return False, "Missing required field: user_id"
        
        if "username" in profile and profile["username"]:
            username = profile["username"].lstrip("@")
            if len(username) < 3:
                return False, "Username must be at least 3 characters"
            if len(username) > 30:
                return False, "Username must be no more than 30 characters"
        
        if "bio" in profile and len(profile.get("bio", "")) > 500:
            return False, "Bio exceeds maximum length (500 characters)"
        
        return True, None


class SocialGraphSchema:
    """Social graph data model (following, followers, blocking, muting)"""
    
    @staticmethod
    def create_social_graph(user_id: str) -> Dict[str, Any]:
        """
        Create a new social graph
        
        Args:
            user_id: User ID
            
        Returns:
            Social graph data dictionary
        """
        return {
            "user_id": user_id,
            "following": [],
            "followers": [],
            "blocked": [],
            "muted": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def validate_social_graph(graph: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate social graph data structure
        
        Args:
            graph: Social graph data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "user_id" not in graph:
            return False, "Missing required field: user_id"
        
        required_lists = ["following", "followers", "blocked", "muted"]
        for field in required_lists:
            if field not in graph:
                return False, f"Missing required field: {field}"
            if not isinstance(graph[field], list):
                return False, f"Field {field} must be a list"
        
        return True, None


class SettingsSchema:
    """User settings data model"""
    
    @staticmethod
    def create_default_settings(user_id: str) -> Dict[str, Any]:
        """
        Create default settings for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Settings data dictionary
        """
        return {
            "user_id": user_id,
            "account": {
                "username": "",
                "email": "",
                "phone_number": "",
                "display_name": "",
                "bio": "",
                "avatar_url": "",
                "banner_url": "",
                "location": "",
                "website": ""
            },
            "privacy": {
                "profile_visibility": "public",
                "private_account": False,
                "dm_enabled": True,
                "show_online_status": True,
                "blocked_users": [],
                "muted_users": []
            },
            "notifications": {
                "email_enabled": False,
                "push_enabled": True,
                "mentions": True,
                "follows": True,
                "likes": True,
                "comments": True,
                "reposts": False
            },
            "content": {
                "auto_play_videos": False,
                "content_filter": "moderate",
                "language": "en",
                "timezone": "UTC"
            },
            "security": {
                "two_factor_enabled": False,
                "login_notifications": True,
                "password_hash": "",
                "login_history": []
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def validate_settings(settings: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate settings data structure
        
        Args:
            settings: Settings data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if "user_id" not in settings:
            return False, "Missing required field: user_id"
        
        required_sections = ["account", "privacy", "notifications", "content"]
        for section in required_sections:
            if section not in settings:
                return False, f"Missing required section: {section}"
        
        return True, None

