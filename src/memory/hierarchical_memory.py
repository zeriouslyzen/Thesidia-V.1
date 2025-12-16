#!/usr/bin/env python3
"""
Hierarchical Semantic Memory - SHIMI Implementation
Replaces flat vector memory with hierarchical semantic organization
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

from .concept_hierarchy import ConceptHierarchy
from .semantic_encoder import SemanticEncoder
from .traversal_engine import TraversalEngine


class SemanticHierarchy:
    """
    Hierarchical semantic memory system.
    
    Organizes knowledge in a tree structure from abstract to specific concepts,
    enabling top-down semantic traversal and efficient retrieval.
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize hierarchical memory system.
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.storage_dir = self.base_dir / "data" / "memory" / "hierarchical"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.concept_tree = ConceptHierarchy()
        self.semantic_encoder = SemanticEncoder()
        self.traversal_engine = TraversalEngine(self.concept_tree)
        
        # Knowledge storage: concept_id -> knowledge items
        self.knowledge_store: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Concept relationships: parent -> [children]
        self.concept_relationships: Dict[str, List[str]] = defaultdict(list)
        
        # Load existing hierarchy if available
        self._load_hierarchy()
    
    def store_knowledge(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Store knowledge in hierarchical structure.
        
        Args:
            text: Knowledge text to store
            metadata: Optional metadata
            
        Returns:
            Concept ID where knowledge was stored
        """
        # Extract concepts from text
        concepts = self.semantic_encoder.extract_concepts(text)
        
        # Find or create concept nodes in hierarchy
        concept_id = self.concept_tree.add_or_get_concept(concepts[0] if concepts else "general")
        
        # Store knowledge at concept node
        knowledge_item = {
            "text": text,
            "concepts": concepts,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "concept_id": concept_id
        }
        
        self.knowledge_store[concept_id].append(knowledge_item)
        
        # Update relationships if multiple concepts
        if len(concepts) > 1:
            parent_concept = concepts[0]
            for child_concept in concepts[1:]:
                child_id = self.concept_tree.add_or_get_concept(child_concept)
                if child_id not in self.concept_relationships[concept_id]:
                    self.concept_relationships[concept_id].append(child_id)
        
        # Save hierarchy
        self._save_hierarchy()
        
        return concept_id
    
    def retrieve_context(self, query: str, top_k: int = 5, traversal_mode: str = "top_down") -> Dict[str, Any]:
        """
        Retrieve relevant context using hierarchical traversal.
        
        Args:
            query: Query string
            top_k: Number of results to return
            traversal_mode: "top_down" or "bottom_up"
            
        Returns:
            Dictionary with retrieved context
        """
        # Extract concepts from query
        query_concepts = self.semantic_encoder.extract_concepts(query)
        
        if not query_concepts:
            return {"formatted": "", "concepts": [], "knowledge_items": []}
        
        # Find matching concept nodes
        matching_concepts = []
        for concept in query_concepts:
            concept_id = self.concept_tree.find_concept(concept)
            if concept_id:
                matching_concepts.append(concept_id)
        
        # Traverse hierarchy to find related knowledge
        if traversal_mode == "top_down":
            related_concepts = self.traversal_engine.traverse_top_down(matching_concepts)
        else:
            related_concepts = self.traversal_engine.traverse_bottom_up(matching_concepts)
        
        # Collect knowledge from related concepts
        knowledge_items = []
        for concept_id in related_concepts[:top_k]:
            if concept_id in self.knowledge_store:
                knowledge_items.extend(self.knowledge_store[concept_id])
        
        # Format context
        formatted_context = self._format_context(knowledge_items)
        
        return {
            "formatted": formatted_context,
            "concepts": query_concepts,
            "knowledge_items": knowledge_items[:top_k]
        }
    
    def _format_context(self, knowledge_items: List[Dict[str, Any]]) -> str:
        """
        Format knowledge items into context string.
        
        Args:
            knowledge_items: List of knowledge items
            
        Returns:
            Formatted context string
        """
        if not knowledge_items:
            return ""
        
        context_parts = []
        for item in knowledge_items[:5]:  # Limit to 5 items
            text = item.get("text", "")
            if text:
                context_parts.append(f"- {text[:200]}...")
        
        return "\n".join(context_parts)
    
    def _save_hierarchy(self):
        """Save hierarchy to disk."""
        try:
            hierarchy_data = {
                "concept_tree": self.concept_tree.to_dict(),
                "concept_relationships": dict(self.concept_relationships),
                "knowledge_store": {
                    k: v for k, v in self.knowledge_store.items()
                },
                "saved_at": datetime.now().isoformat()
            }
            
            storage_file = self.storage_dir / "hierarchy.json"
            with open(storage_file, 'w') as f:
                json.dump(hierarchy_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save hierarchy: {e}")
    
    def _load_hierarchy(self):
        """Load hierarchy from disk."""
        try:
            storage_file = self.storage_dir / "hierarchy.json"
            if not storage_file.exists():
                return
            
            with open(storage_file, 'r') as f:
                hierarchy_data = json.load(f)
            
            # Restore concept tree
            if "concept_tree" in hierarchy_data:
                self.concept_tree.from_dict(hierarchy_data["concept_tree"])
            
            # Restore relationships
            if "concept_relationships" in hierarchy_data:
                self.concept_relationships = defaultdict(list, hierarchy_data["concept_relationships"])
            
            # Restore knowledge store
            if "knowledge_store" in hierarchy_data:
                self.knowledge_store = defaultdict(list, hierarchy_data["knowledge_store"])
        except Exception as e:
            print(f"Warning: Could not load hierarchy: {e}")

