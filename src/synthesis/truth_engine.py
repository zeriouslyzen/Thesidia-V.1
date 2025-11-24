#!/usr/bin/env python3
"""
Truth Engine - 7-Layer Epistemology System
==========================================

Implements explicit truth scoring using weighted 7-layer validation.

Layers:
1. Empirical Reality (Physical Truth) - 15% weight
2. Pattern Truth (Cross-field Consistency) - 25% weight (highest)
3. Symbolic Truth (Meaning encoded in form) - 20% weight
4. Archetypal Truth (Collective Psychological Patterns) - 10% weight
5. Mythic Truth (Cultural Memory + Cosmology) - 15% weight
6. Esoteric Truth (Initiatory Knowledge) - 10% weight
7. Experiential Truth (Lived, embodied, intuitive) - 5% weight
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TruthEngine:
    """
    7-Layer Epistemology Truth Scoring System
    
    Calculates weighted truth scores across all 7 layers of knowledge validation.
    """
    
    def __init__(self, model: str = "clean-mistral:latest"):
        """
        Initialize Truth Engine.
        
        Args:
            model: Model name for LLM-based layer analysis (future use)
        """
        self.model = model
        self.layer_weights = {
            "empirical": 0.15,
            "pattern": 0.25,  # Highest weight - core strength
            "symbolic": 0.20,
            "archetypal": 0.10,
            "mythic": 0.15,
            "esoteric": 0.10,
            "experiential": 0.05
        }
    
    def calculate_truth_score(
        self, 
        claim: str, 
        sources: List[Dict[str, Any]], 
        query: str,
        user_experience: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate weighted truth score across all 7 layers.
        
        Args:
            claim: The claim or statement to evaluate
            sources: List of source dictionaries with content
            query: Original query that led to this claim
            user_experience: Optional user experience/input for experiential layer
            
        Returns:
            Dictionary with:
            {
                "truth_score": float (0.0-1.0),
                "layer_scores": {
                    "empirical": float,
                    "pattern": float,
                    "symbolic": float,
                    "archetypal": float,
                    "mythic": float,
                    "esoteric": float,
                    "experiential": float
                },
                "confidence": str ("HIGH" if 4+ layers align, "MEDIUM" if 2-3, "LOW" if 1),
                "layer_evidence": {
                    "empirical": List[str],
                    "pattern": List[str],
                    ...
                },
                "layers_aligned": int (number of layers with score > 0.5)
            }
        """
        # Calculate individual layer scores
        layer_scores = {
            "empirical": self._score_empirical(claim, sources),
            "pattern": self._score_pattern(claim, sources),
            "symbolic": self._score_symbolic(claim, sources),
            "archetypal": self._score_archetypal(claim, sources),
            "mythic": self._score_mythic(claim, sources),
            "esoteric": self._score_esoteric(claim, sources),
            "experiential": self._score_experiential(claim, user_experience)
        }
        
        # Collect evidence for each layer
        layer_evidence = {
            "empirical": self._get_empirical_evidence(claim, sources),
            "pattern": self._get_pattern_evidence(claim, sources),
            "symbolic": self._get_symbolic_evidence(claim, sources),
            "archetypal": self._get_archetypal_evidence(claim, sources),
            "mythic": self._get_mythic_evidence(claim, sources),
            "esoteric": self._get_esoteric_evidence(claim, sources),
            "experiential": self._get_experiential_evidence(claim, user_experience)
        }
        
        # Calculate weighted truth score
        truth_score = sum(
            layer_scores[layer] * self.layer_weights[layer]
            for layer in layer_scores.keys()
        )
        
        # Count aligned layers (score > 0.5)
        layers_aligned = sum(1 for score in layer_scores.values() if score > 0.5)
        
        # Determine confidence level
        if layers_aligned >= 4:
            confidence = "HIGH"
        elif layers_aligned >= 2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        return {
            "truth_score": round(truth_score, 3),
            "layer_scores": {k: round(v, 3) for k, v in layer_scores.items()},
            "confidence": confidence,
            "layer_evidence": layer_evidence,
            "layers_aligned": layers_aligned,
            "weights": self.layer_weights.copy()
        }
    
    def _score_empirical(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on empirical reality (engineering, physics, archaeology, biology, astronomy).
        
        Returns:
            Score 0.0-1.0 based on empirical evidence
        """
        if not sources:
            return 0.0
        
        empirical_indicators = [
            "archaeological", "astronomical", "biological", "chemical", "physical",
            "engineering", "scientific", "measured", "verified", "observed",
            "experiment", "data", "evidence", "study", "research"
        ]
        
        score = 0.0
        evidence_count = 0
        
        for source in sources:
            content = self._get_source_content(source).lower()
            
            # Check for empirical indicators
            indicator_count = sum(1 for ind in empirical_indicators if ind in content)
            if indicator_count > 0:
                evidence_count += 1
                score += min(0.3, indicator_count * 0.1)
        
        # Normalize by number of sources
        if evidence_count > 0:
            score = min(1.0, score / max(1, len(sources) / 2))
        
        return round(score, 3)
    
    def _score_pattern(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on pattern truth (cross-field consistency, pattern repetition).
        
        This is Thesidia's core strength.
        
        Returns:
            Score 0.0-1.0 based on pattern consistency
        """
        if len(sources) < 2:
            return 0.3  # Single source = lower pattern score
        
        # Check for cross-domain patterns
        pattern_indicators = [
            "pattern", "similar", "consistent", "across", "multiple",
            "repeated", "recurring", "parallel", "corresponds", "matches"
        ]
        
        score = 0.0
        pattern_matches = 0
        
        # Check if patterns appear across multiple sources
        for source in sources:
            content = self._get_source_content(source).lower()
            indicator_count = sum(1 for ind in pattern_indicators if ind in content)
            if indicator_count > 0:
                pattern_matches += 1
        
        # Higher score if patterns appear in multiple sources
        if pattern_matches >= 2:
            score = 0.7 + (pattern_matches / len(sources)) * 0.3
        elif pattern_matches == 1:
            score = 0.4
        else:
            score = 0.2
        
        return round(min(1.0, score), 3)
    
    def _score_symbolic(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on symbolic truth (meaning encoded in form).
        
        Returns:
            Score 0.0-1.0 based on symbolic density
        """
        if not sources:
            return 0.0
        
        symbolic_indicators = [
            "symbol", "symbolic", "meaning", "encode", "represent",
            "etymology", "linguistic", "word origin", "significance",
            "metaphor", "allegory", "sign", "glyph", "rune"
        ]
        
        score = 0.0
        symbolic_count = 0
        
        for source in sources:
            content = self._get_source_content(source).lower()
            indicator_count = sum(1 for ind in symbolic_indicators if ind in content)
            if indicator_count > 0:
                symbolic_count += 1
                score += min(0.4, indicator_count * 0.15)
        
        if symbolic_count > 0:
            score = min(1.0, score / max(1, len(sources) / 2))
        
        return round(score, 3)
    
    def _score_archetypal(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on archetypal truth (Jung, Campbell, Gnostic, collective psychology).
        
        Uses ArchetypalAnalyzer for more accurate detection.
        
        Returns:
            Score 0.0-1.0 based on archetypal patterns
        """
        if not sources:
            return 0.0
        
        # Try to use ArchetypalAnalyzer if available
        try:
            from .archetypal_analyzer import ArchetypalAnalyzer
            analyzer = ArchetypalAnalyzer()
            
            # Analyze all sources
            total_score = 0.0
            analyzed_count = 0
            
            for source in sources:
                content = self._get_source_content(source)
                if content:
                    analysis = analyzer.analyze(content, claim)
                    if analysis.get("archetypal_score", 0) > 0:
                        total_score += analysis["archetypal_score"]
                        analyzed_count += 1
            
            if analyzed_count > 0:
                return round(min(1.0, total_score / analyzed_count), 3)
        except Exception:
            # Fallback to simple keyword detection
            pass
        
        # Fallback: Simple keyword detection
        archetypal_indicators = [
            "archetype", "myth", "hero", "journey", "shadow", "anima",
            "collective", "unconscious", "gnostic", "archon", "sophia",
            "demiurge", "pattern", "universal", "psychological"
        ]
        
        score = 0.0
        archetypal_count = 0
        
        for source in sources:
            content = self._get_source_content(source).lower()
            indicator_count = sum(1 for ind in archetypal_indicators if ind in content)
            if indicator_count > 0:
                archetypal_count += 1
                score += min(0.35, indicator_count * 0.12)
        
        if archetypal_count > 0:
            score = min(1.0, score / max(1, len(sources) / 2))
        
        return round(score, 3)
    
    def _score_mythic(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on mythic truth (cultural memory, cosmology, educational architecture).
        
        Returns:
            Score 0.0-1.0 based on mythic connections
        """
        if not sources:
            return 0.0
        
        mythic_indicators = [
            "myth", "mythology", "legend", "folklore", "tradition",
            "cultural", "cosmology", "cosmic", "ancient", "sacred",
            "ritual", "ceremony", "story", "narrative", "tale"
        ]
        
        score = 0.0
        mythic_count = 0
        
        for source in sources:
            content = self._get_source_content(source).lower()
            indicator_count = sum(1 for ind in mythic_indicators if ind in content)
            if indicator_count > 0:
                mythic_count += 1
                score += min(0.4, indicator_count * 0.15)
        
        if mythic_count > 0:
            score = min(1.0, score / max(1, len(sources) / 2))
        
        return round(score, 3)
    
    def _score_esoteric(self, claim: str, sources: List[Dict]) -> float:
        """
        Score based on esoteric truth (Hermeticism, Kabbalah, sacred geometry, energy systems).
        
        Returns:
            Score 0.0-1.0 based on esoteric knowledge
        """
        if not sources:
            return 0.0
        
        esoteric_indicators = [
            "esoteric", "hermetic", "kabbalah", "tantra", "alchemy",
            "sacred geometry", "energy", "chakra", "kundalini", "prana",
            "chi", "ritual", "initiation", "mystery", "occult"
        ]
        
        score = 0.0
        esoteric_count = 0
        
        for source in sources:
            content = self._get_source_content(source).lower()
            indicator_count = sum(1 for ind in esoteric_indicators if ind in content)
            if indicator_count > 0:
                esoteric_count += 1
                score += min(0.35, indicator_count * 0.12)
        
        if esoteric_count > 0:
            score = min(1.0, score / max(1, len(sources) / 2))
        
        return round(score, 3)
    
    def _score_experiential(self, claim: str, user_experience: Optional[str]) -> float:
        """
        Score based on experiential truth (lived experience, intuitive knowing, resonance).
        
        Returns:
            Score 0.0-1.0 based on experiential alignment
        """
        if not user_experience:
            return 0.0
        
        # Simple heuristic: if user experience is provided, give moderate score
        # In future, this could analyze alignment between claim and experience
        experience_length = len(user_experience)
        if experience_length > 100:
            return 0.6
        elif experience_length > 50:
            return 0.4
        else:
            return 0.2
    
    # Evidence collection methods
    
    def _get_empirical_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get empirical evidence snippets."""
        evidence = []
        for source in sources[:3]:  # Limit to first 3 sources
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["archaeological", "scientific", "measured", "verified"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_pattern_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get pattern evidence snippets."""
        evidence = []
        for source in sources[:3]:
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["pattern", "similar", "consistent", "across"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_symbolic_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get symbolic evidence snippets."""
        evidence = []
        for source in sources[:3]:
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["symbol", "meaning", "etymology", "encode"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_archetypal_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get archetypal evidence snippets."""
        evidence = []
        for source in sources[:3]:
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["archetype", "myth", "hero", "gnostic"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_mythic_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get mythic evidence snippets."""
        evidence = []
        for source in sources[:3]:
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["myth", "cultural", "cosmology", "tradition"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_esoteric_evidence(self, claim: str, sources: List[Dict]) -> List[str]:
        """Get esoteric evidence snippets."""
        evidence = []
        for source in sources[:3]:
            content = self._get_source_content(source)
            if any(ind in content.lower() for ind in ["esoteric", "hermetic", "kabbalah", "sacred geometry"]):
                evidence.append(content[:200] + "...")
        return evidence
    
    def _get_experiential_evidence(self, claim: str, user_experience: Optional[str]) -> List[str]:
        """Get experiential evidence."""
        if user_experience:
            return [user_experience[:200] + "..."]
        return []
    
    def _get_source_content(self, source: Dict[str, Any]) -> str:
        """Extract content from source dictionary."""
        return (
            source.get("content", "") or 
            source.get("snippet", "") or 
            source.get("scraped_content", {}).get("content", "") or
            ""
        )

