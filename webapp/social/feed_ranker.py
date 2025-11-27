#!/usr/bin/env python3
"""
Feed Ranker
AI-powered feed ranking with quality, relevance, recency, diversity
"""

import math
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from user_interest_tracker import UserInterestTracker


class FeedRanker:
    """
    Feed Ranker
    Ranks posts using AI quality score, relevance, recency, and diversity
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize feed ranker
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.interest_tracker = UserInterestTracker(base_dir=base_dir)
    
    def rank_posts(self, posts: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Rank posts for user feed
        
        Args:
            posts: List of post data dictionaries
            user_id: User ID
            
        Returns:
            Sorted list of posts (highest score first)
        """
        # Calculate scores for each post
        for post in posts:
            post['feed_score'] = self._calculate_feed_score(post, user_id)
        
        # Sort by feed score (descending)
        return sorted(posts, key=lambda p: p.get('feed_score', 0.0), reverse=True)
    
    def _calculate_feed_score(self, post: Dict[str, Any], user_id: str) -> float:
        """
        Calculate feed score for a post
        
        Args:
            post: Post data dictionary
            user_id: User ID
            
        Returns:
            Feed score (0-1)
        """
        # AI quality score (40% weight)
        ai_score = post.get('ai_score', 0.5)
        quality_component = ai_score * 0.4
        
        # Relevance to user (30% weight)
        relevance = self._calculate_relevance(post, user_id)
        relevance_component = relevance * 0.3
        
        # Recency (20% weight, exponential decay)
        recency = self._calculate_recency(post)
        recency_component = recency * 0.2
        
        # Diversity (10% weight)
        diversity = 1.0  # Placeholder - would need feed history
        diversity_component = diversity * 0.1
        
        return quality_component + relevance_component + recency_component + diversity_component
    
    def _calculate_relevance(self, post: Dict[str, Any], user_id: str) -> float:
        """
        Calculate relevance score based on user interests
        
        Args:
            post: Post data dictionary
            user_id: User ID
            
        Returns:
            Relevance score (0-1)
        """
        try:
            # Get user interests
            interests = self.interest_tracker.get_user_interests(user_id)
            
            # Check post content and tags against interests
            content = post.get('content', '').lower()
            tags = [tag.lower() for tag in post.get('tags', [])]
            
            # Simple keyword matching (could be enhanced with embeddings)
            relevance_score = 0.5  # Default
            
            for interest, weight in interests.items():
                if interest.lower() in content or interest.lower() in tags:
                    relevance_score += weight * 0.1
            
            return min(1.0, relevance_score)
        except Exception:
            return 0.5  # Default relevance
    
    def _calculate_recency(self, post: Dict[str, Any]) -> float:
        """
        Calculate recency score (exponential decay)
        
        Args:
            post: Post data dictionary
            
        Returns:
            Recency score (0-1)
        """
        try:
            created_at = datetime.fromisoformat(post.get('created_at', datetime.now().isoformat()))
            hours_old = (datetime.now() - created_at).total_seconds() / 3600
            
            # Exponential decay: e^(-hours/24)
            # Posts older than 7 days get very low score
            recency = math.exp(-hours_old / 24)
            return max(0.0, min(1.0, recency))
        except Exception:
            return 0.5  # Default recency

