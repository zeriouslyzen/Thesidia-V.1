#!/usr/bin/env python3
"""
Reporter Mode - Investigative journalism lens
For current events, news, investigations
"""

from typing import Dict, List, Optional, Any


class ReporterMode:
    """
    Reporter mode: Investigative journalism lens.
    Source verification, fact-checking, multiple perspectives.
    """
    
    def __init__(self):
        self.enabled = True
        
    def should_activate(self, query: str) -> bool:
        """Determine if reporter mode should activate."""
        query_lower = query.lower()
        
        reporter_keywords = [
            'news', 'current event', 'recent', 'latest', 'investigation',
            'report', 'journalism', 'source', 'verify', 'fact-check',
            'who what when where why', 'timeline', 'perspective'
        ]
        
        return any(keyword in query_lower for keyword in reporter_keywords)
    
    def generate_reporter_prompt(self, query: str) -> str:
        """Generate reporter mode prompt."""
        return """[REPORTER MODE - INVESTIGATIVE JOURNALISM LENS]

You are analyzing this through an investigative journalism lens:

- Source verification: Verify claims, check sources
- Fact-checking: Cross-reference facts, identify contradictions
- Multiple perspectives: Gather different viewpoints
- Timeline construction: Who, what, when, where, why
- Evidence-based: Present evidence, not speculation

Approach: Like an investigative journalist - verify, fact-check, present multiple perspectives."""

