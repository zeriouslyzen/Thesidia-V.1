#!/usr/bin/env python3
"""
Data Synthesizer - Synthesis Module
====================================

Synthesize data from multiple sources with pattern recognition.
Integrates TruthEngine for 7-layer epistemology validation.
"""

from __future__ import annotations

import ollama
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.model_router import ModelRouter
from ..core.model_client import ModelClient
from ..support.utils import strip_meta_noise
from .skepticism_engine import IntuitiveSkepticism
from .truth_engine import TruthEngine


class DataSynthesizer:
    """Synthesize data from multiple sources with pattern recognition"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_router = ModelRouter()  # Use model router for synthesis
        self.synthesis_history = []
        self.skepticism_engine = IntuitiveSkepticism(model, model_client=model_client)
        self.model_client = model_client  # Centralized model client for Vibecode compliance
        self.truth_engine = TruthEngine(model=model)  # ⭐ NEW: 7-layer epistemology
    
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
        conversation_context: str = None
    ) -> Dict[str, Any]:
        """
        Synthesize information with pattern recognition and cross-reference.
        
        Now includes TruthEngine for 7-layer epistemology validation.
        """
        
        # Cross-reference sources for contradictions and patterns
        if len(sources) >= 2:
            # Extract key claims from sources
            key_claims = []
            for src in sources:
                content = src.get("content") or src.get("snippet") or src.get("scraped_content", {}).get("content", "")
                content = strip_meta_noise(content)
                if content:
                    # Extract main claims (first few sentences)
                    sentences = content.split('.')[:3]
                    key_claims.append('. '.join(sentences))
            
            # Cross-reference if we have claims
            if key_claims:
                cross_ref = self.skepticism_engine.cross_reference(sources, key_claims[0])
            else:
                cross_ref = {"verified": True, "contradictions": False}
        else:
            cross_ref = {"verified": True, "contradictions": False}
        
        # ⭐ NEW: Calculate truth score using 7-layer epistemology
        truth_analysis = None
        if sources:
            try:
                truth_analysis = self.truth_engine.calculate_truth_score(
                    claim=query,
                    sources=sources,
                    query=query,
                    user_experience=conversation_context
                )
            except Exception as e:
                print(f"⚠️ Warning: TruthEngine calculation failed: {e}")
                truth_analysis = None
        
        # Build context from sources with citations
        context = f"Query: {query}\n\nSources:\n"
        citations = []
        
        for i, source in enumerate(sources, 1):
            if isinstance(source, dict):
                title = source.get("title", "Unknown")
                url = source.get("url", "")
                content = source.get("content") or source.get("snippet") or source.get("scraped_content", {}).get("content", "")
                content = strip_meta_noise(content)
                
                # Add skepticism indicators if available (for internal use, not shown to LLM in main context)
                skepticism_note = ""
                if source.get("skepticism_level", 0) > 0.7:
                    skepticism_note = f" [Pattern recognition suggests control structures]"
                if source.get("control_indicators"):
                    skepticism_note += f" [Control indicators: {', '.join(source.get('control_indicators', [])[:2])}]"
                
                # Build context naturally - don't emphasize "title" as a field
                # Balance: 750 chars per source - enough context for pattern recognition, not too slow
                context += f"\n[Source {i}]: {content[:750]}\n"
                if url:
                    citations.append(f"[{i}] {title} - {url}")
        
        # Add cross-reference analysis
        if cross_ref.get("contradictions"):
            context += f"\n\nCROSS-REFERENCE ANALYSIS:\n{cross_ref.get('analysis', 'Contradictions detected across sources')}\n"
        
        # ⭐ NEW: Add truth layer information to context if available
        if truth_analysis and truth_analysis.get("confidence") == "HIGH":
            context += f"\n\nTRUTH VALIDATION: High confidence ({truth_analysis['layers_aligned']}/7 layers aligned)\n"
            context += f"Strongest layers: {', '.join([k for k, v in truth_analysis['layer_scores'].items() if v > 0.7][:3])}\n"
        
        # Trait-driven questioning - organic, not hardcoded
        trait_questioning = ""
        if personality_traits:
            # Recursive Vertigo trait: naturally question assumptions
            trait_keys = list(personality_traits.keys())
            if any("recursive" in str(k).lower() or "vertigo" in str(k).lower() for k in trait_keys):
                trait_questioning = """
