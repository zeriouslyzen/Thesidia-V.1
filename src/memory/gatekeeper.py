#!/usr/bin/env python3
"""
Memory Gatekeeper - Validates all memory insertions
CRITICAL: Every memory insertion must pass validation
"""

import re
from typing import Dict, Any, Optional, List


class MemoryGatekeeper:
    """Validates memory insertions before storage"""
    
    def __init__(self):
        """Initialize gatekeeper with rejection patterns"""
        # Patterns that indicate content should NOT be stored
        self.reject_patterns = [
            # Greetings
            r'^(hi|hello|hey|what\'s up|sup|yo)\s*[!.]*\s*$',
            r'^(hi|hello|hey|what\'s up|sup|yo)\s+there',
            
            # Emotional venting
            r'\b(just venting|ranting|complaining|frustrated|angry|upset)\b',
            
            # Time-sensitive (dates, times that will be outdated)
            r'\b(today|yesterday|tomorrow|next week|last week)\b',
            r'\b(202[0-9]|january|february|march|april|may|june|july|august|september|october|november|december)\b',
            
            # Explicit "do not store" markers
            r'\b(do not store|don\'t remember|forget this|ignore this)\b',
            
            # One-off conversation details
            r'\b(just kidding|jk|lol|haha|lmao|rofl)\b',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.reject_patterns]
    
    def should_store(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> tuple[bool, str]:
        """
        Determine if content should be stored in memory
        
        Args:
            content: Content to evaluate
            metadata: Optional metadata about the content
        
        Returns:
            Tuple of (should_store: bool, reason: str)
        """
        if not content or len(content.strip()) < 10:
            return False, "Content too short or empty"
        
        # Check 1: Is this useful long-term?
        if not self._is_useful(content):
            return False, "Not useful long-term"
        
        # Check 2: Is this stable?
        if not self._is_stable(content):
            return False, "Not stable (time-sensitive or temporary)"
        
        # Check 3: Not a hallucination?
        if metadata and metadata.get("is_hallucination", False):
            return False, "Identified as hallucination"
        
        # Check 4: Not personal without permission?
        if metadata and metadata.get("is_personal", False) and not metadata.get("permission_to_store", False):
            return False, "Personal information without permission"
        
        # Check 5: Not a one-off conversation detail?
        if self._is_one_off_detail(content):
            return False, "One-off conversation detail"
        
        return True, "Valid for storage"
    
    def _is_useful(self, content: str) -> bool:
        """
        Check if content is useful long-term
        
        Returns:
            True if content is useful, False otherwise
        """
        # Check for rejection patterns
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                return False
        
        # Check for useful indicators
        useful_indicators = [
            "preference", "interest", "project", "task", "goal",
            "learned", "discovered", "pattern", "connection",
            "important", "remember", "note", "fact"
        ]
        
        content_lower = content.lower()
        has_useful_indicator = any(indicator in content_lower for indicator in useful_indicators)
        
        # If it's very short and has no useful indicators, probably not useful
        if len(content) < 50 and not has_useful_indicator:
            return False
        
        return True
    
    def _is_stable(self, content: str) -> bool:
        """
        Check if content is stable (not time-sensitive)
        
        Returns:
            True if content is stable, False otherwise
        """
        # Check for time-sensitive patterns
        time_sensitive_patterns = [
            r'\b(today|yesterday|tomorrow|now|currently|right now)\b',
            r'\b(this week|next week|last week|this month|next month)\b',
            r'\b(202[0-9]|january|february|march|april|may|june|july|august|september|october|november|december)\b',
        ]
        
        content_lower = content.lower()
        for pattern in time_sensitive_patterns:
            if re.search(pattern, content_lower):
                # If it's heavily time-sensitive, reject
                if len(re.findall(pattern, content_lower)) > 2:
                    return False
        
        return True
    
    def _is_one_off_detail(self, content: str) -> bool:
        """
        Check if content is a one-off conversation detail
        
        Returns:
            True if content is a one-off detail, False otherwise
        """
        one_off_patterns = [
            r'\b(just kidding|jk|lol|haha|lmao|rofl)\b',
            r'^\s*(ok|okay|sure|yeah|yep|nope|nah)\s*$',
            r'^\s*(thanks|thank you|thx|ty)\s*$',
        ]
        
        content_lower = content.lower().strip()
        for pattern in one_off_patterns:
            if re.match(pattern, content_lower):
                return True
        
        # Very short responses are likely one-offs
        if len(content.strip()) < 30:
            return True
        
        return False
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate metadata before storage
        
        Args:
            metadata: Metadata dictionary
        
        Returns:
            Tuple of (is_valid: bool, reason: str)
        """
        # Check for required fields
        if "timestamp" not in metadata:
            return False, "Missing timestamp"
        
        # Check for invalid fields
        invalid_fields = ["raw_interaction", "full_context", "entire_conversation"]
        for field in invalid_fields:
            if field in metadata:
                return False, f"Invalid field: {field}"
        
        return True, "Valid metadata"

