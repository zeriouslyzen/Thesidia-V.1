#!/usr/bin/env python3
"""
Scientific Simulator - Scientific simulations and experiments
Model chemical reactions, simulate physical systems, test environmental interactions
Grounded in real science
"""

from typing import Dict, List, Optional, Any
import re


class ScientificSimulator:
    """
    Scientific simulation system for modeling interactions.
    Grounded in real science - not mystical speculation.
    """
    
    def __init__(self):
        self.enabled = True
        
    def should_simulate(self, query: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if scientific simulation would be helpful.
        Returns True if simulation is relevant.
        """
        query_lower = query.lower()
        
        # Simulation request keywords
        simulation_keywords = [
            'simulate', 'model', 'what happens if', 'if X and Y', 'interaction',
            'combine', 'effect', 'result', 'outcome', 'predict', 'calculate'
        ]
        
        # Multi-factor interactions (good for simulation)
        multi_factor = any(phrase in query_lower for phrase in [
            'wind + sound', 'aluminum + bioelectric', 'chemical + physical',
            'environmental +', 'if X and Y combine'
        ])
        
        return any(keyword in query_lower for keyword in simulation_keywords) or multi_factor
    
    def generate_simulation_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate scientific simulation prompt.
        """
        prompt_parts = [
            "[SCIENTIFIC SIMULATION MODE]",
            "",
            "You are modeling scientific interactions. Show:",
            "",
            "- What factors are being combined/interacting",
            "- Scientific principles involved (physics, chemistry, biology)",
            "- Predicted outcomes based on real science",
            "- Uncertainty and limitations (what we know vs. what we're modeling)",
            "",
            "GROUNDING:",
            "- All simulations must be grounded in real scientific principles",
            "- Cite relevant laws/theories (e.g., electromagnetic principles, chemical reactions)",
            "- NOT mystical speculation - use real physics/chemistry/biology",
            "- Acknowledge uncertainty when appropriate",
            "",
            "EXAMPLES:",
            "- 'Based on electromagnetic principles, aluminum might interfere with bioelectric fields by...'",
            "- 'If we model wind + sound + electromagnetic charge, we get resonance patterns that...'",
            "- 'Chemical reaction: X + Y → Z, based on known reaction pathways...'",
            "",
            "Be scientific, precise, and acknowledge limitations."
        ]
        
        # Add context-specific instructions
        if context:
            factors = context.get('factors', [])
            if factors:
                prompt_parts.append(f"\nFactors to model: {', '.join(factors)}")
        
        return "\n".join(prompt_parts)
    
    def extract_simulation_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract simulation content from response.
        Returns dict with simulation findings.
        """
        # Look for simulation patterns
        simulation_patterns = [
            r'based on (.*?) principles?',
            r'if we model (.*?)(?:,|\.|$)',
            r'simulation shows? (.*?)(?:,|\.|$)',
            r'predicted outcome[:\s]+(.*?)(?=\n\n|\n[A-Z]|$)',
        ]
        
        simulation_findings = []
        for pattern in simulation_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            simulation_findings.extend(matches)
        
        return {
            'simulation_findings': [f.strip() for f in simulation_findings],
            'has_simulation': len(simulation_findings) > 0
        }

