#!/usr/bin/env python3
"""
Ephemeral Memory - Layer A
Only the last N interactions (e.g., 2-4)
Never stored permanently, always overwritten
Only used for maintaining immediate conversation flow
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class EphemeralMemory:
    """Manages short-term conversation context (last 2-4 interactions)"""
    
    def __init__(self, base_dir: Path = None, max_interactions: int = 2):
        """
        Initialize ephemeral memory
        
        Args:
            base_dir: Base directory for data storage
            max_interactions: Maximum number of interactions to keep (default: 2)
        """
        self.base_dir = base_dir or Path(".")
        # Support both user-specific and global memory
        if "users" in str(self.base_dir):
            # User-specific: base_dir is already user_dir
            self.memory_file = self.base_dir / "state" / "ephemeral_context.json"
        else:
            # Global: use data/state
            self.memory_file = self.base_dir / "data" / "state" / "ephemeral_context.json"
        self.max_interactions = max_interactions
        
        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage (fast access)
        self.interactions: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """Load ephemeral context from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.interactions = data.get("interactions", [])[-self.max_interactions:]
            except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
                print(f"Warning: Could not load ephemeral memory: {e}")
                self.interactions = []
        else:
            self.interactions = []
    
    def _save(self):
        """Save ephemeral context to disk"""
        try:
            data = {
                "interactions": self.interactions[-self.max_interactions:],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Could not save ephemeral memory: {e}")
    
    def add_interaction(self, user_input: str, assistant_output: str, metadata: Optional[Dict] = None):
        """
        Add a new interaction to ephemeral memory
        
        Args:
            user_input: User's message
            assistant_output: Assistant's response
            metadata: Optional metadata (timestamp, etc.)
        """
        interaction = {
            "user": user_input[:500],  # Truncate to prevent bloat
            "assistant": assistant_output[:800],  # Truncate to prevent bloat
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.interactions.append(interaction)
        
        # Keep only last N interactions
        if len(self.interactions) > self.max_interactions:
            self.interactions = self.interactions[-self.max_interactions:]
        
        # Save to disk
        self._save()
    
    def get_last_n(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Get last N interactions
        
        Args:
            n: Number of interactions to return (default: max_interactions)
        
        Returns:
            List of interaction dictionaries
        """
        if n is None:
            n = self.max_interactions
        
        return self.interactions[-n:]
    
    def get_context_string(self) -> str:
        """
        Get formatted context string for prompt injection
        
        Returns:
            Formatted string with recent interactions
        """
        if not self.interactions:
            return ""
        
        context = "\n\nRecent messages in this chat only:\n"
        for i, interaction in enumerate(self.interactions, 1):
            user_input = interaction.get('user', '')[:200]
            assistant_output = interaction.get('assistant', '')[:300]
            context += f"User: {user_input}\nThesidia: {assistant_output}\n"
        
        return context
    
    def clear(self):
        """Clear all ephemeral memory"""
        self.interactions = []
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about ephemeral memory"""
        return {
            "total_interactions": len(self.interactions),
            "max_interactions": self.max_interactions,
            "memory_file": str(self.memory_file),
            "last_updated": self.interactions[-1]["timestamp"] if self.interactions else None
        }

