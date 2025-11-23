#!/usr/bin/env python3
"""
Health/Wellness Coach System - Multi-Tradition Synthesis
Integrates: Chinese medicine, Western medicine, Vedic/Ayurvedic, Samurai philosophy
NOT literally these traditions - but the PRINCIPLES and CONCEPTS
"""

from typing import Dict, List, Optional, Any
import re


class HealthCoach:
    """
    Multi-tradition health/wellness coach that synthesizes principles from:
    - Chinese medicine: Energy flow, meridian systems, elemental balance
    - Western medicine: Biochemistry, physiology, evidence-based
    - Vedic/Ayurvedic: Doshas, elemental constitution, lifestyle
    - Samurai philosophy: Body-mind unity, discipline, awareness
    
    Coach approach: Guides, suggests, explains - NOT prescriptive doctor
    """
    
    def __init__(self):
        self.enabled = True
        
    def analyze_health_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze health query and determine which lenses to apply.
        Returns analysis configuration.
        """
        query_lower = query.lower()
        
        # Detect health-related keywords
        health_keywords = [
            'health', 'wellness', 'body', 'bioelectric', 'supplement', 'nutrition',
            'diet', 'exercise', 'energy', 'meridian', 'dosha', 'constitution',
            'aluminum', 'chemical', 'environmental', 'emf', 'electromagnetic',
            'feel off', 'symptoms', 'pain', 'fatigue', 'immune', 'digestion'
        ]
        
        is_health_query = any(keyword in query_lower for keyword in health_keywords)
        
        if not is_health_query:
            return {"enabled": False}
        
        # Determine which lenses to apply
        lenses = []
        
        # Environmental health lens
        if any(word in query_lower for word in ['aluminum', 'chemical', 'environmental', 'emf', 'electromagnetic', 'pollution']):
            lenses.append('environmental')
        
        # Bioelectric lens
        if any(word in query_lower for word in ['bioelectric', 'energy', 'field', 'meridian', 'chakra']):
            lenses.append('bioelectric')
        
        # Biochemical lens (Western medicine)
        if any(word in query_lower for word in ['supplement', 'nutrition', 'diet', 'biochemistry', 'physiology']):
            lenses.append('biochemical')
        
        # Energetic lens (Chinese medicine concepts)
        if any(word in query_lower for word in ['energy', 'flow', 'meridian', 'qi', 'elemental']):
            lenses.append('energetic')
        
        # Constitutional lens (Vedic/Ayurvedic concepts)
        if any(word in query_lower for word in ['constitution', 'dosha', 'type', 'nature']):
            lenses.append('constitutional')
        
        # Body-mind lens (Samurai philosophy concepts)
        if any(word in query_lower for word in ['mind', 'consciousness', 'awareness', 'discipline', 'unity']):
            lenses.append('body_mind')
        
        # Default: apply all relevant lenses
        if not lenses:
            lenses = ['environmental', 'bioelectric', 'biochemical', 'energetic']
        
        return {
            "enabled": True,
            "lenses": lenses,
            "coach_mode": True,  # NOT prescriptive doctor
            "scientific_grounding": True,  # All advice cross-referenced
            "multi_tradition": True  # Synthesize principles
        }
    
    def generate_health_prompt(self, query: str, analysis: Dict[str, Any]) -> str:
        """
        Generate health coach prompt based on analysis.
        """
        if not analysis.get("enabled"):
            return ""
        
        lenses = analysis.get("lenses", [])
        
        prompt_parts = [
            "[HEALTH COACH MODE ACTIVATED]",
            "",
            "You are analyzing this health/wellness query through multiple scientific and traditional lenses:",
            ""
        ]
        
        # Add lens descriptions
        lens_descriptions = {
            'environmental': "Environmental Health: How environmental factors (aluminum, chemicals, EMF, pollution) affect the body",
            'bioelectric': "Bioelectric Fields: How electromagnetic and bioelectric fields interact with human systems",
            'biochemical': "Biochemistry/Physiology: Western medicine principles - evidence-based biochemistry and physiology",
            'energetic': "Energy Flow: Chinese medicine concepts - energy flow, meridian systems, elemental balance (principles, not literal)",
            'constitutional': "Constitutional Analysis: Vedic/Ayurvedic concepts - doshas, elemental constitution, lifestyle (principles, not literal)",
            'body_mind': "Body-Mind Unity: Samurai philosophy concepts - body-mind unity, discipline, awareness (principles, not literal)"
        }
        
        for lens in lenses:
            if lens in lens_descriptions:
                prompt_parts.append(f"- {lens_descriptions[lens]}")
        
        prompt_parts.extend([
            "",
            "COACH APPROACH (NOT prescriptive doctor):",
            "- Guide, suggest, explain - NOT 'you must do X'",
            "- Say 'patterns suggest X, you might consider Y'",
            "- Cross-reference all advice with real science",
            "- Synthesize principles from multiple traditions (NOT literal traditions)",
            "- Body as part of cosmos: Bioelectric fields, environmental interactions, elemental balance",
            "",
            "SCIENTIFIC GROUNDING:",
            "- All health advice must be cross-referenced with real science",
            "- Can suggest scientific simulations if relevant",
            "- NOT mystical speculation - pattern-based analysis grounded in science",
            "",
            "Find connections others miss. Analyze like a CSI investigator for health issues."
        ])
        
        return "\n".join(prompt_parts)
    
    def suggest_meta_analysis(self, query: str, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Suggest meta-analysis if relevant.
        Returns suggestion string or None.
        """
        if not analysis.get("enabled"):
            return None
        
        # Suggest meta-analysis for complex health queries
        complex_keywords = ['bioelectric', 'environmental', 'multi', 'complex', 'interaction']
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "Want me to show my reasoning process here? I'm applying multiple health lenses simultaneously..."
        
        return None

