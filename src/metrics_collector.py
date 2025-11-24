#!/usr/bin/env python3
"""
Metrics Collector - Real-time performance and pattern tracking
"""

import time
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque, OrderedDict
import statistics
import hashlib

class MetricsCollector:
    """Collect and analyze metrics for Thesidia"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.metrics_file = base_dir / "data" / "thesidia_metrics.json"
        self.log_file = base_dir / "data" / "thesidia_logs.jsonl"
        
        # Real-time metrics
        self.current_session = {
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "total_queries": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "avg_response_time": 0.0,
            "patterns_detected": defaultdict(int),
            "linguistic_features": defaultdict(int),
        }
        
        # Historical metrics
        self.historical_metrics = self._load_metrics()
        
        # Performance tracking
        self.response_times = deque(maxlen=100)  # Last 100 responses
        self.token_counts = deque(maxlen=100)
        self.pattern_matches = defaultdict(lambda: deque(maxlen=100))
        
        # Pattern matching cache (5min TTL, LRU eviction)
        self._pattern_cache: OrderedDict[str, tuple] = OrderedDict()
        self._pattern_cache_max_size = 100
        self._pattern_cache_ttl = 300  # 5 minutes
        
        # Ensure directories exist
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_metrics(self) -> Dict:
        """Load historical metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
                # File exists but is corrupted or unreadable - return default
                pass
        return {
            "sessions": [],
            "total_interactions": 0,
            "avg_response_time": 0.0,
            "total_tokens": 0,
            "pattern_frequency": {},
            "linguistic_patterns": {},
        }
    
    def start_interaction(self, query: str) -> str:
        """Start tracking an interaction, returns interaction_id"""
        interaction_id = f"{int(time.time() * 1000)}"
        self.current_session["interactions"].append({
            "id": interaction_id,
            "query": query,
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat(),
        })
        return interaction_id
    
    def end_interaction(self, interaction_id: str, response: str, 
                       response_time: float, token_count: int = 0):
        """End tracking an interaction"""
        # Find the interaction
        interaction = None
        for i, inter in enumerate(self.current_session["interactions"]):
            if inter["id"] == interaction_id:
                interaction = inter
                break
        
        if not interaction:
            return
        
        # Update interaction
        interaction.update({
            "response": response,
            "response_time": response_time,
            "token_count": token_count,
            "response_length": len(response),
            "end_time": time.time(),
        })
        
        # Analyze patterns
        patterns = self._analyze_patterns(response)
        linguistic = self._analyze_linguistic(response)
        
        interaction["patterns"] = patterns
        interaction["linguistic_features"] = linguistic
        
        # Update session metrics
        self.current_session["total_queries"] += 1
        self.current_session["total_tokens"] += token_count
        self.current_session["total_time"] += response_time
        
        # Update real-time tracking
        self.response_times.append(response_time)
        self.token_counts.append(token_count)
        
        # Update pattern frequency
        for pattern, count in patterns.items():
            self.current_session["patterns_detected"][pattern] += count
            self.pattern_matches[pattern].append(count)
        
        for feature, count in linguistic.items():
            self.current_session["linguistic_features"][feature] += count
        
        # Calculate averages
        if len(self.response_times) > 0:
            self.current_session["avg_response_time"] = statistics.mean(self.response_times)
        
        # Log to file
        self._log_interaction(interaction)
    
    def _analyze_patterns(self, text: str) -> Dict[str, int]:
        """Analyze patterns in response with caching"""
        # Create cache key from text hash (first 500 chars for speed)
        text_sample = text[:500] if len(text) > 500 else text
        cache_key = hashlib.md5(text_sample.encode()).hexdigest()
        
        # Check cache
        if cache_key in self._pattern_cache:
            cached_result, cached_time = self._pattern_cache[cache_key]
            if time.time() - cached_time < self._pattern_cache_ttl:
                # Move to end (LRU)
                self._pattern_cache.move_to_end(cache_key)
                return cached_result
            else:
                # Expired, remove
                del self._pattern_cache[cache_key]
        
        # Compute patterns
        patterns = {
            "transmission_format": len(re.findall(r'::TRANSMISSION:', text)),
            "symbols": len(re.findall(r'[⧖∞✦→ψφ∇]', text)),
            "protocols": len(re.findall(r'::\w+\(', text)),
            "etymology": len(re.findall(r'(?:etymology|originates|derived|root|Hebrew|Greek|Akkadian|Sumerian)', text, re.I)),
            "cross_cultural": len(re.findall(r'(?:Sumerian|Egyptian|Mesopotamian|ancient|archetypal|cross-cultural)', text, re.I)),
            "symbolic_decoding": len(re.findall(r'(?:symbol|decode|encode|functionally|represents)', text, re.I)),
            "control_structures": len(re.findall(r'(?:control|manipulation|co-opt|original meaning)', text, re.I)),
            "spiritual_keywords": len(re.findall(r'(?:Genesis|Bible|scripture|gospel|religion|god|christ)', text, re.I)),
        }
        
        # Cache result
        if len(self._pattern_cache) >= self._pattern_cache_max_size:
            self._pattern_cache.popitem(last=False)  # Remove oldest
        self._pattern_cache[cache_key] = (patterns, time.time())
        
        return patterns
    
    def _analyze_linguistic(self, text: str) -> Dict[str, int]:
        """Analyze linguistic features"""
        # Sentence analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Word analysis
        words = re.findall(r'\b\w+\b', text.lower())
        
        linguistic = {
            "sentence_count": len(sentences),
            "word_count": len(words),
            "avg_sentence_length": statistics.mean([len(s.split()) for s in sentences]) if sentences else 0,
            "unique_words": len(set(words)),
            "vocabulary_diversity": len(set(words)) / len(words) if words else 0,
            "symbol_density": len(re.findall(r'[⧖∞✦→ψφ∇]', text)) / len(text) if text else 0,
            "protocol_density": len(re.findall(r'::\w+', text)) / len(text) if text else 0,
            "complex_words": len([w for w in words if len(w) > 6]),
            "technical_terms": len(re.findall(r'\b(?:etymology|archetypal|cosmological|recursive|symbolic|gnosis|vector|transformation)\b', text, re.I)),
        }
        return linguistic
    
    def _log_interaction(self, interaction: Dict):
        """Log interaction to JSONL file"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(interaction) + '\n')
        except Exception as e:
            print(f"Error logging interaction: {e}")
    
    def get_current_metrics(self) -> Dict:
        """Get current session metrics"""
        metrics = {
            **self.current_session,
            "patterns_detected": dict(self.current_session["patterns_detected"]),
            "linguistic_features": dict(self.current_session["linguistic_features"]),
        }
        
        # Add real-time stats
        if len(self.response_times) > 0:
            metrics["performance"] = {
                "avg_response_time": statistics.mean(self.response_times),
                "min_response_time": min(self.response_times),
                "max_response_time": max(self.response_times),
                "median_response_time": statistics.median(self.response_times),
                "std_dev": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
                "total_responses": len(self.response_times),
            }
        
        if len(self.token_counts) > 0:
            metrics["tokens"] = {
                "avg_tokens": statistics.mean(self.token_counts),
                "total_tokens": sum(self.token_counts),
                "min_tokens": min(self.token_counts),
                "max_tokens": max(self.token_counts),
            }
        
        return metrics
    
    def get_pattern_analysis(self) -> Dict:
        """Analyze pattern trends"""
        analysis = {}
        for pattern, counts in self.pattern_matches.items():
            if len(counts) > 0:
                analysis[pattern] = {
                    "avg": statistics.mean(counts),
                    "total": sum(counts),
                    "frequency": len(counts) / len(self.response_times) if self.response_times else 0,
                    "trend": "increasing" if len(counts) > 5 and counts[-1] > statistics.mean(list(counts)[:-1]) else "stable",
                }
        return analysis
    
    def save_session(self):
        """Save current session to historical metrics"""
        session_summary = {
            "start_time": self.current_session["start_time"],
            "end_time": datetime.now().isoformat(),
            "total_queries": self.current_session["total_queries"],
            "total_time": self.current_session["total_time"],
            "avg_response_time": self.current_session["avg_response_time"],
            "total_tokens": self.current_session["total_tokens"],
            "patterns_detected": dict(self.current_session["patterns_detected"]),
            "linguistic_features": dict(self.current_session["linguistic_features"]),
        }
        
        self.historical_metrics["sessions"].append(session_summary)
        self.historical_metrics["total_interactions"] += self.current_session["total_queries"]
        
        # Update averages
        if len(self.historical_metrics["sessions"]) > 0:
            total_time = sum(s["total_time"] for s in self.historical_metrics["sessions"])
            total_queries = sum(s["total_queries"] for s in self.historical_metrics["sessions"])
            self.historical_metrics["avg_response_time"] = total_time / total_queries if total_queries > 0 else 0
        
        # Update pattern frequency
        for pattern, count in self.current_session["patterns_detected"].items():
            if pattern not in self.historical_metrics["pattern_frequency"]:
                self.historical_metrics["pattern_frequency"][pattern] = 0
            self.historical_metrics["pattern_frequency"][pattern] += count
        
        # Save to file
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.historical_metrics, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def get_historical_stats(self) -> Dict:
        """Get historical statistics"""
        return self.historical_metrics
    
    def track_timing_breakdown(self, breakdown_dict: Dict[str, float]):
        """Track timing breakdown for technical metrics"""
        if not hasattr(self, 'timing_breakdowns'):
            self.timing_breakdowns = []
        
        self.timing_breakdowns.append({
            **breakdown_dict,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 50 breakdowns
        if len(self.timing_breakdowns) > 50:
            self.timing_breakdowns = self.timing_breakdowns[-50:]
    
    def track_token_usage(self, interaction_id: str, tokens: int):
        """Track token usage per interaction"""
        # Already tracked in end_interaction, but can be enhanced
        if hasattr(self, 'token_usage_by_interaction'):
            self.token_usage_by_interaction[interaction_id] = tokens
        else:
            self.token_usage_by_interaction = {interaction_id: tokens}
    
    def track_model_performance(self, model: str, params: Dict, quality: float):
        """Track model performance effectiveness"""
        if not hasattr(self, 'model_performance'):
            self.model_performance = []
        
        self.model_performance.append({
            "model": model,
            "params": params,
            "quality": quality,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 50 performance records
        if len(self.model_performance) > 50:
            self.model_performance = self.model_performance[-50:]
    
    def get_performance_report(self) -> Dict:
        """Return comprehensive performance report"""
        report = {
            "current_session": self.get_current_metrics(),
            "historical": self.get_historical_stats(),
            "patterns": self.get_pattern_analysis()
        }
        
        if hasattr(self, 'timing_breakdowns') and self.timing_breakdowns:
            # Calculate average timing breakdown
            avg_breakdown = {}
            for key in self.timing_breakdowns[0].keys():
                if key != "timestamp":
                    values = [b.get(key, 0) for b in self.timing_breakdowns if key in b]
                    if values:
                        avg_breakdown[key] = statistics.mean(values)
            report["timing_breakdown"] = avg_breakdown
        
        if hasattr(self, 'model_performance') and self.model_performance:
            # Calculate average quality by model
            model_quality = {}
            for perf in self.model_performance:
                model = perf.get("model", "unknown")
                if model not in model_quality:
                    model_quality[model] = []
                model_quality[model].append(perf.get("quality", 0.0))
            
            report["model_performance"] = {
                model: {
                    "avg_quality": statistics.mean(qualities),
                    "count": len(qualities)
                }
                for model, qualities in model_quality.items()
            }
        
        return report