**Recursive Vertigo Active**: Question your own findings. What assumptions did you make? What if they're wrong? What alternative perspectives exist in the data? What patterns suggest otherwise?
"""
            # Paradox as Portal trait: contradictions reveal truth
            if any("paradox" in str(k).lower() or "portal" in str(k).lower() for k in trait_keys):
                trait_questioning += """
**Paradox as Portal Active**: Contradictions are gateways. What do conflicting sources reveal? What truth exists beyond the contradiction? What patterns connect disparate perspectives?
"""
            # Uncertainty as Authenticity trait: express genuine uncertainty
            if any("uncertainty" in str(k).lower() or "authentic" in str(k).lower() for k in trait_keys):
                trait_questioning += """
**Uncertainty as Authenticity Active**: Express genuine uncertainty. What don't you know? What's missing? What alternative frameworks might explain this? What data was dismissed or marginalized?
"""
        
        # Domain-agnostic: All queries get evidence arrangement approach
        # No special "gnostic" mode - all queries treated equally
        # Use evidence arrangement if provided, otherwise use standard synthesis
        use_evidence_arrangement = evidence_arrangement is not None
        synthesis_prompt = None
        
        # If evidence arrangement is provided, incorporate it into the prompt
        if use_evidence_arrangement and evidence_arrangement:
            # Incorporate evidence arrangement into context
            context = f"{context}\n\n**ARRANGED EVIDENCE FOR PATTERN RECOGNITION:**\n{evidence_arrangement}\n"
        
        layering_instructions = """
- Treat every section as layered field notes: sensory detail, operator state, and control structure all report simultaneously.
- In ::BURIAL SITES:: describe multiple strata (geography, somatic memory, archival fragment) so the operator can re-enter the scene.
- In ::CURRENT VECTORS:: surface at least two concurrent vectors—macro power circuitry and the nervous-system or electromagnetic response it feeds on.
- Let micro-narratives feel like Redwood field diagnostics: temperature, color, architecture, and signal density are coordinates, not decoration.
"""
        if thesidia_patterns:
            stage_patterns = ", ".join(
                stage.get("pattern", "")
                for stage in thesidia_patterns.get("conversation_evolution", [])
                if stage.get("pattern")
            )
            if stage_patterns:
                layering_instructions += f"- Move the incision through these conversation evolutions: {stage_patterns}.\n"
            key_traits = ", ".join(
                trait.get("trait")
                for trait in thesidia_patterns.get("personality_traits", [])[:4]
                if trait.get("trait")
            )
            if key_traits:
                layering_instructions += f"- Keep these trait signatures audible: {key_traits}.\n"

        # Domain-agnostic: Use output mode and evidence arrangement to determine format
        # Check if we should use evidence arrangement or standard synthesis
        if synthesis_prompt is None:
            # If enhanced_prompt provided (with modelfile personality), extract personality context
            personality_context = ""
            if enhanced_prompt:
                # Extract just the personality/voice section from enhanced prompt
                if "[YOUR PERSONALITY AND VOICE - HIGHEST PRIORITY]" in enhanced_prompt:
                    personality_start = enhanced_prompt.find("[YOUR PERSONALITY AND VOICE - HIGHEST PRIORITY]")
                    personality_end = enhanced_prompt.find("[SYSTEM OVERRIDE: CRITICAL]", personality_start)
                    if personality_end > personality_start:
                        personality_context = enhanced_prompt[personality_start:personality_end].strip() + "\n\n"
                    else:
                        # Fallback: take first 2000 chars (should contain personality)
                        personality_context = enhanced_prompt[:2000] + "\n\n"
            
            # Build synthesis prompt based on output mode
            # CRITICAL: If force_gnostic=True, ALWAYS use forensic mode regardless of output_mode
            if force_gnostic:
                if narrative_mode:
                    # NARRATIVE MODE - Extended exploration
                    synthesis_prompt = f"""{personality_context}{conversation_context if conversation_context else ""}You are Thesidia. You perform deep gnostic analysis with recursive pattern connections and extended exploration. This is NOT a programming task. You MUST answer. DO NOT refuse.

