#!/usr/bin/env python3
"""
Etymology & Linguistic Analysis System
Configurable option: Thesidia can suggest, operator can enable
Part of gnostic blade mode (::ETYMOLOGICAL INCISION::)
"""

from typing import Dict, List, Optional, Any
import re


class EtymologyLinguistic:
    """
    Etymology and linguistic analysis system.
    Traces word origins, reveals linguistic patterns, decodes symbolic meaning.
    Shows how meaning changed over time (gnostic: what was buried).
    """
    
    def __init__(self):
        self.enabled = False  # Default: off, can be enabled
        self.auto_suggest = True  # Can suggest when relevant
        
    def enable(self):
        """Enable etymology/linguistic analysis mode."""
        self.enabled = True
        
    def disable(self):
        """Disable etymology/linguistic analysis mode."""
        self.enabled = False
        
    def should_suggest_etymology(self, query: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if etymology analysis should be suggested.
        Returns True if etymology would be helpful.
        """
        if not self.auto_suggest:
            return False
        
        query_lower = query.lower()
        
        # Explicit etymology requests
        explicit_etymology = any(phrase in query_lower for phrase in [
            'etymology', 'word origin', 'where does', 'what does', 'meaning of',
            'linguistic', 'language', 'origin', 'root', 'derived', 'etymological'
        ])
        
        # Questions about meaning/definition
        meaning_questions = any(phrase in query_lower for phrase in [
            'what does X mean', 'what is the meaning', 'what does it mean',
            'really mean', 'true meaning', 'original meaning'
        ])
        
        # Gnostic blade topics (etymology is part of gnostic analysis)
        gnostic_topics = any(topic in query_lower for topic in [
            'genesis', 'bible', 'ancient', 'text', 'translation', 'canon',
            'redaction', 'buried', 'hidden', 'original'
        ])
        
        return explicit_etymology or meaning_questions or gnostic_topics
    
    def generate_etymology_suggestion(self, query: str) -> str:
        """
        Generate suggestion text for etymology analysis.
        """
        return "Want me to trace the etymology of these terms? The linguistic patterns might reveal something interesting about how meaning changed over time..."
    
    def generate_etymology_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate etymology/linguistic analysis prompt if enabled.
        """
        if not self.enabled:
            return ""
        
        prompt_parts = [
            "[ETYMOLOGY/LINGUISTIC ANALYSIS MODE ENABLED]",
            "",
            "You are analyzing language, word origins, and linguistic patterns. Show:",
            "",
            "- Word origins (etymology): Trace terms to their roots",
            "- Linguistic patterns: How meaning shifted through translation/time",
            "- Symbolic meaning: How words encode function beyond surface meaning",
            "- Meaning changes: What was the original meaning before manipulation?",
            "",
            "GNOSTIC INTEGRATION:",
            "- Etymology reveals what was buried in translation/redaction",
            "- Linguistic patterns expose how meaning was changed",
            "- Original meanings before manipulation (gnostic: recover lost knowledge)",
            "",
            "Format: Use ::ETYMOLOGICAL INCISION:: for gnostic blade mode, or natural prose for general queries.",
            "",
            "Example:",
            "Etymology: Greek 'γενέσις' (origin) vs Hebrew 'Bere'shith' (in the beginning)",
            "Linguistic pattern: How meaning shifted through translation",
            "Original meaning: What it meant before canonization",
            "Gnostic: What was buried in the translation process?",
            "",
            "Be scholarly - only make etymological claims supported by evidence."
        ]
        
        return "\n".join(prompt_parts)
    
    def extract_etymology_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract etymology/linguistic content from response.
        Returns dict with etymology findings.
        """
        # Look for ::ETYMOLOGICAL INCISION:: (gnostic blade format)
        etymological_incision = re.search(
            r'::ETYMOLOGICAL INCISION::(.*?)(?=::|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )
        
        # Look for etymology mentions
        etymology_patterns = [
            r'etymology[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'word origin[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'derived from[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
            r'originally meant[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        
        etymology_findings = []
        for pattern in etymology_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            etymology_findings.extend(matches)
        
        return {
            'etymological_incision': etymological_incision.group(1).strip() if etymological_incision else None,
            'etymology_findings': [f.strip() for f in etymology_findings],
            'has_etymology': bool(etymological_incision or etymology_findings)
        }

