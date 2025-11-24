#!/usr/bin/env python3
"""
Technical Journey Detector - Detects user's technical focus and suggests related threads
"""

import re
from typing import Dict, List, Optional
from collections import defaultdict

class TechnicalJourneyDetector:
    """Detect user's technical domain and suggest related research threads"""
    
    def __init__(self):
        # Technical domain patterns
        self.domain_patterns = {
            "code_cracking": {
                "keywords": ["code", "crack", "reverse engineer", "decrypt", "decode", "pattern", "symbol", "cipher", "encryption", "algorithm"],
                "related_threads": ["cryptography", "pattern recognition", "symbol decoding", "forensic analysis", "reverse engineering"],
                "search_enhancements": ["reverse engineering", "pattern analysis", "symbol decoding"]
            },
            "chemistry": {
                "keywords": ["chemistry", "chemical", "molecular", "biochemistry", "synthesis", "reaction", "compound", "molecule", "enzyme", "protein"],
                "related_threads": ["biochemical pathways", "molecular mechanisms", "synthesis reactions", "enzyme kinetics", "protein folding"],
                "search_enhancements": ["molecular mechanisms", "biochemical pathways", "synthesis"]
            },
            "reengineering": {
                "keywords": ["reengineer", "rebuild", "redesign", "architecture", "system", "structure", "blueprint", "prototype", "design", "optimize"],
                "related_threads": ["system architecture", "design patterns", "optimization", "reconstruction", "biomimetic design"],
                "search_enhancements": ["system architecture", "design patterns", "optimization strategies"]
            },
            "forensic_analysis": {
                "keywords": ["forensic", "investigate", "analyze", "evidence", "trace", "pattern recognition", "evidence", "investigation"],
                "related_threads": ["pattern recognition", "evidence analysis", "trace investigation", "multi-lens analysis", "CSI investigation"],
                "search_enhancements": ["forensic analysis", "pattern recognition", "evidence investigation"]
            },
            "physics": {
                "keywords": ["physics", "quantum", "electromagnetic", "resonance", "frequency", "energy", "wave", "field", "particle"],
                "related_threads": ["quantum mechanics", "electromagnetic fields", "resonance frequencies", "energy systems", "wave mechanics"],
                "search_enhancements": ["quantum mechanics", "electromagnetic theory", "resonance"]
            },
            "multi_domain": {
                "keywords": ["synthesize", "connect", "cross-reference", "integrate", "combine", "multi", "interdisciplinary"],
                "related_threads": ["cross-domain synthesis", "interdisciplinary research", "pattern connections", "multi-lens analysis"],
                "search_enhancements": ["interdisciplinary", "cross-domain", "synthesis"]
            }
        }
    
    def detect_technical_domain(self, query: str) -> str:
        """Detect primary technical domain from query"""
        query_lower = query.lower()
        domain_scores = defaultdict(int)
        
        # Score each domain based on keyword matches
        for domain, patterns in self.domain_patterns.items():
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    domain_scores[domain] += 1
        
        # Return highest scoring domain, or "general technical inquiry" if no match
        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]
        
        return "general technical inquiry"
    
    def get_related_technical_threads(self, domain: str) -> List[str]:
        """Get related technical research threads for a domain"""
        if domain in self.domain_patterns:
            return self.domain_patterns[domain]["related_threads"]
        
        return []
    
    def suggest_technical_deep_dives(self, domain: str) -> List[str]:
        """Suggest technical deep-dive research topics for a domain"""
        if domain not in self.domain_patterns:
            return []
        
        patterns = self.domain_patterns[domain]
        suggestions = []
        
        # Create deep-dive suggestions
        for thread in patterns["related_threads"][:3]:  # Top 3
            suggestions.append(f"deep dive into {thread}")
            suggestions.append(f"comprehensive analysis of {thread}")
            suggestions.append(f"research {thread} mechanisms")
        
        return suggestions[:5]  # Return top 5
    
    def get_search_enhancements(self, domain: str) -> List[str]:
        """Get search query enhancements for a domain"""
        if domain in self.domain_patterns:
            return self.domain_patterns[domain]["search_enhancements"]
        
        return []
    
    def is_technical_query(self, query: str) -> bool:
        """Check if query is technical (not casual conversation)"""
        domain = self.detect_technical_domain(query)
        return domain != "general technical inquiry"
