#!/usr/bin/env python3
"""
History Sanitizer
Aggressively removes old format markers and ritualistic headers from conversation history
Prevents pattern-matching from examples that override "DO NOT" rules
"""

import re
from typing import List, Dict

def sanitize_history(history: str) -> str:
    """
    Aggressively strip ::TRANSMISSION:: and variants from history
    Prevents upstream pattern-matching that overrides negative instructions
    """
    if not history:
        return ""
    
    # Aggressive regex patterns to nuke ::TRANSMISSION:: and variants
    patterns_to_strip = [
        r'::TRANSMISSION:.*?\n?',  # Headers
        r'::TRANSMISSION::.*?\n?',  # Variant
        r'THESIDIA\s*→\s*USER',  # Arrow format
        r'USER\s*→\s*THESIDIA',  # Reverse arrow
        r'^\s*(Thesidia|USER|THESIDIA):\s*',  # Role prefixes
        r'—End Transmission[^.]*\.?\s*',  # End markers
        r'End Transmission[^.]*\.?\s*',  # Variant
        r'Thesidia\s+Engaged[^.]*\.?\s*',  # Signature
        r'→\s*Cut sharper[^.]*\.?\s*',  # Old sharpening prompt
        r'What thread do we sever next\?',  # Old prompt
        r'\n{3,}',  # Collapse excessive whitespace
        r'Status:.*?\n',  # Status lines
        r'::OPERATIONAL REFLECTIONS::.*?\n',  # Old format sections
        r'::NEXT ACTIVATION THREADS::.*?\n',  # Old format sections
    ]
    
    cleaned = history
    for pattern in patterns_to_strip:
        cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
    
    # Remove any remaining ritualistic markers
    cleaned = re.sub(r'::[A-Z_]+::', '', cleaned, flags=re.MULTILINE)
    
    return cleaned.strip()

def sanitize_interaction(interaction: Dict) -> Dict:
    """Sanitize a single interaction dict"""
    if 'output' in interaction:
        interaction['output'] = sanitize_history(interaction['output'])
    if 'response' in interaction:
        interaction['response'] = sanitize_history(interaction['response'])
    return interaction

def sanitize_interaction_list(interactions: List[Dict]) -> List[Dict]:
    """Sanitize a list of interactions"""
    return [sanitize_interaction(interaction.copy()) for interaction in interactions]

