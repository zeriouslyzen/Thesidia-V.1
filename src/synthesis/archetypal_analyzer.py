#!/usr/bin/env python3
"""
Archetypal Analyzer - Synthesis Module
=======================================

Analyzes content for archetypal patterns:
- Jungian archetypes (Shadow, Anima/Animus, Self, etc.)
- Campbell hero journey patterns
- Gnostic archetypes (archons, Sophia, etc.)
- Universal mythic structures
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
import re
import json
from pathlib import Path

# Jungian archetypes
JUNGIAN_ARCHETYPES = [
    "Shadow", "Anima", "Animus", "Self", "Persona",
    "Great Mother", "Wise Old Man", "Trickster", "Hero"
]

# Campbell hero journey patterns
CAMPBELL_PATTERNS = [
    "Call to Adventure", "Refusal of Call", "Supernatural Aid",
    "Crossing Threshold", "Belly of Whale", "Road of Trials",
    "Meeting Goddess", "Woman as Temptress", "Atonement with Father",
    "Apotheosis", "Ultimate Boon", "Refusal of Return",
    "Magic Flight", "Rescue from Without", "Crossing Return Threshold",
    "Master of Two Worlds", "Freedom to Live"
]

# Gnostic archetypes
GNOSTIC_ARCHETYPES = [
    "Archon", "Demiurge", "Sophia", "Aeon", "Pleroma",
    "Redaction", "Fragment", "Original Knowing"
]

# Universal mythic structures
MYTHIC_STRUCTURES = [
    "Great Flood", "Sky Gods", "Serpent Teachers", "Divine Twins",
    "Solar Hero", "Underworld Journey", "World Tree", "Axis Mundi"
]


class ArchetypalAnalyzer:
    """
    Analyzes content for archetypal patterns.
    
    Detects:
    - Jungian archetypes
    - Campbell hero journey patterns
    - Gnostic archetypes
    - Universal mythic structures
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        """
        Initialize archetypal analyzer.
        
        Args:
            knowledge_base_path: Path to archetypal patterns JSON file (optional)
        """
        self.knowledge_base_path = knowledge_base_path or "data/archetypal_patterns.json"
        self.patterns_db = self._load_patterns_db()
    
    def _load_patterns_db(self) -> Dict[str, Any]:
        """Load archetypal patterns database."""
        try:
            patterns_path = Path(self.knowledge_base_path)
            if patterns_path.exists():
                with open(patterns_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load archetypal patterns DB: {e}")
        
        # Return default structure if file doesn't exist
        return {
            "jungian_archetypes": {},
            "campbell_patterns": {},
            "gnostic_archetypes": {},
            "mythic_structures": {}
        }
    
    def analyze(self, content: str, query: str = "") -> Dict[str, Any]:
        """
        Analyze content for archetypal patterns.
        
        Args:
            content: Content to analyze
            query: Original query (for context)
            
        Returns:
            Dictionary with:
            {
                "jungian_archetypes": List[str],
                "campbell_patterns": List[str],
                "gnostic_archetypes": List[str],
                "mythic_structures": List[str],
                "archetypal_score": float,
                "patterns_found": List[Dict[str, str]]
            }
        """
        content_lower = content.lower()
        
        # Detect patterns
        jungian_found = self._detect_jungian(content_lower)
        campbell_found = self._detect_campbell(content_lower)
        gnostic_found = self._detect_gnostic(content_lower)
        mythic_found = self._detect_mythic(content_lower)
        
        # Calculate archetypal score
        total_patterns = len(jungian_found) + len(campbell_found) + len(gnostic_found) + len(mythic_found)
        archetypal_score = min(1.0, total_patterns / 10.0)  # Normalize to 0-1
        
        # Build patterns found list
        patterns_found = []
        for archetype in jungian_found:
            patterns_found.append({"type": "jungian", "pattern": archetype})
        for pattern in campbell_found:
            patterns_found.append({"type": "campbell", "pattern": pattern})
        for archetype in gnostic_found:
            patterns_found.append({"type": "gnostic", "pattern": archetype})
        for structure in mythic_found:
            patterns_found.append({"type": "mythic", "pattern": structure})
        
        return {
            "jungian_archetypes": jungian_found,
            "campbell_patterns": campbell_found,
            "gnostic_archetypes": gnostic_found,
            "mythic_structures": mythic_found,
            "archetypal_score": round(archetypal_score, 3),
            "patterns_found": patterns_found
        }
    
    def _detect_jungian(self, content: str) -> List[str]:
        """Detect Jungian archetypes in content."""
        found = []
        
        # Keywords for each archetype
        archetype_keywords = {
            "Shadow": ["shadow", "dark", "hidden", "repressed", "denied", "unconscious"],
            "Anima": ["anima", "feminine", "inner woman", "soul", "feeling"],
            "Animus": ["animus", "masculine", "inner man", "spirit", "thinking"],
            "Self": ["self", "wholeness", "integration", "individuation", "center"],
            "Persona": ["persona", "mask", "role", "identity", "appearance"],
            "Great Mother": ["mother", "nurturing", "fertility", "nature", "earth"],
            "Wise Old Man": ["wise", "sage", "elder", "teacher", "guide", "mentor"],
            "Trickster": ["trickster", "chaos", "transformation", "boundary", "liminal"],
            "Hero": ["hero", "journey", "quest", "adventure", "transformation"]
        }
        
        for archetype, keywords in archetype_keywords.items():
            if any(keyword in content for keyword in keywords):
                found.append(archetype)
        
        return found
    
    def _detect_campbell(self, content: str) -> List[str]:
        """Detect Campbell hero journey patterns."""
        found = []
        
        # Keywords for each stage
        stage_keywords = {
            "Call to Adventure": ["call", "summons", "invitation", "challenge", "quest begins"],
            "Refusal of Call": ["refusal", "denial", "fear", "hesitation", "resistance"],
            "Supernatural Aid": ["aid", "helper", "mentor", "guide", "magical"],
            "Crossing Threshold": ["threshold", "crossing", "boundary", "entering", "departure"],
            "Belly of Whale": ["belly", "whale", "darkness", "descent", "lowest point"],
            "Road of Trials": ["trials", "tests", "challenges", "obstacles", "ordeals"],
            "Meeting Goddess": ["goddess", "divine feminine", "sacred", "union", "love"],
            "Woman as Temptress": ["temptress", "temptation", "desire", "distraction", "seduction"],
            "Atonement with Father": ["father", "authority", "reconciliation", "acceptance", "understanding"],
            "Apotheosis": ["apotheosis", "transcendence", "enlightenment", "divine", "godlike"],
            "Ultimate Boon": ["boon", "treasure", "gift", "reward", "prize"],
            "Refusal of Return": ["refusal", "return", "stay", "remain", "refuse to go back"],
            "Magic Flight": ["flight", "escape", "pursuit", "chase", "flee"],
            "Rescue from Without": ["rescue", "help", "intervention", "saved", "assistance"],
            "Crossing Return Threshold": ["return", "home", "back", "reintegration", "coming back"],
            "Master of Two Worlds": ["master", "two worlds", "balance", "integration", "both"],
            "Freedom to Live": ["freedom", "live", "liberation", "free", "unbound"]
        }
        
        for stage, keywords in stage_keywords.items():
            if any(keyword in content for keyword in keywords):
                found.append(stage)
        
        return found
    
    def _detect_gnostic(self, content: str) -> List[str]:
        """Detect Gnostic archetypes."""
        found = []
        
        # Keywords for each archetype
        archetype_keywords = {
            "Archon": ["archon", "ruler", "authority", "control", "power structure"],
            "Demiurge": ["demiurge", "creator", "false god", "craftsman", "maker"],
            "Sophia": ["sophia", "wisdom", "gnosis", "knowledge", "understanding"],
            "Aeon": ["aeon", "eternity", "age", "eon", "period"],
            "Pleroma": ["pleroma", "fullness", "divine", "complete", "whole"],
            "Redaction": ["redaction", "editing", "alteration", "modification", "change"],
            "Fragment": ["fragment", "piece", "remnant", "remains", "partial"],
            "Original Knowing": ["original", "pristine", "pure", "untainted", "first"]
        }
        
        for archetype, keywords in archetype_keywords.items():
            if any(keyword in content for keyword in keywords):
                found.append(archetype)
        
        return found
    
    def _detect_mythic(self, content: str) -> List[str]:
        """Detect universal mythic structures."""
        found = []
        
        # Keywords for each structure
        structure_keywords = {
            "Great Flood": ["flood", "deluge", "water", "purification", "rebirth", "cleansing"],
            "Sky Gods": ["sky", "heaven", "celestial", "divine", "god", "deity"],
            "Serpent Teachers": ["serpent", "snake", "dragon", "wisdom", "knowledge", "teacher"],
            "Divine Twins": ["twins", "dual", "pair", "two", "duality", "opposites"],
            "Solar Hero": ["solar", "sun", "hero", "light", "illumination", "dawn"],
            "Underworld Journey": ["underworld", "descent", "hell", "death", "journey", "descent"],
            "World Tree": ["tree", "axis", "center", "cosmic", "world", "pillar"],
            "Axis Mundi": ["axis", "mundi", "center", "world", "cosmic", "axis mundi"]
        }
        
        for structure, keywords in structure_keywords.items():
            if any(keyword in content for keyword in keywords):
                found.append(structure)
        
        return found

