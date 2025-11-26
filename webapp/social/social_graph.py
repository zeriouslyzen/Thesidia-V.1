#!/usr/bin/env python3
"""
Social Graph Manager
Follow/unfollow, blocking, muting functionality
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.schema import SocialGraphSchema


class SocialGraph:
    """
    Social Graph Manager
    Manages following, followers, blocking, and muting
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize social graph manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.users_dir = self.base_dir / "data" / "users"
        self.schema = SocialGraphSchema()
    
    def get_social_graph(self, user_id: str) -> Dict[str, Any]:
        """
        Get social graph for user
        
        Args:
            user_id: User ID
            
        Returns:
            Social graph data dictionary
        """
        social_file = self.users_dir / user_id / "social.json"
        
        if social_file.exists():
            try:
                with open(social_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Create new social graph
        graph = self.schema.create_social_graph(user_id)
        self.save_social_graph(user_id, graph)
        return graph
    
    def save_social_graph(self, user_id: str, graph: Dict[str, Any]):
        """Save social graph to disk"""
        social_file = self.users_dir / user_id / "social.json"
        social_file.parent.mkdir(parents=True, exist_ok=True)
        
        graph['updated_at'] = datetime.now().isoformat()
        
        with open(social_file, 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)
    
    def follow_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Follow a user
        
        Args:
            user_id: User ID of follower
            target_user_id: User ID to follow
            
        Returns:
            True if successful
        """
        if user_id == target_user_id:
            return False
        
        # Get user's social graph
        user_graph = self.get_social_graph(user_id)
        if target_user_id in user_graph['following']:
            return True  # Already following
        
        user_graph['following'].append(target_user_id)
        self.save_social_graph(user_id, user_graph)
        
        # Update target user's followers
        target_graph = self.get_social_graph(target_user_id)
        if user_id not in target_graph['followers']:
            target_graph['followers'].append(user_id)
            self.save_social_graph(target_user_id, target_graph)
        
        return True
    
    def unfollow_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Unfollow a user
        
        Args:
            user_id: User ID of follower
            target_user_id: User ID to unfollow
            
        Returns:
            True if successful
        """
        # Get user's social graph
        user_graph = self.get_social_graph(user_id)
        if target_user_id in user_graph['following']:
            user_graph['following'].remove(target_user_id)
            self.save_social_graph(user_id, user_graph)
        
        # Update target user's followers
        target_graph = self.get_social_graph(target_user_id)
        if user_id in target_graph['followers']:
            target_graph['followers'].remove(user_id)
            self.save_social_graph(target_user_id, target_graph)
        
        return True
    
    def block_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Block a user
        
        Args:
            user_id: User ID blocking
            target_user_id: User ID to block
            
        Returns:
            True if successful
        """
        if user_id == target_user_id:
            return False
        
        # Unfollow if following
        self.unfollow_user(user_id, target_user_id)
        
        # Add to blocked list
        user_graph = self.get_social_graph(user_id)
        if target_user_id not in user_graph['blocked']:
            user_graph['blocked'].append(target_user_id)
            self.save_social_graph(user_id, user_graph)
        
        return True
    
    def unblock_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Unblock a user
        
        Args:
            user_id: User ID unblocking
            target_user_id: User ID to unblock
            
        Returns:
            True if successful
        """
        user_graph = self.get_social_graph(user_id)
        if target_user_id in user_graph['blocked']:
            user_graph['blocked'].remove(target_user_id)
            self.save_social_graph(user_id, user_graph)
        
        return True
    
    def mute_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Mute a user
        
        Args:
            user_id: User ID muting
            target_user_id: User ID to mute
            
        Returns:
            True if successful
        """
        user_graph = self.get_social_graph(user_id)
        if target_user_id not in user_graph['muted']:
            user_graph['muted'].append(target_user_id)
            self.save_social_graph(user_id, user_graph)
        
        return True
    
    def unmute_user(self, user_id: str, target_user_id: str) -> bool:
        """
        Unmute a user
        
        Args:
            user_id: User ID unmuting
            target_user_id: User ID to unmute
            
        Returns:
            True if successful
        """
        user_graph = self.get_social_graph(user_id)
        if target_user_id in user_graph['muted']:
            user_graph['muted'].remove(target_user_id)
            self.save_social_graph(user_id, user_graph)
        
        return True
    
    def get_followers(self, user_id: str) -> List[str]:
        """Get list of follower user IDs"""
        graph = self.get_social_graph(user_id)
        return graph.get('followers', [])
    
    def get_following(self, user_id: str) -> List[str]:
        """Get list of following user IDs"""
        graph = self.get_social_graph(user_id)
        return graph.get('following', [])
    
    def is_following(self, user_id: str, target_user_id: str) -> bool:
        """Check if user is following target"""
        graph = self.get_social_graph(user_id)
        return target_user_id in graph.get('following', [])
    
    def is_blocked(self, user_id: str, target_user_id: str) -> bool:
        """Check if user has blocked target"""
        graph = self.get_social_graph(user_id)
        return target_user_id in graph.get('blocked', [])
    
    def is_muted(self, user_id: str, target_user_id: str) -> bool:
        """Check if user has muted target"""
        graph = self.get_social_graph(user_id)
        return target_user_id in graph.get('muted', [])

