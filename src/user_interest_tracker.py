#!/usr/bin/env python3
"""
User Interest Tracker - Tracks user topics, research threads, and technical journey
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict, Counter
import hashlib

class UserInterestTracker:
    """Track user interests across sessions for refined search and proactive suggestions"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".")
        self.interests_file = self.base_dir / "data" / "user_interests.json"
        
        # Ensure data directory exists
        self.interests_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing interests
        self.interests = self._load_interests()
        
        # Topic extraction patterns
        self.technical_keywords = {
            "code_cracking": ["code", "crack", "reverse engineer", "decrypt", "decode", "pattern", "symbol"],
            "chemistry": ["chemistry", "chemical", "molecular", "biochemistry", "synthesis", "reaction", "compound"],
            "reengineering": ["reengineer", "rebuild", "redesign", "architecture", "system", "structure", "blueprint"],
            "forensic": ["forensic", "investigate", "analyze", "evidence", "trace", "pattern recognition"],
            "physics": ["physics", "quantum", "electromagnetic", "resonance", "frequency", "energy"],
            "history": ["history", "ancient", "origins", "civilization", "archaeology", "historical"],
            "consciousness": ["consciousness", "awareness", "mind", "meditation", "chi gong", "mind-body"],
            "power_structures": ["power", "control", "system", "structure", "archon", "financial", "bitcoin"]
        }
    
    def _load_interests(self) -> Dict:
        """Load user interests from file"""
        if self.interests_file.exists():
            try:
                with open(self.interests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError, ValueError):
                pass
        
        return {
            "topics": {},  # topic -> {count, last_seen, first_seen, related_topics}
            "research_threads": [],  # [{topic, queries, findings, started, last_updated}]
            "technical_domains": {},  # domain -> {count, topics, last_seen}
            "journey_context": {
                "primary_focus": None,
                "active_threads": [],
                "recent_topics": []
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_interests(self):
        """Save user interests to file"""
        self.interests["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.interests_file, 'w', encoding='utf-8') as f:
                json.dump(self.interests, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Failed to save user interests: {e}")
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        text_lower = text.lower()
        topics = []
        
        # Extract technical domains
        for domain, keywords in self.technical_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(domain)
        
        # Extract specific terms (nouns, technical terms)
        # Simple extraction: look for capitalized words or technical terms
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for word in words[:5]:  # Limit to top 5
            if len(word) > 3:  # Filter out short words
                topics.append(word.lower())
        
        # Extract quoted terms (often important concepts)
        quoted = re.findall(r'"([^"]+)"', text)
        topics.extend([q.lower() for q in quoted[:3]])
        
        return list(set(topics))  # Remove duplicates
    
    def track_topic(self, query: str, response: str):
        """Track topics from query and response"""
        # Extract topics from both query and response
        query_topics = self._extract_topics(query)
        response_topics = self._extract_topics(response)
        all_topics = list(set(query_topics + response_topics))
        
        now = datetime.now().isoformat()
        
        # Update topic counts
        for topic in all_topics:
            if topic not in self.interests["topics"]:
                self.interests["topics"][topic] = {
                    "count": 0,
                    "first_seen": now,
                    "last_seen": now,
                    "related_topics": []
                }
            
            self.interests["topics"][topic]["count"] += 1
            self.interests["topics"][topic]["last_seen"] = now
            
            # Track related topics (topics that appear together)
            for other_topic in all_topics:
                if other_topic != topic:
                    if other_topic not in self.interests["topics"][topic]["related_topics"]:
                        self.interests["topics"][topic]["related_topics"].append(other_topic)
        
        # Update journey context
        self.interests["journey_context"]["recent_topics"] = all_topics[:10]  # Keep last 10
        
        # Update primary focus (most frequent topic in last 10 interactions)
        if all_topics:
            topic_counts = Counter([t for topic_list in [all_topics] for t in topic_list])
            if topic_counts:
                self.interests["journey_context"]["primary_focus"] = topic_counts.most_common(1)[0][0]
        
        # Save interests
        self._save_interests()
    
    def get_user_interests(self) -> Dict:
        """Get current user interest profile"""
        # Sort topics by count and recency
        topics_list = []
        for topic, data in self.interests["topics"].items():
            # Calculate score: count * recency_weight
            last_seen = datetime.fromisoformat(data["last_seen"])
            days_ago = (datetime.now() - last_seen).days
            recency_weight = max(0.1, 1.0 - (days_ago / 30.0))  # Decay over 30 days
            score = data["count"] * recency_weight
            
            topics_list.append({
                "topic": topic,
                "count": data["count"],
                "score": score,
                "last_seen": data["last_seen"],
                "related_topics": data["related_topics"][:5]  # Top 5 related
            })
        
        # Sort by score
        topics_list.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "top_topics": topics_list[:10],  # Top 10 topics
            "primary_focus": self.interests["journey_context"]["primary_focus"],
            "recent_topics": self.interests["journey_context"]["recent_topics"],
            "active_threads": self.interests["journey_context"]["active_threads"],
            "technical_domains": self.interests["technical_domains"]
        }
    
    def suggest_related_research(self, current_query: str, limit: int = 3) -> List[str]:
        """Suggest related research threads based on user interests"""
        current_topics = self._extract_topics(current_query)
        suggestions = []
        
        # Find topics related to current query
        for topic in current_topics:
            if topic in self.interests["topics"]:
                related = self.interests["topics"][topic]["related_topics"]
                for related_topic in related[:2]:  # Top 2 related
                    if related_topic not in suggestions:
                        suggestions.append(f"research {related_topic}")
        
        # Get top topics that aren't in current query
        user_interests = self.get_user_interests()
        for topic_data in user_interests["top_topics"][:5]:
            topic = topic_data["topic"]
            if topic not in current_topics and topic not in suggestions:
                suggestions.append(f"explore {topic}")
        
        return suggestions[:limit]
    
    def get_journey_context(self) -> str:
        """Get user's technical journey context for prompts"""
        interests = self.get_user_interests()
        
        context_parts = []
        
        if interests["primary_focus"]:
            context_parts.append(f"user's primary focus: {interests['primary_focus']}")
        
        if interests["recent_topics"]:
            context_parts.append(f"recent topics: {', '.join(interests['recent_topics'][:5])}")
        
        if interests["active_threads"]:
            context_parts.append(f"active research threads: {len(interests['active_threads'])}")
        
        if context_parts:
            return " | ".join(context_parts)
        
        return ""
