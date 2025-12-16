#!/usr/bin/env python3
"""
Schema Manager - Manage cognitive schemas
Handles schema storage, retrieval, and relationship tracking
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
import uuid
from datetime import datetime


class SchemaManager:
    """
    Manages cognitive schemas.
    
    Handles schema storage, retrieval, and relationship tracking.
    """
    
    def __init__(self):
        """Initialize schema manager."""
        # schema_id -> schema dict
        self.schemas: Dict[str, Dict[str, Any]] = {}
        
        # Schema relationships: schema_id -> [related_schema_ids]
        self.schema_relationships: Dict[str, List[str]] = defaultdict(list)
        
        # Schema versioning: schema_id -> [version_history]
        self.schema_versions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def create_schema(self, name: str, initial_knowledge: Optional[str] = None) -> str:
        """
        Create a new schema.
        
        Args:
            name: Schema name
            initial_knowledge: Optional initial knowledge
            
        Returns:
            Schema ID
        """
        schema_id = str(uuid.uuid4())
        
        schema = {
            "schema_id": schema_id,
            "name": name,
            "knowledge_items": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1
        }
        
        if initial_knowledge:
            schema["knowledge_items"].append({
                "knowledge": initial_knowledge,
                "added_at": datetime.now().isoformat()
            })
        
        self.schemas[schema_id] = schema
        
        # Record version
        self.schema_versions[schema_id].append({
            "version": 1,
            "schema": schema.copy(),
            "timestamp": datetime.now().isoformat()
        })
        
        return schema_id
    
    def get_schema(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        Get schema by ID.
        
        Args:
            schema_id: Schema ID
            
        Returns:
            Schema dictionary or None
        """
        return self.schemas.get(schema_id)
    
    def update_schema(self, schema_id: str, knowledge: str):
        """
        Update schema with new knowledge.
        
        Args:
            schema_id: Schema ID
            knowledge: New knowledge to add
        """
        if schema_id not in self.schemas:
            return
        
        schema = self.schemas[schema_id]
        schema["knowledge_items"].append({
            "knowledge": knowledge,
            "added_at": datetime.now().isoformat()
        })
        schema["updated_at"] = datetime.now().isoformat()
        schema["version"] += 1
        
        # Record version
        self.schema_versions[schema_id].append({
            "version": schema["version"],
            "schema": schema.copy(),
            "timestamp": datetime.now().isoformat()
        })
    
    def find_matching_schemas(self, query: str, top_k: int = 5) -> List[str]:
        """
        Find schemas matching a query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of matching schema IDs
        """
        query_lower = query.lower()
        matches = []
        
        for schema_id, schema in self.schemas.items():
            # Simple keyword matching (can be enhanced with embeddings)
            schema_name = schema.get("name", "").lower()
            knowledge_text = " ".join([
                item.get("knowledge", "")
                for item in schema.get("knowledge_items", [])
            ]).lower()
            
            # Check if query matches schema name or knowledge
            if query_lower in schema_name or query_lower in knowledge_text:
                matches.append(schema_id)
        
        return matches[:top_k]
    
    def link_schemas(self, schema1_id: str, schema2_id: str):
        """
        Link two schemas.
        
        Args:
            schema1_id: First schema ID
            schema2_id: Second schema ID
        """
        if schema1_id not in self.schema_relationships:
            self.schema_relationships[schema1_id] = []
        if schema2_id not in self.schema_relationships[schema1_id]:
            self.schema_relationships[schema1_id].append(schema2_id)
        
        # Bidirectional link
        if schema2_id not in self.schema_relationships:
            self.schema_relationships[schema2_id] = []
        if schema1_id not in self.schema_relationships[schema2_id]:
            self.schema_relationships[schema2_id].append(schema1_id)
    
    def get_schema_version_history(self, schema_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a schema.
        
        Args:
            schema_id: Schema ID
            
        Returns:
            List of version records
        """
        return self.schema_versions.get(schema_id, [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schemas to dictionary."""
        return {
            "schemas": self.schemas,
            "schema_relationships": dict(self.schema_relationships),
            "schema_versions": {
                k: v for k, v in self.schema_versions.items()
            }
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load schemas from dictionary."""
        self.schemas = data.get("schemas", {})
        self.schema_relationships = defaultdict(list, data.get("schema_relationships", {}))
        self.schema_versions = defaultdict(list, data.get("schema_versions", {}))

