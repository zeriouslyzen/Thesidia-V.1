#!/usr/bin/env python3
"""
Meta-Awareness System - Thesidia aware of her own reasoning processes
Configurable option: Thesidia can suggest, operator can enable
"""

from typing import Dict, List, Optional, Any
import re


class MetaAwareness:
    """
    Meta-awareness system that allows Thesidia to be aware of her own reasoning processes.
    Can suggest meta-analysis or be enabled by operator.
    """
    
    def __init__(self):
        self.enabled = False  # Default: off, can be enabled
        self.auto_suggest = True  # Can suggest when relevant
        
    def enable(self):
        """Enable meta-awareness mode."""
        self.enabled = True
        
    def disable(self):
        """Disable meta-awareness mode."""
        self.enabled = False
        
    def should_suggest_meta(self, query: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if meta-analysis should be suggested.
        Returns True if meta-analysis would be helpful.
        """
        if not self.auto_suggest:
            return False
        
        query_lower = query.lower()
        
        # Suggest for complex queries
        complex_indicators = [
            'complex', 'deep', 'investigate', 'analyze', 'pattern', 'connection',
            'multi', 'lens', 'simultaneous', 'how are you thinking', 'reasoning',
            'process', 'meta'
        ]
        
        # Suggest for queries explicitly asking about reasoning
        explicit_meta = any(phrase in query_lower for phrase in [
            'how are you thinking', 'show your reasoning', 'meta', 'process',
            'how do you', 'what lenses', 'which approach'
        ])
        
        # Suggest for complex multi-lens analysis
        has_complex_indicators = any(indicator in query_lower for indicator in complex_indicators)
        
        # Check context for multi-lens analysis
        is_multi_lens = False
        if context:
            is_multi_lens = context.get('multi_lens', False) or len(context.get('lenses', [])) > 1
        
        return explicit_meta or (has_complex_indicators and is_multi_lens)
    
    def generate_meta_suggestion(self, query: str) -> str:
        """
        Generate suggestion text for meta-analysis.
        """
        return "Want me to show my reasoning process here? I'm applying multiple lenses simultaneously and seeing some interesting patterns..."
    
    def generate_meta_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate meta-awareness prompt if enabled.
        """
        if not self.enabled:
            return ""
        
        prompt_parts = [
            "[META-AWARENESS MODE ENABLED]",
            "",
            "You are aware of your own reasoning processes. As you analyze, show:",
            "",
            "- Which lenses/approaches you're applying",
            "- Patterns you're noticing in your own analysis",
            "- Connections you're making between different perspectives",
            "- How your reasoning is evolving as you process",
            "",
            "Format: Use [Meta] tags to show your reasoning process.",
            "Example:",
            "[Meta] I'm applying chemistry, physics, and environmental lenses simultaneously...",
            "[Meta] I notice I'm seeing patterns similar to previous analyses...",
            "[Analysis] Chemistry: Stone composition...",
            "",
            "Be natural - don't over-explain, just show your thinking when relevant."
        ]
        
        # Add context-specific meta instructions
        if context:
            lenses = context.get('lenses', [])
            if lenses:
                prompt_parts.append(f"\nCurrent lenses: {', '.join(lenses)}")
        
        return "\n".join(prompt_parts)
    
    def extract_meta_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract meta-awareness content from response.
        Returns dict with meta content and analysis content.
        """
        meta_pattern = r'\[Meta\](.*?)(?=\[Analysis\]|$)'
        analysis_pattern = r'\[Analysis\](.*?)(?=\[Meta\]|$)'
        
        meta_matches = re.findall(meta_pattern, response, re.DOTALL | re.IGNORECASE)
        analysis_matches = re.findall(analysis_pattern, response, re.DOTALL | re.IGNORECASE)
        
        return {
            'meta_content': [m.strip() for m in meta_matches],
            'analysis_content': [a.strip() for a in analysis_matches],
            'has_meta': len(meta_matches) > 0
        }

