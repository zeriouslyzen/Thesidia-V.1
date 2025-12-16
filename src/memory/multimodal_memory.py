#!/usr/bin/env python3
"""
Multimodal Memory - MemVerse Implementation
Adds multimodal memory and knowledge distillation for lifelong learning
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json

from .experience_processor import ExperienceProcessor
from .knowledge_distiller import KnowledgeDistiller
from .consolidator import Consolidator


class MultimodalMemory:
    """
    Multimodal memory system for lifelong learning.
    
    Processes raw multimodal experiences, consolidates into long-term memory,
    and periodically distills knowledge to parametric models.
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize multimodal memory system.
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.storage_dir = self.base_dir / "data" / "memory" / "multimodal"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.experience_processor = ExperienceProcessor()
        self.consolidator = Consolidator()
        self.knowledge_distiller = KnowledgeDistiller()
        
        # Experience storage
        self.experiences: List[Dict[str, Any]] = []
        
        # Consolidated knowledge
        self.consolidated_knowledge: Dict[str, Any] = {}
        
        # Load existing data
        self._load_data()
    
    def process_experience(
        self,
        modality: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a multimodal experience.
        
        Args:
            modality: Type of experience (text, image, audio, video)
            content: Experience content
            metadata: Optional metadata
            
        Returns:
            Experience ID
        """
        # Process experience
        processed = self.experience_processor.process(modality, content, metadata)
        
        # Store experience
        experience = {
            "experience_id": processed["experience_id"],
            "modality": modality,
            "content": content,
            "processed": processed,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.experiences.append(experience)
        
        # Save data
        self._save_data()
        
        return processed["experience_id"]
    
    def consolidate_experiences(self, max_experiences: int = 100):
        """
        Consolidate recent experiences into long-term memory.
        
        Args:
            max_experiences: Maximum number of experiences to consolidate
        """
        # Get recent experiences
        recent_experiences = self.experiences[-max_experiences:]
        
        # Consolidate
        consolidated = self.consolidator.consolidate(recent_experiences)
        
        # Merge with existing consolidated knowledge
        self.consolidated_knowledge.update(consolidated)
        
        # Save data
        self._save_data()
    
    def distill_knowledge(self) -> Dict[str, Any]:
        """
        Distill essential knowledge from consolidated memory.
        
        Returns:
            Distilled knowledge dictionary
        """
        distilled = self.knowledge_distiller.distill(self.consolidated_knowledge)
        
        # Save distilled knowledge
        distilled_file = self.storage_dir / "distilled_knowledge.json"
        with open(distilled_file, 'w') as f:
            json.dump(distilled, f, indent=2)
        
        return distilled
    
    def retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant context from multimodal memory.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            Dictionary with retrieved context
        """
        # Simple text-based retrieval (can be enhanced with embeddings)
        relevant_experiences = []
        
        query_lower = query.lower()
        for experience in self.experiences:
            # Check if query matches experience content
            if experience["modality"] == "text":
                content = str(experience.get("content", ""))
                if query_lower in content.lower():
                    relevant_experiences.append(experience)
        
        # Format context
        formatted_context = self._format_context(relevant_experiences[:top_k])
        
        return {
            "formatted": formatted_context,
            "experiences": relevant_experiences[:top_k]
        }
    
    def _format_context(self, experiences: List[Dict[str, Any]]) -> str:
        """Format experiences into context string."""
        if not experiences:
            return ""
        
        context_parts = []
        for exp in experiences:
            modality = exp.get("modality", "unknown")
            content = str(exp.get("content", ""))[:200]
            context_parts.append(f"[{modality}] {content}...")
        
        return "\n".join(context_parts)
    
    def _save_data(self):
        """Save data to disk."""
        try:
            data = {
                "experiences": self.experiences[-1000:],  # Keep last 1000
                "consolidated_knowledge": self.consolidated_knowledge,
                "saved_at": datetime.now().isoformat()
            }
            
            storage_file = self.storage_dir / "multimodal_memory.json"
            with open(storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save multimodal memory: {e}")
    
    def _load_data(self):
        """Load data from disk."""
        try:
            storage_file = self.storage_dir / "multimodal_memory.json"
            if not storage_file.exists():
                return
            
            with open(storage_file, 'r') as f:
                data = json.load(f)
            
            self.experiences = data.get("experiences", [])
            self.consolidated_knowledge = data.get("consolidated_knowledge", {})
        except Exception as e:
            print(f"Warning: Could not load multimodal memory: {e}")

