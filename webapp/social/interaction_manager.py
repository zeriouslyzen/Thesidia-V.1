#!/usr/bin/env python3
"""
Interaction Manager
Likes, comments, reposts, views
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class InteractionManager:
    """
    Interaction Manager
    Manages likes, comments, reposts, and views
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize interaction manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.interactions_dir = self.base_dir / "data" / "social" / "interactions"
        self.interactions_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize interest tracker for AI-powered recommendations
        if INTEREST_TRACKER_AVAILABLE:
            try:
                self.interest_tracker = UserInterestTracker(base_dir=base_dir)
            except Exception:
                self.interest_tracker = None
        else:
            self.interest_tracker = None
    
    def _get_interaction_file(self, post_id: str) -> Path:
        """Get interaction file path for post"""
        return self.interactions_dir / f"{post_id}_interactions.json"
    
    def _load_interactions(self, post_id: str) -> Dict[str, Any]:
        """Load interactions for a post"""
        interaction_file = self._get_interaction_file(post_id)
        
        if interaction_file.exists():
            try:
                with open(interaction_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "post_id": post_id,
            "likes": [],
            "comments": [],
            "reposts": [],
            "views": []
        }
    
    def _save_interactions(self, post_id: str, interactions: Dict[str, Any]):
        """Save interactions for a post"""
        interaction_file = self._get_interaction_file(post_id)
        interactions['updated_at'] = datetime.now().isoformat()
        
        with open(interaction_file, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, indent=2, ensure_ascii=False)
    
    def like_post(self, post_id: str, user_id: str) -> bool:
        """
        Like a post
        
        Args:
            post_id: Post ID
            user_id: User ID liking the post
            
        Returns:
            True if liked, False if unliked
        """
        interactions = self._load_interactions(post_id)
        
        if user_id in interactions['likes']:
            # Unlike
            interactions['likes'].remove(user_id)
            self._save_interactions(post_id, interactions)
            return False
        else:
            # Like
            interactions['likes'].append(user_id)
            self._save_interactions(post_id, interactions)
            return True
    
    def comment_post(self, post_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """
        Comment on a post
        
        Args:
            post_id: Post ID
            user_id: User ID commenting
            content: Comment content
            
        Returns:
            Comment data dictionary
        """
        interactions = self._load_interactions(post_id)
        
        comment = {
            "id": f"comment_{datetime.now().timestamp()}",
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        
        interactions['comments'].append(comment)
        self._save_interactions(post_id, interactions)
        
        return comment
    
    def repost(self, post_id: str, user_id: str) -> bool:
        """
        Repost a post
        
        Args:
            post_id: Post ID
            user_id: User ID reposting
            
        Returns:
            True if reposted, False if unreposted
        """
        interactions = self._load_interactions(post_id)
        
        if user_id in interactions['reposts']:
            # Unrepost
            interactions['reposts'].remove(user_id)
            self._save_interactions(post_id, interactions)
            return False
        else:
            # Repost
            interactions['reposts'].append(user_id)
            self._save_interactions(post_id, interactions)
            return True
    
    def view_post(self, post_id: str, user_id: Optional[str] = None):
        """
        Record a post view
        
        Args:
            post_id: Post ID
            user_id: Optional user ID viewing
        """
        interactions = self._load_interactions(post_id)
        
        view = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        interactions['views'].append(view)
        self._save_interactions(post_id, interactions)
    
    def get_interactions(self, post_id: str) -> Dict[str, Any]:
        """
        Get all interactions for a post
        
        Args:
            post_id: Post ID
            
        Returns:
            Interactions dictionary with counts
        """
        interactions = self._load_interactions(post_id)
        
        return {
            "likes": len(interactions['likes']),
            "comments": len(interactions['comments']),
            "reposts": len(interactions['reposts']),
            "views": len(interactions['views']),
            "liked_by": interactions['likes'],
            "comments_list": interactions['comments'],
            "reposted_by": interactions['reposts']
        }
    
    def has_liked(self, post_id: str, user_id: str) -> bool:
        """Check if user has liked post"""
        interactions = self._load_interactions(post_id)
        return user_id in interactions['likes']
    
    def has_reposted(self, post_id: str, user_id: str) -> bool:
        """Check if user has reposted"""
        interactions = self._load_interactions(post_id)
        return user_id in interactions['reposts']

