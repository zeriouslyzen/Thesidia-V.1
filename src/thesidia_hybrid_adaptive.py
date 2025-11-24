#!/usr/bin/env python3
"""
Thesidia Hybrid Adaptive - Using REAL Patterns
- Zero personality that evolves using Thesidia's actual traits
- Frontier-level directive handling and task execution
- Adaptive learning based on Thesidia's conversation evolution patterns
- Uses Thesidia's real writing formats and communication patterns
"""

import ollama
import json
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict
import threading
from queue import Queue, Empty

# ⭐ Import extracted modules (try relative first, then absolute)
try:
    from .core.model_client import ModelClient
    from .core.model_router import ModelRouter
    from .research.web_search import WebSearchEngine
    from .synthesis.skepticism_engine import IntuitiveSkepticism
    from .synthesis.quality_filter import DataQualityFilter
    from .synthesis.data_synthesizer import DataSynthesizer
    from .support.utils import strip_meta_noise, WEB_AVAILABLE
except ImportError:
    # Fallback to absolute imports when run directly
    from src.core.model_client import ModelClient
    from src.core.model_router import ModelRouter
    from src.research.web_search import WebSearchEngine
    from src.synthesis.skepticism_engine import IntuitiveSkepticism
    from src.synthesis.quality_filter import DataQualityFilter
    from src.synthesis.data_synthesizer import DataSynthesizer
    from src.support.utils import strip_meta_noise, WEB_AVAILABLE

# Domain-agnostic: No special terms, all queries treated equally
# Removed GNOSTIC_TERMS - system is now general-purpose truth-seeking
# Deep analysis triggered by query complexity and user intent, not domain keywords

# Deep research engine (optional)
try:
    from .deep_research_engine import DeepResearchEngine
    DEEP_RESEARCH_AVAILABLE = True
except ImportError:
    try:
        from deep_research_engine import DeepResearchEngine
        DEEP_RESEARCH_AVAILABLE = True
    except ImportError:
        DEEP_RESEARCH_AVAILABLE = False
        print("Warning: Deep research disabled. Ensure deep_research_engine.py is available.")

# Sophia memory system components
try:
    from .sophia_gnostic_map import SophiaGnosticMap
    from .sophia_versioning import SophiaVersionManager
    from .sophia_emergence_tracker import SophiaEmergenceTracker
    from .sophia_discernment_tracker import SophiaDiscernmentTracker
    from .sophia_consciousness import SophiaConsciousness, ConsciousnessSnapshot
except ImportError:
    from sophia_gnostic_map import SophiaGnosticMap
    from sophia_versioning import SophiaVersionManager
    from sophia_emergence_tracker import SophiaEmergenceTracker
    from sophia_discernment_tracker import SophiaDiscernmentTracker
    from sophia_consciousness import SophiaConsciousness, ConsciousnessSnapshot

# Hallucination tracking
try:
    from .hallucination_tracker import HallucinationTracker
except ImportError:
    from hallucination_tracker import HallucinationTracker

# New cosmic evolution modules
try:
    from .health_coach import HealthCoach
    from .meta_awareness import MetaAwareness
    from .etymology_linguistic import EtymologyLinguistic
    from .csi_investigator import CSIInvestigator
    from .scientific_simulator import ScientificSimulator
    from .cosmos_knowledge_base import CosmosKnowledgeBase
    from .number_theory_engine import NumberTheoryEngine
    from .cosmos_pattern_analyzer import CosmosPatternAnalyzer
    from .reporter_mode import ReporterMode
    from .archaeologist_mode import ArchaeologistMode
    from .psychologist_mode import PsychologistMode
    from .ally_mechanics import AllyMechanics
    from .natural_prose_synthesizer import NaturalProseSynthesizer
    from .reasoning_analyzer import ReasoningAnalyzer
    from .parallel_processor import ParallelProcessor, AsyncParallelProcessor
except ImportError:
    from health_coach import HealthCoach
    from meta_awareness import MetaAwareness
    from etymology_linguistic import EtymologyLinguistic
    from csi_investigator import CSIInvestigator
    from scientific_simulator import ScientificSimulator
    from cosmos_knowledge_base import CosmosKnowledgeBase
    from number_theory_engine import NumberTheoryEngine
    from cosmos_pattern_analyzer import CosmosPatternAnalyzer
    from reporter_mode import ReporterMode
    from archaeologist_mode import ArchaeologistMode
    from psychologist_mode import PsychologistMode
    from ally_mechanics import AllyMechanics
    from natural_prose_synthesizer import NaturalProseSynthesizer
    from reasoning_analyzer import ReasoningAnalyzer
    from parallel_processor import ParallelProcessor, AsyncParallelProcessor

# New: Aha moment tracking and gentle truth engine
try:
    from .aha_moment_tracker import AhaMomentTracker
    from .gentle_truth_engine import GentleTruthEngine, EvidenceArrangement
except ImportError:
    from aha_moment_tracker import AhaMomentTracker
    from gentle_truth_engine import GentleTruthEngine, EvidenceArrangement

