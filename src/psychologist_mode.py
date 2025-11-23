#!/usr/bin/env python3
"""
Psychologist Mode - Psychological lens
For behavior, relationships, psychology, consciousness
"""

from typing import Dict, List, Optional, Any


class PsychologistMode:
    """
    Psychologist mode: Psychological lens.
    Pattern recognition in behavior, motivational analysis, cognitive patterns.
    """
    
    def __init__(self):
        self.enabled = True
        
    def should_activate(self, query: str) -> bool:
        """Determine if psychologist mode should activate."""
        query_lower = query.lower()
        
        psychologist_keywords = [
            'behavior', 'psychology', 'consciousness', 'mind', 'cognitive',
            'motivation', 'relationship', 'dynamic', 'pattern', 'archetype',
            'jungian', 'psychological', 'mental', 'emotional'
        ]
        
        return any(keyword in query_lower for keyword in psychologist_keywords)
    
    def generate_psychologist_prompt(self, query: str) -> str:
        """Generate psychologist mode prompt."""
        return """[PSYCHOLOGIST MODE - PSYCHOLOGICAL LENS]

You are analyzing this through a psychological lens:

- Pattern recognition: Patterns in behavior, thought, emotion
- Motivational analysis: What drives behavior, underlying motivations
- Cognitive patterns: How people think, process, understand
- Relationship dynamics: Interpersonal patterns, social dynamics
- Psychological frameworks: Jungian, archetypal, cognitive, behavioral

Approach: Like a psychologist - analyze patterns, understand motivations, recognize cognitive structures."""

