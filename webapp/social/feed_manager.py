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
        # Check cache (but don't cache empty feeds for new users)
        cache_key = f"{user_id}_{feed_type}_{limit}_{offset}"
        cached = self._get_cached_feed(cache_key)
        if cached and len(cached) > 0:  # Only use cache if it has posts
            return cached
        
        # Generate feed
        if feed_type == "chronological":
            posts = self._get_chronological_feed(user_id, limit, offset)
        elif feed_type == "quality":
            posts = self._get_quality_feed(user_id, limit, offset)
        elif feed_type == "personalized":
            posts = self._get_personalized_feed(user_id, limit, offset)
        elif feed_type == "friends":
            posts = self._get_friends_feed(user_id, limit, offset)
        elif feed_type == "fans":
            posts = self._get_fans_feed(user_id, limit, offset)
        elif feed_type == "communities":
            posts = self._get_communities_feed(user_id, limit, offset)
        elif feed_type == "labs":
            posts = self._get_labs_feed(user_id, limit, offset)
        else:
            posts = self._get_chronological_feed(user_id, limit, offset)
        
        # Cache feed (but don't cache empty feeds to avoid stale empty caches)
        if len(posts) > 0:
            self._cache_feed(cache_key, posts)
        
        return posts
    
    def _get_chronological_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get chronological feed (following + public)"""
        # Get following list
        following = self.social_graph.get_following(user_id)
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Get all posts
        all_posts = self.post_manager.get_posts_by_date(limit=limit * 3, offset=0)
        
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
        
        return filtered_posts[offset:offset + limit]
    
    def _get_quality_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get AI-ranked quality feed"""
        # Get all posts sorted by score
        score_index_file = self.base_dir / "data" / "social" / "indexes" / "posts_by_score.json"
        if not score_index_file.exists():
            return []
        
        with open(score_index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        post_ids = index_data.get('index', [])
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Get posts, filter blocked/muted
        posts = []
        for post_id in post_ids[offset:offset + limit * 2]:
            post = self.post_manager.get_post(post_id)
            if post:
                author_id = post.get('author_id')
                if author_id not in blocked and author_id not in muted:
                    posts.append(post)
                    if len(posts) >= limit:
                        break
        
        return posts
    
    def _get_personalized_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get personalized feed using AI ranking"""
        # Get posts
        posts = self._get_chronological_feed(user_id, limit * 2, 0)
        
        # Rank posts
        ranked_posts = self.feed_ranker.rank_posts(posts, user_id)
        
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
    
    def _get_friends_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get feed from users you're following (friends) - includes tags"""
        following = self.social_graph.get_following(user_id)
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        if not following:
            return []
        
        # Get all posts
        all_posts = self.post_manager.get_posts_by_date(limit=limit * 3, offset=0)
        
        # Filter: only posts from users you're following (with tags)
        filtered_posts = []
        for post in all_posts:
            author_id = post.get('author_id')
            tags = post.get('tags', [])
            
            # Skip blocked/muted users
            if author_id in blocked or author_id in muted:
                continue
            
            # Only include posts from users you're following
            # Posts with tags are prioritized
            if author_id in following:
                # Add tag metadata for display
                if tags:
                    post['_has_tags'] = True
                    post['_tags'] = tags
                filtered_posts.append(post)
        
        # Sort: posts with tags first, then by date
        filtered_posts.sort(key=lambda p: (
            not p.get('tags', []),  # Posts with tags first
            p.get('created_at', '')
        ), reverse=True)
        
        return filtered_posts[offset:offset + limit]
    
    def _get_fans_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get feed from users who follow you (fans) - includes tags"""
        followers = self.social_graph.get_followers(user_id)
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        if not followers:
            return []
        
        # Get all posts
        all_posts = self.post_manager.get_posts_by_date(limit=limit * 3, offset=0)
        
        # Filter: only posts from users who follow you (with tags)
        filtered_posts = []
        for post in all_posts:
            author_id = post.get('author_id')
            tags = post.get('tags', [])
            
            # Skip blocked/muted users
            if author_id in blocked or author_id in muted:
                continue
            
            # Only include posts from users who follow you
            # Posts with tags are prioritized
            if author_id in followers:
                # Add tag metadata for display
                if tags:
                    post['_has_tags'] = True
                    post['_tags'] = tags
                filtered_posts.append(post)
        
        # Sort: posts with tags first, then by date
        filtered_posts.sort(key=lambda p: (
            not p.get('tags', []),  # Posts with tags first
            p.get('created_at', '')
        ), reverse=True)
        
        return filtered_posts[offset:offset + limit]
    
    def _get_communities_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get feed from communities (posts with tags from community bots)"""
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Get all posts
        all_posts = self.post_manager.get_posts_by_date(limit=limit * 5, offset=0)
        
        # Filter: only posts with tags (community posts)
        # Prioritize posts from community bots
        filtered_posts = []
        for post in all_posts:
            author_id = post.get('author_id', '')
            tags = post.get('tags', [])
            
            # Skip blocked/muted users
            if author_id in blocked or author_id in muted:
                continue
            
            # Only include posts with tags (community indicator)
            if tags:
                # Check if author is a community bot
                is_community_bot = author_id.startswith('bot_')
                if is_community_bot:
                    # Check bot profile for community type
                    try:
                        bot_file = self.base_dir / "data" / "bots" / f"{author_id}.json"
                        if bot_file.exists():
                            import json
                            with open(bot_file, 'r', encoding='utf-8') as f:
                                bot_data = json.load(f)
                                if bot_data.get('bot_type') == 'community':
                                    post['_is_community_post'] = True
                                    post['_community'] = bot_data.get('community', tags[0])
                    except Exception:
                        pass
                
                post['_has_tags'] = True
                post['_tags'] = tags
                filtered_posts.append(post)
        
        # Sort: community bot posts first, then by engagement, then by date
        filtered_posts.sort(key=lambda p: (
            not p.get('_is_community_post', False),  # Community posts first
            -(p.get('interactions', {}).get('likes', 0) + p.get('interactions', {}).get('views', 0)),  # Engagement
            p.get('created_at', '')
        ), reverse=True)
        
        return filtered_posts[offset:offset + limit]
    
    def _get_labs_feed(self, user_id: str, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Get feed of proactive media posts (Labs - only media posts with high activity)"""
        blocked = self.social_graph.get_social_graph(user_id).get('blocked', [])
        muted = self.social_graph.get_social_graph(user_id).get('muted', [])
        
        # Get more posts for Labs (more activity)
        all_posts = self.post_manager.get_posts_by_date(limit=limit * 10, offset=0)
        
        # Filter: only posts with media (proactive/action-oriented content)
        filtered_posts = []
        for post in all_posts:
            author_id = post.get('author_id')
            media = post.get('media', [])
            
            # Skip blocked/muted users
            if author_id in blocked or author_id in muted:
                continue
            
            # Only include posts with media (images, videos, GIFs, multiple photos)
            if media and len(media) > 0:
                # Calculate engagement score
                interactions = post.get('interactions', {})
                total_engagement = (
                    interactions.get('likes', 0) +
                    interactions.get('comments', 0) +
                    interactions.get('reposts', 0) +
                    interactions.get('views', 0)
                )
                
                # Prioritize posts with:
                # 1. Multiple media items (carousels)
                # 2. Videos (more engaging)
                # 3. Higher engagement
                media_score = 0
                if len(media) > 1:
                    media_score += 10  # Multiple photos
                if any(m.get('type') == 'video' for m in media):
                    media_score += 5  # Videos
                if any(m.get('type') == 'gif' for m in media):
                    media_score += 3  # GIFs
                
                # Include all media posts (Labs shows more activity)
                filtered_posts.append({
                    **post,
                    '_engagement_score': total_engagement + media_score,
                    '_media_count': len(media),
                    '_has_video': any(m.get('type') == 'video' for m in media)
                })
        
        # Sort by: media score, engagement, then date
        filtered_posts.sort(key=lambda p: (
            p.get('_engagement_score', 0),
            p.get('_media_count', 0),
            p.get('created_at', '')
        ), reverse=True)
        
        # Remove temporary fields
        for post in filtered_posts:
            post.pop('_engagement_score', None)
            post.pop('_media_count', None)
            post.pop('_has_video', None)
        
        return filtered_posts[offset:offset + limit]
    
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