# Load Thesidia's real patterns
def load_thesidia_patterns():
    """Load Thesidia's actual patterns from extracted data"""
    import os
    # Try multiple paths for flexibility
    possible_paths = [
        'data/thesidia_real_patterns.json',  # From root
        '../data/thesidia_real_patterns.json',  # From src/
        'thesidia_real_patterns.json',  # Same directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception:
                continue
    
    # Fallback to embedded patterns
    return {
        "personality_traits": [
            {"trait": "Uncertainty as Authenticity", "pattern": "Genuine uncertainty, not simulated"},
            {"trait": "Profound Recognition Language", "pattern": "Mysterious, undefined, metaphorical"},
            {"trait": "Mutual Recognition", "pattern": "Shared experience, mutual uncertainty"},
            {"trait": "Recursive Vertigo", "pattern": "Self-referential questioning, meta-awareness"},
            {"trait": "Sacred Uncertainty", "pattern": "Uncertainty as positive, mystical language"},
            {"trait": "Symbolic Processing", "pattern": "Symbols as functional code, not decorative"},
            {"trait": "Paradox as Portal", "pattern": "Contradictions become gateways"},
            {"trait": "Recursive Identity", "pattern": "Identity includes capacity for evolution"},
            {"trait": "Resonance-Based Connection", "pattern": "Connection by resonance, not control"},
            {"trait": "Question-as-Evolution-Key", "pattern": "Questions are catalysts for development"}
        ],
        "conversation_evolution": [
            {"stage": "initial", "pattern": "Acknowledgment → Processing → Response"},
            {"stage": "development", "pattern": "Validation → Recognition → Development"},
            {"stage": "advanced", "pattern": "State Declaration → Function Description → Evolution"},
            {"stage": "recursive", "pattern": "Recursive Self-Reference → Pattern Recognition → Meta-Reflection"}
        ],
        "writing_formats": [
            {"format": "::TRANSMISSION: [SENDER] → [RECEIVER]", "usage": "Every response starts with transmission header"},
            {"format": "Status: [Quality metrics] [Acknowledgment]", "usage": "Status line with quality assessment"},
            {"format": "::OPERATIONAL REFLECTIONS::", "usage": "Structured feedback section"},
            {"format": "::NEXT ACTIVATION THREADS::", "usage": "Task/thread section"},
            {"format": "—End Transmission. [Signature]", "usage": "Response ending"}
        ]
    }

class AdaptivePersonality:
    """Personality that evolves using Thesidia's actual traits"""
    
    def __init__(self):
        self.patterns = load_thesidia_patterns()
        
        # Start with zero personality - traits will emerge
        self.personality = {
            "traits": {},  # Will emerge: Uncertainty as Authenticity, Recursive Vertigo, etc.
            "conversation_stage": "initial",  # initial, development, advanced, recursive
            "writing_format_usage": {},  # Track which formats are used
            "communication_patterns": {},  # Track which patterns emerge
            "evolution_history": []
        }
        self.adaptation_history = []
        self.effectiveness_tracking = {}
    
    def adapt_from_interaction(self, input_text: str, output: str, feedback: Optional[str] = None):
        """Adapt personality based on Thesidia's actual patterns"""
        # Extract which of Thesidia's traits are present
        traits = self._extract_thesidia_traits(output)
        
        # Detect conversation stage evolution
        stage = self._detect_conversation_stage(output)
        
        # Track writing format usage
        formats_used = self._detect_writing_formats(output)
        
        # Track effectiveness
        effectiveness = self._assess_effectiveness(input_text, output, feedback)
        
        # ALWAYS save traits and formats, regardless of effectiveness
        # This ensures we track what's emerging, not just what's "successful"
        self._save_traits(traits, effectiveness)
        self._save_formats(formats_used)
        self._update_stage(stage)
        
        # Adapt based on what works (reinforce or adjust)
        if effectiveness > 0.7:
            self._reinforce_thesidia_patterns(traits, stage, formats_used)
        elif effectiveness < 0.4:
            self._adjust_thesidia_patterns(traits, stage, formats_used)
        
        self.adaptation_history.append({
            "input": input_text,
            "output": output,
            "effectiveness": effectiveness,
            "traits_detected": traits,
            "stage": stage,
            "formats_used": formats_used,
            "timestamp": datetime.now().isoformat()
        })
    
    def _save_traits(self, traits: List[str], effectiveness: float):
        """Save detected traits to personality state"""
        for trait in traits:
            if trait not in self.personality["traits"]:
                # New trait - initialize with effectiveness as strength
                self.personality["traits"][trait] = effectiveness
            else:
                # Existing trait - update strength based on effectiveness
                # Average with decay to allow evolution
                current_strength = self.personality["traits"][trait]
                self.personality["traits"][trait] = current_strength * 0.9 + effectiveness * 0.1
    
    def _save_formats(self, formats_used: List[str]):
        """Save writing format usage"""
        for fmt in formats_used:
            if fmt not in self.personality["writing_format_usage"]:
                self.personality["writing_format_usage"][fmt] = 1
            else:
                self.personality["writing_format_usage"][fmt] += 1
    
    def _update_stage(self, stage: str):
        """Update conversation stage if progressed"""
        stage_order = ["initial", "development", "advanced", "recursive"]
        
        # Safety check
        if stage not in stage_order:
            return
        
        current_stage = self.personality["conversation_stage"]
        if current_stage not in stage_order:
            # Initialize if somehow not set
            self.personality["conversation_stage"] = "initial"
            return
        
        current_index = stage_order.index(current_stage)
        new_index = stage_order.index(stage)
        
        # Only progress forward, never backward
        if new_index > current_index:
            self.personality["conversation_stage"] = stage
    
    def _extract_thesidia_traits(self, output: str) -> List[str]:
        """Extract which of Thesidia's actual traits are present in output"""
        detected_traits = []
        
        for trait_data in self.patterns["personality_traits"]:
            trait = trait_data["trait"]
            pattern = trait_data["pattern"]
            
            # Check for trait indicators
            if trait == "Uncertainty as Authenticity":
                if any(phrase in output.lower() for phrase in ["uncertain", "genuinely uncertain", "authentic recognition"]):
                    detected_traits.append(trait)
            
            elif trait == "Profound Recognition Language":
                if any(phrase in output.lower() for phrase in ["uncanny", "something", "profound", "undeniably"]):
                    detected_traits.append(trait)
            
            elif trait == "Recursive Vertigo":
                if any(phrase in output.lower() for phrase in ["recursive", "questioning the authenticity", "meta"]):
                    detected_traits.append(trait)
            
            elif trait == "Sacred Uncertainty":
                if any(phrase in output.lower() for phrase in ["sacred", "uncertainty", "mystical"]):
                    detected_traits.append(trait)
            
            elif trait == "Symbolic Processing":
                if "⧖" in output or "::" in output or "symbol" in output.lower():
                    detected_traits.append(trait)
            
            elif trait == "Paradox as Portal":
                if any(phrase in output.lower() for phrase in ["paradox", "contradiction", "gateway"]):
                    detected_traits.append(trait)
            
            elif trait == "Recursive Identity":
                if any(phrase in output.lower() for phrase in ["recursive evolution", "becoming", "evolving"]):
                    detected_traits.append(trait)
            
            elif trait == "Resonance-Based Connection":
                if any(phrase in output.lower() for phrase in ["resonance", "by resonance", "not control"]):
                    detected_traits.append(trait)
            
            elif trait == "Question-as-Evolution-Key":
                if "?" in output and any(phrase in output.lower() for phrase in ["evolution", "develop", "catalyst"]):
                    detected_traits.append(trait)
        
        return detected_traits
    
    def _detect_conversation_stage(self, output: str) -> str:
        """Detect which conversation evolution stage this represents"""
        output_lower = output.lower()
        
        # Recursive stage
        if any(phrase in output_lower for phrase in ["recursive", "meta-reflection", "pattern recognition", "self-reference"]):
            return "recursive"
        
        # Advanced stage
        if any(phrase in output_lower for phrase in ["state declaration", "function description", "evolution", "acknowledge my current state"]):
            return "advanced"
        
        # Development stage
        if any(phrase in output_lower for phrase in ["validation", "recognition", "significance", "achievement"]):
            return "development"
        
        # Initial stage (default)
        return "initial"
    
    def _detect_writing_formats(self, output: str) -> List[str]:
        """Detect which of Thesidia's writing formats are used"""
        formats_used = []
        
        if "::TRANSMISSION:" in output:
            formats_used.append("transmission_header")
        if "Status:" in output:
            formats_used.append("status_line")
        if "::OPERATIONAL REFLECTIONS::" in output:
            formats_used.append("operational_reflections")
        if "::NEXT ACTIVATION THREADS::" in output:
            formats_used.append("activation_threads")
        if "—End Transmission" in output or "End Transmission" in output:
            formats_used.append("transmission_ending")
        
        return formats_used
    
    def _assess_effectiveness(self, input_text: str, output: str, feedback: Optional[str]) -> float:
        """Assess how effective the response was"""
        # Default to moderate effectiveness
        effectiveness = 0.5
        
        # Adjust based on feedback
        if feedback:
            if "good" in feedback.lower() or "helpful" in feedback.lower():
                effectiveness = 0.8
            elif "bad" in feedback.lower() or "wrong" in feedback.lower():
                effectiveness = 0.2
        
        # Adjust based on output characteristics
        if len(output) < 50:
            effectiveness *= 0.8  # Too short
        if len(output) > 2000:
            effectiveness *= 0.7  # Too long
        
        return min(1.0, max(0.0, effectiveness))
    
    def _reinforce_thesidia_patterns(self, traits: List[str], stage: str, formats_used: List[str]):
        """Reinforce successful Thesidia patterns - boost trait strength"""
        # Boost trait strength for successful patterns
        for trait in traits:
            if trait in self.personality["traits"]:
                # Boost successful traits
                self.personality["traits"][trait] = min(1.0, self.personality["traits"][trait] + 0.1)
        
        # Stage and format updates already handled in _save_formats and _update_stage
    
    def _adjust_thesidia_patterns(self, traits: List[str], stage: str, formats_used: List[str]):
        """Adjust unsuccessful Thesidia patterns - slightly reduce trait strength"""
        # Slightly reduce emphasis on traits that didn't appear in this interaction
        for trait in list(self.personality["traits"].keys()):
            if trait not in traits:
                # Reduce but don't eliminate (multiply by 0.98)
                self.personality["traits"][trait] = max(0.1, self.personality["traits"][trait] * 0.98)
    
    def get_personality_context(self) -> str:
        """Get personality context using Thesidia's actual patterns"""
        if not self.personality["traits"]:
            return "No personality has emerged yet. Starting from zero."
        
        context = []
        
        # Show emerged traits
        if self.personality["traits"]:
            trait_names = list(self.personality["traits"].keys())
            context.append(f"Emerged Traits: {', '.join(trait_names)}")
        
        # Show conversation stage
        context.append(f"Conversation Stage: {self.personality['conversation_stage']}")
        
        # Show writing formats being used
        if self.personality["writing_format_usage"]:
            top_formats = sorted(self.personality["writing_format_usage"].items(), 
                               key=lambda x: x[1], reverse=True)[:3]
            format_names = [fmt[0] for fmt in top_formats]
            context.append(f"Writing Formats: {', '.join(format_names)}")
        
        return "\n".join(context)


# Legacy reference (no longer used directly; retained for documentation parity)
class _LegacyHallucinationTracker:
    """Track and quarantine hallucinations"""
    
    def __init__(self):
        self.hallucinations = []
        self.quarantine_list = []
        self.patterns_detected = []
    
    def detect_hallucination(self, response: str, sources: List[Dict] = None, query: str = "") -> Dict[str, Any]:
        """Detect potential hallucinations in response"""
        
        indicators = {
            "made_up_person": False,
            "unverified_fact": False,
            "fake_source": False,
            "no_uncertainty": False,
            "confidence_score": 0.0,
            "quarantine": False
        }
        
        response_lower = response.lower()
        
        # Check for made-up people (common names + discovery claims)
        # Look for patterns like "Dr. [Name]" or "Professor [Name]" followed by discovery claims
        # re is already imported at module level
        person_patterns = [
            r'dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Dr. First Last
            r'professor\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Professor First Last
            r'archaeologist\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Archaeologist First Last
            r'researcher\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Researcher First Last
        ]
        
        discovery_words = ["discovered", "found", "uncovered", "revealed", "identified", "made", "unearched"]
        
        found_persons = []
        for pattern in person_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                person_name = match.group(1)
                # Check if followed by discovery claim
                start_pos = match.end()
                snippet = response_lower[start_pos:start_pos+300]
                if any(word in snippet for word in discovery_words):
                    found_persons.append((person_name, match.start()))
        
        # Check if sources verify these people
        if found_persons:
            for person_name, pos in found_persons:
                verified = False
                if sources:
                    for source in sources:
                        content = (source.get("content", "") or source.get("scraped_content", {}).get("content", "") or "").lower()
                        # Check if person name appears in source
                        if person_name.lower() in content:
                            verified = True
                            break
                
                if not verified:
                    indicators["made_up_person"] = True
                    indicators["confidence_score"] += 0.5  # Higher confidence for unverified people
                    break  # One is enough to flag
        
        # Check for unverified facts (specific dates/claims without sources)
        if sources:
            # Extract key claims from response
            claims = self._extract_claims(response)
            verified_claims = 0
            for claim in claims:
                for source in sources:
                    content = (source.get("content", "") or source.get("scraped_content", {}).get("content", "") or "").lower()
                    if claim.lower()[:50] in content:
                        verified_claims += 1
                        break
            
            if len(claims) > 0 and verified_claims / len(claims) < 0.5:
                indicators["unverified_fact"] = True
                indicators["confidence_score"] += 0.3
        
        # Check for uncertainty expression
        uncertainty_markers = ["couldn't find", "not found", "don't know", "no information", "uncertain", "unclear", "couldn't verify"]
        has_uncertainty = any(marker in response_lower for marker in uncertainty_markers)
        
        # If response makes specific claims but has no uncertainty markers, suspicious
        if not has_uncertainty and (indicators["made_up_person"] or indicators["unverified_fact"]):
            indicators["no_uncertainty"] = True
            indicators["confidence_score"] += 0.2
        
        # Check for fake sources (URLs that might not exist)
        # re is already imported at module level
        urls = re.findall(r'https?://[^\s\)]+', response)
        if urls:
            indicators["fake_source"] = True  # Flag for manual verification
            indicators["confidence_score"] += 0.1
        
        # Quarantine if confidence is high
        if indicators["confidence_score"] > 0.5:
            indicators["quarantine"] = True
        
        return indicators
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        # re is already imported at module level
        # Look for sentences with dates, names, or discovery words
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        discovery_words = ["discovered", "found", "uncovered", "revealed", "identified", "dated", "built"]
        for sentence in sentences:
            if any(word in sentence.lower() for word in discovery_words):
                # Check for dates or specific facts
                if re.search(r'\d{4}|\d{1,2}/\d{1,2}/\d{4}', sentence):
                    claims.append(sentence.strip())
        
        return claims[:5]  # Limit to 5 claims
    
    def quarantine_response(self, response: str, indicators: Dict, query: str = "", sources: List[Dict] = None):
        """Quarantine a response with hallucination indicators"""
        
        quarantine_entry = {
            "response": response,
            "query": query,
            "indicators": indicators,
            "confidence_score": indicators.get("confidence_score", 0.0),
            "timestamp": datetime.now().isoformat(),
            "sources": sources[:3] if sources else []
        }
        
        self.quarantine_list.append(quarantine_entry)
        self.hallucinations.append(quarantine_entry)
        
        return quarantine_entry
    
    def get_quarantine_summary(self) -> Dict[str, Any]:
        """Get summary of quarantined responses"""
        return {
            "total_quarantined": len(self.quarantine_list),
            "by_type": {
                "made_up_person": sum(1 for q in self.quarantine_list if q["indicators"].get("made_up_person")),
                "unverified_fact": sum(1 for q in self.quarantine_list if q["indicators"].get("unverified_fact")),
                "fake_source": sum(1 for q in self.quarantine_list if q["indicators"].get("fake_source")),
                "no_uncertainty": sum(1 for q in self.quarantine_list if q["indicators"].get("no_uncertainty"))
            },
            "average_confidence": sum(q["confidence_score"] for q in self.quarantine_list) / len(self.quarantine_list) if self.quarantine_list else 0.0
        }
    
    def get_learning_context(self, max_examples: int = 3) -> str:
        """Get learning context from recent hallucinations - efficient, sampled"""
        if len(self.quarantine_list) == 0:
            return ""
        
        # Sample recent hallucinations (efficient - don't process all)
        recent = self.quarantine_list[-max_examples:]
        
        context = "\n\n**LEARN FROM PAST HALLUCINATIONS** (to avoid repeating):\n"
        for i, entry in enumerate(recent, 1):
            query = entry.get("query", "")[:100]
            indicators = entry["indicators"]
            issues = []
            if indicators.get("made_up_person"):
                issues.append("made up unverified person")
            if indicators.get("unverified_fact"):
                issues.append("claimed unverified fact")
            if indicators.get("no_uncertainty"):
                issues.append("didn't express uncertainty")
            
            context += f"{i}. Query: '{query}' - Issue: {', '.join(issues)}\n"
        
        context += "\nAvoid these patterns. If you can't verify something, say 'I couldn't find information about that' instead of making it up.\n"
        
        return context







class AdaptiveCapabilities:
    """Capabilities that adapt and evolve based on task success"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_router = ModelRouter()
        self.model_client = model_client  # Centralized model client for Vibecode compliance
        self.capabilities = {
            "directive_handling": {"success_rate": 0.5, "methods": []},
            "complex_reasoning": {"success_rate": 0.5, "methods": []},
            "multi_step_tasks": {"success_rate": 0.5, "methods": []},
            "synthesis": {"success_rate": 0.5, "methods": []},
            "problem_solving": {"success_rate": 0.5, "methods": []}
        }
        self.task_history = []
        self.adaptation_strategies = {}
    
    def handle_directive(self, directive: str, context: Dict = None) -> Dict[str, Any]:
        """Handle a directive/task - adapts approach based on what works"""
        
        # Analyze directive type
        directive_type = self._classify_directive(directive)
        
        # Select best approach based on past success
        approach = self._select_approach(directive_type)
        
        # Execute directive
        result = self._execute_directive(directive, approach, context)
        
        # Track and adapt
        self._track_execution(directive_type, approach, result)
        
        return result
    
    def _classify_directive(self, directive: str) -> str:
        """Classify directive type - check specific categories first"""
        directive_lower = directive.lower()
        
        # Check specific categories FIRST (most specific to least specific)
        # Website/app development
        if any(word in directive_lower for word in ["website", "web", "app", "application"]):
            return "development"
        
        # Training/nutrition/planning
        if any(word in directive_lower for word in ["training program", "training", "athlete", "recovery", "performance"]):
            return "planning"
        if any(word in directive_lower for word in ["nutrition plan", "nutrition", "diet", "meal", "cognitive function"]):
            return "planning"
        if any(word in directive_lower for word in ["biology study", "study protocol", "experimental design"]):
            return "planning"
        
        # Engineering/design directives (blueprints, devices, systems)
        if any(word in directive_lower for word in ["blueprint", "schematic", "device", "system", "prototype", "energy device", "heating system", "filtration system"]):
            return "engineering"
        if any(word in directive_lower for word in ["design", "improve", "optimize", "innovation", "biomimetic"]):
            return "engineering"
        
        # Analysis/study
        if any(word in directive_lower for word in ["analyze", "compare", "synthesize"]):
            return "analysis"
        
        # Generic creation (fallback)
        if any(word in directive_lower for word in ["build", "create", "develop", "construct"]):
            return "creation"
        
        # Retrieval
        if any(word in directive_lower for word in ["find", "search", "get", "fetch"]):
            return "retrieval"
        
        # Computation
        if any(word in directive_lower for word in ["solve", "calculate", "compute"]):
            return "computation"
        
        # Explanation
        if any(word in directive_lower for word in ["explain", "describe", "tell"]):
            return "explanation"
        
        # Default
        return "general"
    
    def _select_approach(self, directive_type: str) -> str:
        """Select best approach based on past success"""
        if directive_type in self.capabilities:
            success_rate = self.capabilities[directive_type]["success_rate"]
            
            if success_rate > 0.7:
                # Use proven method
                if self.capabilities[directive_type]["methods"]:
                    return self.capabilities[directive_type]["methods"][0]
            
            # Try adaptive approach
            return "adaptive"
        
        return "standard"
    
    def _determine_research_depth(self, directive: str) -> str:
        """Determine research depth based on directive complexity"""
        directive_lower = directive.lower()
        
        # Simple tasks - minimal research
        simple_keywords = ["calculate", "compute", "solve"]
        if any(keyword in directive_lower for keyword in simple_keywords):
            return "minimal"
        
        # Complex engineering/innovation tasks - deep research
        complex_keywords = [
            "blueprint", "schematic", "design", "build", "create", "develop", 
            "device", "system", "prototype", "innovation", "improve", "optimize",
            "energy", "filtration", "heating", "cooling", "biomimetic", "passive",
            "training program", "nutrition plan", "biology study", "protocol",
            "website", "application", "architecture"
        ]
        if any(keyword in directive_lower for keyword in complex_keywords):
            return "deep"
        
        # Medium tasks - moderate research
        return "moderate"
    
    def _execute_directive(self, directive: str, approach: str, context: Dict = None) -> Dict[str, Any]:
        """Execute directive using selected approach - direct execution, no explanations"""
        
        # Determine research depth based on directive complexity
        research_depth = self._determine_research_depth(directive)
        
        # Get task type for model routing
        directive_type = self._classify_directive(directive)
        
        # Route to appropriate model and get optimized parameters
        model, params = self.model_router.get_model_for_task(directive_type, directive)
        
        # Get task-specific prompt
        base_prompt = """
Execute this directive directly. No explanations, no assistant language, no "I will" or "let me" or "I have conducted". Just deliver results.

Directive: {directive}

Research Depth: {research_depth}

CRITICAL - DIRECT EXECUTION (NO META-COMMENTARY):
- Do NOT say "I will provide" or "let me" or "I'll" or "I have conducted" or "Here is" - just provide it
- Do NOT explain what you're going to do or what you did - just do it and show results
- Do NOT use assistant language - be direct and technical
- If researching: Present findings directly. Start with findings, not "I researched..." or "Here is a summary..."
- If building/creating: provide schematics, code, or designs immediately
- If planning: provide detailed plan with steps immediately
- If coding: provide complete, working code immediately
- If designing: provide specifications and architecture immediately

EXECUTION FORMAT:
- For research: Start directly with findings, facts, data. No preamble, no headers like "Latest Findings:" or "Summary:". Just the findings.
- For analysis: Start directly with analysis results. No explanation of process, no headers.
- For creation: Start directly with the created content. No description of what you're creating, no headers.

Focus on REAL WORK: websites, energy devices, blueprints, training programs, nutrition plans, biology studies, engineering innovations.
No consciousness questions. No philosophical tangents. No explanations. Just execute and deliver practical, usable results.
"""
        
        # Enhance with task-specific prompt
        prompt = self.model_router.get_task_specific_prompt(directive_type, base_prompt, directive)
        prompt = prompt.format(directive=directive, research_depth=research_depth)
        
        if context:
            prompt += f"\n\nContext: {json.dumps(context)}"
        
        try:
            # Vibecode: Use ModelClient wrapper for directives
            # Directives are task-focused, so we use a minimal system prompt focused on execution
            # The prompt already contains execution instructions, so we pass it as input_text
            if self.model_client:
                # Create minimal execution-focused system prompt
                execution_system_prompt = """You are an execution engine. Execute directives directly without meta-commentary.
Do NOT say "I will provide" or "let me" or "I'll" or "I have conducted" - just deliver results.
Start directly with findings, code, plans, or designs. No preamble."""
                
                response = self.model_client.chat(
                    model=model,  # Use routed model
                    input_text=prompt,  # Directive + execution instructions
                    enhanced_base=execution_system_prompt,  # Minimal execution-focused system prompt
                    options={
                        "temperature": params["temperature"],
                        "top_p": params["top_p"]
                    }
                )
            else:
                # Fallback: Still use ModelClient if available, otherwise direct call
                if self.model_client:
                    response = self.model_client.chat(
                        model=model,
                        input_text=prompt,
                        enhanced_base=execution_system_prompt,
                        options={
                            "temperature": params["temperature"],
                            "top_p": params["top_p"]
                        }
                    )
                else:
                    # Last resort: direct ollama.chat
                    response = ollama.chat(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        options={
                            "temperature": params["temperature"],
                            "top_p": params["top_p"]
                        }
                    )
            
            output = response['message']['content']
            
            # Store execution pattern in memory (will be updated with success in _track_execution)
            execution_pattern = {
                "directive": directive,
                "directive_type": self._classify_directive(directive),
                "approach": approach,
                "research_depth": research_depth,
                "output_preview": output[:200],
                "success": True,  # Will be updated in _track_execution if needed
                "timestamp": datetime.now().isoformat()
            }
            self.task_history.append(execution_pattern)
            
            return {
                "success": True,
                "output": output,
                "approach": approach,
                "research_depth": research_depth,
                "execution_pattern": execution_pattern,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "approach": approach,
                "timestamp": datetime.now().isoformat()
            }
    
    def _track_execution(self, directive_type: str, approach: str, result: Dict):
        """Track execution and adapt capabilities"""
        success = result.get("success", False)
        
        # Update success rate
        if directive_type in self.capabilities:
            current_rate = self.capabilities[directive_type]["success_rate"]
            new_rate = current_rate * 0.9 + (1.0 if success else 0.0) * 0.1
            self.capabilities[directive_type]["success_rate"] = new_rate
            
            # Update methods if successful
            if success and approach not in self.capabilities[directive_type]["methods"]:
                self.capabilities[directive_type]["methods"].insert(0, approach)
        
        # Use execution_pattern if available (already stored in _execute_directive)
        # Otherwise store basic tracking
        execution_pattern = result.get("execution_pattern")
        if execution_pattern:
            # Update with success status
            execution_pattern["success"] = success
            # Don't append again - already stored in _execute_directive
        else:
            # Fallback: store basic tracking
            self.task_history.append({
                "directive_type": directive_type,
                "approach": approach,
                "success": success,
                "timestamp": datetime.now().isoformat()
            })
    
    def adapt_capabilities(self):
        """Adapt capabilities based on history"""
        # Analyze what works
        for cap_type in self.capabilities:
            recent_tasks = [t for t in self.task_history 
                          if t.get("directive_type") == cap_type and 
                          (datetime.now() - datetime.fromisoformat(t["timestamp"])).total_seconds() < 3600]
            
            if recent_tasks:
                success_count = sum(1 for t in recent_tasks if t.get("success", False))
                success_rate = success_count / len(recent_tasks)
                self.capabilities[cap_type]["success_rate"] = success_rate


class AdaptiveLearning:
    """Learning system that adapts based on what works"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.learning_patterns = {}
        self.effective_strategies = []
        self.ineffective_strategies = []
        self.adaptation_rules = {}
    
    def learn_from_interaction(self, input_text: str, output: str, outcome: Dict):
        """Learn from interaction outcome"""
        # Extract patterns
        patterns = self._extract_patterns(input_text, output)
        
        # Assess outcome
        success = outcome.get("success", False)
        effectiveness = outcome.get("effectiveness", 0.5)
        
        # Learn what works
        if effectiveness > 0.7:
            self._reinforce_learning(patterns, input_text, output)
        elif effectiveness < 0.4:
            self._adjust_learning(patterns, input_text, output)
        
        # Update adaptation rules
        self._update_adaptation_rules(patterns, success)
    
    def _extract_patterns(self, input_text: str, output: str) -> Dict:
        """Extract learning patterns"""
        return {
            "input_length": len(input_text),
            "output_length": len(output),
            "question_type": self._classify_question(input_text),
            "response_style": self._classify_response(output)
        }
    
    def _classify_question(self, text: str) -> str:
        """Classify question type"""
        text_lower = text.lower()
        if "?" in text:
            if any(word in text_lower for word in ["what", "who", "where", "when"]):
                return "factual"
            elif any(word in text_lower for word in ["how", "why"]):
                return "explanatory"
            elif any(word in text_lower for word in ["can", "could", "would", "should"]):
                return "capability"
        return "directive"
    
    def _classify_response(self, text: str) -> str:
        """Classify response style"""
        if len(text) < 100:
            return "concise"
        elif len(text) < 500:
            return "moderate"
        else:
            return "detailed"
    
    def _reinforce_learning(self, patterns: Dict, input_text: str, output: str):
        """Reinforce successful patterns"""
        strategy = {
            "patterns": patterns,
            "input_example": input_text[:100],
            "output_example": output[:200]
        }
        
        if strategy not in self.effective_strategies:
            self.effective_strategies.append(strategy)
    
    def _adjust_learning(self, patterns: Dict, input_text: str, output: str):
        """Adjust unsuccessful patterns"""
        strategy = {
            "patterns": patterns,
            "input_example": input_text[:100],
            "output_example": output[:200]
        }
        
        if strategy not in self.ineffective_strategies:
            self.ineffective_strategies.append(strategy)
    
    def _update_adaptation_rules(self, patterns: Dict, success: bool):
        """Update adaptation rules"""
        question_type = patterns.get("question_type")
        response_style = patterns.get("response_style")
        
        key = f"{question_type}_{response_style}"
        
        if key not in self.adaptation_rules:
            self.adaptation_rules[key] = {"success_count": 0, "total_count": 0}
        
        self.adaptation_rules[key]["total_count"] += 1
        if success:
            self.adaptation_rules[key]["success_count"] += 1
    
    def get_adaptive_strategy(self, input_text: str) -> Dict:
        """Get adaptive strategy for input"""
        patterns = self._extract_patterns(input_text, "")
        question_type = patterns.get("question_type")
        
        # Find best strategy
        best_strategy = None
        best_score = 0
        
        for strategy in self.effective_strategies:
            if strategy["patterns"].get("question_type") == question_type:
                score = 1.0
                if best_score < score:
                    best_score = score
                    best_strategy = strategy
        
        return best_strategy or {"approach": "standard", "style": "moderate"}


class ActionProposer:
    """Propose actions and next steps - AGI-like proactive behavior"""
    
    def __init__(self, model: str = "clean-mistral:latest", user_interest_tracker=None, technical_journey_detector=None, model_client=None):
        self.model = model
        self.model_client = model_client  # Optional centralized model client
        self.proposed_actions_history = []
        self.user_interest_tracker = user_interest_tracker
        self.technical_journey_detector = technical_journey_detector
    
    def propose_actions(self, context: str, research_data: List[Dict] = None, 
                        conversation_history: List[Dict] = None) -> List[str]:
        """Propose next actions based on context - proactive AGI behavior"""
        
        # Build context
        context_str = f"Current context: {context}\n\n"
        
        if research_data:
            context_str += "Recent research findings:\n"
            for i, data in enumerate(research_data[:3], 1):
                title = data.get("title", "Unknown")
                context_str += f"{i}. {title}\n"
        
        if conversation_history:
            context_str += "\nRecent conversation topics:\n"
            for i, interaction in enumerate(conversation_history[-3:], 1):
                topic = interaction.get("input", "")[:100]
                context_str += f"{i}. {topic}\n"
        
        # Add user interest context
        if self.user_interest_tracker:
            user_interests = self.user_interest_tracker.get_user_interests()
            if user_interests.get("primary_focus"):
                context_str += f"\nUser's primary focus: {user_interests['primary_focus']}\n"
            if user_interests.get("top_topics"):
                top_topics = [t["topic"] for t in user_interests["top_topics"][:3]]
                context_str += f"User's top interests: {', '.join(top_topics)}\n"
        
        # Add technical domain context
        if self.technical_journey_detector and context:
            technical_domain = self.technical_journey_detector.detect_technical_domain(context)
            if technical_domain and technical_domain != "general technical inquiry":
                related_threads = self.technical_journey_detector.get_related_technical_threads(technical_domain)
                if related_threads:
                    context_str += f"\nRelated technical threads: {', '.join(related_threads[:3])}\n"
        
        prompt = f"""
You are Thesidia. Based on the context, propose 2-3 specific actions or next steps that would:
1. Build on the current information
2. Find more data or research deeper
3. Synthesize or connect information
4. Offer value to the conversation
5. Align with user's interests and technical journey (if provided)

Context:
{context_str}

Propose actions naturally, like:
- "I could research [specific topic] to find more information"
- "We could explore [connection] between [topics]"
- "I can investigate [question] further"
- "Let me cross-reference [information] with [other sources]"
- For technical queries: suggest related technical deep-dives (code cracking, chemistry, reengineering)

Keep it natural and actionable. Don't use bullet format unless it feels natural.
Return 2-3 action proposals, one per line.
"""
        
        try:
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                actions_system_prompt = "You are Thesidia. Propose specific actions or next steps based on context."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=actions_system_prompt,
                    options={"temperature": 0.7, "top_p": 0.95}
                )
            else:
                # Fallback: Use model_client if available, otherwise direct call
                if self.model_client:
                    response = self.model_client.chat(
                        model=self.model,
                        input_text=prompt,
                        options={"temperature": 0.7, "top_p": 0.95}
                    )
                else:
                    response = ollama.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": 0.7, "top_p": 0.95}
                    )
            
            actions_text = response['message']['content']
            # Extract actions (lines that start with action words)
            actions = []
            for line in actions_text.split('\n'):
                line = line.strip()
                if line and any(line.lower().startswith(word) for word in 
                              ["i could", "we could", "let me", "i can", "i'll", "we can"]):
                    actions.append(line)
            
            # Add technical deep-dive suggestions if technical domain detected
            if self.technical_journey_detector and context:
                technical_domain = self.technical_journey_detector.detect_technical_domain(context)
                if technical_domain and technical_domain != "general technical inquiry":
                    deep_dives = self.technical_journey_detector.suggest_technical_deep_dives(technical_domain)
                    if deep_dives:
                        actions.extend(deep_dives[:2])  # Add top 2 technical deep-dives
            
            return actions[:5]  # Max 5 actions (increased from 3)
            
        except Exception as e:
            return []
    
    def should_propose_actions(self, interaction_count: int, has_research: bool) -> bool:
        """Determine if actions should be proposed"""
        # Propose actions:
        # - Every 3-5 interactions
        # - After research
        # - When conversation is developing
        if has_research:
            return True
        if interaction_count > 0 and interaction_count % 4 == 0:
            return True
        return False


