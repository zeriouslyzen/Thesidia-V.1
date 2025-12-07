#!/usr/bin/env python3
"""
Post Manager
Create, update, delete posts with content sanitization and media handling
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.schema import PostSchema
from webapp.middleware.security import security_middleware


class PostManager:
    """
    Post Manager
    Manages posts with content sanitization and media handling
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize post manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.posts_dir = self.base_dir / "data" / "social" / "posts"
        # Try to create directory, but handle read-only filesystem (e.g., Vercel)
        try:
            self.posts_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot create posts directory (read-only filesystem): {e}")
            print("Using in-memory post storage (not persistent)")
        self.schema = PostSchema()
    
    def create_post(
        self,
        author_id: str,
        content: str,
        media: Optional[list] = None,
        tags: Optional[list] = None,
        visibility: str = "public"
    ) -> Dict[str, Any]:
        """
        Create a new post
        
        Args:
            author_id: User ID of post author
            content: Post text content
            media: Optional list of media items
            tags: Optional list of tags
            visibility: Post visibility (public, followers, private)
            
        Returns:
            Post data dictionary
        """
        # Sanitize content
        content = security_middleware.sanitize_input(content)
        
        # Validate content length
        is_valid, error = security_middleware.validate_input_length(content, max_length=10000)
        if not is_valid:
            raise ValueError(error)
        
        # Create post
        post = self.schema.create_post(author_id, content, media, tags, visibility)
        
        # Save post
        post_file = self.posts_dir / f"{post['id']}.json"
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        
        # Update indexes
        self._update_indexes(post)
        
        return post
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get post by ID
        
        Args:
            post_id: Post ID
            
        Returns:
            Post data dictionary or None
        """
        post_file = self.posts_dir / f"{post_id}.json"
        
        if not post_file.exists():
            return None
        
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def update_post(self, post_id: str, author_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a post
        
        Args:
            post_id: Post ID
            author_id: User ID (must be post author)
            updates: Dictionary of fields to update
            
        Returns:
            Updated post data dictionary or None
        """
        post = self.get_post(post_id)
        if not post:
            return None
        
        # Verify author
        if post.get('author_id') != author_id:
            raise PermissionError("Only post author can update post")
        
        # Sanitize content if updating
        if 'content' in updates:
            updates['content'] = security_middleware.sanitize_input(updates['content'])
            is_valid, error = security_middleware.validate_input_length(updates['content'], max_length=10000)
            if not is_valid:
                raise ValueError(error)
        
        # Update post
        post.update(updates)
        post['updated_at'] = datetime.now().isoformat()
        
        # Validate
        is_valid, error = self.schema.validate_post(post)
        if not is_valid:
            raise ValueError(error)
        
        # Save
        post_file = self.posts_dir / f"{post_id}.json"
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        
        # Update indexes
        self._update_indexes(post)
        
        return post
    
    def delete_post(self, post_id: str, author_id: str) -> bool:
        """
        Delete a post
        
        Args:
            post_id: Post ID
            author_id: User ID (must be post author)
            
        Returns:
            True if deleted, False otherwise
        """
        post = self.get_post(post_id)
        if not post:
            return False
        
        # Verify author
        if post.get('author_id') != author_id:
            raise PermissionError("Only post author can delete post")
        
        # Delete post file
        post_file = self.posts_dir / f"{post_id}.json"
        if post_file.exists():
            post_file.unlink()
        
        # Remove from indexes
        self._remove_from_indexes(post_id, post.get('author_id'))
        
        return True
    
    def get_posts_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get posts by user
        
        Args:
            user_id: User ID
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            
        Returns:
            List of post data dictionaries
        """
        # Load index
        index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_user.json"
        if not index_file.exists():
            return []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            post_ids = index_data.get('index', {}).get(user_id, [])
            
            # Get posts
            posts = []
            for post_id in post_ids[offset:offset + limit]:
                post = self.get_post(post_id)
                if post:
                    posts.append(post)
            
            return posts
        except Exception:
            return []
    
    def get_posts_by_date(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get posts sorted by date (chronological)
        
        Args:
            limit: Maximum number of posts to return
            offset: Number of posts to skip
            
        Returns:
            List of post data dictionaries
        """
        # Load index
        index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_date.json"
        if not index_file.exists():
            return []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            post_ids = index_data.get('index', [])
            
            # Get posts
            posts = []
            for post_id in post_ids[offset:offset + limit]:
                post = self.get_post(post_id)
                if post:
                    posts.append(post)
            
            return posts
        except Exception:
            return []
    
    def _update_indexes(self, post: Dict[str, Any]):
        """Update all indexes with post"""
        post_id = post['id']
        author_id = post['author_id']
        created_at = post['created_at']
        ai_score = post.get('ai_score', 0.0)
        
        # Update posts_by_user index
        user_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_user.json"
        if user_index_file.exists():
            with open(user_index_file, 'r', encoding='utf-8') as f:
                user_index = json.load(f)
        else:
            user_index = {"index": {}}
        
        if author_id not in user_index['index']:
            user_index['index'][author_id] = []
        if post_id not in user_index['index'][author_id]:
            user_index['index'][author_id].insert(0, post_id)
        
        with open(user_index_file, 'w', encoding='utf-8') as f:
            json.dump(user_index, f, indent=2, ensure_ascii=False)
        
        # Update posts_by_date index
        date_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_date.json"
        if date_index_file.exists():
            with open(date_index_file, 'r', encoding='utf-8') as f:
                date_index = json.load(f)
        else:
            date_index = {"index": []}
        
        if post_id not in date_index['index']:
            date_index['index'].insert(0, post_id)
        
        with open(date_index_file, 'w', encoding='utf-8') as f:
            json.dump(date_index, f, indent=2, ensure_ascii=False)
        
        # Update posts_by_score index (sorted by score)
        score_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_score.json"
        if score_index_file.exists():
            with open(score_index_file, 'r', encoding='utf-8') as f:
                score_index = json.load(f)
        else:
            score_index = {"index": []}
        
        # Remove if exists, then insert in sorted position
        if post_id in score_index['index']:
            score_index['index'].remove(post_id)
        
        # Insert in sorted position (highest score first)
        inserted = False
        for i, existing_id in enumerate(score_index['index']):
            existing_post = self.get_post(existing_id)
            if existing_post and existing_post.get('ai_score', 0.0) < ai_score:
                score_index['index'].insert(i, post_id)
                inserted = True
                break
        
        if not inserted:
            score_index['index'].append(post_id)
        
        with open(score_index_file, 'w', encoding='utf-8') as f:
            json.dump(score_index, f, indent=2, ensure_ascii=False)
    
    def _remove_from_indexes(self, post_id: str, author_id: Optional[str] = None):
        """Remove post from all indexes"""
        # Remove from posts_by_user
        user_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_user.json"
        if user_index_file.exists() and author_id:
            with open(user_index_file, 'r', encoding='utf-8') as f:
                user_index = json.load(f)
            if author_id in user_index.get('index', {}):
                if post_id in user_index['index'][author_id]:
                    user_index['index'][author_id].remove(post_id)
            with open(user_index_file, 'w', encoding='utf-8') as f:
                json.dump(user_index, f, indent=2, ensure_ascii=False)
        
        # Remove from posts_by_date
        date_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_date.json"
        if date_index_file.exists():
            with open(date_index_file, 'r', encoding='utf-8') as f:
                date_index = json.load(f)
            if post_id in date_index.get('index', []):
                date_index['index'].remove(post_id)
            with open(date_index_file, 'w', encoding='utf-8') as f:
                json.dump(date_index, f, indent=2, ensure_ascii=False)
        
        # Remove from posts_by_score
        score_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_score.json"
        if score_index_file.exists():
            with open(score_index_file, 'r', encoding='utf-8') as f:
                score_index = json.load(f)
            if post_id in score_index.get('index', []):
                score_index['index'].remove(post_id)
            with open(score_index_file, 'w', encoding='utf-8') as f:
                json.dump(score_index, f, indent=2, ensure_ascii=False)

