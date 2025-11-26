#!/usr/bin/env python3
"""
Feed Cache Manager
Per-user feed caching with TTL and invalidation
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class FeedCache:
    """
    Feed Cache Manager
    Manages per-user feed caching with TTL
    """
    
    def __init__(self, base_dir: Path = None, ttl_seconds: int = 300):
        """
        Initialize feed cache
        
        Args:
            base_dir: Base directory for data storage
            ttl_seconds: Cache TTL in seconds (default 5 minutes)
        """
        self.base_dir = base_dir or Path(".")
        self.cache_dir = self.base_dir / "data" / "feed"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
    
    def get_cached_feed(self, user_id: str, feed_type: str, limit: int, offset: int) -> Optional[list]:
        """
        Get cached feed if available and not expired
        
        Args:
            user_id: User ID
            feed_type: Feed type
            limit: Feed limit
            offset: Feed offset
            
        Returns:
            Cached posts list or None
        """
        cache_key = self._get_cache_key(user_id, feed_type, limit, offset)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check TTL
            cached_at = datetime.fromisoformat(cache_data.get('cached_at', '1970-01-01T00:00:00'))
            if datetime.now() - cached_at > timedelta(seconds=self.ttl_seconds):
                cache_file.unlink()
                return None
            
            return cache_data.get('posts', [])
        except Exception:
            return None
    
    def cache_feed(self, user_id: str, feed_type: str, limit: int, offset: int, posts: List):
        """
        Cache feed
        
        Args:
            user_id: User ID
            feed_type: Feed type
            limit: Feed limit
            offset: Feed offset
            posts: Posts list to cache
        """
        cache_key = self._get_cache_key(user_id, feed_type, limit, offset)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "posts": posts
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    def invalidate_user_cache(self, user_id: str):
        """
        Invalidate all cache for a user
        
        Args:
            user_id: User ID
        """
        for cache_file in self.cache_dir.glob(f"{user_id}_*.json"):
            cache_file.unlink()
    
    def invalidate_all_cache(self):
        """Invalidate all feed cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
    
    def _get_cache_key(self, user_id: str, feed_type: str, limit: int, offset: int) -> str:
        """Generate cache key"""
        return f"{user_id}_{feed_type}_{limit}_{offset}"

