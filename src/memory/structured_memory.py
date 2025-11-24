#!/usr/bin/env python3
"""
Structured Memory - Layer B
Long-term structured memory (facts about user/system state)
NOT conversation history - this is structured, curated, human-readable entries
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class StructuredMemory:
    """Manages structured long-term memory (user profile, preferences, system state)"""
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize structured memory
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        # Support both user-specific and global memory
        if "users" in str(self.base_dir):
            # User-specific: base_dir is already user_dir
            self.memory_file = self.base_dir / "memory" / "structured_memory.json"
        else:
            # Global: use data/memory
            self.memory_file = self.base_dir / "data" / "memory" / "structured_memory.json"
        
        # Ensure directory exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        self.memory = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load structured memory from disk"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError, ValueError) as e:
                print(f"Warning: Could not load structured memory: {e}")
                return self._default_structure()
        else:
            return self._default_structure()
    
    def _default_structure(self) -> Dict[str, Any]:
        """Return default structured memory structure"""
        return {
            "user_profile": {
                "preferences": {},
                "interests": [],
                "technical_domains": [],
                "research_threads": []
            },
            "system_state": {
                "personality": {},
                "capabilities": {},
                "learning": {
                    "effective_strategies": [],
                    "adaptation_rules": {}
                }
            },
            "projects": {},
            "custom_rules": {},
            "skills": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save(self):
        """Save structured memory to disk"""
        try:
            self.memory["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Could not save structured memory: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from structured memory using dot notation
        
        Args:
            key: Dot-notation key (e.g., "user_profile.preferences")
            default: Default value if key not found
        
        Returns:
            Value at key or default
        """
        keys = key.split('.')
        value = self.memory
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set a value in structured memory using dot notation
        
        Args:
            key: Dot-notation key (e.g., "user_profile.preferences")
            value: Value to set
        """
        keys = key.split('.')
        target = self.memory
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        # Set the value
        target[keys[-1]] = value
        self._save()
    
    def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile"""
        if "user_profile" not in self.memory:
            self.memory["user_profile"] = {}
        
        self.memory["user_profile"].update(updates)
        self._save()
    
    def update_system_state(self, updates: Dict[str, Any]):
        """Update system state"""
        if "system_state" not in self.memory:
            self.memory["system_state"] = {}
        
        self.memory["system_state"].update(updates)
        self._save()
    
    def add_project(self, project_id: str, project_data: Dict[str, Any]):
        """Add or update a project"""
        if "projects" not in self.memory:
            self.memory["projects"] = {}
        
        self.memory["projects"][project_id] = {
            **project_data,
            "last_updated": datetime.now().isoformat()
        }
        self._save()
    
    def get_relevant(self, query: str) -> Dict[str, Any]:
        """
        Get relevant structured memory entries based on query
        
        Args:
            query: Query string to match against
        
        Returns:
            Dictionary of relevant memory entries
        """
        query_lower = query.lower()
        relevant = {}
        
        # Check user profile
        if "user_profile" in self.memory:
            profile = self.memory["user_profile"]
            if any(term in query_lower for term in ["preference", "interest", "user", "profile"]):
                relevant["user_profile"] = profile
        
        # Check projects
        if "projects" in self.memory:
            projects = self.memory["projects"]
            if any(term in query_lower for term in ["project", "task", "work"]):
                relevant["projects"] = projects
        
        # Check system state
        if "system_state" in self.memory:
            system = self.memory["system_state"]
            if any(term in query_lower for term in ["personality", "capability", "system"]):
                relevant["system_state"] = system
        
        return relevant
    
    def get_all(self) -> Dict[str, Any]:
        """Get all structured memory"""
        return self.memory.copy()
    
    def clear(self, section: Optional[str] = None):
        """
        Clear structured memory (or a specific section)
        
        Args:
            section: Optional section to clear (e.g., "user_profile")
        """
        if section:
            if section in self.memory:
                self.memory[section] = self._default_structure().get(section, {})
        else:
            self.memory = self._default_structure()
        
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about structured memory"""
        return {
            "memory_file": str(self.memory_file),
            "sections": list(self.memory.keys()),
            "user_profile_keys": list(self.memory.get("user_profile", {}).keys()),
            "projects_count": len(self.memory.get("projects", {})),
            "last_updated": self.memory.get("last_updated")
        }

