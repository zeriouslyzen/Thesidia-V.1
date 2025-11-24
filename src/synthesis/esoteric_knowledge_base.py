#!/usr/bin/env python3
"""
Esoteric Knowledge Base - Synthesis Module
==========================================

Structured esoteric knowledge systems:
- Hermeticism (7 Principles, Emerald Tablet)
- Kabbalah (Tree of Life, Sephirot, Paths)
- Tantra (Chakras, Kundalini, Energy systems)
- Alchemy (Transmutation, Elements, Stages)
- Sacred Geometry (Golden Ratio, Platonic Solids, Flower of Life)
- Energy Systems (Prana, Chi, Bioelectric fields)
- Ritual Architecture (Temple design, Alignment, Resonance)
- Mystery Schools (Initiation, Knowledge transmission)
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
import json
from pathlib import Path


class EsotericKnowledgeBase:
    """
    Structured esoteric knowledge systems.
    
    Provides access to:
    - Hermeticism
    - Kabbalah
    - Tantra
    - Alchemy
    - Sacred Geometry
    - Energy Systems
    - Ritual Architecture
    - Mystery Schools
    """
    
    def __init__(self, data_dir: str = "data/esoteric"):
        """
        Initialize esoteric knowledge base.
        
        Args:
            data_dir: Directory containing esoteric knowledge JSON files
        """
        self.data_dir = Path(data_dir)
        self.hermetic_principles = self._load_hermeticism()
        self.kabbalah_tree = self._load_kabbalah()
        self.tantra_systems = self._load_tantra()
        self.alchemy_stages = self._load_alchemy()
        self.sacred_geometry = self._load_sacred_geometry()
        self.energy_systems = self._load_energy_systems()
        self.ritual_architecture = self._load_ritual_architecture()
    
    def analyze_esoteric(self, content: str, query: str = "") -> Dict[str, Any]:
        """
        Analyze content for esoteric patterns.
        
        Args:
            content: Content to analyze
            query: Original query (for context)
            
        Returns:
            Dictionary with:
            {
                "hermetic_principles": List[str],
                "kabbalah_paths": List[str],
                "tantra_systems": List[str],
                "alchemy_stages": List[str],
                "sacred_geometry": List[str],
                "energy_systems": List[str],
                "ritual_patterns": List[str],
                "esoteric_score": float
            }
        """
        content_lower = content.lower()
        
        # Detect patterns
        hermetic_found = self._detect_hermetic(content_lower)
        kabbalah_found = self._detect_kabbalah(content_lower)
        tantra_found = self._detect_tantra(content_lower)
        alchemy_found = self._detect_alchemy(content_lower)
        geometry_found = self._detect_sacred_geometry(content_lower)
        energy_found = self._detect_energy_systems(content_lower)
        ritual_found = self._detect_ritual_architecture(content_lower)
        
        # Calculate esoteric score
        total_patterns = len(hermetic_found) + len(kabbalah_found) + len(tantra_found) + len(alchemy_found) + len(geometry_found) + len(energy_found) + len(ritual_found)
        esoteric_score = min(1.0, total_patterns / 10.0)  # Normalize to 0-1
        
        return {
            "hermetic_principles": hermetic_found,
            "kabbalah_paths": kabbalah_found,
            "tantra_systems": tantra_found,
            "alchemy_stages": alchemy_found,
            "sacred_geometry": geometry_found,
            "energy_systems": energy_found,
            "ritual_patterns": ritual_found,
            "esoteric_score": round(esoteric_score, 3)
        }
    
    def _load_hermeticism(self) -> Dict[str, Any]:
        """Load Hermetic principles and correspondences."""
        try:
            file_path = self.data_dir / "hermeticism.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Return default structure
        return {
            "seven_principles": {
                "mentalism": {"principle": "All is Mind", "indicators": ["mind", "mental", "thought", "consciousness"]},
                "correspondence": {"principle": "As above, so below", "indicators": ["correspondence", "as above", "so below", "macrocosm", "microcosm"]},
                "vibration": {"principle": "Nothing rests; everything moves", "indicators": ["vibration", "frequency", "resonance", "oscillation"]},
                "polarity": {"principle": "Everything is dual", "indicators": ["polarity", "opposites", "duality", "pairs"]},
                "rhythm": {"principle": "Everything flows", "indicators": ["rhythm", "cycle", "flow", "pendulum"]},
                "cause_and_effect": {"principle": "Every cause has its effect", "indicators": ["cause", "effect", "karma", "consequence"]},
                "gender": {"principle": "Gender is in everything", "indicators": ["gender", "masculine", "feminine", "yin", "yang"]}
            }
        }
    
    def _load_kabbalah(self) -> Dict[str, Any]:
        """Load Kabbalistic Tree of Life structure."""
        try:
            file_path = self.data_dir / "kabbalah.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "sephirot": {
                "keter": {"meaning": "Crown", "indicators": ["keter", "crown", "divine will"]},
                "chokhmah": {"meaning": "Wisdom", "indicators": ["chokhmah", "wisdom", "masculine"]},
                "binah": {"meaning": "Understanding", "indicators": ["binah", "understanding", "feminine"]},
                "chesed": {"meaning": "Mercy", "indicators": ["chesed", "mercy", "love"]},
                "gevurah": {"meaning": "Severity", "indicators": ["gevurah", "severity", "judgment"]},
                "tiferet": {"meaning": "Beauty", "indicators": ["tiferet", "beauty", "harmony"]},
                "netzach": {"meaning": "Victory", "indicators": ["netzach", "victory", "eternity"]},
                "hod": {"meaning": "Glory", "indicators": ["hod", "glory", "splendor"]},
                "yesod": {"meaning": "Foundation", "indicators": ["yesod", "foundation", "basis"]},
                "malkuth": {"meaning": "Kingdom", "indicators": ["malkuth", "kingdom", "manifestation"]}
            }
        }
    
    def _load_tantra(self) -> Dict[str, Any]:
        """Load Tantric systems (chakras, kundalini, etc.)."""
        try:
            file_path = self.data_dir / "tantra.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "chakras": {
                "root": {"indicators": ["root chakra", "muladhara", "earth", "grounding"]},
                "sacral": {"indicators": ["sacral chakra", "svadhisthana", "water", "creativity"]},
                "solar_plexus": {"indicators": ["solar plexus", "manipura", "fire", "power"]},
                "heart": {"indicators": ["heart chakra", "anahata", "air", "love"]},
                "throat": {"indicators": ["throat chakra", "vishuddha", "ether", "communication"]},
                "third_eye": {"indicators": ["third eye", "ajna", "light", "intuition"]},
                "crown": {"indicators": ["crown chakra", "sahasrara", "consciousness", "divine"]}
            },
            "kundalini": {"indicators": ["kundalini", "serpent power", "awakening", "energy"]}
        }
    
    def _load_alchemy(self) -> Dict[str, Any]:
        """Load Alchemical stages and correspondences."""
        try:
            file_path = self.data_dir / "alchemy.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "stages": {
                "calcination": {"indicators": ["calcination", "fire", "burning", "purification"]},
                "dissolution": {"indicators": ["dissolution", "water", "dissolving", "breaking down"]},
                "separation": {"indicators": ["separation", "air", "distillation", "purification"]},
                "conjunction": {"indicators": ["conjunction", "union", "merging", "combination"]},
                "fermentation": {"indicators": ["fermentation", "decay", "transformation", "putrefaction"]},
                "distillation": {"indicators": ["distillation", "purification", "refinement", "sublimation"]},
                "coagulation": {"indicators": ["coagulation", "solidification", "crystallization", "completion"]}
            },
            "elements": {
                "fire": {"indicators": ["fire", "sulfur", "spirit", "will"]},
                "water": {"indicators": ["water", "mercury", "soul", "emotion"]},
                "air": {"indicators": ["air", "salt", "body", "matter"]},
                "earth": {"indicators": ["earth", "quintessence", "philosopher's stone"]}
            }
        }
    
    def _load_sacred_geometry(self) -> Dict[str, Any]:
        """Load Sacred geometry patterns."""
        try:
            file_path = self.data_dir / "sacred_geometry.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "patterns": {
                "golden_ratio": {"indicators": ["golden ratio", "phi", "1.618", "divine proportion"]},
                "flower_of_life": {"indicators": ["flower of life", "sacred geometry", "pattern"]},
                "platonic_solids": {"indicators": ["platonic solid", "tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"]},
                "vesica_piscis": {"indicators": ["vesica piscis", "mandorla", "almond", "intersection"]},
                "metatron_cube": {"indicators": ["metatron cube", "sacred geometry", "pattern"]},
                "sri_yantra": {"indicators": ["sri yantra", "yantra", "sacred diagram"]}
            }
        }
    
    def _load_energy_systems(self) -> Dict[str, Any]:
        """Load Energy system knowledge (prana, chi, bioelectric)."""
        try:
            file_path = self.data_dir / "energy_systems.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "systems": {
                "prana": {"indicators": ["prana", "life force", "breath", "vital energy"]},
                "chi": {"indicators": ["chi", "qi", "energy", "vital force"]},
                "bioelectric": {"indicators": ["bioelectric", "electromagnetic", "field", "resonance"]},
                "meridians": {"indicators": ["meridian", "energy channel", "pathway", "nadis"]},
                "aura": {"indicators": ["aura", "energy field", "electromagnetic field"]}
            }
        }
    
    def _load_ritual_architecture(self) -> Dict[str, Any]:
        """Load Ritual architecture patterns."""
        try:
            file_path = self.data_dir / "ritual_architecture.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "patterns": {
                "temple_design": {"indicators": ["temple", "sacred space", "architecture", "design"]},
                "alignment": {"indicators": ["alignment", "astronomical", "solstice", "equinox"]},
                "resonance": {"indicators": ["resonance", "acoustic", "frequency", "sound"]},
                "sacred_sites": {"indicators": ["sacred site", "power spot", "ley line", "vortex"]}
            }
        }
    
    # Detection methods
    
    def _detect_hermetic(self, content: str) -> List[str]:
        """Detect Hermetic principles."""
        found = []
        for principle, data in self.hermetic_principles.get("seven_principles", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(principle)
        return found
    
    def _detect_kabbalah(self, content: str) -> List[str]:
        """Detect Kabbalistic paths/sephirot."""
        found = []
        for sephira, data in self.kabbalah_tree.get("sephirot", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(sephira)
        return found
    
    def _detect_tantra(self, content: str) -> List[str]:
        """Detect Tantric systems."""
        found = []
        # Check chakras
        for chakra, data in self.tantra_systems.get("chakras", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(chakra)
        # Check kundalini
        if any(ind in content for ind in self.tantra_systems.get("kundalini", {}).get("indicators", [])):
            found.append("kundalini")
        return found
    
    def _detect_alchemy(self, content: str) -> List[str]:
        """Detect Alchemical stages."""
        found = []
        for stage, data in self.alchemy_stages.get("stages", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(stage)
        return found
    
    def _detect_sacred_geometry(self, content: str) -> List[str]:
        """Detect Sacred geometry patterns."""
        found = []
        for pattern, data in self.sacred_geometry.get("patterns", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(pattern)
        return found
    
    def _detect_energy_systems(self, content: str) -> List[str]:
        """Detect Energy systems."""
        found = []
        for system, data in self.energy_systems.get("systems", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(system)
        return found
    
    def _detect_ritual_architecture(self, content: str) -> List[str]:
        """Detect Ritual architecture patterns."""
        found = []
        for pattern, data in self.ritual_architecture.get("patterns", {}).items():
            indicators = data.get("indicators", [])
            if any(ind in content for ind in indicators):
                found.append(pattern)
        return found

