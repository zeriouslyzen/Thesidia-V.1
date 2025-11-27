#!/usr/bin/env python3
"""
Feed Manager
Chronological and AI-ranked feeds with caching
"""

import json
import math
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.post_manager import PostManager
from webapp.social.social_graph import SocialGraph
from webapp.social.feed_ranker import FeedRanker


class FeedManager:
    """
    Feed Manager
    Generates chronological and AI-ranked feeds with caching
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize feed manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.feed_cache_dir = self.base_dir / "data" / "feed"
        self.feed_cache_dir.mkdir(parents=True, exist_ok=True)
        self.post_manager = PostManager(base_dir=base_dir)
        self.social_graph = SocialGraph(base_dir=base_dir)
        self.feed_ranker = FeedRanker(base_dir=base_dir)
        self.cache_ttl = 300  # 5 minutes
    
    def get_feed(
        self,
        user_id: str,
        feed_type: str = "chronological",
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get feed for user
        
        Args:
            user_id: User ID
            feed_type: Feed type (chronological, quality, personalized)
            limit: Maximum number of posts
            offset: Number of posts to skip
            
        Returns:
            List of post data dictionaries
        """
        # Enforce pagination limits
        max_limit = 100
        if limit > max_limit:
            limit = max_limit
        if limit < 1:
            limit = 20
        if offset < 0:
            offset = 0
        
        # Check cache
        cache_key = f"{user_id}_{feed_type}_{limit}_{offset}"
        cached = self._get_cached_feed(cache_key)
        if cached:
            return cached
        
        # Generate feed
        if feed_type == "chronological":
            posts = self._get_chronological_feed(user_id, limit, offset)
        elif feed_type == "quality":
            posts = self._get_quality_feed(user_id, limit, offset)
        elif feed_type == "personalized":
            posts = self._get_personalized_feed(user_id, limit, offset)
        else:
            posts = self._get_chronological_feed(user_id, limit, offset)
        
        # Cache feed
        self._cache_feed(cache_key, posts)
        
        return posts
    
    def _get_chronological_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get chronological feed (following + public)"""
        # Enforce pagination limits
        max_limit = 100
        if limit > max_limit:
            limit = max_limit
        if limit < 1:
            limit = 20
        
        # Get following list
        following = self.social_graph.get_following(user_id)
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Get posts with reasonable limit to avoid loading too many
        # Load more than needed to account for filtering
        fetch_limit = min(limit * 3, 300)  # Cap at 300 posts max
        all_posts = self.post_manager.get_posts_by_date(limit=fetch_limit, offset=0)
        
        # Filter: following + public, exclude blocked/muted
        filtered_posts = []
        for post in all_posts:
            author_id = post.get('author_id')
            visibility = post.get('visibility', 'public')
            
            # Skip blocked/muted users
            if author_id in blocked or author_id in muted:
                continue
            
            # Include if following or public
            if author_id in following or visibility == 'public':
                filtered_posts.append(post)
        
        # Apply offset and limit
        return filtered_posts[offset:offset + limit]
    
    def _get_quality_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get AI-ranked quality feed"""
        # Enforce pagination limits
        max_limit = 100
        if limit > max_limit:
            limit = max_limit
        if limit < 1:
            limit = 20
        
        # Get all posts sorted by score
        score_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_score.json"
        if not score_index_file.exists():
            return []
        
        with open(score_index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        post_ids = index_data.get('index', [])
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Batch load posts to avoid N+1 queries
        # Load more than needed to account for filtering
        fetch_count = min(limit * 2, 200)  # Cap at 200 posts max
        candidate_ids = post_ids[offset:offset + fetch_count]
        posts = self.post_manager.get_posts_batch(candidate_ids)
        
        # Filter blocked/muted
        filtered_posts = []
        for post in posts:
            if not post:
                continue
            author_id = post.get('author_id')
            if author_id not in blocked and author_id not in muted:
                filtered_posts.append(post)
                if len(filtered_posts) >= limit:
                    break
        
        return filtered_posts
    
    def _get_personalized_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get personalized feed using AI ranking"""
        # Enforce pagination limits
        max_limit = 100
        if limit > max_limit:
            limit = max_limit
        if limit < 1:
            limit = 20
        
        # Get posts (with reasonable limit)
        fetch_limit = min(limit * 2, 200)  # Cap at 200 posts max
        posts = self._get_chronological_feed(user_id, fetch_limit, 0)
        
        # Rank posts
        ranked_posts = self.feed_ranker.rank_posts(posts, user_id)
        
        # Apply offset and limit
        return ranked_posts[offset:offset + limit]
    
    def _get_cached_feed(self, cache_key: str) -> Optional[list]:
        """Get cached feed"""
        cache_file = self.feed_cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check TTL
            cached_at = datetime.fromisoformat(cache_data.get('cached_at', '1970-01-01T00:00:00'))
            if datetime.now() - cached_at > timedelta(seconds=self.cache_ttl):
                cache_file.unlink()
                return None
            
            return cache_data.get('posts', [])
        except Exception:
            return None
    
    def _cache_feed(self, cache_key: str, posts: list):
        """Cache feed"""
        cache_file = self.feed_cache_dir / f"{cache_key}.json"
        
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "posts": posts
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def invalidate_cache(self, user_id: Optional[str] = None):
        """Invalidate feed cache"""
        if user_id:
            # Invalidate specific user's cache
            for cache_file in self.feed_cache_dir.glob(f"{user_id}_*.json"):
                cache_file.unlink()
        else:
            # Invalidate all cache
            for cache_file in self.feed_cache_dir.glob("*.json"):
                cache_file.unlink()

