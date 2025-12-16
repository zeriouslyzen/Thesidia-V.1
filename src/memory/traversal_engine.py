#!/usr/bin/env python3
"""
Traversal Engine - Semantic path traversal
Provides top-down and bottom-up traversal of concept hierarchy
"""

from typing import List, Set, Dict, Optional
from collections import deque

from .concept_hierarchy import ConceptHierarchy


class TraversalEngine:
    """
    Semantic path traversal engine.
    
    Provides efficient traversal of concept hierarchy for knowledge retrieval.
    """
    
    def __init__(self, concept_hierarchy: ConceptHierarchy):
        """
        Initialize traversal engine.
        
        Args:
            concept_hierarchy: ConceptHierarchy instance
        """
        self.hierarchy = concept_hierarchy
    
    def traverse_top_down(self, start_concepts: List[str], max_depth: int = 3) -> List[str]:
        """
        Traverse hierarchy top-down (abstract -> specific).
        
        Args:
            start_concepts: List of starting concept IDs
            max_depth: Maximum depth to traverse
            
        Returns:
            List of concept IDs in traversal order
        """
        visited: Set[str] = set()
        result: List[str] = []
        
        # Start from root and traverse down to start concepts
        queue = deque([self.hierarchy.root_id])
        depth = 0
        
        while queue and depth < max_depth:
            level_size = len(queue)
            depth += 1
            
            for _ in range(level_size):
                current_id = queue.popleft()
                
                if current_id in visited:
                    continue
                
                visited.add(current_id)
                
                # Add to result if it's a start concept or ancestor
                if current_id in start_concepts or self._is_ancestor_of_any(current_id, start_concepts):
                    result.append(current_id)
                
                # Add children to queue
                children = self.hierarchy.get_children(current_id)
                queue.extend(children)
        
        # Add start concepts if not already included
        for concept_id in start_concepts:
            if concept_id not in visited:
                result.append(concept_id)
                visited.add(concept_id)
        
        return result
    
    def traverse_bottom_up(self, start_concepts: List[str], max_depth: int = 3) -> List[str]:
        """
        Traverse hierarchy bottom-up (specific -> abstract).
        
        Args:
            start_concepts: List of starting concept IDs
            max_depth: Maximum depth to traverse
            
        Returns:
            List of concept IDs in traversal order
        """
        visited: Set[str] = set()
        result: List[str] = []
        
        # Start from start concepts and traverse up to root
        queue = deque(start_concepts)
        depth = 0
        
        while queue and depth < max_depth:
            level_size = len(queue)
            depth += 1
            
            for _ in range(level_size):
                current_id = queue.popleft()
                
                if current_id in visited:
                    continue
                
                visited.add(current_id)
                result.append(current_id)
                
                # Add parent to queue
                parent_id = self.hierarchy.get_parent(current_id)
                if parent_id and parent_id not in visited:
                    queue.append(parent_id)
        
        return result
    
    def find_semantic_path(self, concept1_id: str, concept2_id: str) -> Optional[List[str]]:
        """
        Find semantic path between two concepts.
        
        Args:
            concept1_id: First concept ID
            concept2_id: Second concept ID
            
        Returns:
            List of concept IDs forming the path, or None if no path exists
        """
        # Get paths to root
        path1 = self.hierarchy.get_path_to_root(concept1_id)
        path2 = self.hierarchy.get_path_to_root(concept2_id)
        
        if not path1 or not path2:
            return None
        
        # Find lowest common ancestor
        lca = None
        for node_id in path1:
            if node_id in path2:
                lca = node_id
                break
        
        if not lca:
            return None
        
        # Build path: concept1 -> LCA -> concept2
        path = []
        
        # Add path from concept1 to LCA
        lca_index = path1.index(lca)
        path.extend(path1[:lca_index + 1])
        
        # Add path from LCA to concept2 (reverse)
        lca_index2 = path2.index(lca)
        path.extend(reversed(path2[:lca_index2]))
        
        return path
    
    def _is_ancestor_of_any(self, ancestor_id: str, concept_ids: List[str]) -> bool:
        """
        Check if ancestor_id is an ancestor of any concept in concept_ids.
        
        Args:
            ancestor_id: Potential ancestor concept ID
            concept_ids: List of concept IDs to check
            
        Returns:
            True if ancestor_id is an ancestor of any concept
        """
        for concept_id in concept_ids:
            path = self.hierarchy.get_path_to_root(concept_id)
            if ancestor_id in path:
                return True
        return False

