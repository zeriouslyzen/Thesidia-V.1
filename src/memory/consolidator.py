#!/usr/bin/env python3
"""
Consolidator - Consolidate experiences into long-term memory
Builds hierarchical knowledge organization
"""

from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime


class Consolidator:
    """
    Consolidates experiences into long-term memory.
    
    Builds hierarchical knowledge organization from raw experiences.
    """
    
    def __init__(self):
        """Initialize consolidator."""
        pass
    
    def consolidate(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate experiences into long-term memory.
        
        Args:
            experiences: List of experiences to consolidate
            
        Returns:
            Consolidated knowledge dictionary
        """
        consolidated = {
            "concepts": defaultdict(int),
            "facts": [],
            "patterns": [],
            "relationships": defaultdict(list),
            "consolidated_at": datetime.now().isoformat()
        }
        
        # Extract concepts from experiences
        for exp in experiences:
            modality = exp.get("modality", "unknown")
            content = str(exp.get("content", ""))
            
            # Simple concept extraction (can be enhanced)
            words = content.split()
            for word in words:
                if len(word) > 4:  # Filter short words
                    consolidated["concepts"][word.lower()] += 1
            
            # Extract facts (simple: sentences ending with periods)
            if "." in content:
                sentences = content.split(".")
                consolidated["facts"].extend([s.strip() for s in sentences if len(s.strip()) > 10])
        
        # Convert defaultdict to regular dict
        consolidated["concepts"] = dict(consolidated["concepts"])
        consolidated["relationships"] = dict(consolidated["relationships"])
        
        return consolidated

