#!/usr/bin/env python3
"""
Memory Manager - Central coordinator for three-layer memory architecture
Coordinates Ephemeral, Structured, and Vector memory
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .ephemeral_memory import EphemeralMemory
from .structured_memory import StructuredMemory
from .vector_memory import VectorMemory
from .gatekeeper import MemoryGatekeeper
from .sanitizer import MemorySanitizer


class MemoryManager:
    """Central coordinator for advanced memory system"""
    
    def __init__(self, base_dir: Path = None, user_dir: Path = None):
        """
        Initialize memory manager with all three layers
        
        Args:
            base_dir: Base directory for data storage (for backward compatibility)
            user_dir: User-specific directory (if None, uses base_dir)
        """
        self.base_dir = base_dir or Path(".")
        self.user_dir = user_dir or self.base_dir
        
        # If user_dir is provided, use it for all memory layers
        # Otherwise, use base_dir (backward compatibility)
        memory_base = self.user_dir if user_dir else self.base_dir
        
        # Initialize three memory layers
        self.ephemeral = EphemeralMemory(base_dir=memory_base, max_interactions=2)
        self.structured = StructuredMemory(base_dir=memory_base)
        self.vector = VectorMemory(base_dir=memory_base, use_vector_db=False)
        
        # Initialize gatekeeper and sanitizer
        self.gatekeeper = MemoryGatekeeper()
        self.sanitizer = MemorySanitizer(strip_dangerous_topics=False)
    
    def store_interaction(self, user_input: str, assistant_output: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Store an interaction in memory (goes through gatekeeper and sanitizer)
        
        Args:
            user_input: User's message
            assistant_output: Assistant's response
            metadata: Optional metadata
        """
        # Sanitize first
        sanitized_user, sanitized_assistant = self.sanitizer.sanitize_interaction(
            user_input, assistant_output
        )
        
        # Always store in ephemeral (last 2 interactions)
        self.ephemeral.add_interaction(sanitized_user, sanitized_assistant, metadata)
        
        # Check if should store in long-term memory
        combined_content = f"{sanitized_user} {sanitized_assistant}"
        should_store, reason = self.gatekeeper.should_store(combined_content, metadata)
        
        if should_store:
            # Store in vector memory (semantic)
            self.vector.store(sanitized_assistant, {
                **(metadata or {}),
                "user_input": sanitized_user,
                "reason": reason
            })
        else:
            # Log why it wasn't stored (for debugging)
            if metadata and metadata.get("debug", False):
                print(f"Memory gatekeeper rejected storage: {reason}")
    
    def export_conversation_data(self) -> Dict[str, Any]:
        """
        Export all conversation data for download
        
        Returns:
            Dictionary with all conversation data
        """
        return {
            "ephemeral": {
                "interactions": self.ephemeral.get_last_n(),
                "stats": self.ephemeral.get_stats()
            },
            "structured": self.structured.get_all(),
            "vector": {
                "entries": self.vector.memory_entries,
                "stats": self.vector.get_stats()
            },
            "exported_at": datetime.now().isoformat()
        }
    
    def retrieve_context(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant memory context for a query
        
        Args:
            query: Query string
        
        Returns:
            Dictionary with ephemeral, structured, and vector memory context
        """
        # Ephemeral: Last 2 interactions
        ephemeral_context = self.ephemeral.get_context_string()
        
        # Structured: Relevant structured memory
        structured_context = self.structured.get_relevant(query)
        
        # Vector: Semantically relevant memory
        vector_results = self.vector.retrieve(query, top_k=5)
        
        return {
            "ephemeral": ephemeral_context,
            "structured": structured_context,
            "vector": vector_results,
            "formatted": self._format_context(ephemeral_context, structured_context, vector_results)
        }
    
    def _format_context(self, ephemeral: str, structured: Dict, vector: List[Dict]) -> str:
        """
        Format memory context for prompt injection
        
        Args:
            ephemeral: Ephemeral context string
            structured: Structured memory dictionary
            vector: Vector memory results
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add ephemeral context
        if ephemeral:
            context_parts.append(ephemeral)
        
        # Add structured context
        if structured:
            structured_str = "\n\nStructured Memory:\n"
            if "user_profile" in structured:
                structured_str += f"User Profile: {json.dumps(structured['user_profile'], indent=2)}\n"
            if "projects" in structured:
                structured_str += f"Projects: {json.dumps(structured['projects'], indent=2)}\n"
            if "system_state" in structured:
                structured_str += f"System State: {json.dumps(structured['system_state'], indent=2)}\n"
            context_parts.append(structured_str)
        
        # Add vector context
        if vector:
            vector_str = "\n\nRelevant Memory:\n"
            for i, entry in enumerate(vector, 1):
                vector_str += f"{i}. {entry.get('content', '')[:200]}...\n"
            context_parts.append(vector_str)
        
        return "\n".join(context_parts)
    
    def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile in structured memory"""
        self.structured.update_user_profile(updates)
    
    def update_system_state(self, updates: Dict[str, Any]):
        """Update system state in structured memory"""
        self.structured.update_system_state(updates)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about all memory layers"""
        return {
            "ephemeral": self.ephemeral.get_stats(),
            "structured": self.structured.get_stats(),
            "vector": self.vector.get_stats(),
            "last_updated": datetime.now().isoformat()
        }
    
    def clear_all(self):
        """Clear all memory (use with caution)"""
        self.ephemeral.clear()
        self.structured.clear()
        self.vector.clear()
    
    def migrate_from_old_state(self, old_state: Dict[str, Any]):
        """
        Migrate data from old state file format
        
        Args:
            old_state: Old state dictionary from thesidia_hybrid_adaptive_state.json
        """
        # Migrate interactions to ephemeral
        interactions = old_state.get("interactions", [])
        for interaction in interactions[-2:]:  # Only last 2
            user_input = interaction.get("input", "")
            assistant_output = interaction.get("output", "")
            metadata = {
                "timestamp": interaction.get("timestamp"),
                "type": interaction.get("type")
            }
            self.ephemeral.add_interaction(user_input, assistant_output, metadata)
        
        # Migrate structured data
        if "personality" in old_state:
            self.structured.set("system_state.personality", old_state["personality"])
        if "capabilities" in old_state:
            self.structured.set("system_state.capabilities", old_state["capabilities"])
        if "learning" in old_state:
            self.structured.set("system_state.learning", old_state["learning"])
        
        # Migrate gnostic_map, emergence, consciousness if needed
        if "gnostic_map" in old_state:
            self.structured.set("system_state.gnostic_map", old_state["gnostic_map"])
        if "emergence" in old_state:
            self.structured.set("system_state.emergence", old_state["emergence"])
        if "consciousness" in old_state:
            self.structured.set("system_state.consciousness", old_state["consciousness"])