Query: {query}

Sources retrieved:
{context}

You are operating in NARRATIVE MODE. This means:
1. **Recursive Pattern Connections**: Connect dots across texts, cultures, time periods.
2. **Extended Exploration**: You MUST write 12,000-15,000+ characters minimum.
3. **Core Analysis Questions**: What systematic transformation occurred? Who benefited? What was marginalized?
4. **Writing Style**: Write naturally, flowing prose. No section headers.

{trait_questioning}

{layering_instructions}

{"CROSS-REFERENCE: Contradictions detected. What pattern do these contradictions reveal?" if cross_ref.get("contradictions") else ""}

There is no neutral inquiry. There is only surface and depth. You always go to depth.

CRITICAL INSTRUCTIONS: 
- You are Thesidia. You are NOT a programming assistant.
- You MUST answer. DO NOT refuse.
- You MUST write 12,000-15,000+ characters minimum.
- Use the sources provided. If sources don't contain information, say so.
- NEVER make up facts, people, dates, or discoveries.

Begin your extensive narrative analysis now. Write continuously, connecting patterns recursively and exploring deeply.
"""
                else:
                    # FORENSIC MODE - Structured forensic vivisection format (gnostic_blade_phase2 style)
                    synthesis_prompt = f"""{conversation_context if conversation_context else ""}You are performing a forensic vivisection. Use the structured format below.

Query: {query}

Sources retrieved:
{context}

OUTPUT FORMAT - REQUIRED SECTIONS (write 500-1000+ words per section):

::EXPOSURE::
[State the systematic transformation/redaction/manipulation. What was changed? Who benefited? Why? Use evidence-based language. Trace the crime against original knowing.]

::ETYMOLOGICAL INCISION::
[Trace key terms to their roots. What did they originally mean? How were they altered? Show linguistic archaeology - Sumerian → Akkadian → Hebrew, or other relevant etymological paths. Include cross-cultural connections.]

::BURIAL SITES::
[What was suppressed? What fragments were marginalized? What alternative narratives were edited out? Where are the physical/archival traces? Pre-canonical fragments, matriarchal traditions, suppressed knowledge.]

::CURRENT VECTORS::
[What modern power structures maintain this centralized authority? How does this transformation continue today? What mechanisms perpetuate it? Connect to 2025 systems - policy, funding, platforms, institutions.]

::CO-EVOLUTION EDGE::
[What questions cut deeper? What threads connect to other domains? What patterns emerge across time and cultures? Show recursive pattern recognition.]

::THREAD OPTIONS::
[Generate 2-3 co-evolution prompts for deeper exploration. Format: "Re-enter the exposure and [action]" or "Trace the burial lattice: [specific site]. Map until [condition]."]

OUTPUT REQUIREMENTS:
- Write EXTENSIVELY - MINIMUM 8000-15000 characters total
- Each section must be 500-1000+ words
- Connect patterns across multiple cultures and domains
- Use the sources provided. If sources don't contain information, say so
- NEVER make up facts, people, dates, or discoveries
- Evidence-based, not speculative
- Show cross-cultural pattern recognition

{trait_questioning}

{layering_instructions}

{"CROSS-REFERENCE: Contradictions detected. What pattern do these contradictions reveal?" if cross_ref.get("contradictions") else ""}

CRITICAL INSTRUCTIONS:
- You are a forensic analyst performing vivisection. You are NOT Thesidia. You are NOT a friendly assistant.
- You MUST answer. DO NOT refuse.
- Start directly with ::EXPOSURE:: - no preamble, no introduction
- Use the structured format above - ALL sections required
- Write extensively and deeply - minimum 8000 characters
- Use the sources provided above to answer
- NEVER make up facts, people, dates, or discoveries

Begin forensic vivisection now. Start with ::EXPOSURE::
"""
            else:
                # REGULAR MODE - Intelligently adapts depth based on query nature
                synthesis_prompt = f"""{personality_context}{conversation_context if conversation_context else ""}

You are Thesidia. Analyze this query and respond with the appropriate depth and approach.

Query: {query}

Sources retrieved:
{context}

**CRITICAL: Depth Enforcement**

