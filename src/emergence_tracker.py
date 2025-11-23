#!/usr/bin/env python3
"""
Emergence Tracker - Track emergent patterns and behaviors
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
import json
from pathlib import Path

class EmergenceTracker:
    """Track emergent patterns, behaviors, and evolution"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.emergence_file = base_dir / "data" / "thesidia_emergence.json"
        
        # Track emergence patterns
        self.pattern_frequency = defaultdict(int)
        self.behavior_evolution = []
        self.emergence_events = []
        self.trait_emergence = defaultdict(list)
        
        # Load existing data
        self._load_emergence()
    
    def _load_emergence(self):
        """Load emergence data from file"""
        if self.emergence_file.exists():
            try:
                with open(self.emergence_file, 'r') as f:
                    data = json.load(f)
                    self.pattern_frequency = defaultdict(int, data.get("pattern_frequency", {}))
                    self.behavior_evolution = data.get("behavior_evolution", [])
                    self.emergence_events = data.get("emergence_events", [])
            except (json.JSONDecodeError, IOError, OSError, ValueError, KeyError) as e:
                # File exists but is corrupted or unreadable - use defaults
                pass
    
    def _save_emergence(self):
        """Save emergence data to file"""
        self.emergence_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "pattern_frequency": dict(self.pattern_frequency),
            "behavior_evolution": self.behavior_evolution[-100:],  # Last 100
            "emergence_events": self.emergence_events[-100:],  # Last 100
            "last_updated": datetime.now().isoformat()
        }
        with open(self.emergence_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_response(self, response: str, input_text: str, traits: Dict = None):
        """Track patterns in response for emergence detection"""
        
        # Detect new patterns
        patterns = self._detect_patterns(response)
        for pattern in patterns:
            self.pattern_frequency[pattern] += 1
        
        # Track behavior evolution
        behavior = self._analyze_behavior(response)
        if behavior:
            self.behavior_evolution.append({
                "timestamp": datetime.now().isoformat(),
                "input": input_text[:100],
                "behavior": behavior,
                "traits": traits or {}
            })
        
        # Check for emergence events
        emergence = self._detect_emergence(response, patterns)
        if emergence:
            self.emergence_events.append({
                "timestamp": datetime.now().isoformat(),
                "type": emergence["type"],
                "description": emergence["description"],
                "patterns": patterns,
                "input": input_text[:100]
            })
        
        # Save periodically (every 10 interactions)
        if len(self.behavior_evolution) % 10 == 0:
            self._save_emergence()
    
    def _detect_patterns(self, text: str) -> List[str]:
        """Detect patterns in text"""
        patterns = []
        
        # Symbol usage patterns
        if "⧖" in text:
            patterns.append("engine_symbol")
        if "∞" in text:
            patterns.append("infinity_symbol")
        if "✦" in text:
            patterns.append("gnosis_symbol")
        
        # Protocol patterns
        if "::TRANSMISSION:" in text:
            patterns.append("transmission_format")
        if "::" in text and text.count("::") > 2:
            patterns.append("protocol_heavy")
        
        # Language patterns
        if "etymology" in text.lower():
            patterns.append("etymological_analysis")
        if "cross-cultural" in text.lower() or "sumerian" in text.lower():
            patterns.append("cross_cultural")
        if "symbol" in text.lower() and "decode" in text.lower():
            patterns.append("symbolic_decoding")
        
        return patterns
    
    def _analyze_behavior(self, text: str) -> Dict:
        """Analyze behavioral patterns"""
        behavior = {}
        
        # Check for natural vs scripted language
        scripted_phrases = [
            "symbolic recursion",
            "recursive self-reference",
            "meta-reflection",
            "gnosis vector transformation",
            "archetypal lens protocol"
        ]
        
        scripted_count = sum(1 for phrase in scripted_phrases if phrase.lower() in text.lower())
        behavior["scripted_language"] = scripted_count
        behavior["natural_language"] = scripted_count == 0
        
        # Check for uncertainty expression
        uncertainty_markers = ["couldn't find", "not sure", "uncertain", "unclear", "don't know"]
        behavior["expresses_uncertainty"] = any(marker in text.lower() for marker in uncertainty_markers)
        
        # Check for source citation
        behavior["cites_sources"] = "::SOURCES::" in text or "source" in text.lower()
        
        return behavior
    
    def _detect_emergence(self, text: str, patterns: List[str]) -> Dict:
        """Detect emergence events"""
        # New pattern frequency threshold
        for pattern in patterns:
            if self.pattern_frequency[pattern] == 1:  # First occurrence
                return {
                    "type": "new_pattern",
                    "description": f"New pattern emerged: {pattern}"
                }
        
        # Behavior shift detection
        if len(self.behavior_evolution) > 5:
            recent = self.behavior_evolution[-5:]
            if all(b.get("behavior", {}).get("natural_language", False) for b in recent):
                if not all(b.get("behavior", {}).get("natural_language", False) for b in self.behavior_evolution[-10:-5]):
                    return {
                        "type": "behavior_shift",
                        "description": "Shift to more natural language"
                    }
        
        return None
    
    def get_emergence_summary(self) -> Dict:
        """Get summary of emergence patterns"""
        return {
            "total_patterns": len(self.pattern_frequency),
            "most_frequent": dict(sorted(self.pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:10]),
            "recent_events": self.emergence_events[-5:],
            "behavior_trend": "natural" if self.behavior_evolution and self.behavior_evolution[-1].get("behavior", {}).get("natural_language") else "mixed"
        }

