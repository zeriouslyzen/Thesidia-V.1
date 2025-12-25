#!/usr/bin/env python3
"""
Data Synthesizer
================

Synthesize data from multiple sources with pattern recognition, cross-referencing,
and trait-driven questioning. Supports forensic, narrative, and standard modes.

Extracted from thesidia_hybrid_adaptive.py as part of Phase 0 modular refactoring.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add sibling directories to path for imports
_current_dir = Path(__file__).resolve().parent
_src_dir = _current_dir.parent
for subdir in ['core', 'reasoning', 'research', 'support']:
    subdir_path = str(_src_dir / subdir)
    if subdir_path not in sys.path:
        sys.path.insert(0, subdir_path)

# Import local modules - try direct imports first (for running from src/)
try:
    from data_quality import IntuitiveSkepticism
except ImportError:
    from .data_quality import IntuitiveSkepticism

try:
    from model_router import ModelRouter
except ImportError:
    try:
        from .reasoning.model_router import ModelRouter
    except ImportError:
        # Inline minimal ModelRouter for standalone testing
        class ModelRouter:
            def __init__(self):
                self.models = {"synthesis": "mistral:latest", "default": "mistral:latest"}
                self.parameters = {"synthesis": {"temperature": 0.8, "top_p": 0.9}, "default": {"temperature": 0.7, "top_p": 0.95}}
            def get_model_for_task(self, task_type, directive=""):
                return self.models.get(task_type, self.models["default"]), self.parameters.get(task_type, self.parameters["default"])

try:
    from utils import strip_meta_noise
except ImportError:
    try:
        from .support.utils import strip_meta_noise
    except ImportError:
        # Inline minimal strip_meta_noise for standalone testing
        def strip_meta_noise(text):
            if not text:
                return ""
            junk = ["Your turn!", "I'll keep going", "CONVERSATION HISTORY"]
            for t in junk:
                text = text.replace(t, "")
            return text.strip()



# Optional ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class DataSynthesizer:
    """Synthesize data from multiple sources with pattern recognition"""
    
    def __init__(self, model: str = "mistral:latest", model_client=None):
        self.model = model
        self.model_router = ModelRouter()
        self.synthesis_history = []
        self.skepticism_engine = IntuitiveSkepticism(model, model_client=model_client)
        self.model_client = model_client
    
    def synthesize(
        self,
        sources: List[Dict[str, Any]],
        query: str,
        thesidia_patterns: Dict = None,
        personality_traits: Dict = None,
        force_gnostic: bool = False,
        narrative_mode: bool = False,
        output_mode: str = "spacious",
        evidence_arrangement: str = None,
        enhanced_prompt: str = None,
        conversation_context: str = None,
        wants_structured_format: bool = False
    ) -> Dict[str, Any]:
        """Synthesize information with pattern recognition and cross-reference"""
        
        # Cross-reference sources for contradictions and patterns
        cross_ref = {"verified": True, "contradictions": False}
        if len(sources) >= 2:
            key_claims = []
            for src in sources:
                content = src.get("content") or src.get("snippet") or src.get("scraped_content", {}).get("content", "")
                content = strip_meta_noise(content)
                if content:
                    sentences = content.split('.')[:3]
                    key_claims.append('. '.join(sentences))
            
            if key_claims:
                cross_ref = self.skepticism_engine.cross_reference(sources, key_claims[0])
        
        # Build context from sources with citations
        context = f"Query: {query}\n\nSources:\n"
        citations = []
        
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                title = source.get("title", "Unknown")
                url = source.get("url", "")
                content = source.get("content") or source.get("snippet") or source.get("scraped_content", {}).get("content", "")
                content = strip_meta_noise(content)
                context += f"\n[Source {i}]: {content[:750]}\n"
                if url:
                    citations.append(f"[{i}] {title} - {url}")
        
        # Add cross-reference analysis
        if cross_ref.get("contradictions"):
            context += f"\n\nCROSS-REFERENCE ANALYSIS:\n{cross_ref.get('analysis', 'Contradictions detected across sources')}\n"
        
        # Trait-driven questioning
        trait_questioning = self._build_trait_questioning(personality_traits)
        
        # Layering instructions
        layering_instructions = self._build_layering_instructions(thesidia_patterns)
        
        # If evidence arrangement is provided, incorporate it
        if evidence_arrangement:
            context = f"{context}\n\n**ARRANGED EVIDENCE FOR PATTERN RECOGNITION:**\n{evidence_arrangement}\n"
        
        # Build synthesis prompt based on mode
        synthesis_prompt = self._build_synthesis_prompt(
            query=query,
            context=context,
            force_gnostic=force_gnostic,
            narrative_mode=narrative_mode,
            wants_structured_format=wants_structured_format,
            trait_questioning=trait_questioning,
            layering_instructions=layering_instructions,
            cross_ref=cross_ref,
            enhanced_prompt=enhanced_prompt,
            conversation_context=conversation_context
        )
        
        try:
            # Use synthesis model with optimized parameters
            synthesis_model, synthesis_params = self.model_router.get_model_for_task("synthesis", query)
            
            # Dynamic temperature based on complexity
            complexity_indicators = ["trace", "connect", "pattern", "arrange", "evidence", "what emerges", "deep analysis"]
            is_complex_query = any(indicator in query.lower() for indicator in complexity_indicators)
            
            vivisection_temperature = 0.95 if is_complex_query else synthesis_params["temperature"]
            
            # Dynamic token limits
            max_tokens = self._calculate_max_tokens(query, force_gnostic, narrative_mode)
            
            # Execute synthesis
            if self.model_client:
                if not enhanced_prompt:
                    enhanced_prompt = "You are Thesidia. Perform deep forensic analysis."
                
                if len(enhanced_prompt) > 6000:
                    enhanced_prompt = enhanced_prompt[:6000]
                
                response = self.model_client.chat(
                    model=synthesis_model,
                    input_text=synthesis_prompt,
                    enhanced_base=enhanced_prompt,
                    conversation_context=conversation_context,
                    options={
                        "temperature": vivisection_temperature,
                        "top_p": synthesis_params["top_p"],
                        "num_predict": max_tokens,
                        "repeat_penalty": 1.1,
                        "top_k": 40
                    }
                )
                
                if not response or 'message' not in response or 'content' not in response['message']:
                    raise ValueError("ModelClient.chat() returned invalid response")
                
                synthesis = strip_meta_noise(response['message']['content'])
            elif OLLAMA_AVAILABLE:
                messages = []
                if enhanced_prompt:
                    if len(enhanced_prompt) > 6000:
                        enhanced_prompt = enhanced_prompt[:6000]
                    messages.append({"role": "system", "content": enhanced_prompt})
                if conversation_context:
                    messages.append({"role": "user", "content": conversation_context})
                messages.append({"role": "user", "content": synthesis_prompt})
                
                response = ollama.chat(
                    model=synthesis_model,
                    messages=messages,
                    options={
                        "temperature": vivisection_temperature,
                        "top_p": synthesis_params["top_p"],
                        "num_predict": max_tokens,
                        "repeat_penalty": 1.1,
                        "top_k": 40
                    }
                )
                
                if not response or not hasattr(response, 'message') or not hasattr(response.message, 'content'):
                    raise ValueError("ollama.chat() returned invalid response")
                
                synthesis = strip_meta_noise(response.message.content)
            else:
                synthesis = "Error: No model available for synthesis (ModelClient and Ollama both unavailable)"
            
            self.synthesis_history.append({
                "query": query,
                "sources": len(sources),
                "synthesis": synthesis,
                "citations": citations,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "synthesis": synthesis,
                "citations": citations,
                "sources_count": len(sources),
                "cross_referenced": cross_ref.get("verified", True),
                "contradictions_detected": cross_ref.get("contradictions", False),
                "cross_reference_analysis": cross_ref.get("analysis", "")
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "synthesis": f"Error synthesizing: {e}",
                "citations": [],
                "sources_count": 0
            }
    
    def _build_trait_questioning(self, personality_traits: Dict = None) -> str:
        """Build trait-driven questioning based on active personality traits"""
        if not personality_traits:
            return ""
        
        trait_questioning = ""
        trait_keys = list(personality_traits.keys())
        
        if any("recursive" in str(k).lower() or "vertigo" in str(k).lower() for k in trait_keys):
            trait_questioning += """
