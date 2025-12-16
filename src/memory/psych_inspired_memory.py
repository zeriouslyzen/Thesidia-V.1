#!/usr/bin/env python3
"""
Psych-Inspired Memory - PISA Implementation
Implements Piaget-inspired schema adaptation
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json

from .schema_manager import SchemaManager
from .adaptation_engine import AdaptationEngine


class PsychInspiredMemory:
    """
    Psychologically-inspired adaptive memory system.
    
    Implements Piaget-inspired schema adaptation:
    - Schema updation (assimilation)
    - Schema evolution (accommodation)
    - Schema creation (new knowledge)
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize psych-inspired memory system.
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.storage_dir = self.base_dir / "data" / "memory" / "psych_inspired"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.schema_manager = SchemaManager()
        self.adaptation_engine = AdaptationEngine(self.schema_manager)
        
        # Load existing schemas
        self._load_schemas()
    
    def process_knowledge(self, knowledge: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Process knowledge and adapt schemas.
        
        Args:
            knowledge: Knowledge text
            metadata: Optional metadata
            
        Returns:
            Schema ID that knowledge was integrated into
        """
        # Find matching schemas
        matching_schemas = self.schema_manager.find_matching_schemas(knowledge)
        
        if matching_schemas:
            # Assimilation: update existing schema
            schema_id = matching_schemas[0]
            self.adaptation_engine.assimilate(schema_id, knowledge, metadata)
        else:
            # Accommodation: create new schema or evolve existing
            schema_id = self.adaptation_engine.accommodate(knowledge, metadata)
        
        # Save schemas
        self._save_schemas()
        
        return schema_id
    
    def retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context using schemas.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            Dictionary with retrieved context
        """
        # Find relevant schemas
        relevant_schemas = self.schema_manager.find_matching_schemas(query)
        
        # Get knowledge from schemas
        knowledge_items = []
        for schema_id in relevant_schemas[:top_k]:
            schema = self.schema_manager.get_schema(schema_id)
            if schema:
                knowledge_items.extend(schema.get("knowledge_items", []))
        
        # Format context
        formatted_context = self._format_context(knowledge_items)
        
        return {
            "formatted": formatted_context,
            "schemas": [self.schema_manager.get_schema(sid) for sid in relevant_schemas[:top_k]],
            "knowledge_items": knowledge_items[:top_k]
        }
    
    def _format_context(self, knowledge_items: List[Dict[str, Any]]) -> str:
        """Format knowledge items into context string."""
        if not knowledge_items:
            return ""
        
        context_parts = []
        for item in knowledge_items[:5]:
            text = item.get("knowledge", "")
            if text:
                context_parts.append(f"- {text[:200]}...")
        
        return "\n".join(context_parts)
    
    def _save_schemas(self):
        """Save schemas to disk."""
        try:
            schemas_data = self.schema_manager.to_dict()
            schemas_data["saved_at"] = datetime.now().isoformat()
            
            storage_file = self.storage_dir / "schemas.json"
            with open(storage_file, 'w') as f:
                json.dump(schemas_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save schemas: {e}")
    
    def _load_schemas(self):
        """Load schemas from disk."""
        try:
            storage_file = self.storage_dir / "schemas.json"
            if not storage_file.exists():
                return
            
            with open(storage_file, 'r') as f:
                schemas_data = json.load(f)
            
            self.schema_manager.from_dict(schemas_data)
        except Exception as e:
            print(f"Warning: Could not load schemas: {e}")

