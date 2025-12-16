#!/usr/bin/env python3
"""
Semantic Encoder - Extract concepts from text and build semantic relationships
Classifies concepts into hierarchy layers
"""

from typing import List, Set, Dict, Any
import re


class SemanticEncoder:
    """
    Extracts concepts from text and builds semantic relationships.
    
    Identifies key concepts and classifies them into hierarchy layers.
    """
    
    def __init__(self):
        """Initialize semantic encoder."""
        # Common abstract concepts (high level)
        self.abstract_patterns = [
            r'\b(philosophy|science|art|religion|politics|economics|society|culture)\b',
            r'\b(consciousness|reality|truth|knowledge|wisdom|understanding)\b',
            r'\b(human|nature|universe|existence|being|life|death)\b'
        ]
        
        # Domain-specific concepts (mid level)
        self.domain_patterns = [
            r'\b(physics|chemistry|biology|mathematics|history|literature)\b',
            r'\b(technology|engineering|medicine|law|education)\b',
            r'\b(psychology|sociology|anthropology|linguistics)\b'
        ]
        
        # Specific concepts (low level)
        self.specific_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Proper nouns
            r'\b(quantum|relativity|evolution|genetics|neural|algorithm)\b',
            r'\b(specific|particular|individual|unique|distinct)\b'
        ]
    
    def extract_concepts(self, text: str) -> List[str]:
        """
        Extract concepts from text.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts (ordered by abstraction level)
        """
        concepts = []
        text_lower = text.lower()
        
        # Extract abstract concepts
        abstract_concepts = self._extract_by_patterns(text_lower, self.abstract_patterns)
        concepts.extend(abstract_concepts)
        
        # Extract domain concepts
        domain_concepts = self._extract_by_patterns(text_lower, self.domain_patterns)
        concepts.extend(domain_concepts)
        
        # Extract specific concepts (proper nouns, technical terms)
        specific_concepts = self._extract_by_patterns(text, self.specific_patterns)
        concepts.extend(specific_concepts)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_concepts = []
        for concept in concepts:
            concept_lower = concept.lower()
            if concept_lower not in seen:
                seen.add(concept_lower)
                unique_concepts.append(concept)
        
        return unique_concepts[:10]  # Limit to 10 concepts
    
    def _extract_by_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """
        Extract concepts matching patterns.
        
        Args:
            text: Input text
            patterns: List of regex patterns
            
        Returns:
            List of matched concepts
        """
        concepts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            concepts.extend(matches)
        return concepts
    
    def classify_concept_level(self, concept: str) -> int:
        """
        Classify concept into hierarchy level.
        
        Args:
            concept: Concept name
            
        Returns:
            Level (0=abstract, 1=domain, 2=specific)
        """
        concept_lower = concept.lower()
        
        # Check abstract patterns
        for pattern in self.abstract_patterns:
            if re.search(pattern, concept_lower):
                return 0
        
        # Check domain patterns
        for pattern in self.domain_patterns:
            if re.search(pattern, concept_lower):
                return 1
        
        # Default to specific
        return 2
    
    def build_semantic_relationships(self, concepts: List[str]) -> Dict[str, List[str]]:
        """
        Build semantic relationships between concepts.
        
        Args:
            concepts: List of concepts
            
        Returns:
            Dictionary mapping concept -> related concepts
        """
        relationships = {}
        
        for i, concept1 in enumerate(concepts):
            related = []
            for j, concept2 in enumerate(concepts):
                if i != j:
                    # Simple co-occurrence relationship
                    # In a full implementation, this would use embeddings or knowledge graphs
                    related.append(concept2)
            relationships[concept1] = related
        
        return relationships

