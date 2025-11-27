#!/usr/bin/env python3
"""
AI Quality Scorer
Multi-factor quality scoring for posts using Thesidia AI
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys
import json
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Try to import Thesidia (may not be available on Vercel)
try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    THESIDIA_AVAILABLE = True
except ImportError:
    THESIDIA_AVAILABLE = False
    ThesidiaHybridAdaptive = None


class AIQualityScorer:
    """
    AI Quality Scorer
    Calculates quality scores for posts using multiple factors
    """
    
    def __init__(self, base_dir: Path = None, thesidia: Optional[Any] = None):
        """
        Initialize AI quality scorer
        
        Args:
            base_dir: Base directory for data storage
            thesidia: Optional ThesidiaHybridAdaptive instance
        """
        self.base_dir = base_dir or Path(".")
        self.thesidia = thesidia
        self._thesidia_initialized = False
        
        # Initialize Thesidia if available and not provided
        if not self.thesidia and THESIDIA_AVAILABLE:
            try:
                self.thesidia = ThesidiaHybridAdaptive()
                self._thesidia_initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize Thesidia for quality scoring: {e}")
                self.thesidia = None
    
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
        """Detect spam probability using AI (higher = less spam)"""
        content = post.get('content', '')
        
        # Basic heuristic checks first (fast)
        content_lower = content.lower()
        spam_indicators = [
            'click here', 'buy now', 'limited time', 'act now',
            'free money', 'guaranteed', 'no risk', 'make money fast'
        ]
        
        spam_count = sum(1 for indicator in spam_indicators if indicator in content_lower)
        link_count = content.count('http://') + content.count('https://')
        caps_ratio = sum(1 for c in content if c.isupper()) / max(len(content), 1)
        
        # Quick heuristic score
        heuristic_score = 1.0
        heuristic_score -= spam_count * 0.2
        heuristic_score -= min(link_count * 0.1, 0.3)
        heuristic_score -= max(0, (caps_ratio - 0.3) * 2)
        heuristic_score = max(0.0, min(1.0, heuristic_score))
        
        # If heuristic suggests spam, use AI for deeper analysis
        if heuristic_score < 0.7 and self.thesidia:
            try:
                ai_score = self._ai_spam_detection(content)
                # Combine heuristic and AI (weighted)
                return (heuristic_score * 0.4) + (ai_score * 0.6)
            except Exception:
                return heuristic_score
        
        return heuristic_score
    
    def _ai_spam_detection(self, content: str) -> float:
        """Use Thesidia AI to detect spam"""
        if not self.thesidia:
            return 0.5
        
        try:
            prompt = f"""Analyze this social media post for spam indicators:

Post: {content[:500]}

Rate the likelihood this is spam (0.0 = definitely spam, 1.0 = definitely not spam).
Consider: promotional language, excessive links, suspicious patterns, low-quality content.

Respond with ONLY a number between 0.0 and 1.0:"""
            
            # Use Thesidia's model client if available
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.1}  # Low temp for classification
                )
                result_text = response.get('message', {}).get('content', '0.5')
            else:
                # Fallback to simple analysis
                return 0.5
            
            # Extract number from response
            numbers = re.findall(r'0?\.\d+|1\.0|\d+\.\d+', result_text)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(1.0, score))
            
            return 0.5
        except Exception as e:
            print(f"Error in AI spam detection: {e}")
            return 0.5
    
    def _check_content_uniqueness(self, post: Dict[str, Any]) -> float:
        """Check content uniqueness using AI analysis"""
        content = post.get('content', '')
        
        if len(content) < 20:
            return 0.5  # Too short to assess
        
        # Check for repetitive patterns
        words = content.lower().split()
        if len(words) < 5:
            return 0.5
        
        # Check word diversity
        unique_words = len(set(words))
        word_diversity = unique_words / len(words)
        
        # Check for repeated phrases
        phrases = []
        for i in range(len(words) - 2):
            phrases.append(' '.join(words[i:i+3]))
        
        unique_phrases = len(set(phrases))
        phrase_diversity = unique_phrases / max(len(phrases), 1)
        
        # Combine metrics
        uniqueness_score = (word_diversity * 0.6) + (phrase_diversity * 0.4)
        
        # Use AI for deeper analysis if available
        if self.thesidia and uniqueness_score < 0.7:
            try:
                ai_uniqueness = self._ai_uniqueness_check(content)
                return (uniqueness_score * 0.5) + (ai_uniqueness * 0.5)
            except Exception:
                return uniqueness_score
        
        return max(0.0, min(1.0, uniqueness_score))
    
    def _ai_uniqueness_check(self, content: str) -> float:
        """Use AI to check content uniqueness"""
        if not self.thesidia:
            return 0.5
        
        try:
            prompt = f"""Analyze this social media post for originality and uniqueness:

Post: {content[:500]}

Rate how unique and original this content is (0.0 = completely generic/repetitive, 1.0 = highly original).
Consider: repetitive language, generic phrases, copy-paste patterns, original thought.

Respond with ONLY a number between 0.0 and 1.0:"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.1}
                )
                result_text = response.get('message', {}).get('content', '0.5')
                
                numbers = re.findall(r'0?\.\d+|1\.0|\d+\.\d+', result_text)
                if numbers:
                    return max(0.0, min(1.0, float(numbers[0])))
            
            return 0.5
        except Exception:
            return 0.5
    
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
        """Check sentiment balance using AI analysis"""
        content = post.get('content', '')
        
        # Basic sentiment word check
        positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'happy', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst', 'disgusting', 'hateful']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        # Basic balance score
        total = positive_count + negative_count
        if total == 0:
            basic_balance = 1.0  # Neutral
        else:
            ratio = positive_count / total
            basic_balance = 1.0 - abs(ratio - 0.5) * 2
        
        # Use AI for deeper sentiment analysis
        if self.thesidia:
            try:
                ai_sentiment = self._ai_sentiment_analysis(content)
                # Combine basic and AI analysis
                return (basic_balance * 0.4) + (ai_sentiment * 0.6)
            except Exception:
                return max(0.0, min(1.0, basic_balance))
        
        return max(0.0, min(1.0, basic_balance))
    
    def _ai_sentiment_analysis(self, content: str) -> float:
        """Use AI for sentiment analysis"""
        if not self.thesidia:
            return 0.5
        
        try:
            prompt = f"""Analyze the sentiment balance of this social media post:

Post: {content[:500]}

Rate the sentiment balance (0.0 = extremely negative/positive/unbalanced, 1.0 = well-balanced/constructive).
Consider: extreme negativity, toxic language, excessive positivity that seems fake, balanced discussion.

Respond with ONLY a number between 0.0 and 1.0:"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.1}
                )
                result_text = response.get('message', {}).get('content', '0.5')
                
                numbers = re.findall(r'0?\.\d+|1\.0|\d+\.\d+', result_text)
                if numbers:
                    return max(0.0, min(1.0, float(numbers[0])))
            
            return 0.5
        except Exception:
            return 0.5

