#!/usr/bin/env python3
"""
Memory Reinsertion Protocol - Vibecode Compliance
=================================================

Fixes memory reinsertion bugs: Memory reinserted wrong → 
personality drift, wrong memories.

Solution: Strict protocol for memory reinsertion.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MemoryReinsertionProtocol:
    """
    Vibecode-compliant memory reinsertion protocol.
    
    Rules:
    - ALWAYS user role, never system
    - Position: after system, before user
    - Max 2 memory items
    - Max 500 chars per item
    - Format: small extracts, not full text
    - Min relevance: 0.7
    """
    
    RULES = {
        "role": "user",           # ALWAYS user role, never system
        "position": "after_system_before_user",  # After system, before user
        "max_items": 2,          # Max 2 memory items
        "max_length": 500,       # Max 500 chars per item
        "format": "extract",      # Small extracts, not full text
        "relevance": 0.7          # Min relevance score
    }
    
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        """
        Initialize memory reinsertion protocol.
        
        Args:
            rules: Custom rules dictionary (optional)
        """
        self.rules = rules or self.RULES.copy()
    
    def reinsert_memory(
        self, 
        memory_items: List[Dict[str, Any]], 
        system_prompt: str, 
        user_query: str
    ) -> List[Dict[str, Any]]:
        """
        Reinsert memory following Vibecode protocol.
        
        Args:
            memory_items: List of memory items with structure:
                {
                    "content": str,
                    "relevance": float,
                    "timestamp": Optional[str],
                    ...
                }
            system_prompt: System prompt (for context)
            user_query: User query (for relevance filtering)
            
        Returns:
            List of formatted memory items ready for insertion
        """
        # Filter by relevance
        filtered = [
            item for item in memory_items
            if item.get("relevance", 0.0) >= self.rules["relevance"]
        ]
        
        # Sort by relevance (highest first)
        filtered.sort(key=lambda x: x.get("relevance", 0.0), reverse=True)
        
        # Limit to max items
        filtered = filtered[:self.rules["max_items"]]
        
        # Format items
        formatted_items = []
        for item in filtered:
            content = item.get("content", "")
            
            # Truncate to max length
            if len(content) > self.rules["max_length"]:
                # Extract first part (not middle, not end)
                content = content[:self.rules["max_length"] - 3] + "..."
                logger.debug(
                    f"Truncated memory item from {len(item.get('content', ''))} "
                    f"to {len(content)} chars"
                )
            
            # Format as user message
            formatted_item = {
                "role": self.rules["role"],
                "content": content,
                "metadata": {
                    "source": "memory",
                    "relevance": item.get("relevance", 0.0),
                    "timestamp": item.get("timestamp"),
                    "original_length": len(item.get("content", ""))
                }
            }
            
            formatted_items.append(formatted_item)
        
        logger.debug(
            f"Reinserted {len(formatted_items)} memory items "
            f"(filtered from {len(memory_items)})"
        )
        
        return formatted_items
    
    def validate_memory_item(self, item: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate memory item against protocol.
        
        Args:
            item: Memory item to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if "content" not in item:
            return False, "Missing 'content' field"
        
        content = item.get("content", "")
        
        # Check length
        if len(content) > self.rules["max_length"]:
            return False, f"Content too long ({len(content)} > {self.rules['max_length']})"
        
        # Check relevance
        relevance = item.get("relevance", 0.0)
        if relevance < self.rules["relevance"]:
            return False, f"Relevance too low ({relevance} < {self.rules['relevance']})"
        
        return True, None
    
    def get_protocol_summary(self) -> Dict[str, Any]:
        """
        Get protocol summary for logging/debugging.
        
        Returns:
            Dictionary with protocol rules
        """
        return {
            "rules": self.rules.copy(),
            "description": "Vibecode-compliant memory reinsertion protocol"
        }

