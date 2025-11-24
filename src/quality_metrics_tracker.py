#!/usr/bin/env python3
"""
Quality Metrics Tracker - Tracks response quality, depth, pattern recognition, and truth-seeking
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque

class QualityMetricsTracker:
    """Track response quality metrics for engineering optimization"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".")
        self.metrics_file = self.base_dir / "data" / "quality_metrics.json"
        
        # Ensure data directory exists
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing metrics
        self.metrics = self._load_metrics()
        
        # Quality indicators
        self.depth_indicators = [
            "mechanism", "molecular", "cellular", "systemic", "biochemical", "pathway",
            "neurotransmitter", "autonomic", "nervous system", "HPA axis", "cortisol",
            "bioelectric", "resonance", "frequency", "electromagnetic"
        ]
        
        self.pattern_indicators = [
            "pattern", "connection", "relates", "links", "connects", "synthesis",
            "cross-reference", "across", "between", "interconnected", "weave"
        ]
        
        self.truth_seeking_indicators = [
            "exposes", "reveals", "unveils", "hidden", "suppressed", "marginalized",
            "dismissed", "redacted", "transformed", "systematic", "power structure",
            "archon", "control", "manipulation"
        ]
    
    def _load_metrics(self) -> Dict:
        """Load quality metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError, ValueError):
                pass
        
        return {
            "interactions": [],
            "quality_trends": {
                "depth_scores": [],
                "pattern_scores": [],
                "truth_seeking_scores": [],
                "overall_scores": []
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_metrics(self):
        """Save quality metrics to file"""
        self.metrics["last_updated"] = datetime.now().isoformat()
        
        # Convert deques to lists for JSON serialization
        metrics_copy = json.loads(json.dumps(self.metrics, default=str))
        for key in ["depth_scores", "pattern_scores", "truth_seeking_scores", "overall_scores"]:
            if key in metrics_copy.get("quality_trends", {}):
                metrics_copy["quality_trends"][key] = list(metrics_copy["quality_trends"][key])
        
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_copy, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Failed to save quality metrics: {e}")
    
    def measure_response_quality(self, query: str, response: str) -> Dict[str, float]:
        """Measure response quality scores"""
        response_lower = response.lower()
        
        # Depth score (0-1)
        depth_score = self._measure_depth(response_lower, query)
        
        # Pattern recognition score (0-1)
        pattern_score = self._measure_pattern_recognition(response_lower)
        
        # Truth-seeking score (0-1)
        truth_seeking_score = self._measure_truth_seeking(response_lower, query)
        
        # Overall score (weighted average)
        overall_score = (depth_score * 0.3 + pattern_score * 0.3 + truth_seeking_score * 0.4)
        
        scores = {
            "depth": depth_score,
            "pattern_recognition": pattern_score,
            "truth_seeking": truth_seeking_score,
            "overall": overall_score
        }
        
        # Ensure quality_trends exists
        if "quality_trends" not in self.metrics:
            self.metrics["quality_trends"] = {
                "depth_scores": [],
                "pattern_scores": [],
                "truth_seeking_scores": [],
                "overall_scores": []
            }
        
        # Store in metrics (keep only last 100)
        self.metrics["quality_trends"]["depth_scores"].append(depth_score)
        self.metrics["quality_trends"]["pattern_scores"].append(pattern_score)
        self.metrics["quality_trends"]["truth_seeking_scores"].append(truth_seeking_score)
        self.metrics["quality_trends"]["overall_scores"].append(overall_score)
        
        # Keep only last 100 for each
        for key in ["depth_scores", "pattern_scores", "truth_seeking_scores", "overall_scores"]:
            scores_list = self.metrics["quality_trends"].get(key, [])
            if len(scores_list) > 100:
                self.metrics["quality_trends"][key] = scores_list[-100:]
        
        # Store interaction
        self.metrics["interactions"].append({
            "query": query[:200],
            "response_length": len(response),
            "scores": scores,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 interactions
        if len(self.metrics["interactions"]) > 100:
            self.metrics["interactions"] = self.metrics["interactions"][-100:]
        
        self._save_metrics()
        
        return scores
    
    def _measure_depth(self, response_lower: str, query: str) -> float:
        """Measure mechanism depth score"""
        # Check for mind-body topics
        mind_body_keywords = ["meditation", "chi gong", "qigong", "yoga", "breathing", "mind-body"]
        is_mind_body = any(keyword in query.lower() for keyword in mind_body_keywords)
        
        if is_mind_body:
            # For mind-body topics, check for mechanism depth
            mechanism_count = sum(1 for indicator in self.depth_indicators if indicator in response_lower)
            # Normalize: 5+ indicators = high depth (1.0), 0 = no depth (0.0)
            return min(1.0, mechanism_count / 5.0)
        else:
            # For other topics, check for general depth (length, detail, analysis)
            # Longer, more detailed responses = higher depth
            word_count = len(response_lower.split())
            if word_count > 500:
                return 1.0
            elif word_count > 200:
                return 0.7
            elif word_count > 100:
                return 0.4
            else:
                return 0.2
    
    def _measure_pattern_recognition(self, response_lower: str) -> float:
        """Measure pattern recognition score"""
        pattern_count = sum(1 for indicator in self.pattern_indicators if indicator in response_lower)
        # Normalize: 5+ indicators = high pattern recognition (1.0)
        return min(1.0, pattern_count / 5.0)
    
    def _measure_truth_seeking(self, response_lower: str, query: str) -> float:
        """Measure truth-seeking score (unfiltered, direct, evidence-based)"""
        # Check for truth-seeking indicators
        truth_count = sum(1 for indicator in self.truth_seeking_indicators if indicator in response_lower)
        
        # Check for protective hedging (negative indicator)
        hedging_phrases = [
            "it's hard to say", "it's difficult", "well, it's", "while i enjoy",
            "it should be noted", "keep in mind", "please note"
        ]
        hedging_count = sum(1 for phrase in hedging_phrases if phrase in response_lower)
        
        # Check for direct start (positive indicator)
        direct_start = not response_lower.startswith(("well", "while", "it's", "i think", "i believe"))
        
        # Calculate score
        truth_score = min(1.0, truth_count / 3.0)  # 3+ indicators = high
        hedging_penalty = min(0.5, hedging_count * 0.2)  # Penalty for hedging
        direct_bonus = 0.2 if direct_start else 0.0
        
        return min(1.0, max(0.0, truth_score - hedging_penalty + direct_bonus))
    
    def track_truth_seeking_indicators(self, response: str) -> Dict[str, bool]:
        """Track specific truth-seeking indicators"""
        response_lower = response.lower()
        
        return {
            "exposes_hidden_truths": any(word in response_lower for word in ["exposes", "reveals", "unveils", "hidden"]),
            "challenges_mainstream": any(word in response_lower for word in ["mainstream", "conventional", "traditional view"]),
            "presents_evidence": any(word in response_lower for word in ["evidence", "research shows", "studies indicate"]),
            "no_protective_hedging": not any(phrase in response_lower for phrase in ["it's hard to say", "it's difficult", "while i enjoy"])
        }
    
    def track_mechanism_depth(self, response: str, topic: str) -> Dict[str, Any]:
        """Track mechanism depth for specific topics"""
        response_lower = response.lower()
        
        # Check for chemistry/biology indicators
        chemistry_indicators = ["molecular", "biochemical", "pathway", "enzyme", "protein", "neurotransmitter"]
        biology_indicators = ["cellular", "systemic", "autonomic", "nervous system", "HPA axis", "cortisol"]
        physics_indicators = ["bioelectric", "resonance", "frequency", "electromagnetic", "wave"]
        
        chemistry_count = sum(1 for ind in chemistry_indicators if ind in response_lower)
        biology_count = sum(1 for ind in biology_indicators if ind in response_lower)
        physics_count = sum(1 for ind in physics_indicators if ind in response_lower)
        
        return {
            "chemistry_depth": chemistry_count,
            "biology_depth": biology_count,
            "physics_depth": physics_count,
            "total_mechanism_indicators": chemistry_count + biology_count + physics_count,
            "has_mechanism_depth": (chemistry_count + biology_count + physics_count) >= 3
        }
    
    def get_quality_trends(self) -> Dict[str, float]:
        """Get quality trends (averages over last N interactions)"""
        trends = {}
        
        for metric_name in ["depth_scores", "pattern_scores", "truth_seeking_scores", "overall_scores"]:
            scores = self.metrics["quality_trends"].get(metric_name, [])
            if isinstance(scores, deque):
                scores = list(scores)
            if scores:
                trends[metric_name] = {
                    "average": sum(scores) / len(scores),
                    "recent_average": sum(scores[-10:]) / min(10, len(scores)) if len(scores) >= 10 else sum(scores) / len(scores),
                    "count": len(scores)
                }
            else:
                trends[metric_name] = {
                    "average": 0.0,
                    "recent_average": 0.0,
                    "count": 0
                }
        
        return trends