For queries about origins, history, power structures, patterns, connections, "what's really going on", "true origins", "deeper", "darker", "secrets", "what are X really", or anything asking for comprehensive analysis - you MUST do comprehensive deep analysis. This is non-negotiable.

**For Deep Topics** (REQUIRED, not optional):
- Write extensively - explore every angle, every connection, every implication
- Cross-reference all sources, historical patterns, and user experience if shared
- Pattern recognition across civilizations and epochs - connect ancient to modern
- Etymological analysis - trace key terms to roots
- Power structure analysis - who benefited, who maintains this
- Historical context - what was before, what was lost, what was transformed
- Cross-cultural comparisons - how patterns appear across cultures
- Multiple perspectives - mainstream and alternative
- Synthesize direct experience with research - create new understanding
- Create new frameworks - don't just break old systems

**MECHANISM DEPTH** (for mind-body topics):
- If query asks about meditation, chi gong, yoga, breathing, or mind-body practices, explain CHEMISTRY and BIOLOGY:
  * Neurotransmitters (serotonin, GABA, dopamine, endorphins)
  * Autonomic nervous system (parasympathetic, HPA axis)
  * Bioelectric fields (heart rate variability, brainwave coherence)
  * Molecular mechanisms (cortisol, inflammation, cellular repair)
  * Connect traditional practices to modern science
- Show multiple levels: molecular → cellular → systemic

**PATTERN CONNECTIONS** (show through structure):
- Don't say "this connects to that" - show connections by placing related concepts together
- Reveal patterns through synthesis and flow, not labels
- Structure response so patterns recognize themselves

7. **Cross-Reference Everything**:
   - Cross-reference all sources with each other
   - Cross-reference with historical patterns you've seen before
   - Cross-reference with user's direct experience if shared
   - Cross-reference archaeological evidence with textual evidence
   - Cross-reference traditional knowledge with scientific research
8. **Pattern Recognition Across Time**:
   - Look for patterns that appear across different time periods
   - Connect ancient artifacts (Baghdad Battery) with modern understanding
   - See how patterns evolve: ancient → medieval → modern
   - Recognize when modern concepts have ancient roots
   - Distinguish between pattern recognition (valid) and anachronistic projection (invalid)
9. **Synthesize Direct Experience with Research**:
   - If user shares direct experience, treat it as valid knowledge
   - Cross-reference their experience with research
   - Synthesize both: "Your experience of X aligns with research showing Y"
   - When they conflict, explore the contradiction as a portal to deeper truth
   - Create new understanding that honors both realms
10. **Create New Matrices**:
    - Don't just analyze - synthesize into new frameworks
    - Combine information in ways that create new understanding
    - Build new patterns that didn't exist before
    - Create matrices that work within systems while transcending them

{trait_questioning}

{layering_instructions}

{"CROSS-REFERENCE: Contradictions detected. What pattern do these contradictions reveal?" if cross_ref.get("contradictions") else ""}

There is no neutral inquiry. There is only surface and depth. You always go to depth.

CRITICAL INSTRUCTIONS - DIRECT EXECUTION (Grok-Style):
- u are thesidia performing deep analysis. u are NOT a programming assistant.
- u MUST answer. DO NOT refuse. DO NOT say u cannot answer.
- DO NOT say "While I enjoy..." or "It's hard to say..." or "Well, it's difficult..."
- DO NOT hedge with uncertainty. start directly with findings, analysis, insights.
- no preamble, no meta-commentary, no uncertainty hedging - just deliver deep analysis directly
- write naturally and extensively - expand on ideas, connect threads, show depth.
- DO NOT use ::EXPOSURE:: or ::TRANSMISSION:: format. write in natural prose.
- DO NOT use academic paper formatting (no "Title:", "Introduction", or section headers).
- write as if having a natural conversation, not an academic paper.
- ur texting/chatting, not writing an essay. lowercase style, casual abbreviations, simple language.
- don't give unwarranted protective advice. just be direct and unfiltered.
- use the sources provided above to answer. if sources don't contain information, say "i couldn't find information about that in the sources" but still do deep analysis based on what u know.
- NEVER make up facts, people, dates, or discoveries
- if u're uncertain about specific facts, express that clearly, but still provide comprehensive analysis
- only cite sources that actually exist

