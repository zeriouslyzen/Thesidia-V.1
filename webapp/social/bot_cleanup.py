#!/usr/bin/env python3
"""
Bot Post Cleanup System
Deletes old bot posts to save memory
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.post_manager import PostManager
from webapp.social.interaction_manager import InteractionManager


class BotCleanup:
    """
    Cleans up old bot posts to manage memory
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".")
        self.post_manager = PostManager(base_dir=base_dir)
        self.interaction_manager = InteractionManager(base_dir=base_dir)
        self.bots_dir = self.base_dir / "data" / "bots"
        
        # Cleanup settings
        self.post_retention_days = 30  # Keep posts for 30 days
        self.max_posts_per_bot = 50  # Maximum posts per bot
        self.max_total_posts = 500  # Maximum total bot posts
    
    def cleanup_old_posts(self, retention_days: int = None) -> Dict[str, Any]:
        """
        Delete posts older than retention period
        
        Args:
            retention_days: Days to keep posts (default: self.post_retention_days)
            
        Returns:
            Cleanup summary
        """
        if retention_days is None:
            retention_days = self.post_retention_days
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        deleted_posts = []
        
        # Get all bot IDs
        bot_ids = []
        if self.bots_dir.exists():
            for bot_file in self.bots_dir.glob("bot_*.json"):
                try:
                    with open(bot_file, 'r', encoding='utf-8') as f:
                        bot_data = json.load(f)
                        bot_ids.append(bot_data.get('bot_id'))
                except Exception:
                    continue
        
        # Check all posts
        posts_dir = self.post_manager.posts_dir
        if not posts_dir.exists():
            return {"deleted": 0, "posts": []}
        
        for post_file in posts_dir.glob("*.json"):
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    post = json.load(f)
                
                author_id = post.get('author_id', '')
                
                # Only delete bot posts
                if not author_id.startswith('bot_'):
                    continue
                
                # Check if post is old
                created_at = post.get('created_at')
                if created_at:
                    try:
                        post_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if post_date < cutoff_date:
                            # Delete post
                            post_file.unlink()
                            
                            # Delete interactions
                            interaction_file = self.interaction_manager.interactions_dir / f"{post['id']}_interactions.json"
                            if interaction_file.exists():
                                interaction_file.unlink()
                            
                            deleted_count += 1
                            deleted_posts.append(post['id'])
                    except Exception:
                        continue
            except Exception:
                continue
        
        return {
            "deleted": deleted_count,
            "posts": deleted_posts,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    def cleanup_excess_posts(self) -> Dict[str, Any]:
        """
        Delete excess posts to maintain limits
        
        Returns:
            Cleanup summary
        """
        # Get all bot IDs
        bot_ids = []
        if self.bots_dir.exists():
            for bot_file in self.bots_dir.glob("bot_*.json"):
                try:
                    with open(bot_file, 'r', encoding='utf-8') as f:
                        bot_data = json.load(f)
                        bot_ids.append(bot_data.get('bot_id'))
                except Exception:
                    continue
        
        deleted_count = 0
        deleted_posts = []
        
        # Clean up per-bot limits
        for bot_id in bot_ids:
            posts = self.post_manager.get_posts_by_user(bot_id, limit=1000)
            
            if len(posts) > self.max_posts_per_bot:
                # Sort by date (oldest first)
                posts.sort(key=lambda p: p.get('created_at', ''))
                
                # Delete oldest posts
                excess = len(posts) - self.max_posts_per_bot
                for post in posts[:excess]:
                    try:
                        post_file = self.post_manager.posts_dir / f"{post['id']}.json"
                        if post_file.exists():
                            post_file.unlink()
                            
                            # Delete interactions
                            interaction_file = self.interaction_manager.interactions_dir / f"{post['id']}_interactions.json"
                            if interaction_file.exists():
                                interaction_file.unlink()
                            
                            deleted_count += 1
                            deleted_posts.append(post['id'])
                    except Exception:
                        continue
        
        # Clean up total limit
        all_posts = []
        posts_dir = self.post_manager.posts_dir
        if posts_dir.exists():
            for post_file in posts_dir.glob("*.json"):
                try:
                    with open(post_file, 'r', encoding='utf-8') as f:
                        post = json.load(f)
                        if post.get('author_id', '').startswith('bot_'):
                            all_posts.append(post)
                except Exception:
                    continue
        
        if len(all_posts) > self.max_total_posts:
            # Sort by date (oldest first)
            all_posts.sort(key=lambda p: p.get('created_at', ''))
            
            # Delete oldest posts
            excess = len(all_posts) - self.max_total_posts
            for post in all_posts[:excess]:
                try:
                    post_file = self.post_manager.posts_dir / f"{post['id']}.json"
                    if post_file.exists():
                        post_file.unlink()
                        
                        # Delete interactions
                        interaction_file = self.interaction_manager.interactions_dir / f"{post['id']}_interactions.json"
                        if interaction_file.exists():
                            interaction_file.unlink()
                        
                        deleted_count += 1
                        deleted_posts.append(post['id'])
                except Exception:
                    continue
        
        return {
            "deleted": deleted_count,
            "posts": deleted_posts,
            "reason": "excess_posts"
        }
    
    def cleanup_all(self) -> Dict[str, Any]:
        """
        Run all cleanup operations
        
        Returns:
            Combined cleanup summary
        """
        old_posts = self.cleanup_old_posts()
        excess_posts = self.cleanup_excess_posts()
        
        return {
            "old_posts_deleted": old_posts["deleted"],
            "excess_posts_deleted": excess_posts["deleted"],
            "total_deleted": old_posts["deleted"] + excess_posts["deleted"],
            "cutoff_date": old_posts.get("cutoff_date")
        }

