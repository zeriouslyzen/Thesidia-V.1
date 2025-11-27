#!/usr/bin/env python3
"""
AI Recommendations
Generate AI-powered content recommendations based on user interests
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Try to import dependencies
try:
    from user_interest_tracker import UserInterestTracker
    INTEREST_TRACKER_AVAILABLE = True
except ImportError:
    try:
        from src.user_interest_tracker import UserInterestTracker
        INTEREST_TRACKER_AVAILABLE = True
    except ImportError:
        INTEREST_TRACKER_AVAILABLE = False
        UserInterestTracker = None

try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    THESIDIA_AVAILABLE = True
except ImportError:
    THESIDIA_AVAILABLE = False
    ThesidiaHybridAdaptive = None

try:
    from webapp.social.post_manager import PostManager
    from webapp.social.feed_ranker import FeedRanker
except ImportError:
    PostManager = None
    FeedRanker = None


class AIRecommendations:
    """
    AI Recommendations Engine
    Generates personalized content recommendations using AI
    """
    
    def __init__(self, base_dir: Path = None, thesidia: Optional[Any] = None):
        """
        Initialize AI recommendations engine
        
        Args:
            base_dir: Base directory for data storage
            thesidia: Optional ThesidiaHybridAdaptive instance
        """
        self.base_dir = base_dir or Path(".")
        self.thesidia = thesidia
        
        if PostManager:
            self.post_manager = PostManager(base_dir=base_dir)
        else:
            self.post_manager = None
        
        if FeedRanker:
            self.feed_ranker = FeedRanker(base_dir=base_dir)
        else:
            self.feed_ranker = None
        
        # Initialize interest tracker
        if INTEREST_TRACKER_AVAILABLE:
            try:
                self.interest_tracker = UserInterestTracker(base_dir=base_dir)
            except Exception:
                self.interest_tracker = None
        else:
            self.interest_tracker = None
        
        # Initialize Thesidia if available and not provided
        if not self.thesidia and THESIDIA_AVAILABLE:
            try:
                self.thesidia = ThesidiaHybridAdaptive()
            except Exception:
                self.thesidia = None
    
    def recommend_posts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recommend posts for a user using AI"""
        if not self.post_manager or not self.feed_ranker:
            return []
        """
        Recommend posts for a user using AI
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended post dictionaries
        """
        try:
            # Get user interests
            if self.interest_tracker:
                interests = self.interest_tracker.get_user_interests()
                top_topics = interests.get('topics', {})
                # Sort by count
                sorted_topics = sorted(
                    top_topics.items(),
                    key=lambda x: x[1].get('count', 0),
                    reverse=True
                )[:5]
                interest_keywords = [topic for topic, _ in sorted_topics]
            else:
                interest_keywords = []
            
            # Get all recent posts
            all_posts = self.post_manager.get_posts_by_date(limit=100, offset=0)
            
            # Rank posts using feed ranker
            ranked_posts = self.feed_ranker.rank_posts(all_posts, user_id)
            
            # Filter by interests if available
            if interest_keywords:
                recommended = []
                for post in ranked_posts:
                    content = post.get('content', '').lower()
                    tags = [t.lower() for t in post.get('tags', [])]
                    
                    # Check if post matches interests
                    matches = any(
                        keyword.lower() in content or keyword.lower() in tags
                        for keyword in interest_keywords
                    )
                    
                    if matches or len(recommended) < limit:
                        recommended.append(post)
                        if len(recommended) >= limit:
                            break
                
                return recommended[:limit]
            
            return ranked_posts[:limit]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []
    
    def suggest_content_topics(self, user_id: str) -> List[str]:
        """
        Suggest content topics for user to post about using AI
        
        Args:
            user_id: User ID
            
        Returns:
            List of suggested topics
        """
        if not self.thesidia or not self.interest_tracker:
            return []
        
        try:
            # Get user interests
            interests = self.interest_tracker.get_user_interests()
            top_topics = interests.get('topics', {})
            
            # Get top 3 interests
            sorted_topics = sorted(
                top_topics.items(),
                key=lambda x: x[1].get('count', 0),
                reverse=True
            )[:3]
            
            topic_names = [topic for topic, _ in sorted_topics]
            
            prompt = f"""Based on this user's interests: {', '.join(topic_names)}

Suggest 5 interesting content topics or questions they could post about on social media.
Make suggestions that are:
- Related to their interests
- Engaging and thought-provoking
- Likely to generate discussion

Respond with just a simple list, one topic per line:"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.7}
                )
                result = response.get('message', {}).get('content', '')
                
                # Extract topics from response
                topics = []
                for line in result.split('\n'):
                    line = line.strip()
                    # Remove numbering
                    line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    # Remove dashes/bullets
                    line = re.sub(r'^[-•]\s*', '', line)
                    if line and len(line) > 5:
                        topics.append(line)
                
                return topics[:5]
        except Exception as e:
            print(f"Error generating content suggestions: {e}")
        
        return []
    
    def _extract_topics_from_response(self, response_text: str) -> List[str]:
        """Extract topics from AI response"""
        import re
        topics = []
        for line in response_text.split('\n'):
            line = line.strip()
            # Remove numbering
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            # Remove dashes/bullets
            line = re.sub(r'^[-•]\s*', '', line)
            if line and len(line) > 5:
                topics.append(line)
        return topics
    
    def find_similar_users(self, user_id: str, limit: int = 5) -> List[str]:
        """
        Find users with similar interests using AI
        
        Args:
            user_id: User ID
            limit: Maximum number of similar users
            
        Returns:
            List of user IDs
        """
        # This would require user comparison logic
        # For now, return empty list
        # In production, would compare interest profiles
        return []

