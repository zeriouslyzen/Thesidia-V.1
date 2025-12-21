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

from src.core.storage_base import StorageBackend, FileSystemBackend

class PostManager:
    def __init__(self, base_dir: Path = None, backend: Optional[StorageBackend] = None):
        self.base_dir = base_dir or Path(".")
        self.backend = backend or FileSystemBackend(root=str(self.base_dir / "data" / "social"))
        self.backend.ensure_path("posts")
        self.backend.ensure_path("indexes")
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
        self.backend.write_json(f"posts/{post['id']}.json", post)
        
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
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get post by ID
        
        Args:
            post_id: Post ID
            
        Returns:
            Post data dictionary or None
        """
        return self.backend.read_json(f"posts/{post_id}.json")
    
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
    
    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags from all posts
        
        Returns:
            List of unique tag strings
        """
        tags_set = set()
        
        # Load index to get all post IDs
        index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_date.json"
        if not index_file.exists():
            return []
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            post_ids = index_data.get('index', [])
            
            # Get tags from all posts
            for post_id in post_ids:
                post = self.get_post(post_id)
                if post and post.get('tags'):
                    for tag in post['tags']:
                        if tag:  # Only add non-empty tags
                            tags_set.add(tag)
            
            return sorted(list(tags_set))
        except Exception:
            return []
    
    def _update_indexes(self, post: Dict[str, Any]):
        """Update all indexes with post"""
        post_id = post['id']
        author_id = post['author_id']
        ai_score = post.get('ai_score', 0.0)
        
        # Update posts_by_user index
        user_index = self.backend.read_json("indexes/posts_by_user.json") or {"index": {}}
        if author_id not in user_index['index']:
            user_index['index'][author_id] = []
        if post_id not in user_index['index'][author_id]:
            user_index['index'][author_id].insert(0, post_id)
        self.backend.write_json("indexes/posts_by_user.json", user_index)
        
        # Update posts_by_date index
        date_index = self.backend.read_json("indexes/posts_by_date.json") or {"index": []}
        if post_id not in date_index['index']:
            date_index['index'].insert(0, post_id)
        self.backend.write_json("indexes/posts_by_date.json", date_index)
        
        # Update posts_by_score index
        score_index = self.backend.read_json("indexes/posts_by_score.json") or {"index": []}
        if post_id in score_index['index']:
            score_index['index'].remove(post_id)
        
        inserted = False
        for i, existing_id in enumerate(score_index['index']):
            existing_post = self.get_post(existing_id)
            if existing_post and existing_post.get('ai_score', 0.0) < ai_score:
                score_index['index'].insert(i, post_id)
                inserted = True
                break
        if not inserted:
            score_index['index'].append(post_id)
        self.backend.write_json("indexes/posts_by_score.json", score_index)
    
    def _remove_from_indexes(self, post_id: str, author_id: Optional[str] = None):
        """Remove post from all indexes"""
        # Remove from posts_by_user
        if author_id:
            user_index = self.backend.read_json("indexes/posts_by_user.json")
            if user_index and author_id in user_index.get('index', {}):
                if post_id in user_index['index'][author_id]:
                    user_index['index'][author_id].remove(post_id)
                    self.backend.write_json("indexes/posts_by_user.json", user_index)
        
        # Remove from posts_by_date
        date_index = self.backend.read_json("indexes/posts_by_date.json")
        if date_index and post_id in date_index.get('index', []):
            date_index['index'].remove(post_id)
            self.backend.write_json("indexes/posts_by_date.json", date_index)
        
        # Remove from posts_by_score
        score_index = self.backend.read_json("indexes/posts_by_score.json")
        if score_index and post_id in score_index.get('index', []):
            score_index['index'].remove(post_id)
            self.backend.write_json("indexes/posts_by_score.json", score_index)