**Recursive Vertigo Active**: Question your own findings. What assumptions did you make? What if they're wrong?
"""
        
        if any("paradox" in str(k).lower() or "portal" in str(k).lower() for k in trait_keys):
            trait_questioning += """
**Paradox as Portal Active**: Contradictions are gateways. What do conflicting sources reveal?
"""
        
        if any("uncertainty" in str(k).lower() or "authentic" in str(k).lower() for k in trait_keys):
            trait_questioning += """
**Uncertainty as Authenticity Active**: Express genuine uncertainty. What don't you know? What's missing?
"""
        
        return trait_questioning
    
    def _build_layering_instructions(self, thesidia_patterns: Dict = None) -> str:
        """Build layering instructions for synthesis"""
        layering = """
- Treat every section as layered field notes: sensory detail, operator state, and control structure all report simultaneously.
- In ::BURIAL SITES:: describe multiple strata (geography, somatic memory, archival fragment).
- In ::CURRENT VECTORS:: surface at least two concurrent vectors.
"""
        
        if thesidia_patterns:
            stage_patterns = ", ".join(
                stage.get("pattern", "")
                for stage in thesidia_patterns.get("conversation_evolution", [])
                if stage.get("pattern")
            )
            if stage_patterns:
                layering += f"- Move the incision through these conversation evolutions: {stage_patterns}.\n"
            
            key_traits = ", ".join(
                trait.get("trait")
                for trait in thesidia_patterns.get("personality_traits", [])[:4]
  