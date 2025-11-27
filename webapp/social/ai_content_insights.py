#!/usr/bin/env python3
"""
AI Content Insights
Generate AI-powered insights, summaries, and recommendations for posts
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import sys
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Try to import Thesidia
try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    THESIDIA_AVAILABLE = True
except ImportError:
    THESIDIA_AVAILABLE = False
    ThesidiaHybridAdaptive = None


class AIContentInsights:
    """
    AI Content Insights Generator
    Provides AI-powered insights, summaries, and recommendations
    """
    
    def __init__(self, base_dir: Path = None, thesidia: Optional[Any] = None):
        """
        Initialize AI content insights generator
        
        Args:
            base_dir: Base directory for data storage
            thesidia: Optional ThesidiaHybridAdaptive instance
        """
        self.base_dir = base_dir or Path(".")
        self.thesidia = thesidia
        
        # Initialize Thesidia if available and not provided
        if not self.thesidia and THESIDIA_AVAILABLE:
            try:
                self.thesidia = ThesidiaHybridAdaptive()
            except Exception:
                self.thesidia = None
    
    def generate_summary(self, post: Dict[str, Any], max_length: int = 150) -> str:
        """
        Generate AI summary of a post
        
        Args:
            post: Post data dictionary
            max_length: Maximum summary length
            
        Returns:
            Summary string
        """
        content = post.get('content', '')
        if len(content) <= max_length:
            return content
        
        if not self.thesidia:
            # Fallback: simple truncation
            return content[:max_length] + "..."
        
        try:
            prompt = f"""Summarize this social media post in {max_length} characters or less:

Post: {content}

Provide a concise summary that captures the main point:"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.3}
                )
                summary = response.get('message', {}).get('content', '').strip()
                
                # Clean up summary
                summary = re.sub(r'^Summary[:\s]*', '', summary, flags=re.IGNORECASE)
                summary = summary.strip()
                
                if len(summary) > max_length:
                    summary = summary[:max_length] + "..."
                
                return summary
        except Exception:
            pass
        
        # Fallback
        return content[:max_length] + "..."
    
    def generate_key_points(self, post: Dict[str, Any]) -> List[str]:
        """
        Extract key points from a post using AI
        
        Args:
            post: Post data dictionary
            
        Returns:
            List of key points
        """
        content = post.get('content', '')
        
        if not self.thesidia or len(content) < 50:
            # Fallback: simple sentence extraction
            sentences = re.split(r'[.!?]+', content)
            return [s.strip() for s in sentences[:3] if len(s.strip()) > 10]
        
        try:
            prompt = f"""Extract 3-5 key points from this social media post:

Post: {content}

List the main points as a numbered list:"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.2}
                )
                result = response.get('message', {}).get('content', '')
                
                # Extract numbered points
                points = re.findall(r'\d+[\.\)]\s*(.+?)(?=\n\d+[\.\)]|\n\n|$)', result, re.DOTALL)
                if points:
                    return [p.strip() for p in points[:5]]
                
                # Fallback: split by lines
                lines = [l.strip() for l in result.split('\n') if l.strip() and not l.strip().startswith('#')]
                return lines[:5]
        except Exception:
            pass
        
        # Fallback
        sentences = re.split(r'[.!?]+', content)
        return [s.strip() for s in sentences[:3] if len(s.strip()) > 10]
    
    def suggest_related_topics(self, post: Dict[str, Any]) -> List[str]:
        """
        Suggest related topics using AI
        
        Args:
            post: Post data dictionary
            
        Returns:
            List of suggested topics
        """
        content = post.get('content', '')
        tags = post.get('tags', [])
        
        if not self.thesidia:
            return tags[:5]  # Return existing tags
        
        try:
            prompt = f"""Based on this social media post, suggest 3-5 related topics or hashtags:

Post: {content}
Current tags: {', '.join(tags) if tags else 'None'}

Suggest related topics (as simple keywords, not hashtags):"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.4}
                )
                result = response.get('message', {}).get('content', '')
                
                # Extract topics (comma-separated or line-separated)
                topics = []
                for line in result.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # Split by comma
                    line_topics = [t.strip().lower() for t in line.split(',')]
                    topics.extend(line_topics)
                
                # Clean topics
                topics = [t for t in topics if len(t) > 2 and len(t) < 30]
                return topics[:5]
        except Exception:
            pass
        
        return tags[:5] if tags else []
    
    def detect_sentiment(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect sentiment and emotional tone using AI
        
        Args:
            post: Post data dictionary
            
        Returns:
            Dictionary with sentiment analysis
        """
        content = post.get('content', '')
        
        if not self.thesidia:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": []
            }
        
        try:
            prompt = f"""Analyze the sentiment and emotional tone of this social media post:

Post: {content}

Respond in JSON format:
{{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.0-1.0,
    "emotions": ["emotion1", "emotion2"],
    "tone": "description"
}}"""
            
            if hasattr(self.thesidia, 'model_client') and self.thesidia.model_client:
                response = self.thesidia.model_client.chat(
                    model=self.thesidia.model,
                    input_text=prompt,
                    options={"temperature": 0.2}
                )
                result = response.get('message', {}).get('content', '')
                
                # Try to parse JSON
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    import json
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
        except Exception:
            pass
        
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "emotions": []
        }

