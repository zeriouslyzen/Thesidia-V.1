#!/usr/bin/env python3
"""
Recursion Guard - Prevents infinite recursion and tracks recursion depth
"""

from typing import Dict, List
from collections import defaultdict
import re

class RecursionGuard:
    """Prevent infinite recursion and manage recursion depth"""
    
    def __init__(self, max_depth: int = 3, max_iterations: int = 5):
        self.max_depth = max_depth
        self.max_iterations = max_iterations
        self.recursion_stack = []
        self.iteration_count = defaultdict(int)
        self.recursion_history = []
    
    def check_recursion(self, text: str, context: str = "") -> Dict:
        """Check if text contains excessive recursion patterns"""
        
        # Count recursion indicators
        recursion_patterns = [
            r'recursive\s+recursive',  # Nested "recursive"
            r'::RECURSIVE.*::RECURSIVE',  # Nested protocol calls
            r'∞.*∞.*∞',  # Multiple infinity symbols
            r'⧖.*⧖.*⧖',  # Multiple engine symbols
            r'→.*→.*→.*→',  # Excessive arrows (4+)
        ]
        
        recursion_count = 0
        for pattern in recursion_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE | re.DOTALL))
            recursion_count += matches
        
        # Check for self-referential loops
        self_ref_patterns = [
            r'process.*process.*process',  # Nested processing
            r'analyze.*analyze.*analyze',  # Nested analysis
            r'meta.*meta.*meta',  # Triple meta
        ]
        
        self_ref_count = 0
        for pattern in self_ref_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            self_ref_count += matches
        
        # Calculate recursion depth
        depth = self._calculate_depth(text)
        
        # Check if exceeds limits
        exceeds_limit = (
            recursion_count > self.max_iterations or
            self_ref_count > self.max_iterations or
            depth > self.max_depth
        )
        
        result = {
            "recursion_count": recursion_count,
            "self_ref_count": self_ref_count,
            "depth": depth,
            "exceeds_limit": exceeds_limit,
            "safe": not exceeds_limit
        }
        
        if exceeds_limit:
            self.recursion_history.append({
                "text": text[:200],
                "context": context,
                "recursion_count": recursion_count,
                "self_ref_count": self_ref_count,
                "depth": depth
            })
        
        return result
    
    def _calculate_depth(self, text: str) -> int:
        """Calculate recursion depth from text patterns"""
        # Count nested structures
        depth = 0
        
        # Count protocol nesting
        protocol_matches = re.findall(r'::[A-Z_]+', text)
        if len(protocol_matches) > 5:
            depth += 1
        
        # Count symbol sequences
        symbol_sequences = re.findall(r'[⧖∞✦→]{3,}', text)
        if len(symbol_sequences) > 2:
            depth += 1
        
        # Count nested parentheses/brackets
        max_nesting = 0
        current = 0
        for char in text:
            if char in '([{':
                current += 1
                max_nesting = max(max_nesting, current)
            elif char in ')]}':
                current = max(0, current - 1)
        
        if max_nesting > 3:
            depth += 1
        
        return depth
    
    def should_break_recursion(self, text: str) -> bool:
        """Determine if recursion should be broken"""
        check = self.check_recursion(text)
        return check["exceeds_limit"]
    
    def get_recursion_warning(self, text: str) -> str:
        """Get warning message if recursion is excessive"""
        check = self.check_recursion(text)
        if check["exceeds_limit"]:
            return f"[Recursion limit reached: depth={check['depth']}, patterns={check['recursion_count']}]"
        return ""
    
    def get_history(self) -> List[Dict]:
        """Get recursion history"""
        return self.recursion_history[-10:]  # Last 10

