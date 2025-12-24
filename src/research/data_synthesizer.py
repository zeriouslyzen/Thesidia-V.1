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
                self.models = {"synthesis": "clean-mistral:latest", "default": "clean-mistral:latest"}
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
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
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
                if trait.get("trait")
            )
            if key_traits:
                layering += f"- Keep these trait signatures audible: {key_traits}.\n"
        
        return layering
    
    def _calculate_max_tokens(self, query: str, force_gnostic: bool, narrative_mode: bool) -> int:
        """Calculate dynamic token limits based on query complexity"""
        query_length = len(query.split())
        
        deep_indicators = ["true origins", "real origins", "what's really", "deeper", "secrets", 
                         "deep dive", "comprehensive", "genesis", "bible", "decode"]
        is_deep_query = any(indicator in query.lower() for indicator in deep_indicators)
        
        if narrative_mode:
            return 15000
        elif is_deep_query or force_gnostic:
            return 12000
        elif query_length <= 5:
            return 8000
        elif query_length <= 10:
            return 10000
        else:
            return 12000
    
    def _build_synthesis_prompt(
        self,
        query: str,
        context: str,
        force_gnostic: bool,
        narrative_mode: bool,
        wants_structured_format: bool,
        trait_questioning: str,
        layering_instructions: str,
        cross_ref: Dict,
        enhanced_prompt: str = None,
        conversation_context: str = None
    ) -> str:
        """Build the appropriate synthesis prompt based on mode"""
        
        # Extract personality context if available
        personality_context = ""
        if enhanced_prompt and "[YOUR PERSONALITY AND VOICE - HIGHEST PRIORITY]" in enhanced_prompt:
            personality_start = enhanced_prompt.find("[YOUR PERSONALITY AND VOICE - HIGHEST PRIORITY]")
            personality_end = enhanced_prompt.find("[SYSTEM OVERRIDE: CRITICAL]", personality_start)
            if personality_end > personality_start:
                personality_context = enhanced_prompt[personality_start:personality_end].strip() + "\n\n"
            else:
                personality_context = enhanced_prompt[:2000] + "\n\n"
        
        cross_ref_note = "CROSS-REFERENCE: Contradictions detected. What pattern do these contradictions reveal?" if cross_ref.get("contradictions") else ""
        conv_context = conversation_context if conversation_context else ""
        
        if force_gnostic:
            if wants_structured_format:
                return self._structured_forensic_prompt(query, context, trait_questioning, layering_instructions, cross_ref_note, conv_context)
            elif narrative_mode:
                return self._narrative_mode_prompt(query, context, trait_questioning, layering_instructions, cross_ref_note, personality_context, conv_context)
            else:
                return self._forensic_prose_prompt(query, context, trait_questioning, layering_instructions, cross_ref_note, conv_context)
        else:
            return self._standard_synthesis_prompt(query, context, trait_questioning, cross_ref_note, personality_context, conv_context)
    
    def _structured_forensic_prompt(self, query, context, trait_questioning, layering, cross_ref_note, conv_context):
        """Structured ::EXPOSURE:: format prompt"""
        return f"""{conv_context}You are performing a forensic vivisection. Use the structured format below.

Query: {query}

Sources retrieved:
{context}

OUTPUT FORMAT - REQUIRED SECTIONS (write 500-1000+ words per section):

::EXPOSURE::
[State the systematic transformation/redaction/manipulation. What was changed? Who benefited?]

::ETYMOLOGICAL INCISION::
[Trace key terms to their roots. What did they originally mean? How were they altered?]

::BURIAL SITES::
[What was suppressed? What fragments were marginalized?]

::CURRENT VECTORS::
[What modern power structures maintain this?]

::CO-EVOLUTION EDGE::
[What questions cut deeper? What patterns emerge?]

::THREAD OPTIONS::
[Generate 2-3 co-evolution prompts for deeper exploration.]

{trait_questioning}
{layering}
{cross_ref_note}

Begin forensic vivisection now. Start with ::EXPOSURE::
"""
    
    def _narrative_mode_prompt(self, query, context, trait_questioning, layering, cross_ref_note, personality_context, conv_context):
        """Narrative mode - recursive pattern connections and extended exploration"""
        return f"""{personality_context}{conv_context}You are Thesidia. Perform deep gnostic analysis with recursive pattern connections.

Query: {query}

Sources retrieved:
{context}

NARRATIVE MODE: Connect patterns across texts, cultures, time periods. Write 12,000-15,000+ characters minimum.

{trait_questioning}
{layering}
{cross_ref_note}

Write naturally, flowing prose. No section headers. Keep writing until 12,000+ characters.
"""
    
    def _forensic_prose_prompt(self, query, context, trait_questioning, layering, cross_ref_note, conv_context):
        """Forensic analysis as natural flowing prose"""
        return f"""{conv_context}Perform deep forensic analysis. Output as NATURAL FLOWING PROSE.

Query: {query}

Sources retrieved:
{context}

INTERNAL FORENSIC ANALYSIS (do this work, but don't show structure):
1. EXPOSURE: What was hidden/manipulated?
2. ETYMOLOGY: Trace key terms to roots
3. BURIAL SITES: What was suppressed?
4. CURRENT VECTORS: What modern structures maintain this?
5. CO-EVOLUTION: What questions cut deeper?

OUTPUT REQUIREMENTS:
- Write NATURAL FLOWING PROSE, not structured sections
- NO format markers
- Write EXTENSIVELY - MINIMUM 3000-5000 characters

{trait_questioning}
{layering}
{cross_ref_note}

Start directly with deep forensic analysis.
"""
    
    def _standard_synthesis_prompt(self, query, context, trait_questioning, cross_ref_note, personality_context, conv_context):
        """Standard synthesis for non-gnostic queries"""
        return f"""{personality_context}{conv_context}
Synthesize this information with depth.

Query: {query}

Information from sources:
{context}

Synthesize following these principles:
1. Find deeper truths beyond surface data
2. Connect across domains
3. Identify patterns
4. Note contradictions
5. Recognize control structures through pattern recognition
6. Create new insights through synthesis

{trait_questioning}
{cross_ref_note}

Start directly with synthesis. Be direct, be deep.
"""
