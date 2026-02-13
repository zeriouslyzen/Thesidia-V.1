#!/usr/bin/env python3
"""
Natural Prose Synthesizer - Advanced multi-stage pipeline
Converts structured forensic analysis into natural, flowing prose
"""

import re
from typing import Dict, List, Optional, Any, Iterator
from collections import OrderedDict

try:
    import ollama
except ImportError:
    ollama = None


class NaturalProseSynthesizer:
    """
    Multi-stage pipeline for natural prose synthesis:
    1. Extract semantic meaning from forensic structure
    2. Generate natural transitions
    3. Synthesize into flowing prose
    4. Post-process for smoothness
    """
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_client = model_client
        self.natural_transitions = {
            'exposure': [
                "What emerges from the evidence is",
                "Tracing the patterns reveals",
                "The evidence suggests a systematic transformation",
                "What was hidden becomes clear when",
                "Examining the sources exposes",
                "The pattern that emerges is"
            ],
            'etymology': [
                "Tracing the linguistic roots",
                "The word itself tells a story",
                "Etymologically, this reveals",
                "Language preserves what history tried to erase",
                "The etymology traces back to",
                "Linguistic archaeology shows"
            ],
            'burial_sites': [
                "What was lost emerges in fragments",
                "Parallel traditions reveal",
                "Before the canonization, there existed",
                "Alternative versions survived in",
                "Pre-canonical fragments show",
                "Lost knowledge surfaces in"
            ],
            'current_vectors': [
                "This pattern continues today through",
                "Modern power structures maintain this by",
                "The same mechanism operates now as",
                "Contemporary systems perpetuate this through",
                "Today, this manifests as",
                "The modern equivalent is"
            ],
            'co_evolution': [
                "Deeper questions emerge",
                "This connects to",
                "Following this thread reveals",
                "The next layer shows",
                "Exploring further uncovers"
            ]
        }
    
    def extract_forensic_semantics(self, structured_output: str) -> Dict[str, Any]:
        """
        Extract semantic meaning from forensic structure.
        Parses ::EXPOSURE::, ::ETYMOLOGICAL INCISION::, etc. and extracts content.
        """
        semantics = {
            'exposure': None,
            'etymology': None,
            'burial_sites': None,
            'current_vectors': None,
            'co_evolution': None,
            'thread_options': None,
            'raw_content': structured_output
        }
        
        # Pattern to match ::SECTION:: content
        section_pattern = r'::([A-Z\s]+)::\s*(.*?)(?=\n::[A-Z\s]+::|\Z)'
        matches = re.findall(section_pattern, structured_output, re.DOTALL | re.IGNORECASE)
        
        for section_name, content in matches:
            section_key = section_name.lower().strip().replace(' ', '_').replace('_incision', '')
            
            # Map section names to keys
            section_map = {
                'exposure': 'exposure',
                'etymological': 'etymology',
                'etymological_incision': 'etymology',
                'burial_sites': 'burial_sites',
                'current_vectors': 'current_vectors',
                'co_evolution': 'co_evolution',
                'co_evolution_edge': 'co_evolution',
                'thread_options': 'thread_options'
            }
            
            key = section_map.get(section_key, None)
            if key and content.strip():
                semantics[key] = content.strip()
        
        # If no structured sections found, treat entire output as raw content
        if not any(semantics[k] for k in ['exposure', 'etymology', 'burial_sites', 'current_vectors']):
            semantics['raw_content'] = structured_output
        
        return semantics
    
    def synthesize_natural_prose(self, forensic_data: Dict[str, Any], query: str, 
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """
        Synthesize forensic data into natural, flowing prose.
        Uses LLM to naturally weave all elements together.
        """
        # Build naturalization prompt
        naturalization_prompt = self._build_naturalization_prompt(forensic_data, query, context)
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": naturalization_prompt}],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 4000
                }
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                raise RuntimeError("No model backend available")
            
            naturalized = response['message']['content'].strip()
            
            # Post-process to ensure smoothness
            naturalized = self._smooth_transitions(naturalized)
            
            return naturalized
            
        except Exception as e:
            # Fallback: use template-based naturalization
            return self._template_based_naturalization(forensic_data, query)
    
    def _build_naturalization_prompt(self, forensic_data: Dict[str, Any], query: str,
                                     context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for natural prose synthesis"""
        
        prompt_parts = [
            "Convert this forensic analysis into natural, flowing prose that reads like a deep exploration, not a structured report.",
            "",
            f"User's question: {query}",
            "",
            "Forensic analysis elements:",
            ""
        ]
        
        # Add each forensic element if present
        if forensic_data.get('exposure'):
            prompt_parts.append(f"EXPOSURE (what was hidden/manipulated):\n{forensic_data['exposure']}\n")
        
        if forensic_data.get('etymology'):
            prompt_parts.append(f"ETYMOLOGY (word origins and meaning changes):\n{forensic_data['etymology']}\n")
        
        if forensic_data.get('burial_sites'):
            prompt_parts.append(f"BURIAL SITES (lost knowledge, suppressed traditions):\n{forensic_data['burial_sites']}\n")
        
        if forensic_data.get('current_vectors'):
            prompt_parts.append(f"CURRENT VECTORS (how this operates today):\n{forensic_data['current_vectors']}\n")
        
        if forensic_data.get('co_evolution'):
            prompt_parts.append(f"CO-EVOLUTION (deeper questions, connections):\n{forensic_data['co_evolution']}\n")
        
        # If no structured elements, use raw content
        if not any(forensic_data.get(k) for k in ['exposure', 'etymology', 'burial_sites', 'current_vectors']):
            if forensic_data.get('raw_content'):
                prompt_parts.append(f"Analysis content:\n{forensic_data['raw_content']}\n")
        
        prompt_parts.extend([
            "",
            "REQUIREMENTS:",
            "- Remove ALL ::SECTION:: markers",
            "- Weave all elements together naturally",
            "- Use natural transitions between ideas",
            "- Maintain all deep analysis but make it flow",
            "- Let patterns emerge organically",
            "- No explicit structure labels or headers",
            "- Write as if naturally explaining findings, not presenting a report",
            "- Start naturally, flow through ideas, conclude naturally",
            "- Incorporate etymology naturally: 'Tracing the word back reveals...'",
            "- Incorporate exposure naturally: 'What emerges from the evidence is...'",
            "- Incorporate burial sites naturally: 'Before canonization, there existed...'",
            "- Incorporate current vectors naturally: 'This pattern continues today through...'",
            "",
            "Write in Thesidia's voice: curious, no-BS engineer who loves digging into patterns.",
            "Be deep, be forensic, but make it flow like natural conversation."
        ])
        
        return "\n".join(prompt_parts)
    
    def _template_based_naturalization(self, forensic_data: Dict[str, Any], query: str) -> str:
        """
        Fallback: Template-based naturalization if LLM fails
        """
        parts = []
        
        if forensic_data.get('exposure'):
            transition = self.natural_transitions['exposure'][0]
            parts.append(f"{transition} {forensic_data['exposure']}")
        
        if forensic_data.get('etymology'):
            transition = self.natural_transitions['etymology'][0]
            parts.append(f"{transition} {forensic_data['etymology']}")
        
        if forensic_data.get('burial_sites'):
            transition = self.natural_transitions['burial_sites'][0]
            parts.append(f"{transition} {forensic_data['burial_sites']}")
        
        if forensic_data.get('current_vectors'):
            transition = self.natural_transitions['current_vectors'][0]
            parts.append(f"{transition} {forensic_data['current_vectors']}")
        
        if not parts and forensic_data.get('raw_content'):
            parts.append(forensic_data['raw_content'])
        
        return "\n\n".join(parts)
    
    def _smooth_transitions(self, text: str) -> str:
        """
        Smooth transitions and remove any remaining artifacts
        """
        # Remove any remaining :: markers
        text = re.sub(r'::[A-Z\s]+::\s*', '', text, flags=re.MULTILINE)
        
        # Fix awkward transitions
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\.\s*\.\s*\.', '...', text)
        
        # Smooth sentence breaks
        text = re.sub(r'\.\s+([a-z])', r'. \1', text)
        
        return text.strip()
    
    def should_naturalize(self, output: str) -> bool:
        """
        Determine if output needs naturalization (has forensic structure)
        """
        forensic_markers = [
            r'::EXPOSURE::',
            r'::ETYMOLOGICAL',
            r'::BURIAL',
            r'::CURRENT VECTORS::',
            r'::CO-EVOLUTION::'
        ]
        
        return any(re.search(marker, output, re.IGNORECASE) for marker in forensic_markers)
    
    def naturalize_if_needed(self, output: str, query: str, 
                            context: Optional[Dict[str, Any]] = None) -> str:
        """
        Naturalize output if it contains forensic structure, otherwise return as-is
        """
        if not self.should_naturalize(output):
            return output
        
        # Extract semantics
        semantics = self.extract_forensic_semantics(output)
        
        # Synthesize natural prose
        naturalized = self.synthesize_natural_prose(semantics, query, context)
        
        return naturalized