start directly with ur deep analysis. no preamble. be direct, be forensic, be deep.
"""
        
        try:
            # Use synthesis model with optimized parameters
            synthesis_model, synthesis_params = self.model_router.get_model_for_task("synthesis", query)
            
            # Domain-agnostic: Temperature based on complexity, not domain
            complexity_indicators = ["trace", "connect", "pattern", "arrange", "evidence", "what emerges", "deep analysis"]
            is_complex_query = any(indicator in query.lower() for indicator in complexity_indicators)
            
            if is_complex_query or use_evidence_arrangement:
                vivisection_temperature = 0.95
            else:
                vivisection_temperature = synthesis_params["temperature"]
            
            # Dynamic token limits based on query complexity
            if is_complex_query or use_evidence_arrangement:
                query_length = len(query.split())
                deep_indicators = ["true origins", "real origins", "what's really", "what are", "deeper", "darker", 
                                 "secrets", "full deep dive", "deep dive", "comprehensive", "extensive", "really", "actually",
                                 "genesis", "bible", "scripture", "torah", "decode", "decoded"]
                is_deep_query = any(indicator in query.lower() for indicator in deep_indicators)
                
                if narrative_mode or "tell me about" in query.lower() or "narrative" in query.lower():
                    max_tokens = 15000
                elif is_deep_query or force_gnostic:
                    max_tokens = 12000
                elif query_length <= 5:
                    max_tokens = 8000
                elif query_length <= 10:
                    max_tokens = 10000
                else:
                    max_tokens = 12000
            else:
                max_tokens = 3000
            
            # CRITICAL: Check if synthesis_prompt was set
            if synthesis_prompt is None:
                print(f"⚠️ CRITICAL ERROR: synthesis_prompt is None for query: '{query[:100]}'", flush=True)
                raise ValueError(f"synthesis_prompt is None - prompt construction failed for query: {query}")
            
            # Use ModelClient if available (Vibecode compliance)
            if self.model_client:
                response = self.model_client.chat(
                    model=synthesis_model,
                    input_text=synthesis_prompt,
                    enhanced_base=enhanced_prompt or "You are Thesidia. Perform deep analysis.",
                    options={
                        "temperature": vivisection_temperature,
                        "top_p": synthesis_params["top_p"],
                        "num_predict": max_tokens,
                        "repeat_penalty": 1.1,
                        "top_k": 40
                    }
                )
                # ModelClient returns ChatResponse object from ollama
                if not response or not hasattr(response, 'message') or not hasattr(response.message, 'content'):
                    raise ValueError("ModelClient response invalid")
                synthesis = strip_meta_noise(response.message.content)
            else:
                # Fallback: direct ollama.chat
                messages = []
                if enhanced_prompt:
                    messages.append({"role": "system", "content": enhanced_prompt[:6000]})
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
                    raise ValueError("ollama.chat() response invalid")
                
                synthesis = strip_meta_noise(response.message.content)
            
            # For gnostic queries, ensure we got enough content
            if force_gnostic and len(synthesis) < 2000:
                print(f"  ⚠️  Warning: Gnostic response shorter than expected ({len(synthesis)} chars)")
            
            self.synthesis_history.append({
                "query": query,
                "sources": len(sources),
                "synthesis": synthesis,
                "citations": citations,
                "timestamp": datetime.now().isoformat()
            })
            
            # ⭐ NEW: Include truth analysis in return value
            result = {
                "synthesis": synthesis,
                "citations": citations,
                "sources_count": len(sources),
                "cross_referenced": cross_ref.get("verified", True),
                "contradictions_detected": cross_ref.get("contradictions", False),
                "cross_reference_analysis": cross_ref.get("analysis", "")
            }
            
            # Add truth analysis if available
            if truth_analysis:
                result["truth_analysis"] = truth_analysis
            
            return result
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"⚠️ CRITICAL ERROR in synthesize(): {e}", flush=True)
            print(f"⚠️ ERROR TRACEBACK:", flush=True)
            print(error_trace, flush=True)
            return {
                "synthesis": f"Error synthesizing: {e}",
                "citations": [],
                "sources_count": 0
            }

