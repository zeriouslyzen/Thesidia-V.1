#!/usr/bin/env python3
"""
Concept Hierarchy - Dynamic concept tree structure
Manages hierarchical organization of concepts from abstract to specific
"""

from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import uuid


class ConceptNode:
    """Represents a node in the concept hierarchy"""
    
    def __init__(self, concept: str, level: int = 0, parent_id: Optional[str] = None):
        """
        Initialize concept node.
        
        Args:
            concept: Concept name
            level: Hierarchy level (0 = root, higher = more specific)
            parent_id: Parent concept ID
        """
        self.concept_id = str(uuid.uuid4())
        self.concept = concept
        self.level = level
        self.parent_id = parent_id
        self.children_ids: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "concept_id": self.concept_id,
            "concept": self.concept,
            "level": self.level,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConceptNode':
        """Create node from dictionary."""
        node = cls(
            concept=data["concept"],
            level=data.get("level", 0),
            parent_id=data.get("parent_id")
        )
        node.concept_id = data["concept_id"]
        node.children_ids = data.get("children_ids", [])
        node.metadata = data.get("metadata", {})
        return node


class ConceptHierarchy:
    """
    Dynamic concept tree structure.
    
    Organizes concepts hierarchically from abstract (root) to specific (leaves).
    """
    
    def __init__(self):
        """Initialize concept hierarchy."""
        # concept_id -> ConceptNode
        self.nodes: Dict[str, ConceptNode] = {}
        
        # concept_name -> concept_id (for quick lookup)
        self.concept_index: Dict[str, str] = {}
        
        # Root node
        self.root_id = self._create_node("root", level=0).concept_id
    
    def _create_node(self, concept: str, level: int = 0, parent_id: Optional[str] = None) -> ConceptNode:
        """
        Create a new concept node.
        
        Args:
            concept: Concept name
            level: Hierarchy level
            parent_id: Parent concept ID
            
        Returns:
            Created ConceptNode
        """
        node = ConceptNode(concept, level, parent_id)
        self.nodes[node.concept_id] = node
        self.concept_index[concept.lower()] = node.concept_id
        
        # Update parent's children list
        if parent_id and parent_id in self.nodes:
            if node.concept_id not in self.nodes[parent_id].children_ids:
                self.nodes[parent_id].children_ids.append(node.concept_id)
        
        return node
    
    def add_or_get_concept(self, concept: str, parent_concept: Optional[str] = None) -> str:
        """
        Add a concept or get existing concept ID.
        
        Args:
            concept: Concept name
            parent_concept: Optional parent concept name
            
        Returns:
            Concept ID
        """
        concept_lower = concept.lower()
        
        # Check if concept already exists
        if concept_lower in self.concept_index:
            return self.concept_index[concept_lower]
        
        # Determine parent
        parent_id = None
        level = 1
        
        if parent_concept:
            parent_lower = parent_concept.lower()
            if parent_lower in self.concept_index:
                parent_id = self.concept_index[parent_lower]
                parent_node = self.nodes[parent_id]
                level = parent_node.level + 1
        else:
            # Default to root
            parent_id = self.root_id
        
        # Create new node
        node = self._create_node(concept, level, parent_id)
        return node.concept_id
    
    def find_concept(self, concept: str) -> Optional[str]:
        """
        Find concept ID by name.
        
        Args:
            concept: Concept name
            
        Returns:
            Concept ID or None
        """
        return self.concept_index.get(concept.lower())
    
    def get_children(self, concept_id: str) -> List[str]:
        """
        Get children concept IDs.
        
        Args:
            concept_id: Parent concept ID
            
        Returns:
            List of child concept IDs
        """
        if concept_id not in self.nodes:
            return []
        return self.nodes[concept_id].children_ids.copy()
    
    def get_parent(self, concept_id: str) -> Optional[str]:
        """
        Get parent concept ID.
        
        Args:
            concept_id: Concept ID
            
        Returns:
            Parent concept ID or None
        """
        if concept_id not in self.nodes:
            return None
        return self.nodes[concept_id].parent_id
    
    def get_path_to_root(self, concept_id: str) -> List[str]:
        """
        Get path from concept to root.
        
        Args:
            concept_id: Starting concept ID
            
        Returns:
            List of concept IDs from concept to root
        """
        path = []
        current_id = concept_id
        
        while current_id and current_id in self.nodes:
            path.append(current_id)
            current_id = self.nodes[current_id].parent_id
        
        return path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert hierarchy to dictionary."""
        return {
            "root_id": self.root_id,
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "concept_index": self.concept_index
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load hierarchy from dictionary."""
        self.root_id = data.get("root_id")
        self.nodes = {}
        self.concept_index = data.get("concept_index", {})
        
        # Reconstruct nodes
        if "nodes" in data:
            for node_id, node_data in data["nodes"].items():
                node = ConceptNode.from_dict(node_data)
                self.nodes[node_id] = node

