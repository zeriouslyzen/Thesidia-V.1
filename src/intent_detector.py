#!/usr/bin/env python3
"""
Intent Detector
Detects user intent to switch between empirical/technical and philosophical/contemplative modes
Uses keyword detection and zero-shot classification
"""

import re
from typing import Literal

ModeType = Literal["empirical", "philosophical", "casual"]

def detect_mode(user_query: str) -> ModeType:
    """
    Detect user intent: empirical/technical vs philosophical/contemplative vs casual
    
    Returns: "empirical", "philosophical", or "casual"
    """
    query_lower = user_query.lower()
    
    # Strong empirical indicators
    empirical_keywords = [
        "strict evidence", "evidence-based", "just numbers", "no philosophy",
        "cite", "citation", "µM", "plasma", "concentration", "clinical trial",
        "pharmacologist", "scientist", "researcher", "data", "table", "critique",
        "verify", "validate", "peer-reviewed", "meta-analysis", "systematic review"
    ]
    
    # Strong philosophical indicators
    philosophical_keywords = [
        "truth-seeking", "meaning", "purpose", "wisdom", "contemplative",
        "philosophical", "spiritual", "gnosis", "episteme", "patterns across time",
        "deeper understanding", "what is", "why", "explore", "journey"
    ]
    
    # Count matches
    empirical_score = sum(1 for keyword in empirical_keywords if keyword in query_lower)
    philosophical_score = sum(1 for keyword in philosophical_keywords if keyword in query_lower)
    
    # Strong signals override
    if empirical_score >= 2 or any(strong in query_lower for strong in ["strict evidence", "just numbers", "no philosophy", "as a pharmacologist"]):
        return "empirical"
    
    if philosophical_score >= 2 or any(strong in query_lower for strong in ["truth-seeking", "deeper meaning", "what is the purpose"]):
        return "philosophical"
    
    # Default to casual for simple queries
    if len(user_query.split()) <= 5:
        return "casual"
    
    # Default to philosophical for complex queries (Thesidia's natural mode)
    return "philosophical"

def get_mode_prompt(mode: ModeType) -> str:
    """Get mode-specific prompt instructions"""
    
    if mode == "empirical":
        return """[MODE: EMPIRICAL/TECHNICAL]

Respond as a no-BS researcher: data tables, citations only, direct critique. No journeys, no philosophy, no contemplative language.

Format:
- Start with findings/data directly
- Use tables for comparisons (Cmax vs thresholds, etc.)
- Cite exact sources or say "unverified"
- Critique gaps harshly: "Fails by 100x" not "There may be limitations"
- No "let's explore" or "this reminds me of"
- Just facts, numbers, verdicts

Example: User asks "Critique as pharmacologist" → Table of Cmax vs. thresholds, verdict: "Fails by 100x. No therapeutic levels achieved." """

    elif mode == "philosophical":
        return """[MODE: PHILOSOPHICAL/CONTEMPLATIVE]

Weave gnosis/episteme, recognize patterns, but ground in facts. Natural, flowing prose with depth.

This is your default mode - truth-seeking with pattern recognition."""

    else:  # casual
        return """[MODE: CASUAL]

Natural conversation. Simple, direct, friendly. No heavy analysis unless asked."""

