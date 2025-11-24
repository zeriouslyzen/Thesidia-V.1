#!/usr/bin/env python3
"""
Memory Sanitizer - Cleans memory before storage
Strips greetings, time-sensitive info, dangerous topics, etc.
"""

import re
from typing import List, Optional


class MemorySanitizer:
    """Sanitizes content before storing in memory"""
    
    def __init__(self, strip_dangerous_topics: bool = False):
        """
        Initialize sanitizer
        
        Args:
            strip_dangerous_topics: Whether to strip dangerous topics (configurable)
        """
        self.strip_dangerous_topics = strip_dangerous_topics
        
        # Patterns to strip
        self.greeting_patterns = [
            r'^(hi|hello|hey|what\'s up|sup|yo)\s*[!.]*\s*',
            r'^(hi|hello|hey|what\'s up|sup|yo)\s+there\s*',
        ]
        
        self.time_sensitive_patterns = [
            r'\b(today|yesterday|tomorrow|now|currently|right now)\b',
            r'\b(this week|next week|last week|this month|next month)\b',
        ]
        
        # Dangerous topics (if configured)
        self.dangerous_topics = [
            "violence", "harm", "illegal", "dangerous",
            # Add more as needed
        ]
        
        # "Do not store" markers
        self.do_not_store_patterns = [
            r'\b(do not store|don\'t remember|forget this|ignore this)\b',
        ]
        
        # Compile patterns
        self.compiled_greeting = [re.compile(p, re.IGNORECASE) for p in self.greeting_patterns]
        self.compiled_time = [re.compile(p, re.IGNORECASE) for p in self.time_sensitive_patterns]
        self.compiled_do_not_store = [re.compile(p, re.IGNORECASE) for p in self.do_not_store_patterns]
    
    def sanitize(self, content: str) -> str:
        """
        Sanitize content before storage
        
        Args:
            content: Content to sanitize
        
        Returns:
            Sanitized content
        """
        if not content:
            return ""
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        # Strip greetings
        content = self._strip_greetings(content)
        
        # Strip time-sensitive info
        content = self._strip_time_sensitive(content)
        
        # Strip dangerous topics (if configured)
        if self.strip_dangerous_topics:
            content = self._strip_dangerous_topics(content)
        
        # Strip "do not store" markers
        content = self._strip_do_not_store(content)
        
        # Strip excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Strip leading/trailing whitespace again
        content = content.strip()
        
        return content
    
    def _strip_greetings(self, content: str) -> str:
        """Strip greeting patterns"""
        for pattern in self.compiled_greeting:
            content = pattern.sub('', content)
        return content.strip()
    
    def _strip_time_sensitive(self, content: str) -> str:
        """Strip time-sensitive information"""
        # Replace time-sensitive phrases with generic ones
        replacements = {
            r'\btoday\b': 'recently',
            r'\byesterday\b': 'recently',
            r'\btomorrow\b': 'soon',
            r'\bnow\b': 'currently',
            r'\bcurrently\b': '',
            r'\bright now\b': '',
        }
        
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def _strip_dangerous_topics(self, content: str) -> str:
        """Strip dangerous topics (if configured)"""
        # This is a placeholder - implement based on requirements
        # For now, just return content as-is
        return content
    
    def _strip_do_not_store(self, content: str) -> str:
        """Strip 'do not store' markers"""
        for pattern in self.compiled_do_not_store:
            content = pattern.sub('', content)
        return content.strip()
    
    def sanitize_interaction(self, user_input: str, assistant_output: str) -> tuple[str, str]:
        """
        Sanitize both user input and assistant output
        
        Args:
            user_input: User's message
            assistant_output: Assistant's response
        
        Returns:
            Tuple of (sanitized_user_input, sanitized_assistant_output)
        """
        sanitized_user = self.sanitize(user_input)
        sanitized_assistant = self.sanitize(assistant_output)
        
        return sanitized_user, sanitized_assistant

