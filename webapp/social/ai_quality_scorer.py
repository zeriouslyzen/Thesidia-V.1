#!/usr/bin/env python3
"""
AI Quality Scorer
Multi-factor quality scoring for posts
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class AIQualityScorer:
    """
    AI Quality Scorer
    Calculates quality scores for posts using multiple factors
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize AI quality scorer
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
    
    def calculate_quality_score(self, post: Dict[str, Any], author_data: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate quality score for a post
        
        Args:
            post: Post data dictionary
            author_data: Optional author data dictionary
            
        Returns:
            Quality score (0-1)
        """
        factors = {
            "content_length": self._score_content_length(post),
            "spam_detection": self._detect_spam(post),
            "content_diversity": self._check_content_uniqueness(post),
            "engagement_quality": self._calculate_engagement_ratio(post),
            "user_reputation": self._get_user_reputation(author_data) if author_data else 0.5,
            "sentiment_balance": self._check_sentiment_balance(post)
        }
        
        # Weighted average
        weights = {
            "content_length": 0.15,
            "spam_detection": 0.25,
            "content_diversity": 0.15,
            "engagement_quality": 0.15,
            "user_reputation": 0.15,
            "sentiment_balance": 0.15
        }
        
        score = sum(factors[k] * weights[k] for k in factors)
        return max(0.0, min(1.0, score))
    
    def _score_content_length(self, post: Dict[str, Any]) -> float:
        """Score based on content length (optimal: 100-500 chars)"""
        content = post.get('content', '')
        length = len(content)
        
        if length < 10:
            return 0.2  # Too short
        elif length < 100:
            return 0.6  # Short but acceptable
        elif length <= 500:
            return 1.0  # Optimal
        elif length <= 1000:
            return 0.8  # Long but acceptable
        else:
            return 0.6  # Very long
    
    def _detect_spam(self, post: Dict[str, Any]) -> float:
        """Detect spam probability (higher = less spam)"""
        content = post.get('content', '').lower()
        
        # Spam indicators
        spam_indicators = [
            'click here', 'buy now', 'limited time', 'act now',
            'free money', 'guaranteed', 'no risk', 'make money fast'
        ]
        
        spam_count = sum(1 for indicator in spam_indicators if indicator in content)
        
        # Check for excessive links
        link_count = content.count('http://') + content.count('https://')
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        
        # Calculate spam score (lower = more spam)
        spam_score = 1.0
        spam_score -= spam_count * 0.2
        spam_score -= min(link_count * 0.1, 0.3)
        spam_score -= max(0, (caps_ratio - 0.3) * 2)
        
        return max(0.0, min(1.0, spam_score))
    
    def _check_content_uniqueness(self, post: Dict[str, Any]) -> float:
        """Check content uniqueness (placeholder - would need comparison with other posts)"""
        # For now, return default score
        # In production, would compare with other posts using embeddings
        return 0.8
    
    def _calculate_engagement_ratio(self, post: Dict[str, Any]) -> float:
        """Calculate engagement quality ratio"""
        interactions = post.get('interactions', {})
        views = interactions.get('views', 0)
        likes = interactions.get('likes', 0)
        comments = interactions.get('comments', 0)
        
        if views == 0:
            return 0.5  # No views yet
        
        # Engagement ratio
        engagement = (likes + comments * 2) / max(views, 1)
        
        # Normalize (good engagement: >0.1)
        return min(1.0, engagement * 10)
    
    def _get_user_reputation(self, author_data: Optional[Dict[str, Any]]) -> float:
        """Get user reputation score"""
        if not author_data:
            return 0.5
        
        # Placeholder - would calculate based on user history
        # For now, return default
        return 0.7
    
    def _check_sentiment_balance(self, post: Dict[str, Any]) -> float:
        """Check sentiment balance (avoid extreme negativity/positivity)"""
        content = post.get('content', '')
        
        # Simple sentiment check (would use proper sentiment analysis in production)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'happy']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        # Balance score (closer to 0.5 = better)
        total = positive_count + negative_count
        if total == 0:
            return 1.0  # Neutral
        
        ratio = positive_count / total
        balance = 1.0 - abs(ratio - 0.5) * 2
        
        return max(0.0, min(1.0, balance))

