#!/usr/bin/env python3
"""
Bot Detector
Multi-signal bot detection using behavioral and content analysis
"""

from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.post_manager import PostManager
from webapp.social.social_graph import SocialGraph


class BotDetector:
    """
    Bot Detector
    Detects bot accounts using multiple signals
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize bot detector
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.post_manager = PostManager(base_dir=base_dir)
        self.social_graph = SocialGraph(base_dir=base_dir)
    
    def detect_bot(self, user_id: str) -> tuple[float, Dict[str, Any]]:
        """
        Detect if user is a bot
        
        Args:
            user_id: User ID to check
            
        Returns:
            Tuple of (bot_probability, signals_dict)
        """
        signals = {
            "post_frequency": self._check_post_frequency(user_id),
            "content_repetition": self._check_content_repetition(user_id),
            "engagement_patterns": self._check_engagement_patterns(user_id),
            "network_anomalies": self._check_network_anomalies(user_id),
            "account_age": self._check_account_age(user_id)
        }
        
        # Weighted average
        weights = {
            "post_frequency": 0.25,
            "content_repetition": 0.25,
            "engagement_patterns": 0.20,
            "network_anomalies": 0.15,
            "account_age": 0.15
        }
        
        bot_probability = sum(signals[k] * weights[k] for k in signals)
        
        return max(0.0, min(1.0, bot_probability)), signals
    
    def _check_post_frequency(self, user_id: str) -> float:
        """Check for excessive posting (higher = more bot-like)"""
        posts = self.post_manager.get_posts_by_user(user_id, limit=100)
        
        if len(posts) < 5:
            return 0.0  # Not enough data
        
        # Check posting frequency
        if len(posts) == 0:
            return 0.0
        
        # Check if posts are too frequent (more than 10 per hour)
        recent_posts = [p for p in posts if self._is_recent(p, hours=1)]
        if len(recent_posts) > 10:
            return 1.0  # Very bot-like
        
        return min(1.0, len(recent_posts) / 10)
    
    def _check_content_repetition(self, user_id: str) -> float:
        """Check for repetitive content (higher = more bot-like)"""
        posts = self.post_manager.get_posts_by_user(user_id, limit=20)
        
        if len(posts) < 3:
            return 0.0
        
        # Check content similarity
        contents = [p.get('content', '') for p in posts]
        
        # Simple similarity check (would use embeddings in production)
        similar_count = 0
        for i, content1 in enumerate(contents):
            for content2 in contents[i+1:]:
                # Check if very similar (simple check)
                if len(content1) > 0 and len(content2) > 0:
                    similarity = len(set(content1.split()) & set(content2.split())) / max(len(set(content1.split())), len(set(content2.split())), 1)
                    if similarity > 0.8:
                        similar_count += 1
        
        # Normalize
        max_pairs = len(posts) * (len(posts) - 1) / 2
        if max_pairs == 0:
            return 0.0
        
        return min(1.0, similar_count / max_pairs)
    
    def _check_engagement_patterns(self, user_id: str) -> float:
        """Check for unnatural engagement patterns"""
        posts = self.post_manager.get_posts_by_user(user_id, limit=20)
        
        if len(posts) == 0:
            return 0.0
        
        # Check if all posts have very similar engagement
        engagements = []
        for post in posts:
            interactions = post.get('interactions', {})
            views = interactions.get('views', 0)
            likes = interactions.get('likes', 0)
            if views > 0:
                engagements.append(likes / views)
        
        if len(engagements) < 3:
            return 0.0
        
        # Check variance (bots often have very consistent engagement)
        avg_engagement = sum(engagements) / len(engagements)
        variance = sum((e - avg_engagement) ** 2 for e in engagements) / len(engagements)
        
        # Low variance = more bot-like
        if variance < 0.001:
            return 0.8
        
        return 0.0
    
    def _check_network_anomalies(self, user_id: str) -> float:
        """Check for network anomalies (suspicious follower ratios)"""
        graph = self.social_graph.get_social_graph(user_id)
        followers = len(graph.get('followers', []))
        following = len(graph.get('following', []))
        
        if following == 0:
            return 0.0
        
        # Check follower/following ratio
        ratio = followers / following
        
        # Very high ratio (many followers, few following) = suspicious
        if ratio > 100:
            return 0.7
        
        # Very low ratio (many following, few followers) = suspicious
        if ratio < 0.01 and following > 100:
            return 0.6
        
        return 0.0
    
    def _check_account_age(self, user_id: str) -> float:
        """Check account age (new accounts with lots of activity = suspicious)"""
        # Get user info
        user_info_file = self.base_dir / "data" / "users" / user_id / "user_info.json"
        if not user_info_file.exists():
            return 0.0
        
        try:
            import json
            with open(user_info_file, 'r', encoding='utf-8') as f:
                user_info = json.load(f)
            
            created_at = datetime.fromisoformat(user_info.get('created_at', datetime.now().isoformat()))
            account_age_days = (datetime.now() - created_at).days
            
            # Check post count
            posts = self.post_manager.get_posts_by_user(user_id, limit=1)
            post_count = len(posts)
            
            # New account (< 7 days) with many posts (> 50) = suspicious
            if account_age_days < 7 and post_count > 50:
                return 0.8
            
            return 0.0
        except Exception:
            return 0.0
    
    def _is_recent(self, post: Dict[str, Any], hours: int = 1) -> bool:
        """Check if post is recent"""
        try:
            created_at = datetime.fromisoformat(post.get('created_at', datetime.now().isoformat()))
            return (datetime.now() - created_at) < timedelta(hours=hours)
        except Exception:
            return False

