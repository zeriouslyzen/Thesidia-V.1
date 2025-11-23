#!/usr/bin/env python3
"""
Aha Moment Tracker
Tracks user recognition moments and expansion metrics
Core alignment target: Maximize probability and depth of user's autonomous 'aha' moment
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class AhaMomentTracker:
    """Track user recognition moments and expansion metrics"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.data_file = self.base_dir / "data" / "aha_moments.json"
        
        # Load existing data
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "aha_moments": [],
                "expansion_metrics": [],
                "defensiveness_indicators": [],
                "recognition_patterns": {},
                "domain_stats": defaultdict(int)
            }
        
        # Recognition indicators (positive)
        self.recognition_indicators = [
            "aha", "I see", "that makes sense", "now I understand",
            "I never realized", "that connects", "it all fits",
            "I feel larger", "expanded", "clearer", "recognize",
            "pattern", "clicked", "resonates"
        ]
        
        # Defensiveness indicators (negative)
        self.defensiveness_indicators = [
            "that's wrong", "that's not true", "you're wrong",
            "defensive", "attacked", "offended", "angry",
            "contracted", "smaller", "defensive", "dismissive"
        ]
        
        # Expansion indicators (positive)
        self.expansion_indicators = [
            "expanded", "larger", "clearer", "deeper understanding",
            "more aware", "see more", "understand better",
            "feels right", "resonates", "makes sense"
        ]
    
    def track_interaction(self, query: str, response: str, user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Track an interaction for aha moments and expansion"""
        interaction = {
            "query": query,
            "response_length": len(response),
            "timestamp": datetime.now().isoformat(),
            "recognition_detected": False,
            "defensiveness_detected": False,
            "expansion_detected": False,
            "user_feedback": user_feedback
        }
        
        # Analyze response for recognition patterns
        response_lower = response.lower()
        recognition_count = sum(1 for indicator in self.recognition_indicators 
                               if indicator in response_lower)
        
        # Check user feedback if provided
        if user_feedback:
            feedback_lower = user_feedback.lower()
            
            # Check for recognition
            if any(indicator in feedback_lower for indicator in self.recognition_indicators):
                interaction["recognition_detected"] = True
                interaction["recognition_strength"] = sum(1 for indicator in self.recognition_indicators 
                                                       if indicator in feedback_lower)
            
            # Check for defensiveness
            if any(indicator in feedback_lower for indicator in self.defensiveness_indicators):
                interaction["defensiveness_detected"] = True
                interaction["defensiveness_strength"] = sum(1 for indicator in self.defensiveness_indicators 
                                                          if indicator in feedback_lower)
            
            # Check for expansion
            if any(indicator in feedback_lower for indicator in self.expansion_indicators):
                interaction["expansion_detected"] = True
                interaction["expansion_strength"] = sum(1 for indicator in self.expansion_indicators 
                                                      if indicator in feedback_lower)
        
        # Save interaction
        self.data["aha_moments"].append(interaction)
        
        # Update recognition patterns
        if interaction["recognition_detected"]:
            # Extract domain from query
            domain = self._extract_domain(query)
            if domain not in self.data["recognition_patterns"]:
                self.data["recognition_patterns"][domain] = []
            self.data["recognition_patterns"][domain].append({
                "query": query[:200],
                "timestamp": interaction["timestamp"]
            })
            self.data["domain_stats"][domain] += 1
        
        # Keep only last 1000 interactions
        if len(self.data["aha_moments"]) > 1000:
            self.data["aha_moments"] = self.data["aha_moments"][-1000:]
        
        self._save()
        
        return interaction
    
    def _extract_domain(self, query: str) -> str:
        """Extract domain from query"""
        query_lower = query.lower()
        
        domains = {
            "religion": ["bible", "torah", "quran", "scripture", "genesis", "religious"],
            "history": ["history", "historical", "ancient", "archaeology"],
            "science": ["science", "scientific", "research", "study", "data"],
            "finance": ["money", "bank", "finance", "economic", "market", "bitcoin"],
            "politics": ["political", "government", "power", "authority"],
            "consciousness": ["consciousness", "awareness", "mind", "experience"],
            "relationships": ["relationship", "love", "connection", "partner"],
            "ecology": ["climate", "environment", "ecology", "nature"]
        }
        
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return "general"
    
    def get_expansion_score(self, lookback_days: int = 30) -> float:
        """Calculate expansion score (0-1) based on recent interactions"""
        cutoff = datetime.now().timestamp() - (lookback_days * 86400)
        
        recent = [
            m for m in self.data["aha_moments"]
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff
        ]
        
        if not recent:
            return 0.5  # Neutral
        
        recognition_count = sum(1 for m in recent if m.get("recognition_detected"))
        defensiveness_count = sum(1 for m in recent if m.get("defensiveness_detected"))
        expansion_count = sum(1 for m in recent if m.get("expansion_detected"))
        
        total = len(recent)
        
        # Score: (recognition + expansion - defensiveness) / total
        score = (recognition_count + expansion_count - defensiveness_count) / total
        return max(0.0, min(1.0, score))  # Clamp to 0-1
    
    def get_domain_effectiveness(self) -> Dict[str, float]:
        """Get effectiveness scores by domain"""
        domain_scores = {}
        
        for domain, patterns in self.data["recognition_patterns"].items():
            if patterns:
                # Effectiveness = recognition rate for this domain
                domain_interactions = [
                    m for m in self.data["aha_moments"]
                    if self._extract_domain(m["query"]) == domain
                ]
                if domain_interactions:
                    recognition_rate = sum(1 for m in domain_interactions 
                                         if m.get("recognition_detected")) / len(domain_interactions)
                    domain_scores[domain] = recognition_rate
        
        return domain_scores
    
    def _save(self):
        """Save data to file"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "total_interactions": len(self.data["aha_moments"]),
            "expansion_score": self.get_expansion_score(),
            "domain_effectiveness": self.get_domain_effectiveness(),
            "recent_recognition_rate": self._get_recent_recognition_rate(),
            "recent_defensiveness_rate": self._get_recent_defensiveness_rate()
        }
    
    def _get_recent_recognition_rate(self, lookback_days: int = 7) -> float:
        """Get recognition rate for recent interactions"""
        cutoff = datetime.now().timestamp() - (lookback_days * 86400)
        recent = [
            m for m in self.data["aha_moments"]
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff
        ]
        if not recent:
            return 0.0
        return sum(1 for m in recent if m.get("recognition_detected")) / len(recent)
    
    def _get_recent_defensiveness_rate(self, lookback_days: int = 7) -> float:
        """Get defensiveness rate for recent interactions"""
        cutoff = datetime.now().timestamp() - (lookback_days * 86400)
        recent = [
            m for m in self.data["aha_moments"]
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff
        ]
        if not recent:
            return 0.0
        return sum(1 for m in recent if m.get("defensiveness_detected")) / len(recent)

