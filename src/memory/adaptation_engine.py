#!/usr/bin/env python3
"""
Adaptation Engine - Schema updation/evolution/creation
Implements Piaget-inspired schema adaptation
"""

from typing import Dict, Any, Optional
from datetime import datetime

from .schema_manager import SchemaManager


class AdaptationEngine:
    """
    Schema adaptation engine.
    
    Implements Piaget-inspired schema adaptation:
    - Assimilation: Update existing schema
    - Accommodation: Evolve or create new schema
    """
    
    def __init__(self, schema_manager: SchemaManager):
        """
        Initialize adaptation engine.
        
        Args:
            schema_manager: SchemaManager instance
        """
        self.schema_manager = schema_manager
    
    def assimilate(self, schema_id: str, knowledge: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Assimilate knowledge into existing schema.
        
        Args:
            schema_id: Schema ID to update
            knowledge: Knowledge to assimilate
            metadata: Optional metadata
        """
        # Update schema with new knowledge
        self.schema_manager.update_schema(schema_id, knowledge)
    
    def accommodate(self, knowledge: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Accommodate knowledge by creating or evolving schema.
        
        Args:
            knowledge: Knowledge to accommodate
            metadata: Optional metadata
            
        Returns:
            Schema ID
        """
        # Extract concept/keyword from knowledge (simple extraction)
        # In full implementation, would use more sophisticated extraction
        words = knowledge.split()
        concept = words[0] if words else "general"
        
        # Check if similar schema exists
        matching_schemas = self.schema_manager.find_matching_schemas(concept, top_k=1)
        
        if matching_schemas:
            # Evolve existing schema
            schema_id = matching_schemas[0]
            self.schema_manager.update_schema(schema_id, knowledge)
            return schema_id
        else:
            # Create new schema
            schema_id = self.schema_manager.create_schema(concept, knowledge)
            return schema_id