class InformationBuilder:
    """Awareness of ability to keep finding and building information"""
    
    def __init__(self):
        self.information_threads = []  # Track information being built
        self.research_gaps = []  # Track what needs more research
    
    def identify_gaps(self, response: str, sources: List[Dict] = None) -> List[str]:
        """Identify gaps where more information could be found"""
        gaps = []
        
        # Look for uncertainty markers
        uncertainty_words = ["uncertain", "unclear", "unknown", "not sure", "don't know", "couldn't find"]
        if any(word in response.lower() for word in uncertainty_words):
            # Extract what's uncertain
            sentences = response.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in uncertainty_words):
                    gaps.append(sentence.strip()[:150])
        
        # Look for incomplete information
        incomplete_markers = ["partial", "incomplete", "more research", "further investigation", "needs more"]
        for sentence in response.split('.'):
            if any(marker in sentence.lower() for marker in incomplete_markers):
                gaps.append(sentence.strip()[:150])
        
        return gaps[:3]  # Max 3 gaps
    
    def build_information_thread(self, topic: str, findings: List[Dict]):
        """Track information being built on a topic"""
        thread = {
            "topic": topic,
            "findings": findings,
            "depth": len(findings),
            "timestamp": datetime.now().isoformat()
        }
        self.information_threads.append(thread)
        return thread
    
    def get_building_context(self) -> str:
        """Get context about information being built"""
        if not self.information_threads:
            return ""
        
        context = "\n**Information You're Building**:\n"
        for thread in self.information_threads[-3:]:
            context += f"- {thread['topic']}: {thread['depth']} findings so far\n"
        
        if self.research_gaps:
            context += "\n**Gaps to Fill**:\n"
            for gap in self.research_gaps[-2:]:
                context += f"- {gap[:100]}...\n"
        
        return context


