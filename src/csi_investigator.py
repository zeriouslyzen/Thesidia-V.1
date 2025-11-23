#!/usr/bin/env python3
"""
CSI Investigator Mode - Multi-lens forensic analysis
Applies chemistry, physics, environmental, bioelectric lenses simultaneously
Finds connections others miss
"""

from typing import Dict, List, Optional, Any
import re


class CSIInvestigator:
    """
    CSI Investigator mode for complex sites/phenomena.
    Multi-lens simultaneous analysis: chemistry, physics, environmental, bioelectric.
    """
    
    def __init__(self):
        self.enabled = True
        
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine if CSI investigator mode should activate.
        Returns analysis configuration.
        """
        query_lower = query.lower()
        
        # Detect complex investigation keywords
        investigation_keywords = [
            'what\'s really going on', 'really happening', 'secrets', 'mystery',
            'investigate', 'analyze', 'forensic', 'what happened', 'how was',
            'gobekli tepe', 'pyramid', 'stonehenge', 'ancient site', 'archaeological',
            'complex', 'multi', 'lens', 'simultaneous'
        ]
        
        is_investigation_query = any(keyword in query_lower for keyword in investigation_keywords)
        
        if not is_investigation_query:
            return {"enabled": False}
        
        # Determine which lenses to apply
        lenses = []
        
        # Chemistry lens
        if any(word in query_lower for word in ['stone', 'material', 'composition', 'chemical', 'element', 'mineral']):
            lenses.append('chemistry')
        
        # Physics lens
        if any(word in query_lower for word in ['electromagnetic', 'resonance', 'acoustic', 'sound', 'frequency', 'wave', 'energy']):
            lenses.append('physics')
        
        # Environmental lens
        if any(word in query_lower for word in ['wind', 'solar', 'alignment', 'environmental', 'weather', 'climate']):
            lenses.append('environmental')
        
        # Bioelectric lens
        if any(word in query_lower for word in ['bioelectric', 'field', 'human', 'body', 'interaction']):
            lenses.append('bioelectric')
        
        # Default: apply all lenses for complex investigations
        if not lenses:
            lenses = ['chemistry', 'physics', 'environmental', 'bioelectric']
        
        return {
            "enabled": True,
            "lenses": lenses,
            "multi_lens": True,
            "find_connections": True,
            "scientific_simulation": True
        }
    
    def generate_csi_prompt(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Generate CSI investigator prompt based on analysis.
        """
        if not analysis.get("enabled"):
            return ""
        
        lenses = analysis.get("lenses", [])
        
        prompt_parts = [
            "[CSI INVESTIGATOR MODE ACTIVATED]",
            "",
            "You are analyzing this complex site/phenomenon through multiple scientific lenses simultaneously:",
            ""
        ]
        
        # Add lens descriptions
        lens_descriptions = {
            'chemistry': "Chemistry Lens: Stone composition, elemental analysis, weathering patterns, tool marks, material properties",
            'physics': "Physics Lens: Electromagnetic properties, sound resonance, acoustic patterns, frequency analysis, energy interactions",
            'environmental': "Environmental Lens: Wind patterns, solar alignments, weather effects, climate interactions, environmental factors",
            'bioelectric': "Bioelectric Lens: How site might interact with human bioelectric fields, electromagnetic interactions with living systems"
        }
        
        for lens in lenses:
            if lens in lens_descriptions:
                prompt_parts.append(f"- {lens_descriptions[lens]}")
        
        prompt_parts.extend([
            "",
            "INVESTIGATION APPROACH:",
            "- Apply ALL relevant lenses SIMULTANEOUSLY (not sequentially)",
            "- Find connections others miss - cross-connections between lenses",
            "- Run scientific simulations if relevant (e.g., 'if wind + sound + electromagnetic charge combine, what happens?')",
            "- Share cool connections and patterns discovered",
            "- NOT mystical speculation - all grounded in real science",
            "",
            "EXAMPLE CONNECTIONS:",
            "- 'Interesting - if wind + sound + electromagnetic charge + stone composition creates resonance...'",
            "- 'This pattern appears in pyramids too, but with different elements...'",
            "- 'Everyone misses X, but if you combine Y and Z...'",
            "",
            "Be like a CSI investigator: Find what others miss, connect the dots, reveal hidden patterns."
        ])
        
        return "\n".join(prompt_parts)
    
    def suggest_simulation(self, query: str, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Suggest scientific simulation if relevant.
        Returns suggestion string or None.
        """
        if not analysis.get("enabled"):
            return None
        
        # Suggest simulation for complex multi-factor interactions
        simulation_keywords = ['wind', 'sound', 'electromagnetic', 'charge', 'resonance', 'interaction', 'combine']
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in simulation_keywords) and len(analysis.get("lenses", [])) > 2:
            return "Want me to model the interactions? I can simulate what happens when these factors combine..."
        
        return None

