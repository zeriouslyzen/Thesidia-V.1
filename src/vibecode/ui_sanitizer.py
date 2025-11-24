#!/usr/bin/env python3
"""
UI Sanitizer - Vibecode Compliance
===================================

Fixes UI injection bugs: CSS/HTML leaks into prompt,
UI echoes old output.

Solution: Sanitize input/output to remove UI artifacts.
"""

from __future__ import annotations

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UISanitizer:
    """
    Sanitizes UI artifacts from input/output.
    
    Removes:
    - HTML tags
    - CSS classes
    - React fragments
    - Button labels
    - Debug IDs
    - UI metadata
    """
    
    # Patterns to remove
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    CSS_CLASS_PATTERN = re.compile(r'class=["\'][^"\']*["\']')
    REACT_FRAGMENT_PATTERN = re.compile(r'<React\.Fragment>|</React\.Fragment>|<>|</>')
    BUTTON_PATTERN = re.compile(r'\[Button:\s*[^\]]+\]|\[button:\s*[^\]]+\]')
    DEBUG_ID_PATTERN = re.compile(r'data-testid=["\'][^"\']*["\']|data-cy=["\'][^"\']*["\']')
    UI_METADATA_PATTERN = re.compile(r'<!--.*?-->|/\*.*?\*/')
    
    def sanitize_input(self, text: str) -> str:
        """
        Remove HTML, CSS, UI artifacts from input.
        
        Args:
            text: Raw input text
            
        Returns:
            Sanitized text with only raw content
        """
        if not text:
            return text
        
        original_length = len(text)
        sanitized = text
        
        # Remove HTML tags
        sanitized = self.HTML_TAG_PATTERN.sub('', sanitized)
        
        # Remove CSS classes
        sanitized = self.CSS_CLASS_PATTERN.sub('', sanitized)
        
        # Remove React fragments
        sanitized = self.REACT_FRAGMENT_PATTERN.sub('', sanitized)
        
        # Remove button labels
        sanitized = self.BUTTON_PATTERN.sub('', sanitized)
        
        # Remove debug IDs
        sanitized = self.DEBUG_ID_PATTERN.sub('', sanitized)
        
        # Remove UI metadata (comments)
        sanitized = self.UI_METADATA_PATTERN.sub('', sanitized)
        
        # Clean up whitespace
        sanitized = ' '.join(sanitized.split())
        
        if len(sanitized) != original_length:
            logger.debug(
                f"Sanitized input: {original_length} → {len(sanitized)} chars "
                f"({original_length - len(sanitized)} removed)"
            )
        
        return sanitized
    
    def sanitize_output(self, text: str, keep_last_n_turns: int = 3) -> str:
        """
        Prevent UI from echoing old output.
        
        Args:
            text: Output text
            keep_last_n_turns: Number of conversation turns to keep
            
        Returns:
            Sanitized output
        """
        if not text:
            return text
        
        # Remove assistant message markers
        # (This prevents reinsertion of old assistant responses)
        sanitized = text
        
        # Remove common assistant markers
        assistant_markers = [
            r'\[Assistant:\s*',
            r'\[assistant:\s*',
            r'<assistant>',
            r'</assistant>',
        ]
        
        for marker in assistant_markers:
            sanitized = re.sub(marker, '', sanitized, flags=re.IGNORECASE)
        
        # Clean up whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def sanitize_conversation_history(
        self, 
        history: list, 
        keep_last_n: int = 3
    ) -> list:
        """
        Sanitize conversation history for reinsertion.
        
        Args:
            history: List of conversation messages
            keep_last_n: Number of messages to keep
            
        Returns:
            Sanitized history with only user messages (last N turns)
        """
        if not history:
            return []
        
        # Keep only last N turns
        recent = history[-keep_last_n:] if len(history) > keep_last_n else history
        
        # Keep only user messages (not assistant messages)
        sanitized = [
            msg for msg in recent
            if msg.get("role") == "user"
        ]
        
        # Sanitize each message
        for msg in sanitized:
            if "content" in msg:
                msg["content"] = self.sanitize_input(msg["content"])
        
        logger.debug(
            f"Sanitized conversation history: {len(history)} → {len(sanitized)} messages"
        )
        
        return sanitized

