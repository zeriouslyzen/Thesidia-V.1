#!/usr/bin/env python3
"""
Support Utilities
=================

Shared utility functions used across modules.
"""

import re
from typing import List

# Meta noise patterns for cleaning text
META_REGEX_PATTERNS = [
    r'::?CONVERSATION HISTORY::?.*?(?=::|\Z)',
    r'\*\*CONVERSATION HISTORY.*?(?=\*\*|::|\Z)',
    r'Initial Context.*?(?=Current Interaction|This concludes|$)',
    r'Past Interaction.*?(?=Current Interaction|This concludes|$)',
    r'This concludes.*?(?=::|\Z)',
    r'Please (?:continue|respond).*?(?=::|\Z)',
    r'Your turn is finished.*?(?=::|\Z)',
    r'Keep (?:going|playing).*?(?=::|\Z)'
]


def strip_meta_noise(text: str) -> str:
    """
    Remove meta-commentary and conversation artifacts from text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text without meta-noise
    """
    if not text:
        return ""
    cleaned = text
    for pattern in META_REGEX_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    junk_tokens = [
        "Your turn!",
        "I'll keep going",
        "I'll give it another go",
        "Now it's my turn",
        "Now it's Thesidia's turn",
        "As Oracle",
        "meta-analysis",
        "CONVERSATION HISTORY",
        "Initial Context",
        "Past Interaction"
    ]
    for token in junk_tokens:
        cleaned = cleaned.replace(token, "")
    return cleaned.strip()