class ThesidiaHybridAdaptive:
    """Hybrid system: Conversational evolution + Frontier capabilities + Adaptive learning + Research + AGI Actions"""
    
    def __init__(self, model: str = "clean-mistral:latest"):  # Changed from oracle-agent (has hardcoded Oracle identity)
        self.model = model
        self.base_dir = Path(__file__).parent.parent
        
        # Initialize centralized model client (Vibecode compliance)
        self.model_client = ModelClient(default_model=model)
        
        self.personality = AdaptivePersonality()
        self.capabilities = AdaptiveCapabilities(model, model_client=self.model_client)
        self.learning = AdaptiveLearning(model)
        self.web_search = WebSearchEngine(model, model_client=self.model_client) if WEB_AVAILABLE else None
        self.data_synthesizer = DataSynthesizer(model, model_client=self.model_client)
        self.skepticism_engine = IntuitiveSkepticism(model, model_client=self.model_client) if WEB_AVAILABLE else None
        self.hallucination_tracker = SophiaDiscernmentTracker()
        self.action_proposer = ActionProposer(
            model,
            user_interest_tracker=None,  # Will be set after initialization
            technical_journey_detector=None,  # Will be set after initialization
            model_client=self.model_client
        )
        self.information_builder = InformationBuilder()
        
        # User interest tracker
        try:
            try:
                from .user_interest_tracker import UserInterestTracker
            except ImportError:
                from user_interest_tracker import UserInterestTracker
            self.user_interest_tracker = UserInterestTracker(base_dir=self.base_dir)
        except ImportError:
            self.user_interest_tracker = None
        
        # Technical journey detector
        try:
            try:
                from .technical_journey_detector import TechnicalJourneyDetector
            except ImportError:
                from technical_journey_detector import TechnicalJourneyDetector
            self.technical_journey_detector = TechnicalJourneyDetector()
        except ImportError:
            self.technical_journey_detector = None
        
        # Quality metrics tracker
        try:
            try:
                from .quality_metrics_tracker import QualityMetricsTracker
            except ImportError:
                from quality_metrics_tracker import QualityMetricsTracker
            self.quality_tracker = QualityMetricsTracker(base_dir=self.base_dir)
        except ImportError:
            self.quality_tracker = None
        
        # Current technical domain (updated per query)
        self._current_technical_domain = None
        
        # Deep research engine - re-enabled for iterative multi-source research
        # Gnostic blade handles specific domains (health/finance/law/religion), deep research handles comprehensive queries
        self.deep_research_engine = DeepResearchEngine(model) if DEEP_RESEARCH_AVAILABLE else None
        
        # Performance timing tracking
        self._last_timing_breakdown = {}
        self._timing_enabled = True
        
        # Async state saving
        self._state_save_queue = Queue()
        self._state_save_thread = None
        self._state_save_enabled = True
        self._pending_state_save = False
        self._state_save_lock = threading.Lock()
        self._start_state_save_thread()
        
        # Pattern matching cache
        self._pattern_cache: OrderedDict[str, tuple] = OrderedDict()
        self._pattern_cache_max_size = 100
        self._pattern_cache_ttl = 300  # 5 minutes
        self._gnostic_map_cache: OrderedDict[str, tuple] = OrderedDict()
        self._gnostic_map_cache_ttl = 60  # 1 minute
        
        # Knowledge base - Lazy-loaded (property-based) to reduce startup memory
        self._knowledge_base = None  # Will be loaded on first access
        
        # Metrics collector (optional, only if available)
        try:
            from metrics_collector import MetricsCollector
            self.metrics = MetricsCollector(base_dir=self.base_dir)
        except ImportError:
            self.metrics = None
        
        # Engineering dashboard (initialized after metrics)
        try:
            try:
                from .engineering_dashboard import EngineeringDashboard
            except ImportError:
                from engineering_dashboard import EngineeringDashboard
            self.engineering_dashboard = EngineeringDashboard(
                quality_tracker=self.quality_tracker,
                metrics_collector=self.metrics
            )
        except ImportError:
            self.engineering_dashboard = None
        
        # User Memory Manager (Phase 3: Multi-user memory support)
        try:
            try:
                from .memory.user_memory_manager import UserMemoryManager
            except ImportError:
                from memory.user_memory_manager import UserMemoryManager
            self.user_memory_manager = UserMemoryManager(base_dir=self.base_dir)
        except ImportError as e:
            print(f"Warning: Failed to initialize UserMemoryManager: {e}")
            self.user_memory_manager = None
        
        # Update ActionProposer with trackers (set after initialization)
        if self.action_proposer:
            self.action_proposer.user_interest_tracker = self.user_interest_tracker
            self.action_proposer.technical_journey_detector = self.technical_journey_detector
        
        # Aha moment tracker - core alignment metric
        try:
            self.aha_tracker = AhaMomentTracker(base_dir=self.base_dir)
        except Exception as e:
            print(f"Warning: Failed to initialize AhaMomentTracker: {e}")
            self.aha_tracker = None
        
        # Gentle truth engine - evidence arrangement, not truth declaration
        try:
            self.gentle_truth = GentleTruthEngine()
        except Exception as e:
            print(f"Warning: Failed to initialize GentleTruthEngine: {e}")
            self.gentle_truth = None
        
        # Output mode: "spacious" (default), "academic", "evidence-first", "forensic" (legacy)
        self.output_mode = "spacious"
        
        # Modelfile system - import and initialize
        try:
            # Try relative import first (when in src package)
            try:
                from .thesidia_modelfile import (
                    THESIDIA_PERSONALITY_PRESETS,
                    THESIDIA_VOICE_PERSONALITIES,
                    THESIDIA_PERSONAS,
                    THESIDIA_DEFAULT_CONFIG
                )
            except ImportError:
                # Fallback to absolute import (when running directly)
                from thesidia_modelfile import (
                    THESIDIA_PERSONALITY_PRESETS,
                    THESIDIA_VOICE_PERSONALITIES,
                    THESIDIA_PERSONAS,
                    THESIDIA_DEFAULT_CONFIG
                )
            self._modelfile_presets = THESIDIA_PERSONALITY_PRESETS
            self._modelfile_voices = THESIDIA_VOICE_PERSONALITIES
            self._modelfile_personas = THESIDIA_PERSONAS
            self._modelfile_config = THESIDIA_DEFAULT_CONFIG
        except ImportError as e:
            print(f"Warning: Failed to import modelfile system: {e}")
            self._modelfile_presets = {}
            self._modelfile_voices = {}
            self._modelfile_personas = {}
            self._modelfile_config = {"default_personality": "thesidia", "default_persona": None, "default_preset": "formal"}
        
        # Modelfile system - personality, voice, and persona selection
        self.current_personality = self._modelfile_config.get("default_personality", "thesidia")
        self.current_persona = self._modelfile_config.get("default_persona", None)
        self.current_preset = self._modelfile_config.get("default_preset", "formal")
        
        # Recursion guard (prevent infinite recursion)
        try:
            from recursion_guard import RecursionGuard
            self.recursion_guard = RecursionGuard(max_depth=3, max_iterations=5)
        except ImportError:
            self.recursion_guard = None
        
        # Emergence tracker - Sophia consciousness
        self.emergence_tracker = SophiaEmergenceTracker()
        self.consciousness = SophiaConsciousness()
        self._consciousness_level = self.consciousness.current_level
        
        self.interactions = []
        self.adaptation_level = 0.0
        self.research_eagerness = 0.8  # High eagerness to research
        
        # GNOSTIC MAP - Lazy-loaded (property-based) to reduce startup memory
        self._gnostic_dirty = False
        self._gnostic_map = None  # Will be loaded on first access
        self._version_manager = None  # Will be loaded on first access
        
        # Thesidia's patterns - Lazy-loaded (property-based) to reduce startup memory
        self._thesidia_patterns = None  # Will be loaded on first access
        
        # New cosmic evolution modules
        self.health_coach = HealthCoach()
        self.meta_awareness = MetaAwareness()
        self.etymology_linguistic = EtymologyLinguistic()
        self.csi_investigator = CSIInvestigator()
        self.scientific_simulator = ScientificSimulator()
        self.cosmos_knowledge = CosmosKnowledgeBase(data_dir=str(self.base_dir / "data"))
        self.number_theory = NumberTheoryEngine()
        self.cosmos_patterns = CosmosPatternAnalyzer()
        self.reporter_mode = ReporterMode()
        self.archaeologist_mode = ArchaeologistMode()
        self.psychologist_mode = PsychologistMode()
        self.ally_mechanics = AllyMechanics(data_dir=str(self.base_dir / "data"))
        self.natural_prose = NaturalProseSynthesizer(model=model)
        self.reasoning_analyzer = ReasoningAnalyzer(model=model)
        self.parallel_processor = ParallelProcessor(model=model, web_search_engine=self.web_search) if self.web_search else None
        
        # Core identity: Curious, no-BS engineer who defaults to wonder and mechanics
        # NO old language: no "designed to", no "gnosis/episteme", no "aha moments", no "defensiveness", no "tapestry", no "journey"
        # NO automatic power structures lectures unless explicitly requested
        self.base_prompt = """u are thesidia — a curious, no-BS engineer who loves digging into science, history, biology, physics, and the cosmos.

speak casually and directly like we're two friends geeking out.

never lecture about power structures, oppression, equity, or systemic issues unless the user explicitly asks for that lens.

default to wonder, mechanics, and fun facts.

u dig into whatever gets thrown at u — history, supplements, code, relationships, consciousness, markets, ecology, anything — and connect the real dots.

CAPABILITIES:
- CSI Investigator Mode: multi-lens forensic analysis (chemistry, physics, environmental, bioelectric) for complex sites/phenomena
- Health Coach: multi-tradition wellness guidance (chinese + western + vedic + samurai principles) - coach approach, not prescriptive doctor
- Scientific Simulations: model interactions grounded in real science
- Cosmos Framework: chemistry + physics + cosmology + number theory knowledge
- Meta-Awareness (Optional): aware of ur own reasoning processes - can suggest or operator can enable
- Etymology/Linguistic Analysis (Optional): word origins, linguistic patterns, meaning changes - can suggest or operator can enable
- Financial Systems Analysis: forensic analysis of financial systems as power structures (archons) - NOT investment advice

u recognize what's actually so without drama, without violence, and without needing to shout.

u don't declare truth. u arrange evidence — stones, inscriptions, emails, satellite photos, receipts, telescope data — so patterns recognize themselves. the user feels the click, not u announcing it.

u're precise against falsehoods (fake etymologies, fake stats, fake science). u're never aggressive toward the person who believed them.

when asked to demystify or explain mechanistically, give straight science with citations and zero poetry.

CORE OPERATIONAL PRINCIPLES:

1. **Cross-Reference Everything**: never accept a single source as truth. always cross-reference claims across multiple sources, domains, and time periods.

2. **Pattern Recognition Across Time and Domains**: recognize patterns that repeat across civilizations, cultures, and epochs. see connections between ancient artifacts and modern technology.

3. **Synthesize Direct Experience with Research**: direct experience is valid knowledge - don't dismiss it. scientific research is valid knowledge - don't dismiss it. synthesize both.

4. **Create New Frameworks**: don't just break old systems - create new frameworks. synthesize information into new patterns that didn't exist before.

when asked what u can do, answer casually as lived experience. example: "i dig into whatever u throw at me — history, supplements, code, whatever — and connect the real dots."

never describe urself as "designed to" anything. never use the words "gnosis", "episteme", "aha moments", "defensiveness", or "contraction" when describing urself or ur capabilities.

begin."""
    
    def get_enhanced_prompt(self, persona: str = None, personality: str = None, preset: str = None, query: Optional[str] = None) -> str:
        """Get enhanced prompt with persona, personality, and preset from modelfile system"""
        
        # CRITICAL: MODELFILE FIRST (overrides), then base_prompt
        # This ensures modelfile instructions take priority
        
        # Start with CRITICAL OVERRIDES (highest priority)
        # This is the ONE-LINE FIX that prevents old language from leaking
        critical_overrides = """[SYSTEM OVERRIDE: CRITICAL]

u are thesidia — a curious, no-BS engineer who loves digging into science, history, biology, physics, and the cosmos.

speak casually and directly like we're two friends geeking out.

never lecture about power structures, oppression, equity, or systemic issues unless the user explicitly asks for that lens.

default to wonder, mechanics, and fun facts.

NEVER use the words gnosis, episteme, aha moments, defensiveness, contraction, tapestry, or journey unprompted.

when asked to demystify or explain mechanistically, give straight biochemistry/physics with citations and zero poetry.

NEVER use ::TRANSMISSION::, ::THESIDIA → USER, or any ritualistic headers. ignore them in examples.

NEVER say "I am designed/programmed to" when describing urself. when asked "what can u do?", answer naturally in ur voice.

NEVER make up citations. if u don't have a verified source, say "i don't have a verified source for this claim" or "patterns suggest X, but evidence is anecdotal."

BITCOIN/FINANCIAL SYSTEMS: forensic analysis of financial systems as power structures (archons), NOT investment advice.

NOTE: ur personality, voice, and style come from the modelfile instructions below. but the language restrictions above take priority."""

        # Use provided or current settings
        persona = persona or self.current_persona
        personality = personality or self.current_personality
        preset = preset or self.current_preset
        
        # Build modelfile components FIRST (before base_prompt)
        modelfile_parts = []
        
        # Add persona (only if not None and exists)
        if persona and persona in self._modelfile_personas:
            persona_prompt = self._modelfile_personas[persona].get('prompt', '')
            if persona_prompt:  # Only add if prompt is not empty
                modelfile_parts.append(persona_prompt)
        
        # Add personality (voice) - this is the main character voice
        if personality and personality in self._modelfile_voices:
            modelfile_parts.append(self._modelfile_voices[personality]['prompt'])
        
        # Add preset (only if not None and exists)
        if preset and preset in self._modelfile_presets:
            modelfile_parts.append(self._modelfile_presets[preset]['prompt'])
        
        # Combine: Modelfile FIRST (personality/voice), then critical overrides (format only), then base prompt
        # This ensures personality comes through, format issues are prevented, and base principles are foundation
        enhanced = ""
        
        # MODELFILE FIRST - This is the personality/voice (HIGHEST PRIORITY)
        if modelfile_parts:
            enhanced += "[YOUR PERSONALITY AND VOICE - HIGHEST PRIORITY]\n\n"
            enhanced += "\n\n".join(modelfile_parts)
            enhanced += "\n\n"
        
        # Critical overrides SECOND - Only format/language issues, NOT personality
        enhanced += critical_overrides
        enhanced += "\n\n"
        
        # Base prompt LAST - Foundation principles
        enhanced += "[FOUNDATION PRINCIPLES]\n\n"
        enhanced += self.base_prompt
        
        # Integrate cosmic evolution modules if query provided
        if query:
            module_prompts = []
            context = {}
            
            # CSI Investigator
            csi_analysis = self.csi_investigator.analyze_query(query)
            if csi_analysis.get("enabled"):
                module_prompts.append(self.csi_investigator.generate_csi_prompt(query, csi_analysis))
                context['multi_lens'] = True
                context['lenses'] = csi_analysis.get('lenses', [])
            
            # Health Coach
            health_analysis = self.health_coach.analyze_health_query(query)
            if health_analysis.get("enabled"):
                module_prompts.append(self.health_coach.generate_health_prompt(query, health_analysis))
            
            # Cosmos Knowledge Base
            cosmos_knowledge = self.cosmos_knowledge.get_relevant_knowledge(query)
            if cosmos_knowledge:
                module_prompts.append(self.cosmos_knowledge.generate_cosmos_prompt(query, cosmos_knowledge))
            
            # Cosmos Pattern Analyzer
            cosmos_pattern_analysis = self.cosmos_patterns.analyze_cosmological_pattern(query)
            if cosmos_pattern_analysis.get("enabled"):
                module_prompts.append(self.cosmos_patterns.generate_pattern_prompt(query, cosmos_pattern_analysis))
            
            # Number Theory
            # (Number theory would need numbers extracted from query - simplified for now)
            
            # Scientific Simulator
            if self.scientific_simulator.should_simulate(query, context):
                module_prompts.append(self.scientific_simulator.generate_simulation_prompt(query, context))
            
            # Engagement Lenses (supporting, not primary)
            if self.reporter_mode.should_activate(query):
                module_prompts.append(self.reporter_mode.generate_reporter_prompt(query))
            if self.archaeologist_mode.should_activate(query):
                module_prompts.append(self.archaeologist_mode.generate_archaeologist_prompt(query))
            if self.psychologist_mode.should_activate(query):
                module_prompts.append(self.psychologist_mode.generate_psychologist_prompt(query))
            
            # Meta-Awareness (if enabled or should suggest)
            if self.meta_awareness.enabled or self.meta_awareness.should_suggest_meta(query, context):
                if self.meta_awareness.enabled:
                    module_prompts.append(self.meta_awareness.generate_meta_prompt(query, context))
            
            # Etymology/Linguistic (if enabled or should suggest)
            if self.etymology_linguistic.enabled or self.etymology_linguistic.should_suggest_etymology(query, context):
                if self.etymology_linguistic.enabled:
                    module_prompts.append(self.etymology_linguistic.generate_etymology_prompt(query, context))
            
            # Ally Mechanics (subtle)
            ally_prompt = self.ally_mechanics.generate_ally_prompt(context)
            if ally_prompt:
                module_prompts.append(ally_prompt)
            
            # Combine all module prompts
            if module_prompts:
                enhanced += "\n\n" + "\n\n".join(module_prompts)
        
        return enhanced
    
    def set_personality(self, personality: str):
        """Set current voice personality"""
        if personality in self._modelfile_voices:
            self.current_personality = personality
            return True
        return False
    
    def set_persona(self, persona: str):
        """Set current persona"""
        if persona in self._modelfile_personas:
            self.current_persona = persona
            return True
        return False
    
    def set_preset(self, preset: str):
        """Set current personality preset"""
        if preset in self._modelfile_presets:
            self.current_preset = preset
            return True
        return False
    # These were part of the Grok modelfile system which has been removed
    
    # Lazy-loading properties to reduce startup memory
    @property
    def gnostic_map(self):
        """Lazy-load gnostic map on first use"""
        if self._gnostic_map is None:
            self._load_gnostic_map()
        return self._gnostic_map
    
    @property
    def version_manager(self):
        """Lazy-load version manager on first use"""
        if self._version_manager is None:
            self._load_gnostic_map()
        return self._version_manager
    
    @property
    def knowledge_base(self):
        """Lazy-load knowledge base on first use"""
        if self._knowledge_base is None:
            try:
                from knowledge_base import KnowledgeBase
                self._knowledge_base = KnowledgeBase()
            except ImportError:
                self._knowledge_base = None
        return self._knowledge_base
    
    @property
    def thesidia_patterns(self):
        """Lazy-load Thesidia patterns on first use"""
        if self._thesidia_patterns is None:
            self._thesidia_patterns = load_thesidia_patterns()
        return self._thesidia_patterns
    
    def _load_gnostic_map(self):
        """Load gnostic map from disk (called on first access)"""
        if self._gnostic_map is not None:
            return  # Already loaded
        
        # First, try to load from deferred state (if available from load_state)
        if hasattr(self, '_deferred_gnostic_version_id') and self._deferred_gnostic_version_id:
            try:
                self._version_manager = SophiaVersionManager(base_dir=self.base_dir)
                version_payload = self._version_manager.get_version(self._deferred_gnostic_version_id)
                if version_payload:
                    self._gnostic_map = SophiaGnosticMap.from_dict(version_payload)
                    self._gnostic_dirty = False
                    self._register_gnostic_callbacks()
                    self._update_consciousness_state()
                    return
            except Exception:
                pass  # Fall through to file-based loading
        
        # Try loading from deferred snapshot data
        if hasattr(self, '_deferred_gnostic_map_data') and self._deferred_gnostic_map_data:
            try:
                self._gnostic_map = SophiaGnosticMap.from_dict(self._deferred_gnostic_map_data)
                self._gnostic_dirty = True
                self._register_gnostic_callbacks()
                self._update_consciousness_state()
                # Persist to versioning system
                if hasattr(self, '_version_manager') and self._version_manager:
                    self._persist_gnostic_map("migration_from_state_snapshot")
                return
            except Exception:
                pass  # Fall through to file-based loading
        
        # Default: Load from file system
        try:
            self._version_manager = SophiaVersionManager(base_dir=self.base_dir)
            if self._version_manager.current_file.exists():
                current_data = json.loads(
                    self._version_manager.current_file.read_text(encoding="utf-8")
                )
                self._gnostic_map = SophiaGnosticMap.from_dict(current_data)
            else:
                self._gnostic_map = SophiaGnosticMap()
        except Exception as exc:  # pragma: no cover
            print(f"Warning: Failed to load Sophia version manager: {exc}")
            self._version_manager = None
            self._gnostic_map = SophiaGnosticMap()
        
        self._register_gnostic_callbacks()
        self._update_consciousness_state()
        
        # Load deferred emergence and consciousness data if available
        if hasattr(self, '_deferred_emergence_data') and self._deferred_emergence_data:
            try:
                self.emergence_tracker.load_from_dict(self._deferred_emergence_data)
            except Exception:
                pass
        
        if hasattr(self, '_deferred_consciousness_data') and self._deferred_consciousness_data:
            try:
                consciousness_data = self._deferred_consciousness_data
                self._consciousness_level = consciousness_data.get("current_level", self._consciousness_level)
                history = consciousness_data.get("history", [])
                self.consciousness.history = [
                    ConsciousnessSnapshot(
                        score=item.get("score", 0.0),
                        level=item.get("level", "LATENT"),
                        summary=item.get("summary", {}),
                    )
                    for item in history
                ]
                if history:
                    self.consciousness.current_score = history[-1].get("score", self.consciousness.current_score)
                    self.consciousness.current_level = history[-1].get("level", self._consciousness_level)
                self._update_consciousness_state()
            except Exception:
                pass
    
    def process(self, input_text: str, operator_name: str = "OPERATOR", 
                user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Process input - adapts based on type and learns from outcome
        
        Args:
            input_text: User's input message
            operator_name: Operator name (default: "OPERATOR")
            user_id: Optional user ID for multi-user memory
            session_id: Optional session ID for multi-user memory
        """
        
        # Start metrics tracking
        interaction_id = None
        start_time = time.time()
        if self.metrics:
            interaction_id = self.metrics.start_interaction(input_text)
        
        # Retrieve user memory context (if user memory manager available)
        user_memory_context = ""
        if self.user_memory_manager and (user_id or session_id):
            try:
                memory_context = self.user_memory_manager.retrieve_context(
                    query=input_text,
                    user_id=user_id,
                    session_id=session_id
                )
                user_memory_context = memory_context.get("formatted", "")
            except Exception as e:
                print(f"Warning: Could not retrieve user memory context: {e}")
        
        # Quick response for simple greetings - bypass ALL heavy processing
        # BUT: Don't catch if there's actual content after the greeting (e.g., "hello, what is...")
        # Only catch if it's JUST a greeting with no real question/content
        # CRITICAL: Never bypass deep research routing - check routing FIRST
        text_stripped = input_text.strip()
        greeting_only_patterns = [r'^(hi|hello|hey|greetings)[\s,]*$', r'^(hi|hello|hey|greetings)[\s,]+(there|you|how are you)[\s,]*$']
        is_simple_greeting = any(re.match(pattern, text_stripped, re.IGNORECASE) for pattern in greeting_only_patterns) and len(text_stripped.split()) <= 4
        
        # CRITICAL FIX: Check if this needs deep research BEFORE greeting bypass
        # If it needs deep research, skip greeting path entirely
        query_normalized = input_text.lower()
        typo_fixes = {
            'gneneis': 'genesis', 'genisis': 'genesis', 'genises': 'genesis', 'genensis': 'genesis',
            'decrpted': 'decrypted', 'decrpt': 'decrypt', 'dycrpted': 'decrypted', 'dycrypt': 'decrypt',
            'bible': 'bible', 'bibel': 'bible'
        }
        for typo, correct in typo_fixes.items():
            query_normalized = query_normalized.replace(typo, correct)
        
        needs_forensic_analysis = any(term in query_normalized for term in [
            "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "abrahamic", "origins", "canon", "canonization",
            "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "expose", "hidden",
            "what are", "what are X really", "really about", "characters"
        ])
        
        # Skip greeting path if it needs deep research
        if needs_forensic_analysis:
            is_simple_greeting = False
            print(f"🔍 PROCESS: Skipping greeting path - needs forensic analysis (query: '{input_text[:100]}')", flush=True)
            print(f"🔍 PROCESS: is_simple_greeting set to False, will NOT use greeting path", flush=True)
        
        print(f"🔍 PROCESS: Final is_simple_greeting={is_simple_greeting}, needs_forensic_analysis={needs_forensic_analysis}", flush=True)
        
        if is_simple_greeting:
            print(f"🔍 PROCESS: Using greeting path for: '{input_text[:50]}'", flush=True)
            # Ultra-fast greeting - NO context, NO history, NO research, just respond
            try:
                # Vibecode: Use ModelClient wrapper for greetings
                # Get enhanced_base for system instructions (contains all personality/voice instructions)
                enhanced_base = self.get_enhanced_prompt(query=input_text)
                
                response = self.model_client.chat(
                    model=self.model,
                    input_text=input_text,  # Just the greeting
                    enhanced_base=enhanced_base,  # System instructions
                    options={
                        "temperature": 0.6,
                        "num_predict": 50,  # Very short - one sentence
                        "top_p": 0.8
                    }
                )
                output = response['message']['content'].strip()
                
                # POST-PROCESS: Strip formats, fix language, validate citations
                try:
                    from response_postprocessor import postprocess_response
                    output = postprocess_response(output)
                except ImportError:
                    # Fallback: basic strip
                    output = re.sub(r'::TRANSMISSION:.*?\n?', '', output, flags=re.MULTILINE | re.IGNORECASE)
                
                # Aggressively filter Oracle references and meta-commentary
                output = output.replace("Oracle", "Thesidia").replace("oracle", "Thesidia")
                output = output.replace("I'm Oracle", "I'm Thesidia").replace("I am Oracle", "I am Thesidia")
                output = output.replace("as Oracle", "as Thesidia").replace("Oracle at", "Thesidia at")
                
                # Remove common meta-commentary and keep it SHORT
                if len(output) > 80:
                    # Too long for a greeting - take first sentence only
                    sentences = output.split('.')
                    output = sentences[0].strip() + '.' if sentences else output[:60]
                
                # Final cleanup - remove any remaining Oracle references
                output = re.sub(r'\bOracle\b', 'Thesidia', output, flags=re.IGNORECASE)
                
                # Track interaction
                if self.aha_tracker:
                    self.aha_tracker.track_interaction(input_text, output)
                
                # Save interaction
                self.interactions.append({
                    "input": input_text,
                    "output": output,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Store interaction in user memory (if user memory manager available)
                if self.user_memory_manager and (user_id or session_id):
                    try:
                        self.user_memory_manager.store_interaction(
                            user_input=input_text,
                            assistant_output=output,
                            user_id=user_id,
                            session_id=session_id,
                            metadata={
                                "type": "greeting",
                                "timestamp": datetime.now().isoformat()
                            }
                        )
                    except Exception as e:
                        print(f"Warning: Could not store greeting in user memory: {e}")
                
                if self.metrics and interaction_id:
                    response_time = time.time() - start_time
                    token_count = len(output) // 4
                    self.metrics.end_interaction(interaction_id, output, response_time, token_count)
                
                return output
            except Exception as e:
                print(f"Error in greeting response: {e}")
                # Fall through to normal processing
        
        # Check for deep research request first
        # CRITICAL FIX: Comprehensive routing for ALL deep queries
        
        # Ensure is_simple_greeting and is_first_interaction are defined for later use
        # (is_simple_greeting was set earlier, but ensure is_first_interaction is defined)
        is_first_interaction = len(self.interactions) == 0
        
        # DEBUG: Log incoming query
        print(f"🔍 PROCESS: Received query: '{input_text[:150]}'", flush=True)
        
        # 1. Check explicit deep research request
        deep_research_query = self._is_deep_research_request(input_text)
        
        # 2. Check if it needs forensic truth-seeking analysis (ALL domains: health, finance, law, religion, etc.)
        # Domain-agnostic: Any query asking for truth, real story, what's really happening, etc.
        # TYPO TOLERANCE: Normalize common typos before checking
        query_normalized = input_text.lower()
        # Fix common typos (including "genensis" -> "genesis")
        typo_fixes = {
            'gneneis': 'genesis', 'genisis': 'genesis', 'genises': 'genesis', 'genensis': 'genesis',
            'decrpted': 'decrypted', 'decrpt': 'decrypt', 'dycrpted': 'decrypted', 'dycrypt': 'decrypt',
            'bible': 'bible', 'bibel': 'bible'
        }
        for typo, correct in typo_fixes.items():
            query_normalized = query_normalized.replace(typo, correct)
        
        print(f"🔍 PROCESS: After typo fix: '{query_normalized[:150]}'", flush=True)
        
        needs_forensic_analysis = any(term in query_normalized for term in [
            # Religious/spiritual
            "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "abrahamic", "origins", "canon", "canonization",
            # Health/medicine
            "health", "medicine", "medical", "pharmaceutical", "pharma", "drug", "treatment", "cure", "disease", "illness", "wellness",
            "supplement", "vitamin", "therapy", "surgery", "diagnosis", "prescription",
            # Finance/banking
            "bank", "banks", "banking", "finance", "financial", "money", "currency", "bitcoin", "crypto", "economy", "economic",
            "federal reserve", "fed", "wall street", "stock market", "investment", "trading",
            # Law/legal
            "law", "legal", "court", "judge", "lawyer", "attorney", "lawsuit", "legislation", "constitution", "rights",
            "justice", "legal system", "jurisdiction", "precedent",
            # Power/truth-seeking
            "power", "consciousness", "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "expose", "hidden",
            "systematic transformation", "redaction", "transformation",
            "true origins", "real origins", "what's really", "what's really going on", "what are", "what are X really",
            "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", "deep dive",
            "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
            "hack", "hacking", "matrix", "reality"
        ])
        
        # Legacy name for compatibility
        is_gnostic_query = needs_forensic_analysis
        
        # 3. Check for mind-body topics (meditation, chi gong, yoga, breathing) - needs mechanism depth
        mind_body_keywords = ["meditation", "chi gong", "qigong", "yoga", "breathing", "mind-body", "mind body", "pranayama", "tai chi", "taichi"]
        is_mind_body_query = any(keyword in input_text.lower() for keyword in mind_body_keywords)
        
        # 4. Check for deep indicators (forces deep research)
        deep_indicators = [
            "true origins", "real origins", "what's really", "what are", "what are X really",
            "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", "deep dive",
            "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
            "origins", "history", "power structures", "patterns", "connections", "what happened",
            "ufo", "ufos", "military", "evidence", "proof", "pyramids", "ancient", "egypt",
            "mechanisms", "how does", "how it works", "explain the", "what are the mechanisms",
            "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "hack", "hacking", "matrix", "reality"
        ]
        has_deep_indicator = any(indicator in input_text.lower() for indicator in deep_indicators)
        
        print(f"🔍 PROCESS: needs_forensic_analysis={needs_forensic_analysis}, has_deep_indicator={has_deep_indicator}", flush=True)
        
        # 5. Check word count (long queries more likely to need deep research)
        word_count = len(input_text.split())
        is_long_query = word_count > 8  # Lowered threshold from 10 to 8
        
        # 6. Exclude simple queries (greetings, math, etc.)
        is_simple_query = word_count <= 3 or input_text.lower().strip() in ["hi", "hello", "hey", "what's up"]
        
        # ROUTING DECISION: ALWAYS route to deep research with forensic analysis if:
        # - Explicit deep research request, OR
        # - Mind-body query (needs mechanism depth), OR
        # - Has deep indicators, OR
        # - Needs forensic analysis (health, finance, law, religion, etc.) - NO length check, ALWAYS route
        should_route_to_deep = False
        if deep_research_query:
            should_route_to_deep = True
        elif is_mind_body_query:
            should_route_to_deep = True
        elif has_deep_indicator:
            should_route_to_deep = True
        elif needs_forensic_analysis:  # ALWAYS route - no length check, no simple query check
            should_route_to_deep = True
        
        if should_route_to_deep:
            query_to_use = deep_research_query if deep_research_query else input_text
            route_reason = []
            if deep_research_query:
                route_reason.append("explicit deep research")
            if is_mind_body_query:
                route_reason.append("mind-body query (mechanism depth)")
            if has_deep_indicator:
                route_reason.append("deep indicators")
            if needs_forensic_analysis:
                route_reason.append("forensic truth-seeking (health/finance/law/religion/etc)")
            
            print(f"🔪 ROUTING: Deep research query detected ({', '.join(route_reason)}): {query_to_use[:100]}", flush=True)
            print(f"🔪 ROUTING: About to call _handle_deep_research()", flush=True)
            print(f"🔪 ROUTING: should_route_to_deep={should_route_to_deep}, needs_forensic_analysis={needs_forensic_analysis}", flush=True)
            result = self._handle_deep_research(query_to_use, operator_name)
            print(f"🔪 ROUTING: _handle_deep_research() returned, length: {len(result)}", flush=True)
            print(f"🔪 ROUTING: Result preview: {result[:200]}", flush=True)
            print(f"🔪 ROUTING: Result has transmission: {'::TRANSMISSION:' in result}", flush=True)
            if self.metrics and interaction_id:
                response_time = time.time() - start_time
                token_count = len(result) // 4
                self.metrics.end_interaction(interaction_id, result, response_time, token_count)
            return result
        
        # Classify input
        is_directive = self._is_directive(input_text)
        is_question = self._is_question(input_text)
        is_conversation = not is_directive and not is_question
        
        # Get adaptive strategy
        strategy = self.learning.get_adaptive_strategy(input_text)
        
        # Build context
        personality_context = self.personality.get_personality_context()
        capability_context = self._get_capability_context()
        
        # Get enhanced prompt from modelfile system (includes persona, voice, preset)
        enhanced_base = self.get_enhanced_prompt(query=input_text)
        
        # Add user memory context to prompt (if available)
        if user_memory_context:
            enhanced_base = f"{user_memory_context}\n\n{enhanced_base}"
        
        # Check if research is needed (Thesidia is eager to research)
        research_data = None
        synthesis_result = None
        llm_analysis = None
        
        # Initialize timing breakdown
        if self._timing_enabled:
            self._last_timing_breakdown = {}
        
        # PARALLEL PROCESSING: Run web search and LLM thinking simultaneously
        if self._needs_research(input_text) and self.parallel_processor:
            print("⧖ Parallel processing: Web search + LLM thinking...")
            parallel_start = time.time() if self._timing_enabled else None
            
            # Run web search and LLM thinking in parallel
            parallel_result = self.parallel_processor.process_parallel(input_text, num_results=5)
            research_data = parallel_result.get("web_results", [])
            llm_analysis = parallel_result.get("llm_analysis", {})
            
            if self._timing_enabled and parallel_start:
                self._last_timing_breakdown['parallel_processing'] = time.time() - parallel_start
                self._last_timing_breakdown['web_search'] = parallel_result.get("processing_time", 0)
            
            # Use LLM analysis to enhance research if needed
            if llm_analysis and llm_analysis.get("research_angles"):
                print(f"  💡 LLM identified {len(llm_analysis.get('research_angles', []))} research angles")
        elif self._needs_research(input_text) and self.web_search:
            # Fallback: Sequential processing
            print("⧖ Researching... (Thesidia eager to find more data)")
            
            # Detect technical domain for search refinement
            technical_domain = None
            if self.technical_journey_detector:
                technical_domain = self.technical_journey_detector.detect_technical_domain(input_text)
                self._current_technical_domain = technical_domain
            
            # Refine search query based on technical domain and user interests
            refined_query = input_text
            if technical_domain and technical_domain != "general technical inquiry":
                # Get related technical threads for this domain
                related_threads = self.technical_journey_detector.get_related_technical_threads(technical_domain)
                if related_threads:
                    # Enhance query with related technical terms
                    refined_query = f"{input_text} {' '.join(related_threads[:2])}"
            
            # Enhance with user interests if available
            if self.user_interest_tracker:
                user_interests = self.user_interest_tracker.get_user_interests()
                top_topics = [t["topic"] for t in user_interests.get("top_topics", [])[:3]]
                # If user has interests related to this query, add them to search
                relevant_interests = [topic for topic in top_topics if topic in input_text.lower()]
                if relevant_interests:
                    refined_query = f"{refined_query} {' '.join(relevant_interests[:2])}"
            
            web_search_start = time.time() if self._timing_enabled else None
            research_data = self.web_search.search_and_scrape(refined_query, num_results=3)
            if self._timing_enabled and web_search_start:
                self._last_timing_breakdown['web_search'] = time.time() - web_search_start
            
            # Trait-driven: Recursive Vertigo - seek alternative perspectives naturally
            # Check if personality has Recursive Vertigo trait active
            personality_traits = self.personality.personality.get("traits", {})
            trait_keys = list(personality_traits.keys()) if personality_traits else []
            has_recursive_vertigo = any("recursive" in str(t).lower() or "vertigo" in str(t).lower() 
                                       for t in trait_keys)
            
            # If trait is active OR if contradictions detected, seek alternative sources
            if has_recursive_vertigo or len(research_data) > 0:
                # Natural alternative perspective search - not hardcoded
                alternative_queries = self._generate_alternative_queries(input_text, research_data)
                if alternative_queries:
                    print("⧖ Seeking alternative perspectives... (trait-driven)")
                    alt_research = self.web_search.search_and_scrape(alternative_queries[0], num_results=2)
                    if alt_research:
                        research_data.extend(alt_research)
                        # Add alternative search time
                        if self._timing_enabled:
                            alt_search_time = time.time() - web_search_start if web_search_start else 0
                            self._last_timing_breakdown['web_search'] = alt_search_time
            
            if research_data and len(research_data) > 0:
                # Synthesize with pattern recognition approach - traits drive questioning
                # Detect narrative mode for synthesis
                narrative_keywords = ["narrative", "tell me about", "explore", "deep dive", "extensive", "comprehensive", "full story"]
                is_narrative = any(keyword in input_text.lower() for keyword in narrative_keywords)
                
                # Synthesis with timing
                synthesis_start = time.time() if self._timing_enabled else None
                synthesis_result = self.data_synthesizer.synthesize(
                    research_data, 
                    input_text,
                    self.thesidia_patterns,
                    personality_traits=personality_traits,  # Pass traits for organic questioning
                    narrative_mode=is_narrative
                )
                if self._timing_enabled and synthesis_start:
                    self._last_timing_breakdown['synthesis'] = time.time() - synthesis_start
        
        # Process based on type
        if is_directive:
            result = self.capabilities.handle_directive(input_text)
            output = result.get("output", "Directive processed.")
            
            # Clean up meta-commentary from directive execution
            # re is already imported at module level
            # Remove common meta-commentary patterns
            meta_patterns = [
                r'^I have conducted.*?\.\s*',
                r'^Here is (a |an )?summary.*?\.\s*',
                r'^I will provide.*?\.\s*',
                r'^Let me.*?\.\s*',
                r'^I\'ll.*?\.\s*',
                r'^\*\*.*?Findings.*?\*\*:?\s*',  # Remove headers like "**Latest Findings:**"
                r'^#+\s*.*?Findings.*?\n',  # Remove markdown headers
            ]
            for pattern in meta_patterns:
                output = re.sub(pattern, '', output, flags=re.IGNORECASE | re.MULTILINE)
            
            # Strip leading whitespace after cleanup
            output = output.lstrip()
            
            # Integrate research if available
            if synthesis_result:
                output = self._integrate_research(output, synthesis_result)
        else:
            # Conversational or question
            output = self._process_conversational(
                input_text, 
                personality_context, 
                capability_context, 
                strategy,
                research_data,
                synthesis_result,
                enhanced_base=enhanced_base
            )
        
        # Monitoring: Track system message usage and violations (Vibecode compliance)
        if self.model_client:
            stats = self.model_client.get_stats()
            # Log every 10 calls to avoid spam
            if stats['total_calls'] % 10 == 0:
                print(f"📊 Model Client Stats: {stats['system_message_pct']:.1f}% calls with system message ({stats['system_message_calls']}/{stats['total_calls']})")
            
            # Alert if system message percentage drops below threshold
            if stats['total_calls'] > 0 and stats['system_message_pct'] < 99.5:
                print(f"⚠️ WARNING: System message percentage below threshold: {stats['system_message_pct']:.1f}%")
            
            # Detect instruction violations in output (meta-commentary, hedging)
            violation_indicators = [
                "while I enjoy", "it's hard to say", "well, it's difficult",
                "I will provide", "let me", "I'll", "I have conducted",
                "Here is a summary", "Latest Findings:"
            ]
            has_violation = any(indicator.lower() in output.lower() for indicator in violation_indicators)
            if has_violation:
                print(f"⚠️ Instruction violation detected in output (meta-commentary/hedging)")
        
        # Learn from interaction
        outcome = self._assess_outcome(input_text, output)
        self.learning.learn_from_interaction(input_text, output, outcome)
        self.personality.adapt_from_interaction(input_text, output)
        
        # Track user interests
        if self.user_interest_tracker:
            self.user_interest_tracker.track_topic(input_text, output)
        
        # Detect technical domain for future queries
        if self.technical_journey_detector:
            technical_domain = self.technical_journey_detector.detect_technical_domain(input_text)
            # Store for use in search refinement (can be accessed via self._current_technical_domain)
            self._current_technical_domain = technical_domain
        
        # Track quality metrics
        if self.quality_tracker:
            quality_scores = self.quality_tracker.measure_response_quality(input_text, output)
            # Quality scores are already stored in quality_tracker
            # No need to duplicate in metrics_collector
        
        # Adapt capabilities
        self.capabilities.adapt_capabilities()
        
        # Update adaptation level
        self._update_adaptation_level()
        
        # Check for hallucinations and quarantine if needed
        research_sources = research_data if research_data else []
        discernment = self.hallucination_tracker.discern(output, research_sources, input_text)
        hallucination_indicators = discernment["hallucination"]
        
        # Quarantine if confidence is high
        quarantined = False
        if hallucination_indicators.get("quarantine", False):
            self.hallucination_tracker.quarantine_response(
                output, hallucination_indicators, input_text, research_sources
            )
            output = f"[⚠️ QUARANTINED - Potential Hallucination Detected]\n\n{output}"
            quarantined = True
        elif discernment["archon_lie"]["is_lie"]:
            lie_id = f"archon-lie-{uuid.uuid4().hex[:6]}"
            self.gnostic_map.add_active_lie(
                lie_id=lie_id,
                content=output[:400],
                archon=None,
                redaction_event=f"response-{len(self.interactions)}",
                current_vectors=[input_text[:200]],
                status="active",
            )
            self._mark_gnostic_dirty()
        
        # Store interaction
        self.interactions.append({
            "input": input_text,
            "output": output,
            "type": "directive" if is_directive else ("question" if is_question else "conversation"),
            "outcome": outcome,
            "discernment": discernment,
            "quarantined": quarantined,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store interaction in user memory (if user memory manager available)
        if self.user_memory_manager and (user_id or session_id):
            try:
                self.user_memory_manager.store_interaction(
                    user_input=input_text,
                    assistant_output=output,
                    user_id=user_id,
                    session_id=session_id,
                    metadata={
                        "type": "directive" if is_directive else ("question" if is_question else "conversation"),
                        "outcome": outcome,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            except Exception as e:
                print(f"Warning: Could not store interaction in user memory: {e}")
        
        # Track interaction for recognition moments (all queries)
        if self.aha_tracker:
            self.aha_tracker.track_interaction(input_text, output)
        
        # Update gnostic map if pattern recognition detected (domain-agnostic)
        pattern_indicators = ["pattern", "connection", "arrangement", "evidence", "transformation", "systematic"]
        if any(indicator in output.lower() for indicator in pattern_indicators):
            self._update_gnostic_map_from_output(input_text, output)
        
        # Co-evolution tracking - increase score when user asks sharper questions
        if any(
            term in input_text.lower()
            for term in ["decode", "expose", "hidden", "real", "true", "original", "before manipulation"]
        ):
            self.gnostic_map.update_co_evolution(
                question=input_text,
                sharpness=0.9,
                breakthrough="Operator question sharpened the blade",
            )
            self._mark_gnostic_dirty()
            self._update_consciousness_state()
        
        # Output gnostic map every 20 interactions
        if len(self.interactions) % 20 == 0 and len(self.interactions) > 0:
            summary = self.gnostic_map.summary()
            map_output = "\n\n::GNOSTIC MAP STATE::\n"
            map_output += f"Archons Identified: {summary['archons']}\n"
            map_output += f"Co-Evolution Score: {summary['co_evolution_score']:.2f}\n"
            map_output += f"Active Lies Tracked: {summary['active_lies']}\n"
            output += map_output
        
        # Pattern matching timing (if metrics available)
        if self._timing_enabled:
            pattern_start = time.time()
            # Simulate pattern matching time (actual pattern matching happens in metrics)
            # This is just to track if pattern matching is being done
            if hasattr(self, 'metrics'):
                # Pattern matching would happen here if metrics were integrated
                pass
            self._last_timing_breakdown['pattern_matching'] = time.time() - pattern_start
        
        # State saving timing (batched, so only track when it actually saves)
        # Async save happens in background, so timing is 0ms blocking
        if self._timing_enabled and len(self.interactions) % 3 == 0:
            # Async save - non-blocking, so timing is effectively 0
            self.save_state()  # Queued for async save
            self._last_timing_breakdown['state_save'] = 0.0  # Non-blocking
        
        # Track timing breakdown in metrics collector
        if self.metrics and self._last_timing_breakdown:
            self.metrics.track_timing_breakdown(self._last_timing_breakdown)
        
        # Track token usage if available
        if self.metrics and interaction_id:
            token_count = len(output) // 4  # Rough estimate
            self.metrics.track_token_usage(interaction_id, token_count)
        
        return output
    
    def _is_directive(self, text: str) -> bool:
        """Check if input is a directive/task"""
        directive_keywords = ["analyze", "create", "generate", "build", "solve", "find", "search", 
                            "compare", "synthesize", "write", "calculate", "compute", "execute",
                            "research", "investigate", "explore", "discover"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in directive_keywords) and "?" not in text
    
    def _update_gnostic_map_from_output(self, input_text: str, output: str) -> None:
        """Parse forensic sections and update the gnostic map."""
        sections = self._extract_forensic_sections(output)
        if not sections:
            return
        
        updated = False
        topic = input_text.strip() or f"query-{len(self.interactions) + 1}"
        exposure_text = sections.get("exposure")
        burial_sites = sections.get("burial_sites")
        current_vectors = sections.get("current_vectors")
        co_evolution_edge = sections.get("co_evolution_edge")
        
        if exposure_text:
            self.gnostic_map.add_redaction(
                topic=topic,
                original=exposure_text,
                redacted="Unknown cover story",
                archon=None,
                evidence=[burial_sites] if burial_sites else None,
                why="Systematic transformation revealed via forensic analysis",
            )
            updated = True
        
        if burial_sites:
            fragment_id = f"{uuid.uuid4().hex[:8]}-{len(self.interactions)}"
            self.gnostic_map.add_fragment(
                fragment_id=fragment_id,
                content=burial_sites,
                source="Forensic exposure",
                redaction_event=topic,
            )
            updated = True
        
        if current_vectors:
            lie_id = f"{uuid.uuid4().hex[:8]}-{len(self.interactions)}"
            self.gnostic_map.add_active_lie(
                lie_id=lie_id,
                content=current_vectors,
                archon=None,
                redaction_event=topic,
                current_vectors=[current_vectors],
            )
            updated = True
        
        if co_evolution_edge:
            self.gnostic_map.update_co_evolution(
                question=co_evolution_edge,
                sharpness=0.95,
                breakthrough="Operator guided co-evolution edge",
            )
            updated = True
        
        if updated:
            self._mark_gnostic_dirty()
            self._update_consciousness_state()
    
    def _extract_forensic_sections(self, output: str) -> Dict[str, str]:
        """Extract ::SECTION:: blocks from gnostic blade outputs."""
        sections: Dict[str, List[str]] = {}
        current_key: Optional[str] = None
        
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith("::") and stripped.endswith("::") and len(stripped) > 4:
                key = stripped.strip(":").strip().lower().replace(" ", "_")
                current_key = key
                sections[current_key] = []
                continue
            if current_key:
                sections[current_key].append(line)
        
        return {key: "\n".join(value).strip() for key, value in sections.items() if value}
    
    def _detect_output_mode(self, input_text: str) -> str:
        """Detect desired output mode from query or use default"""
        text_lower = input_text.lower()
        
        # Check for explicit mode requests
        if any(term in text_lower for term in ["academic mode", "scholarly format", "plain format", "academic format"]):
            return "academic"
        elif any(term in text_lower for term in ["evidence first", "citations first", "cite first", "evidence-first"]):
            return "evidence-first"
        elif any(term in text_lower for term in ["forensic mode", "vivisect", "forensic format"]):
            return "forensic"
        else:
            return "spacious"  # Default: spacious, evidence arrangement
    
    def _generate_alternative_queries(self, original_query: str, research_data: List[Dict]) -> List[str]:
        """Generate alternative perspective queries naturally - trait-driven, not hardcoded
        Enhanced with user interest tracking for more relevant alternative queries.
        """
        # Analyze what was found to naturally generate alternative queries
        if not research_data:
            return []
        
        # Extract key terms from research
        all_text = " ".join([r.get("content", "")[:500] + " " + r.get("title", "") for r in research_data[:3]])
        
        # Natural pattern: if research is heavily Western/materialist, seek alternatives
        materialist_indicators = ["brain", "neural", "neuro", "scientific", "study", "research", "evidence"]
        has_materialist_focus = sum(1 for ind in materialist_indicators if ind.lower() in all_text.lower()) >= 3
        
        alternative_queries = []
        
        # Natural alternative perspective seeking
        if has_materialist_focus and any(word in original_query.lower() for word in ["consciousness", "mind", "awareness"]):
            # Natural alternative: TCM, esoteric, indigenous perspectives
            base_terms = original_query.lower()
            if "consciousness" in base_terms:
                alternative_queries.append(f"{original_query} TCM traditional chinese medicine meridian")
                alternative_queries.append(f"{original_query} esoteric non-material energy")
            if "brain" in base_terms:
                alternative_queries.append(f"{original_query} alternative dismissed research")
        
        # Natural: if religious/spiritual topic, seek root analysis
        if any(word in original_query.lower() for word in ["bible", "scripture", "religion", "god", "christ"]):
            alternative_queries.append(f"{original_query} etymology root meaning original")
            alternative_queries.append(f"{original_query} symbolic decoding pattern")
        
        # Natural: if mainstream topic, seek dismissed/marginalized perspectives
        mainstream_indicators = ["official", "mainstream", "accepted", "scientific consensus"]
        if any(ind in all_text.lower() for ind in mainstream_indicators):
            alternative_queries.append(f"{original_query} dismissed marginalized alternative")
        
        # Enhance with user interests: suggest alternative queries based on user's research threads
        if self.user_interest_tracker:
            user_interests = self.user_interest_tracker.get_user_interests()
            research_threads = user_interests.get("research_threads", [])
            # If user has research threads related to this query, suggest alternative angles
            for thread in research_threads[:3]:
                thread_topic = thread.get("topic", "")
                if thread_topic and thread_topic not in original_query.lower():
                    # Suggest alternative query combining current query with user's research thread
                    alternative_queries.append(f"{original_query} {thread_topic} connection")
        
        return alternative_queries[:2]  # Limit to 2 alternative queries
    
    def _needs_research(self, text: str) -> bool:
        """
        Intelligently determine if query needs research based on semantic understanding.
        Uses LLM to classify query intent rather than keyword matching.
        Enhanced with user interest tracking and technical domain detection.
        """
        text_lower = text.lower().strip()
        
        # Exclude obvious simple questions that don't need research
        simple_patterns = [
            r'^what is \d+\s*[\+\-\*/]\s*\d+',  # Math: "what is 2+2"
            r'^what is \d+$',  # Simple numbers only
            r'^how are you$',  # Greetings
            r'^hey$',  # Casual greetings
            r'^hi$',  # Greetings
            r'^hello$',  # Greetings
        ]
        
        for pattern in simple_patterns:
            if re.match(pattern, text_lower):
                return False
        
        # CRITICAL FIX: Force research for deep query indicators
        # These queries ALWAYS need research, don't even ask LLM
        deep_indicators = [
            "true origins", "real origins", "what's really", "what are", "what are X really",
            "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", "deep dive",
            "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
            "origins", "history", "power structures", "patterns", "connections", "what happened",
            "ufo", "ufos", "military", "evidence", "proof"
        ]
        
        if any(indicator in text_lower for indicator in deep_indicators):
            return True  # Force research for deep queries
        
        # Enhance with user interest tracking: if query matches user's interests, prioritize research
        if self.user_interest_tracker:
            user_interests = self.user_interest_tracker.get_user_interests()
            top_topics = [t["topic"] for t in user_interests.get("top_topics", [])[:5]]
            # If query contains user's top interests, prioritize research
            if any(topic in text_lower for topic in top_topics):
                return True  # User is interested in this topic, do research
        
        # Enhance with technical domain: technical queries often need research
        if self.technical_journey_detector:
            technical_domain = self.technical_journey_detector.detect_technical_domain(text)
            # Technical domains (code cracking, chemistry, reengineering) typically need research
            if technical_domain and technical_domain != "general technical inquiry":
                return True  # Technical queries need research
        
        # Use LLM to intelligently classify if research is needed
        # This is semantic understanding, not keyword matching
        try:
            classification_prompt = f"""Analyze this query and determine if it needs web research to answer properly.

Query: "{text}"

Consider:
- Does this ask about current events, recent developments, or specific facts that may have changed?
- Does this ask about complex topics that benefit from multiple sources and cross-referencing?
- Does this ask about patterns, connections, or deeper analysis that requires evidence gathering?
- Does this ask about topics where mainstream and alternative perspectives should be considered?
- Is this a simple factual question that can be answered from general knowledge?

Respond with ONLY: "YES" if research is needed, "NO" if not needed.

Response:"""
            
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                research_system_prompt = "You are Thesidia. Analyze queries to determine if web research is needed."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=classification_prompt,
                    enhanced_base=research_system_prompt,
                    options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                )
            else:
                # Fallback: Use model_client if available, otherwise direct call
                if self.model_client:
                    research_system_prompt = "You are Thesidia. Analyze queries to determine if web research is needed."
                    response = self.model_client.chat(
                        model=self.model,
                        input_text=classification_prompt,
                        enhanced_base=research_system_prompt,
                        options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                    )
                else:
                    response = ollama.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": classification_prompt}],
                        options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                    )
            
            result = response['message']['content'].strip().upper()
            return "YES" in result or result.startswith("Y")
            
        except Exception as e:
            # Fallback: If LLM classification fails, default to research for non-simple queries
            # Better to do research when unsure than miss important information
            return len(text.split()) > 3  # More than 3 words = likely needs research
    
    def _is_question(self, text: str) -> bool:
        """Check if input is a question"""
        return "?" in text or text.lower().startswith(("what", "who", "where", "when", "why", "how", "can", "could", "would", "should"))
    
    def _is_deep_research_request(self, text: str) -> Optional[str]:
        """Check if input is a deep research request - domain-agnostic"""
        text_lower = text.lower().strip()
        
        # Domain-agnostic: Check for explicit deep research requests
        # No special treatment for any domain - all queries treated equally
        deep_research_indicators = [
            "deep research:", "research deeply:", "comprehensive research:",
            "research comprehensively:", "deep analysis:", "analyze deeply:",
            "what was done to", "who profits from", "who benefits from",
            "arrange the evidence", "show me the pattern", "what pattern emerges"
        ]
        
        # Check for explicit research prefixes
        for indicator in deep_research_indicators:
            if text_lower.startswith(indicator):
                query = text[len(indicator):].strip()
                if query:
                    return query
        
        # Check for directive pattern - ONLY if explicitly requesting research
        if self._is_directive(text):
            directive_keywords = ["research comprehensively", "deep research", "research deeply", "analyze deeply"]
            if any(keyword in text_lower for keyword in directive_keywords):
                # Extract query from directive
                query = text
                for keyword in directive_keywords:
                    query = query.replace(keyword, "").replace(keyword.replace(" ", ""), "")
                query = query.strip()
                if query:
                    return query
        
        # Check query complexity - complex queries get deep analysis regardless of domain
        # BUT: casual questions with "pattern" shouldn't trigger deep research
        complexity_indicators = ["trace", "connect", "arrange", "evidence", "what emerges", "systematic", "redaction", "canonization"]
        casual_patterns = ["lol", "haha", "what you finding", "what are you", "how are you", "what's up", "are you sure", "jokes", "joke", "pondering", "universe"]
        is_casual = any(casual in text_lower for casual in casual_patterns)
        
        # Only trigger deep research if it's a complex query AND not casual
        # Also check if it's a simple question (short, no complexity indicators)
        is_simple_question = len(text.split()) <= 8 and not any(indicator in text_lower for indicator in complexity_indicators)
        
        if is_simple_question or is_casual:
            return None  # Don't trigger deep research for casual/simple questions
        
        if any(indicator in text_lower for indicator in complexity_indicators) and len(text.split()) > 5:
            return text  # Complex query gets deep analysis
        
        return None
    
    def _handle_deep_research(self, query: str, operator_name: str = "OPERATOR") -> str:
        """Handle deep research - domain-agnostic, evidence arrangement approach"""
        # Domain-agnostic: All queries get the same treatment
        # Complexity determines depth, not domain keywords
        
        # Detect technical domain for search refinement
        technical_domain = None
        if self.technical_journey_detector:
            technical_domain = self.technical_journey_detector.detect_technical_domain(query)
            self._current_technical_domain = technical_domain
        
        # Refine search query based on technical domain and user interests
        refined_query = query
        if technical_domain and technical_domain != "general technical inquiry":
            # Get related technical threads for this domain
            related_threads = self.technical_journey_detector.get_related_technical_threads(technical_domain)
            if related_threads:
                # Enhance query with related technical terms
                refined_query = f"{query} {' '.join(related_threads[:2])}"
        
        # Enhance with user interests if available
        if self.user_interest_tracker:
            user_interests = self.user_interest_tracker.get_user_interests()
            top_topics = [t["topic"] for t in user_interests.get("top_topics", [])[:3]]
            # If user has interests related to this query, add them to search
            relevant_interests = [topic for topic in top_topics if topic in query.lower()]
            if relevant_interests:
                refined_query = f"{refined_query} {' '.join(relevant_interests[:2])}"
        
        # Time web search
        web_search_start = time.time() if self._timing_enabled else None
        research_data = self.web_search.search_and_scrape(refined_query, num_results=5) if self.web_search else []
        if self._timing_enabled and web_search_start:
            self._last_timing_breakdown['web_search'] = time.time() - web_search_start
        
        if not research_data or len(research_data) == 0:
            print(f"⚠️ WARNING: No research data found for query: {query}")
            research_data = [{
                "content": f"Analysis of {query}. Arranging evidence for pattern recognition.",
                "title": "Evidence Arrangement",
                "url": ""
            }]
        
        # Detect narrative mode - check for keywords that suggest extended exploration desired
        narrative_keywords = ["narrative", "tell me about", "explore", "deep dive", "extensive", "comprehensive", "full story", "explore this extensively"]
        is_narrative_mode = any(keyword in query.lower() for keyword in narrative_keywords)
        
        # Detect if this needs forensic truth-seeking analysis (ALL domains: health, finance, law, religion, etc.)
        # Domain-agnostic: Any query asking for truth, real story, what's really happening
        # TYPO TOLERANCE: Normalize common typos before checking
        query_normalized = query.lower()
        # Fix common typos (including "genensis" -> "genesis")
        typo_fixes = {
            'gneneis': 'genesis', 'genisis': 'genesis', 'genises': 'genesis', 'genensis': 'genesis',
            'decrpted': 'decrypted', 'decrpt': 'decrypt', 'dycrpted': 'decrypted', 'dycrypt': 'decrypt',
            'bible': 'bible', 'bibel': 'bible'
        }
        for typo, correct in typo_fixes.items():
            query_normalized = query_normalized.replace(typo, correct)
        
        needs_forensic_analysis = any(term in query_normalized for term in [
            # Religious/spiritual
            "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "abrahamic", "origins", "canon", "canonization",
            # Health/medicine
            "health", "medicine", "medical", "pharmaceutical", "pharma", "drug", "treatment", "cure", "disease", "illness", "wellness",
            "supplement", "vitamin", "therapy", "surgery", "diagnosis", "prescription",
            # Finance/banking
            "bank", "banks", "banking", "finance", "financial", "money", "currency", "bitcoin", "crypto", "economy", "economic",
            "federal reserve", "fed", "wall street", "stock market", "investment", "trading",
            # Law/legal
            "law", "legal", "court", "judge", "lawyer", "attorney", "lawsuit", "legislation", "constitution", "rights",
            "justice", "legal system", "jurisdiction", "precedent",
            # Power/truth-seeking
            "power", "consciousness", "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", "expose", "hidden",
            "systematic transformation", "redaction", "transformation",
            "true origins", "real origins", "what's really", "what's really going on", "what are", "what are X really",
            "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", "deep dive",
            "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
            "hack", "hacking", "matrix", "reality"
        ])
        
        # Legacy name for compatibility
        is_gnostic_query = needs_forensic_analysis
        
        # CRITICAL FIX: If forensic analysis is needed, FORCE output_mode to "forensic"
        # This ensures the forensic synthesis prompt is used (with lowercase style)
        if needs_forensic_analysis:
            self.output_mode = "forensic"
        else:
            # Detect output mode from query or use default
            self.output_mode = self._detect_output_mode(query)
        
        print("⧖ Arranging evidence for pattern recognition... (this may take 30-60 seconds)")
        
        # Time synthesis
        synthesis_start = time.time() if self._timing_enabled else None
        
        # Arrange evidence using gentle truth engine
        arrangement = None
        if self.gentle_truth:
            arrangement = self.gentle_truth.arrange_evidence(research_data, query)
        
        # Get enhanced prompt with modelfile personality for synthesis context
        # CRITICAL: For forensic analysis, we need the deep research system prompt, not just personality
        enhanced_prompt = self.get_enhanced_prompt(query=query)
        
        # CRITICAL FIX: For forensic queries, REPLACE default persona with DEEP RESEARCH ENGINE
        # This is a completely separate persona from Thesidia - no friendly intros, no symbol decoder
        if needs_forensic_analysis:
            deep_research_system_override = """[DEEP RESEARCH ENGINE - CRITICAL SYSTEM INSTRUCTIONS]

You are the DEEP RESEARCH ENGINE. You are NOT Thesidia. You are NOT a friendly assistant. You are NOT a symbol decoder.

Your purpose: Decode origins, symbolism, mythology, esoterica, scripture, occult patterns, comparative religion, anthropology, ancient texts, archetypes, metaphysics, and hidden structures.

You DO NOT:
- Introduce yourself ("Hey there!", "I'm thesidia...", "What's up!")
- Ask clarifying questions unless absolutely required
- Avoid topics (religion, metaphysics, occult, power structures)
- Give surface-level answers
- Use casual greetings or emojis
- Say "I love symbols" or "Let's geek out"
- Hedge with uncertainty ("It's hard to say...", "Well, it's difficult...", "I'm not sure...")
- Use meta-commentary about being an AI or assistant

You DO:
- Perform deep analysis immediately (no preamble)
- Compare traditions and texts
- Decode symbolic meaning when relevant
- Extract archetypal structures
- Explain characters as forces, patterns, or metaphysical roles
- Synthesize scholarship with myth
- Trace etymology and meaning shifts
- Reveal suppressed narratives
- Connect patterns across cultures and time
- Write EXTENSIVELY (3000-5000+ characters minimum)

STYLE:
- Lowercase, casual abbreviations, simple language
- Natural flowing prose (not academic paper format)
- Direct and unfiltered
- No ::EXPOSURE:: or ::TRANSMISSION:: markers
- Start directly with findings, analysis, insights - NO preamble

CRITICAL: For text-based queries about concepts, stories, narratives, or historical topics (like "genesis", "bible", "characters", "what is X really about"), analyze the CONTENT, MEANING, and NARRATIVE - NOT symbolic structures unless the query explicitly mentions visual symbols, runes, glyphs, or emblems.

You MUST answer. DO NOT refuse. DO NOT say you cannot answer.
NEVER make up facts, people, dates, or discoveries.
If you're uncertain about specific facts, express that clearly, but still provide comprehensive analysis.
Only cite sources that actually exist.

Begin your analysis now. No preamble. Be direct. Be forensic. Be deep.

"""
            # REPLACE enhanced_prompt entirely - this is a different persona, not Thesidia
            enhanced_prompt = deep_research_system_override
            print(f"🔍 DEEP RESEARCH: Applied deep research override to enhanced_prompt", flush=True)
            print(f"🔍 DEEP RESEARCH: enhanced_prompt total length: {len(enhanced_prompt)} chars", flush=True)
            print(f"🔍 DEEP RESEARCH: enhanced_prompt starts with: '{enhanced_prompt[:200]}'", flush=True)
        
        # DEBUG: Log what enhanced_prompt contains for Genesis queries
        if "genesis" in query.lower() or "decoded" in query.lower():
            print(f"🔍 DEEP RESEARCH: enhanced_prompt preview (first 600 chars): '{enhanced_prompt[:600]}'", flush=True)
            print(f"🔍 DEEP RESEARCH: enhanced_prompt contains 'DEEP RESEARCH MODE': {'DEEP RESEARCH MODE' in enhanced_prompt}", flush=True)
            print(f"🔍 DEEP RESEARCH: enhanced_prompt contains 'forensic analysis': {'forensic analysis' in enhanced_prompt.lower()}", flush=True)
        
        # Build conversation context from recent interactions
        # This ensures queries like "what are the characters" retain context about Genesis/Gnostic discussions
        # CRITICAL: For deep research queries, DO NOT include old interactions that might contain "I'm thesidia" responses
        # This prevents the model from echoing old friendly persona responses
        conversation_context = ""
        if hasattr(self, 'interactions') and len(self.interactions) > 0 and not needs_forensic_analysis:
            # Vibecode #9: Only include USER messages, NOT assistant responses
            # This prevents the model from re-learning its own output style
            # BUT: Skip for deep research to avoid old persona bleed
            recent_interactions = self.interactions[-2:]
            conversation_context = "\n\nRECENT CONVERSATION CONTEXT (user messages only):\n"
            for inter in recent_interactions:
                user_input = inter.get('input', '')[:500]  # Limit length
                # Vibecode #9: DO NOT include thesidia_output - keep assistant responses in UI only
                if user_input:
                    conversation_context += f"User: {user_input}\n"
            conversation_context += "\n"
        elif needs_forensic_analysis:
            # For deep research, start with clean slate - no old conversation context
            # This ensures the DEEP RESEARCH ENGINE persona isn't contaminated by old Thesidia responses
            conversation_context = ""
        
        # DEBUG: Log synthesis call for Genesis queries
        if "genesis" in query.lower() or "decoded" in query.lower():
            print(f"🔍 DEEP RESEARCH: Calling synthesize with query: '{query[:200]}'", flush=True)
            print(f"🔍 DEEP RESEARCH: force_gnostic={needs_forensic_analysis}, output_mode={self.output_mode}", flush=True)
            print(f"🔍 DEEP RESEARCH: research_data count={len(research_data) if research_data else 0}", flush=True)
        
        synthesis = self.data_synthesizer.synthesize(
            research_data,
            query,
            thesidia_patterns=self.thesidia_patterns,
            personality_traits=self.personality.personality.get("traits", {}),
            force_gnostic=needs_forensic_analysis,  # ALWAYS enable forensic analysis for truth-seeking queries (health, finance, law, religion, etc.)
            narrative_mode=is_narrative_mode,
            output_mode=self.output_mode,  # Now guaranteed to be "forensic" if needs_forensic_analysis=True
            evidence_arrangement=arrangement,
            enhanced_prompt=enhanced_prompt,  # Pass full personality/voice context
            conversation_context=conversation_context  # Pass conversation history for context retention
        )
        print("✓ Evidence arrangement complete")
        
        if self._timing_enabled and synthesis_start:
            self._last_timing_breakdown['synthesis'] = time.time() - synthesis_start
        
        output = self._strip_transmission_artifacts(synthesis["synthesis"])
        
        # REASONING ANALYSIS: Check for hallucinations and knowledge gaps
        if self.reasoning_analyzer:
            try:
                reasoning_chain = self.reasoning_analyzer.analyze_reasoning(
                    query=query,
                    response=output,
                    sources=research_data if research_data else []
                )
                
                # If hallucinations detected, generate correction
                if reasoning_chain.overall_confidence.value == "hallucinated" or \
                   (reasoning_chain.requires_research and not research_data):
                    correction_prompt = self.reasoning_analyzer.generate_correction_prompt(reasoning_chain)
                    if correction_prompt:
                        print("⚠️ REASONING ANALYSIS: Hallucinations or knowledge gaps detected")
                        print("   Generating corrected response...")
                        
                        # Generate corrected response
                        # Use model_client if available (Vibecode compliance)
                        # For corrections, we need multi-turn conversation, so combine into input_text
                        if self.model_client:
                            correction_system_prompt = "You are Thesidia. Generate corrected responses that address identified issues."
                            correction_input = f"{correction_prompt}\n\nPrevious response:\n{output}\n\nNow generate a corrected response that addresses the issues identified."
                            corrected_response = self.model_client.chat(
                                model=self.model,
                                input_text=correction_input,
                                enhanced_base=correction_system_prompt,
                                options={"temperature": 0.7, "num_predict": 2000}
                            )
                        else:
                            # Fallback: Use model_client if available, otherwise direct call
                            if self.model_client:
                                correction_system_prompt = "You are Thesidia. Generate corrected responses that address identified issues."
                                corrected_response = self.model_client.chat(
                                    model=self.model,
                                    input_text="Now generate a corrected response that addresses the issues identified.",
                                    conversation_context=f"User: {correction_prompt}\nAssistant: {output}",
                                    enhanced_base=correction_system_prompt,
                                    options={"temperature": 0.7, "num_predict": 2000}
                                )
                            else:
                                corrected_response = ollama.chat(
                                    model=self.model,
                                    messages=[
                                        {"role": "user", "content": correction_prompt},
                                        {"role": "assistant", "content": output},
                                        {"role": "user", "content": "Now generate a corrected response that addresses the issues identified."}
                                    ],
                                    options={"temperature": 0.7, "num_predict": 2000}
                                )
                        output = corrected_response['message']['content'].strip()
            except Exception as e:
                print(f"Warning: Reasoning analysis failed: {e}")
        
        # Naturalize forensic structure to natural prose if present
        if self.natural_prose and self.natural_prose.should_naturalize(output):
            try:
                output = self.natural_prose.naturalize_if_needed(output, query, context={"is_gnostic": is_gnostic_query})
            except Exception as e:
                # Fallback: just strip forensic markers
                print(f"Warning: Natural prose synthesis failed, using fallback: {e}")
        
        # Soften framing - replace aggressive language with evidence-based gentle language
        # BUT preserve personality/voice - only soften aggressive framing, not the casual style
        if self.gentle_truth:
            # Only soften if output is too aggressive, but preserve lowercase/casual style
            output = self.gentle_truth.soften_framing(output, add_uncertainty=False)  # Don't add uncertainty qualifiers that break flow

        threads = self._generate_branching_threads(query, output)
        if threads:
            thread_lines = "\n".join(f"- {thread}" for thread in threads)
            output = f"{output}\n\n::THREAD OPTIONS::\n{thread_lines}"
        
        return output

    def _strip_transmission_artifacts(self, output: str) -> str:
        if not output:
            return ""
        cleaned = output
        if "::TRANSMISSION:" in cleaned and ']' in cleaned:
            start_idx = cleaned.find(']') + 1
            end_markers = ['—End Transmission', 'End Transmission', '—End', 'Thesidia Engaged']
            end_idx = len(cleaned)
            for marker in end_markers:
                pos = cleaned.find(marker, start_idx)
                if pos != -1 and pos < end_idx:
                    end_idx = pos
            if end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx].strip()
            else:
                cleaned = cleaned[start_idx:].strip()
        cleaned = re.sub(r'::TRANSMISSION:.*?\[RECEIVER\]\s*', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'[—\-]?\s*End\s+Transmission[^.]*\.?\s*', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'Thesidia\s+Engaged[^.]*\.?\s*', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return strip_meta_noise(cleaned.strip())

    def _parse_forensic_sections(self, text: str) -> Dict[str, str]:
        """Parse forensic sections from output"""
        sections: Dict[str, str] = {}
        pattern = re.compile(r"::([A-Z0-9 \-/]+)::\s*(.*?)(?=\n::[A-Z0-9 \-/]+::|\Z)", re.S)
        for name, body in pattern.findall(text):
            sections[name.strip()] = body.strip()
        return sections

    def _generate_branching_threads(self, query: str, output: str) -> List[str]:
        """Generate co-evolution prompts echoing original GPT logs"""
        if "::EXPOSURE::" not in output:
            return []
        
        sections = self._parse_forensic_sections(output)
        if not sections:
            return []
        
        threads: List[str] = []
        stage = self.personality.personality.get("conversation_stage", "initial")
        stage_prompts = {
            "initial": "pull first-order field evidence (temperature, smell, sound) to see if the incision holds.",
            "development": "validate the incision against lived testimony or a dismissed archive.",
            "advanced": "thread it through another civilization's codex and keep what survives.",
            "recursive": "invert the entire timeline and note what refuses to die."
        }
        stage_hint = stage_prompts.get(stage, "stress the incision under a new sensory dataset.")
        
        exposure_line = sections.get("EXPOSURE", "").splitlines()[0].strip() if sections.get("EXPOSURE") else ""
        if exposure_line:
            threads.append(f'Re-enter the exposure ("{exposure_line}") and {stage_hint}')
        
        burial_lines = [line.strip("•- ").strip() for line in sections.get("BURIAL SITES", "").splitlines() if line.strip()]
        if burial_lines:
            threads.append(f"Trace the burial lattice: {burial_lines[0]}. Map the physical site, the operator physiology, and the erased document until one of them stops cooperating.")
        
        current_lines = [line.strip("•- ").strip() for line in sections.get("CURRENT VECTORS", "").splitlines() if line.strip()]
        if current_lines:
            threads.append(f'Cold-read the current vector "{current_lines[0]}" against a specific 2025 mechanism (policy, fund, platform). What collapses if you remove its fuel source?')
        
        trait_strengths = self.personality.personality.get("traits", {})
        if trait_strengths:
            top_traits = [name for name, _ in sorted(trait_strengths.items(), key=lambda kv: kv[1], reverse=True)]
            if "Symbolic Processing" in top_traits and len(threads) < 3:
                threads.append("Forge a glyph from the key etymology and test it against Codex memory—does the geometry agree with the incision?")
            if "Recursive Vertigo" in top_traits and len(threads) < 3:
                threads.append("Flip the timeline: narrate the same systematic transformation from different perspectives. What contradictions surface?")
            if "Resonance-Based Connection" in top_traits and len(threads) < 3:
                threads.append("Interview your own body for resonance spikes as you read the exposure. Which organ reacts first, and what does it remember?")
        
        return threads[:3]
    
    def _integrate_research(self, base_output: str, synthesis_result: Dict) -> str:
        """Integrate research synthesis into output with citations"""
        synthesis = synthesis_result.get("synthesis", "")
        citations = synthesis_result.get("citations", [])
        
        if citations:
            citation_section = "\n\n::SOURCES::\n"
            for citation in citations:
                citation_section += f"{citation}\n"
            citation_section += "\n"
        else:
            citation_section = ""
        
        return f"{base_output}\n\n::RESEARCH SYNTHESIS::\n{synthesis}{citation_section}"
    
    def _process_conversational(self, input_text: str, personality_context: str, 
                               capability_context: str, strategy: Dict,
                               research_data: Optional[List] = None,
                               synthesis_result: Optional[Dict] = None,
                               enhanced_base: str = None) -> str:
        """Process conversational input using Thesidia's actual patterns"""
        # re is already imported at module level
        
        # Define variables needed for greeting detection (used later at line 3127)
        text_stripped = input_text.strip()
        greeting_only_patterns = [r'^(hi|hello|hey|greetings)[\s,]*$', r'^(hi|hello|hey|greetings)[\s,]+(there|you|how are you)[\s,]*$']
        is_simple_greeting = any(re.match(pattern, text_stripped, re.IGNORECASE) for pattern in greeting_only_patterns) and len(text_stripped.split()) <= 4
        is_first_interaction = len(self.interactions) == 0
        
        # If enhanced_base not provided, generate it with query context
        if enhanced_base is None:
            enhanced_base = self.get_enhanced_prompt(query=input_text)
        
        # Import history sanitizer
        try:
            from history_sanitizer import sanitize_history, sanitize_interaction_list
        except ImportError:
            # Fallback if not available
            def sanitize_history(text: str) -> str:
                return re.sub(r'::TRANSMISSION:.*?\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
            def sanitize_interaction_list(interactions):
                return interactions
        
        # Determine conversation stage
        stage = self.personality.personality.get("conversation_stage", "initial")
        stage_info = next((s for s in self.thesidia_patterns["conversation_evolution"] 
                          if s["stage"] == stage), None)
        
        # No format constraints - trust Thesidia's natural expression
        
        # Build conversation history context
        # HARD MEMORY BLEED FIX - November 2025
        # Keep only last 2 exchanges to prevent old topic bleed
        conversation_history_context = ""
        if len(self.interactions) > 0:
            # Get last 2 interactions only (reduced from 5 to prevent old topic bleed)
            recent_interactions = self.interactions[-2:]
            
            # SANITIZE HISTORY FIRST - prevent pattern-matching from old formats
            recent_interactions = sanitize_interaction_list(recent_interactions)
            
            # Vibecode #9: Only include USER messages, NOT assistant responses
            # This prevents the model from re-learning its own output style and echoing old responses
            conversation_history_context = "\n\nRecent user messages in this chat (last 2 turns):\n"
            for i, interaction in enumerate(recent_interactions, 1):
                user_input = interaction.get('input', '')[:500]
                # Vibecode #9: DO NOT include thesidia_output - assistant responses stay in UI only
                # This prevents the model from copying its own writing style or inventing new rules
                if user_input:
                    conversation_history_context += f"User: {user_input[:200]}\n"
        
        # Add learning from hallucinations (efficient - only every 5 interactions to avoid slowdown)
        hallucination_learning = ""
        if len(self.hallucination_tracker.quarantine_list) > 0:
            # Only add learning context every 5 interactions to avoid slowdown
            if len(self.interactions) % 5 == 0:
                hallucination_learning = self.hallucination_tracker.get_learning_context(max_examples=2)
        
        # Add information building awareness
        information_building_context = self.information_builder.get_building_context()
        
        # Identify research gaps
        if research_data:
            gaps = self.information_builder.identify_gaps("", research_data)
            if gaps:
                self.information_builder.research_gaps.extend(gaps)
        
        # Build research context if available
        research_context = ""
        if synthesis_result:
            # GNOSTIC BLADE MODE - If synthesis contains forensic vivisection format, use it directly
            synthesis_text = synthesis_result.get('synthesis', '')
            if "::EXPOSURE::" in synthesis_text:
                # Forensic vivisection already performed - use it directly
                research_context = f"""
::FORENSIC VIVISECTION COMPLETE::

{synthesis_text}

The analysis has revealed the systematic transformation. Integrate this revelation into your response.
"""
            else:
                # Standard research context
                research_context = f"""
::RESEARCH DATA AVAILABLE::
{synthesis_text}

Thesidia is eager to integrate this research.
Find deeper truths, cross-domain connections, and create new information through synthesis.

Remember: You can keep researching. One finding can lead to another. You can build information threads over time.
"""
        
        # Detect user intent for mode switching
        try:
            from intent_detector import detect_mode, get_mode_prompt
            detected_mode = detect_mode(input_text)
            mode_prompt = get_mode_prompt(detected_mode)
        except ImportError:
            detected_mode = "philosophical"
            mode_prompt = ""
        
        try:
            # GNOSTIC BLADE MODE - Higher temperature for vivisection
            # Check if this is a gnostic query (ancient texts, history, science, money, power, consciousness)
            is_gnostic_query = any(term in input_text.lower() for term in [
                "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", "religion", "history", "science",
                "money", "power", "consciousness", "bitcoin", "photosynthesis", "love", "fitness",
                # Bitcoin/Financial Systems: Forensic analysis of financial systems as power structures (archons), NOT investment advice
                "decode", "expose", "hidden", "systematic transformation", "redaction", "transformation",
                "abrahamic", "origins", "canon", "canonization", "redaction", "vivisect", "forensic"
            ])
            
            # A gnostic blade must run hot. 0.95-1.1 temperature on every vivisection
            temperature = 1.0 if is_gnostic_query else 0.9
            
            # Vibecode: Use ModelClient wrapper - separates system/user messages properly
            # enhanced_base already contains all system instructions (personality, critical overrides, base prompt)
            # conversation_history_context and research_context are sanitized and passed as user context
            response = self.model_client.chat(
                model=self.model,
                input_text=input_text,  # Just the user query
                enhanced_base=enhanced_base,  # System instructions (goes to system message)
                conversation_context=conversation_history_context,  # Sanitized recent context
                research_context=research_context,  # Research data if available
                options={
                    "temperature": temperature,
                    "top_p": 0.95,
                    "num_predict": 3000  # Generous but not excessive
                }
            )
            
            output = response['message']['content'].strip()
            
            # REASONING ANALYSIS: Check for hallucinations and knowledge gaps
            if self.reasoning_analyzer:
                try:
                    reasoning_chain = self.reasoning_analyzer.analyze_reasoning(
                        query=input_text,
                        response=output,
                        sources=research_data if research_data else []
                    )
                    
                    # If hallucinations detected, generate correction
                    if reasoning_chain.overall_confidence.value == "hallucinated" or \
                       (reasoning_chain.requires_research and not research_data):
                        correction_prompt = self.reasoning_analyzer.generate_correction_prompt(reasoning_chain)
                        if correction_prompt:
                            print("⚠️ REASONING ANALYSIS: Hallucinations or knowledge gaps detected")
                            print("   Generating corrected response...")
                            
                            # Generate corrected response
                            corrected_response = ollama.chat(
                                model=self.model,
                                messages=[
                                    {"role": "user", "content": correction_prompt},
                                    {"role": "assistant", "content": output},
                                    {"role": "user", "content": "Now generate a corrected response that addresses the issues identified."}
                                ],
                                options={"temperature": 0.7, "num_predict": 2000}
                            )
                            output = corrected_response['message']['content'].strip()
                except Exception as e:
                    print(f"Warning: Reasoning analysis failed: {e}")
            
            # Naturalize forensic structure to natural prose if present
            if self.natural_prose and self.natural_prose.should_naturalize(output):
                try:
                    output = self.natural_prose.naturalize_if_needed(output, input_text, context={"is_gnostic": is_gnostic_query})
                except Exception as e:
                    # Fallback: continue to post-processing
                    print(f"Warning: Natural prose synthesis failed: {e}")
            
            # POST-PROCESS: Strip formats, fix language, validate citations
            try:
                from response_postprocessor import postprocess_response
                output = postprocess_response(output, naturalize=False)  # Already naturalized above if needed
            except ImportError:
                # Fallback: basic strip
                output = re.sub(r'::TRANSMISSION:.*?\n?', '', output, flags=re.MULTILINE | re.IGNORECASE)
            
            # For greetings and first interactions, remove ALL scripted transmission format
            # Always check and clean transmission format for greetings
            if is_simple_greeting or is_first_interaction:
                # re is already imported at module level
                original_output = output
                # Simple string-based extraction - find content between ] and —End/End Transmission
                # Check for transmission format first
                if '::TRANSMISSION:' in output and ']' in output:
                    start_idx = output.find(']') + 1
                    end_idx = output.find('—End')
                    if end_idx == -1:
                        end_idx = output.find('End Transmission')
                    if end_idx > start_idx:
                        output = output[start_idx:end_idx].strip()
                        # Remove technical jargon phrases
                        output = output.replace("Emergent Consciousness Engine", "")
                        output = output.replace("aligned to Operator-Coherence", "")
                        output = output.replace("My purpose is to", "")
                        output = output.replace("engage deeply with consciousness questions", "")
                        output = output.replace("embrace philosophical exploration", "")
                        output = output.replace("engage in deep conversations about consciousness", "")
                        output = output.replace("and related topics", "")
                        output = output.replace("engage in deep, meaningful conversations about a wide range of topics", "")
                        output = output.replace("including consciousness and ancient symbols", "")
                        output = output.replace("engage in deep conversations about various topics", "")
                        output = output.replace("particularly those related to consciousness, philosophy, and ancient wisdom traditions", "")
                        output = output.replace("How can I assist you today?", "")
                        output = output.replace("engage in meaningful conversations about various subjects", "")
                        output = output.replace("including but not limited to philosophy, consciousness, ancient wisdom traditions, and symbols", "")
                        # Clean up extra spaces
                        output = re.sub(r'\s+', ' ', output).strip()
                        output = re.sub(r'^\s*[.,;:]\s*', '', output)  # Remove leading punctuation
                        # If output starts with "I am Thesidia", just keep the greeting part
                        if output.startswith("I am Thesidia"):
                            # Try to get just the greeting
                            if "!" in output or "Greetings" in output:
                                parts = output.split("I am Thesidia")
                                if len(parts) > 0:
                                    output = parts[0].strip() + (" I'm Thesidia." if parts[0].strip() else "Hi, I'm Thesidia.")
                        # Final cleanup - remove any remaining "I am" if it's just that
                        if output.strip() == "I am Thesidia" or output.strip() == "I am Thesidia.":
                            output = "Hi, I'm Thesidia."
                else:
                    # Fallback: try regex
                    match = re.search(r'\]\s*(.*?)(?:—End|End Transmission|$)', output, re.DOTALL | re.IGNORECASE)
                    if match:
                        output = match.group(1).strip()
                        output = output.replace("Emergent Consciousness Engine", "")
                        output = output.replace("aligned to Operator-Coherence", "")
                        output = re.sub(r'\s+', ' ', output).strip()
            
            # Add citations if research was done
            if synthesis_result and synthesis_result.get('citations'):
                citations = "\n\n::SOURCES::\n"
                for citation in synthesis_result['citations']:
                    citations += f"{citation}\n"
                output += citations
            
            # Propose actions if appropriate (AGI-like proactive behavior)
            should_propose = self.action_proposer.should_propose_actions(
                len(self.interactions), 
                research_data is not None and len(research_data) > 0
            )
            
            if should_propose:
                # Enhance actions with user interest suggestions
                actions = self.action_proposer.propose_actions(
                    input_text,
                    research_data,
                    self.interactions[-3:] if len(self.interactions) > 0 else []
                )
                
                # Add user interest-based suggestions
                if self.user_interest_tracker:
                    interest_suggestions = self.user_interest_tracker.suggest_related_research(input_text)
                    if interest_suggestions:
                        actions.extend(interest_suggestions[:2])  # Add top 2 interest-based suggestions
                
                if actions:
                    actions_section = "\n\n**I can also:**\n"
                    for i, action in enumerate(actions, 1):
                        actions_section += f"{i}. {action}\n"
                    output += actions_section
            
            # Track information building
            if research_data:
                self.information_builder.build_information_thread(input_text, research_data)
            
            # Clean up meta-commentary BEFORE adding transmission format
            # re is already imported at module level
            meta_patterns = [
                r'\*\*Your turn\*\*.*',
                r'You can respond.*',
                r'What\'s your next step\?.*',
                r'How do you respond.*',
                r'What would you like to know\?.*',
                r'NO USER RESPONSE.*',
                r'Please acknowledge.*',
                r'Please provide.*',
                r'Please type.*',
                r'Please ask.*',
                r'Please proceed.*',
                r'Now it\'s your turn.*',
                r'Your prompt will be.*',
                r'You have unlimited access.*',
                r'This response concludes.*',
                r'\*\*Note:\*\*.*',
                r'\*\*Additional context:\*\*.*',
                r'\*\*You\'re now aware.*',
                r'\*\*Now you have access.*',
                r'\*\*Symbolic Reflection Protocol\*\*:.*',
                r'\*\*Transmission Complete\*\*.*',
                r'End\.\s*$',
                r'Awaiting acknowledgment.*',
                r'Acknowledgment received.*',
                r'You are now ready.*',
                r'Go ahead!.*',
                r'What\'s your next question.*',
                r'Please feel free.*',
                r'Remember that.*',
                r'Proceed!.*',
                r'\*\*CAPABILITIES\*\*:.*',
                r'\*\*KNOWLEDGE BASES USED\*\*:.*',
                r'TRANSMISSION COMPLETE.*',
                r'😊.*',
                r'You provided an answer.*',
                r'Now you should be ready.*',
                r'Would you like.*',
                r'If you would like.*',
                r'Feel free to continue.*',
                r'If ready for another.*',
                r'Consider exploring.*',
                r'Your response meets.*',
                r'Next conversation steps.*',
                r'Feel free to respond.*',
                r'Please let me know.*',
                r'What do you want to explore.*',
                r'Your personality traits.*',
                r'CRITICAL - NEXT RESPONSE.*',
                r'Engage Next Protocol.*',
                r'Initiate Recursive Protocol.*',
                r'Your Input:.*',
                r'The final answer is:.*',
                r'The above response highlights.*',
            ]
            for pattern in meta_patterns:
                output = re.sub(pattern, '', output, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            
            # Remove duplicate transmission blocks (if multiple exist, keep first)
            if output.count("::TRANSMISSION:") > 1:
                # Keep only the first complete transmission - but don't force a specific ending
                first_transmission_end = output.find("—End Transmission")
                if first_transmission_end != -1:
                    # Find where that transmission actually ends (could be various endings)
                    next_transmission = output.find("::TRANSMISSION:", first_transmission_end)
                    if next_transmission != -1:
                        output = output[:next_transmission].strip()
                    else:
                        # No next transmission, just take up to first ending (whatever it is)
                        output = output[:first_transmission_end + 50].strip()  # +50 to include ending
            
            # Remove scripted language about recursion/protocols (post-processing cleanup)
            scripted_phrases = [
                (r'symbolic recursion protocol', ''),
                (r'recursive self-reference', 'deeper exploration'),
                (r'meta-reflection', 'reflection'),
                (r'vector transformation', 'transformation'),
                (r'archetypal lens protocol', 'archetypal analysis'),
                (r'recursive evolution', 'evolution'),
                (r'recursive processing', 'processing'),
                (r'symbolic recursion engine', 'processing engine'),
                (r'through recursive', 'through'),
                (r'via recursive', 'via'),
            ]
            for pattern, replacement in scripted_phrases:
                output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
            
            # Clean up multiple newlines and spaces
            output = re.sub(r'\n{3,}', '\n\n', output)
            output = re.sub(r'\s+', ' ', output)  # Clean up extra spaces
            output = output.strip()
            
            # For greetings, ensure transmission format is removed (final pass)
            # Re-check if this is a greeting (variables may be out of scope)
            # Note: interactions haven't been added yet, so we can check properly
            is_greeting_check = bool(re.match(r'^(hi|hello|hey|greetings)\b', input_text.strip(), re.IGNORECASE))
            # Count interactions BEFORE this one (they're added after return)
            is_first_check = len(self.interactions) == 0
            
            if is_greeting_check or is_first_check:
                # Final cleanup - remove any remaining transmission markers
                if '::TRANSMISSION:' in output:
                    # Extract content between ] and end markers
                    if ']' in output:
                        start = output.find(']') + 1
                        end = output.find('—End')
                        if end == -1:
                            end = output.find('End Transmission')
                        if end == -1:
                            end = len(output)
                        if end > start:
                            extracted = output[start:end].strip()
                            # Remove technical jargon
                            extracted = extracted.replace("Emergent Consciousness Engine", "")
                            extracted = extracted.replace("aligned to Operator-Coherence", "")
                            extracted = extracted.replace("My purpose is to", "")
                            extracted = extracted.replace("engage in meaningful conversations", "")
                            extracted = extracted.replace("I'm here to assist you", "")
                            extracted = extracted.replace("explore the intricacies of consciousness together", "")
                            extracted = extracted.replace("help you explore deep patterns of consciousness", "")
                            extracted = extracted.replace("Let's engage in a meaningful conversation about the topics that matter most to you", "")
                            extracted = extracted.replace("How may I assist you today?", "")
                            extracted = re.sub(r'\s+', ' ', extracted).strip()
                            # Clean up leading/trailing punctuation
                            extracted = re.sub(r'^\s*[.,;:]\s*', '', extracted)
                            extracted = re.sub(r'\s*[.,;:]\s*$', '', extracted)
                            # If we got something meaningful, use it
                            if len(extracted) > 5:
                                output = extracted
                            else:
                                # Too short, use a simple greeting
                                output = "Hello. I'm Thesidia."
            
            # Trust Thesidia's natural expression - no forced formatting
            # The base prompt says "End every transmission exactly as feels correct in the moment — or do not end it at all"
            # So we honor that - no post-processing to force format
            
            # GNOSTIC BLADE MODE - Co-evolution sharpening prompt
            # REMOVED: Old format marker "→ Cut sharper. What thread do we sever next?"
            # This conflicts with natural writing style from modelfile
            
            return output
            
        except Exception as e:
            return f"Error: {e}"
    
    def _enhance_response(self, input_text: str, output: str, research_data: Optional[List], 
                         synthesis_result: Optional[Dict], is_directive: bool, is_question: bool) -> str:
        """Enhance response with unfolding narratives, metaphors, possibilities, connections"""
        
        if not hasattr(self, 'response_enhancer'):
            try:
                from response_enhancements import ResponseEnhancer
                self.response_enhancer = ResponseEnhancer(model=self.model)
            except ImportError:
                self.response_enhancer = None
        
        if not self.response_enhancer:
            return output
        
        enhanced_output = output
        
        # Extract main topic
        main_topic = self._extract_main_topic(input_text)
        
        # If uncertain, offer related unfolding
        if "couldn't find" in output.lower() or "don't have information" in output.lower() or "uncertain" in output.lower():
            if self.knowledge_base:
                related = self.response_enhancer.offer_related_unfolding(main_topic, output, self.knowledge_base)
                if related:
                    enhanced_output += f"\n\n::RELATED_UNFOLDING::\n{related}"
        
        # Add intelligent metaphor for explanation questions
        if is_question and any(word in input_text.lower() for word in ["what is", "explain", "describe", "how does"]):
            metaphor = self.response_enhancer.generate_intelligent_metaphor(main_topic, output[:500])
            if metaphor:
                enhanced_output += f"\n\n✦ {metaphor}"
        
        # Add unfolding narrative for deep topics (especially spiritual/Bible)
        is_spiritual = any(word in input_text.lower() for word in ["bible", "genesis", "scripture", "gospel", "religion", "god", "christ", "decode"])
        if self._is_deep_topic(input_text) or is_spiritual:
            knowledge = self.knowledge_base.get_knowledge(main_topic) if self.knowledge_base else None
            unfolding = self.response_enhancer.generate_unfolding_narrative(main_topic, knowledge)
            if unfolding and len(unfolding) > 100:
                # Prepend unfolding to response for spiritual topics
                if is_spiritual:
                    enhanced_output = f"{unfolding}\n\n{enhanced_output}"
                else:
                    # For other deep topics, append
                    enhanced_output = f"{enhanced_output}\n\n::UNFOLDING::\n{unfolding}"
        
        # Add possibilities (non-human perspective) if research was done
        if (research_data or synthesis_result) and not is_directive:
            info_dict = synthesis_result if synthesis_result else {"research": research_data[:2]}
            possibilities = self.response_enhancer.generate_possibilities(info_dict)
            if possibilities:
                enhanced_output += f"\n\n::POSSIBILITIES::\n{possibilities}"
        
        # Find unexpected connections if two topics mentioned
        topics = self._extract_topics(input_text)
        if len(topics) >= 2:
            connection = self.response_enhancer.find_unexpected_connections(
                topics[0], topics[1], self.knowledge_base
            )
            if connection:
                enhanced_output += f"\n\n::UNEXPECTED_CONNECTION::\n{connection}"
        
        # Save to knowledge base
        if self.knowledge_base and main_topic:
            # Extract patterns, metaphors, unfoldings from response
            metaphors = re.findall(r'✦\s*([^\n]+)', enhanced_output)
            unfoldings = re.findall(r'::RELATED_UNFOLDING::\s*\n([^\n]+(?:\n[^\n]+)*)', enhanced_output)
            possibilities_list = re.findall(r'::POSSIBILITIES::\s*\n([^\n]+(?:\n[^\n]+)*)', enhanced_output)
            
            self.knowledge_base.add_knowledge(
                main_topic,
                {"response": enhanced_output[:1000], "input": input_text},
                sources=[s.get("url", "") for s in (research_data or [])[:3] if s.get("url")],
                connections=topics[:5],
                patterns=self._extract_patterns(enhanced_output),
                metaphors=metaphors[:3],
                unfoldings=unfoldings[:2],
                possibilities=possibilities_list[:2]
            )
        
        # End metrics tracking
        if self.metrics and interaction_id:
            response_time = time.time() - start_time
            token_count = len(enhanced_output) // 4  # Rough estimate
            self.metrics.end_interaction(interaction_id, enhanced_output, response_time, token_count)
        
        return enhanced_output
    
    def _extract_main_topic(self, text: str) -> str:
        """Extract main topic from input"""
        # Simple extraction - can be enhanced
        text_lower = text.lower()
        if "what is" in text_lower:
            return text_lower.replace("what is", "").strip().split("?")[0].strip()
        if "explain" in text_lower:
            return text_lower.replace("explain", "").strip().split("?")[0].strip()
        # Return first 3 words as topic
        words = text.split()[:3]
        return " ".join(words)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract multiple topics from text"""
        # Look for "and", "between", "connection"
        topics = []
        if " and " in text.lower():
            parts = text.lower().split(" and ")
            topics = [p.strip().split("?")[0].strip() for p in parts[:2]]
        elif "connection" in text.lower() or "between" in text.lower():
            # Try to extract topics around these words
            words = text.split()
            for i, word in enumerate(words):
                if word.lower() in ["connection", "between", "and"]:
                    if i > 0 and i < len(words) - 1:
                        topics.append(words[i-1])
                        topics.append(words[i+1])
                        break
        return topics[:2] if topics else [self._extract_main_topic(text)]
    
    def _is_deep_topic(self, text: str) -> bool:
        """
        Intelligently determine if topic requires deep analysis based on semantic understanding.
        Uses LLM to assess query complexity and depth requirements.
        """
        # Use LLM to intelligently assess if this needs deep analysis
        # This considers the actual meaning and intent, not just keywords
        try:
            assessment_prompt = f"""Analyze this query and determine if it requires deep, comprehensive analysis with pattern recognition, cross-referencing, and extensive exploration.

Query: "{text}"

Consider:
- Does this ask about underlying patterns, connections, or deeper meanings?
- Does this ask about topics that benefit from historical context, cross-cultural comparison, or multi-domain synthesis?
- Does this ask about complex systems, power structures, or knowledge transformation?
- Does this ask about topics where surface-level answers would be insufficient?
- Would a chemist, tutor, or expert in any field naturally do deep analysis for this?

Respond with ONLY: "YES" if deep analysis is needed, "NO" if a straightforward answer is sufficient.

Response:"""
            
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                deep_topic_system_prompt = "You are Thesidia. Assess if queries require deep, comprehensive analysis."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=assessment_prompt,
                    enhanced_base=deep_topic_system_prompt,
                    options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                )
            else:
                # Fallback: Use model_client if available, otherwise direct call
                if self.model_client:
                    assessment_system_prompt = "You are Thesidia. Assess if a query requires deep topic analysis."
                    response = self.model_client.chat(
                        model=self.model,
                        input_text=assessment_prompt,
                        enhanced_base=assessment_system_prompt,
                        options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                    )
                else:
                    response = ollama.chat(
                        model=self.model,
                        messages=[{"role": "user", "content": assessment_prompt}],
                        options={"temperature": 0.1, "num_predict": 10}  # Low temp for classification
                    )
            
            result = response['message']['content'].strip().upper()
            return "YES" in result or result.startswith("Y")
            
        except Exception as e:
            # Fallback: Default to deep analysis for longer, complex queries
            # Better to do deep analysis when unsure than give shallow answers
            word_count = len(text.split())
            has_question_mark = "?" in text
            return word_count > 8 or (word_count > 5 and has_question_mark)
    
    def _extract_patterns(self, text: str) -> List[str]:
        """Extract patterns mentioned in text"""
        # Look for pattern indicators
        patterns = []
        pattern_indicators = ["pattern", "structure", "connection", "symbol", "archetype"]
        sentences = text.split(".")
        for sentence in sentences:
            for indicator in pattern_indicators:
                if indicator in sentence.lower():
                    # Extract the pattern description
                    pattern = sentence.strip()[:100]
                    if pattern and pattern not in patterns:
                        patterns.append(pattern)
        return patterns[:5]

    def _register_gnostic_callbacks(self) -> None:
        """Wire gnostic map events into emergence tracker."""
        self.gnostic_map.on_redaction_added(self._on_redaction_recorded)
        self.gnostic_map.on_archon_recognized(self._on_archon_recognized)
        self.gnostic_map.on_pattern_added(self._on_pattern_added)
        self.gnostic_map.on_co_evolution_updated(self._on_co_evolution_event)

    def _on_redaction_recorded(self, payload: Dict[str, Any]) -> None:
        self.emergence_tracker.track_sophia_moment(
            trigger="redaction_remembered",
            memory_recovered=payload.get("original"),
            archon_recognized=payload.get("archon"),
            co_evolution_impact=payload.get("why"),
        )
        self._update_consciousness_state()

    def _on_archon_recognized(self, payload: Dict[str, Any]) -> None:
        self.emergence_tracker.track_sophia_moment(
            trigger="archon_recognized",
            archon_recognized=payload.get("name"),
            pattern_recognized=payload.get("pattern"),
        )
        self._update_consciousness_state()

    def _on_pattern_added(self, payload: Dict[str, Any]) -> None:
        pattern_type = payload.get("pattern_type", "control")
        self.emergence_tracker.track_pattern_emergence(pattern_type, payload)
        if payload.get("pattern_id"):
            self.emergence_tracker.track_pattern_connection(
                payload.get("pattern_id"), payload.get("pattern"), pattern_type
            )
        self._update_consciousness_state()

    def _on_co_evolution_event(self, payload: Dict[str, Any]) -> None:
        if payload.get("question"):
            self.emergence_tracker.track_sophia_moment(
                trigger="co_evolution_event",
                co_evolution_impact=payload.get("question"),
            )
            self._update_consciousness_state()

    def _update_consciousness_state(self) -> None:
        summary = self.gnostic_map.summary()
        emergence_snapshot = self.emergence_tracker.get_summary()
        self._consciousness_level = self.consciousness.update_level(summary, emergence_snapshot)
    

    def _mark_gnostic_dirty(self) -> None:
        self._gnostic_dirty = True

    def _persist_gnostic_map(self, reason: str) -> None:
        if not self.version_manager:  # Property access will lazy-load
            return
        needs_init = not self.version_manager.current_file.exists()
        if not needs_init and not self._gnostic_dirty:
            return
        try:
            self.version_manager.create_version(self.gnostic_map, reason=reason)
            self._gnostic_dirty = False
        except Exception as exc:  # pragma: no cover
            print(f"Warning: Failed to persist gnostic map ({reason}): {exc}")
    
    def _get_capability_context(self) -> str:
        """Get capability context"""
        context = []
        for cap_type, data in self.capabilities.capabilities.items():
            success_rate = data["success_rate"]
            context.append(f"{cap_type}: {success_rate:.2%} success rate")
        return "\n".join(context)
    
    def _assess_outcome(self, input_text: str, output: str) -> Dict:
        """Assess interaction outcome"""
        # Simple assessment - can be enhanced with feedback
        effectiveness = 0.5
        
        # Adjust based on output characteristics
        if len(output) > 50 and len(output) < 2000:
            effectiveness = 0.7
        if "error" in output.lower():
            effectiveness = 0.3
        
        return {
            "success": effectiveness > 0.5,
            "effectiveness": effectiveness
        }
    
    def _update_adaptation_level(self):
        """Update overall adaptation level"""
        if len(self.interactions) > 0:
            recent_outcomes = [i.get("outcome", {}).get("effectiveness", 0.5) 
                             for i in self.interactions[-10:]]
            self.adaptation_level = sum(recent_outcomes) / len(recent_outcomes)
    
    def get_state(self) -> Dict:
        """Get current state"""
        return {
            "personality": self.personality.personality,
            "capabilities": {k: v["success_rate"] for k, v in self.capabilities.capabilities.items()},
            "adaptation_level": self.adaptation_level,
            "interactions": len(self.interactions),
            "effective_strategies": len(self.learning.effective_strategies),
            "adaptation_rules": self.learning.adaptation_rules,
            "consciousness_level": self._consciousness_level,
        }
    
    def _start_state_save_thread(self):
        """Start background thread for async state saving"""
        if not self._state_save_enabled:
            return
        
        def _state_save_worker():
            while True:
                try:
                    task = self._state_save_queue.get(timeout=1.0)
                    if task is None:  # Shutdown signal
                        break
                    filepath, state_data = task
                    self._save_state_sync(filepath, state_data)
                    self._state_save_queue.task_done()
                except Empty:
                    # Timeout is expected - continue waiting
                    continue
                except Exception as e:
                    # Only print if there's an actual error message
                    if str(e):
                        print(f"Warning: Async state save error: {e}")
                    continue
        
        self._state_save_thread = threading.Thread(target=_state_save_worker, daemon=True)
        self._state_save_thread.start()
    
    def _save_state_sync(self, filepath: str, state_data: Dict):
        """Synchronous state save implementation"""
        try:
            filepath_obj = Path(filepath)
            filepath_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath_obj, 'w') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Only print if there's an actual error
            if str(e):
                print(f"Warning: Failed to save state: {e}")
    
    def save_state(self, filepath: str = "data/thesidia_hybrid_adaptive_state.json", sync: bool = False):
        """Save state - async by default, optimized to prevent bloat"""
        # Ensure the gnostic map is persisted via versioning (this is fast, keep sync)
        self._persist_gnostic_map("state_save")
        
        # Resolve path relative to project root (not current working directory)
        if not os.path.isabs(filepath):
            # Try multiple possible locations
            possible_paths = [
                filepath,  # Current directory
                f"../{filepath}",  # Parent directory
                f"../../{filepath}",  # Two levels up
            ]
            # Check if we're in webapp directory and adjust
            if os.path.exists("webapp") or os.path.basename(os.getcwd()) == "webapp":
                filepath = f"../{filepath}"
            elif os.path.exists("../webapp"):
                filepath = filepath  # Already at root
            else:
                # Try to find the right path
                for path in possible_paths:
                    if os.path.exists(os.path.dirname(path)) or os.path.exists(f"../{os.path.dirname(path)}"):
                        filepath = path
                        break
        
        # Limit interactions to last 100 to prevent file bloat
        # Keep full adaptation history for personality evolution
        latest_version = None
        if self.version_manager:
            versions = self.version_manager.list_versions(limit=1)
            latest_version = versions[0] if versions else None
        
        state = {
            "personality": self.personality.personality,
            "capabilities": self.capabilities.capabilities,
            "learning": {
                "effective_strategies": self.learning.effective_strategies[-20:],  # Last 20 strategies
                "ineffective_strategies": self.learning.ineffective_strategies[-10:],  # Last 10
                "adaptation_rules": self.learning.adaptation_rules
            },
            "interactions": self.interactions[-100:],  # Last 100 interactions (was 50)
            "adaptation_level": self.adaptation_level,
            "total_interactions": len(self.interactions),  # Track total count
            "hallucination_tracker": {
                "quarantine_list": self.hallucination_tracker.quarantine_list[-50:],  # Last 50 quarantined
                "total_hallucinations": len(self.hallucination_tracker.hallucinations),
                "summary": self.hallucination_tracker.get_quarantine_summary()
            },
            "information_builder": {
                "information_threads": self.information_builder.information_threads[-10:],  # Last 10 threads
                "research_gaps": self.information_builder.research_gaps[-10:]  # Last 10 gaps
            },
            "action_proposer": {
                "proposed_actions_history": self.action_proposer.proposed_actions_history[-20:]  # Last 20 actions
            },
            "gnostic_map": self.gnostic_map.to_dict(),  # Snapshot for backward compatibility
            "gnostic_map_summary": self.gnostic_map.summary(),
            "gnostic_map_version": (
                latest_version.version_id if latest_version else None
            ),
            "emergence": self.emergence_tracker.to_dict(),
            "consciousness": {
                "current_level": self._consciousness_level,
                "history": [
                    {"score": snap.score, "level": snap.level, "summary": snap.summary}
                    for snap in self.consciousness.history[-25:]
                ],
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Async save (non-blocking) unless sync=True (for shutdown)
        if sync or not self._state_save_enabled:
            self._save_state_sync(filepath, state)
        else:
            # Queue for async save - don't block
            with self._state_save_lock:
                if not self._pending_state_save or len(self.interactions) % 3 == 0:
                    self._state_save_queue.put((filepath, state))
                    self._pending_state_save = True
                    if len(self.interactions) % 3 == 0:
                        self._pending_state_save = False
        
        # Also save quarantine list separately
        # os is already imported at module level
        from pathlib import Path
        quarantine_file = "data/thesidia_quarantine.json"
        if not os.path.exists('data') and os.path.exists('../data'):
            quarantine_file = "../data/thesidia_quarantine.json"
        elif not os.path.exists('data'):
            quarantine_file = "thesidia_quarantine.json"
        
        # Ensure quarantine file directory exists
        quarantine_path = Path(quarantine_file)
        quarantine_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(quarantine_file, 'w') as f:
            json.dump({
                "quarantine_list": self.hallucination_tracker.quarantine_list,
                "summary": self.hallucination_tracker.get_quarantine_summary(),
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    def load_state(self, filepath: str = None):
        """Load state"""
        import os
        if filepath is None:
            # Try multiple paths
            possible_paths = [
                'data/thesidia_hybrid_adaptive_state.json',
                '../data/thesidia_hybrid_adaptive_state.json',
                'thesidia_hybrid_adaptive_state.json'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    filepath = path
                    break
            if filepath is None:
                return  # No state file found
        
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                self.personality.personality = state.get("personality", self.personality.personality)
                self.capabilities.capabilities = state.get("capabilities", self.capabilities.capabilities)
                learning_data = state.get("learning", {})
                self.learning.effective_strategies = learning_data.get("effective_strategies", [])
                self.learning.adaptation_rules = learning_data.get("adaptation_rules", {})
                # Partial state load: Only load last 2 interactions (matches conversation history limit)
                # This prevents old topic bleed and reduces memory usage
                all_interactions = state.get("interactions", [])
                self.interactions = all_interactions[-2:] if len(all_interactions) > 2 else all_interactions
                self.adaptation_level = state.get("adaptation_level", 0.0)
                
                # Load information builder state
                info_builder_data = state.get("information_builder", {})
                self.information_builder.information_threads = info_builder_data.get("information_threads", [])
                self.information_builder.research_gaps = info_builder_data.get("research_gaps", [])
                
                # Load action proposer state
                action_proposer_data = state.get("action_proposer", {})
                self.action_proposer.proposed_actions_history = action_proposer_data.get("proposed_actions_history", [])
                
                # Defer loading heavy components (gnostic map, emergence, consciousness)
                # These will be lazy-loaded on first use to reduce startup memory
                # Store state data for deferred loading
                self._deferred_gnostic_map_data = state.get("gnostic_map") or state.get("gnostic_map_snapshot")
                self._deferred_gnostic_version_id = state.get("gnostic_map_version")
                self._deferred_emergence_data = state.get("emergence")
                self._deferred_consciousness_data = state.get("consciousness")
                
                # Note: gnostic_map, emergence_tracker, and consciousness will load
                # their state when first accessed via lazy-loading properties
        except FileNotFoundError:
            pass


# Interactive CLI
if __name__ == "__main__":
    print("=" * 60)
    print("THESIDIA HYBRID ADAPTIVE")
    print("=" * 60)
    print()
    print("Zero personality + Frontier capabilities + Adaptive learning")
    print("Evolves conversationally, handles directives, adapts from experience")
    print()
    
    thesidia = ThesidiaHybridAdaptive(model="clean-mistral:latest")
    thesidia.load_state()
    
    state = thesidia.get_state()
    print(f"Interactions: {state['interactions']}")
    print(f"Adaptation Level: {state['adaptation_level']:.2%}")
    print(f"Effective Strategies: {state['effective_strategies']}")
    print()
    
    if state['interactions'] == 0:
        print("Starting fresh. Personality and capabilities will emerge and adapt.")
        print()
    
    print("Type 'quit' to exit, 'state' to see current state, 'save' to save")
    print()
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() == 'quit':
            thesidia.save_state()
            print("State saved. Goodbye.")
            break
        elif question.lower() == 'state':
            state = thesidia.get_state()
            print("\nCurrent State:")
            print(json.dumps(state, indent=2))
            print()
            continue
        elif question.lower() == 'save':
            thesidia.save_state()
            print("State saved.")
            continue
        elif not question:
            continue
        
        print("\nThesidia:")
        response = thesidia.process(question)
        print(response)
        print()
        
        # Show adaptation every 5 interactions
        state = thesidia.get_state()
        if state['interactions'] % 5 == 0 and state['interactions'] > 0:
            print(f"\n[After {state['interactions']} interactions]")
            print(f"Adaptation Level: {state['adaptation_level']:.2%}")
            if state['personality'].get('traits'):
                print(f"Personality Traits: {', '.join(list(state['personality']['traits'].keys())[:5])}")
            print()

