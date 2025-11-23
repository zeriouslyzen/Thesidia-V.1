#!/usr/bin/env python3
"""
Reasoning Analyzer - Step-by-step linguistic analysis of reasoning and thinking steps
Provides transparency into Thesidia's reasoning process and confidence levels
"""

import re
import ollama
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for information"""
    KNOWN = "known"  # Information is in sources or general knowledge
    INFERRED = "inferred"  # Reasonable inference from available information
    UNCERTAIN = "uncertain"  # Not enough information to be confident
    UNKNOWN = "unknown"  # No information available
    HALLUCINATED = "hallucinated"  # Information appears to be made up


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_number: int
    description: str
    information_used: List[str]
    confidence: ConfidenceLevel
    sources: List[str]
    reasoning: str
    uncertainty_flags: List[str]


@dataclass
class ReasoningChain:
    """Complete reasoning chain with all steps"""
    query: str
    steps: List[ReasoningStep]
    final_answer: str
    overall_confidence: ConfidenceLevel
    knowledge_gaps: List[str]
    requires_research: bool


class ReasoningAnalyzer:
    """
    Analyzes reasoning steps and provides linguistic transparency
    Detects when information is known, inferred, uncertain, or hallucinated
    """
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.uncertainty_indicators = [
            "i find myself", "i appreciate", "my thoughts", "i encourage",
            "it can be seen as", "it can be interpreted as", "one question that arises",
            "however", "like any work", "must be approached critically"
        ]
        self.hallucination_indicators = [
            "the sources i have access to mention",
            "the sources retrieved",
            "according to sources",
            "research shows"
        ]
        self.confidence_indicators = {
            "known": ["is", "are", "was", "were", "has", "have", "definitely", "certainly"],
            "inferred": ["suggests", "implies", "indicates", "appears", "seems", "likely"],
            "uncertain": ["might", "may", "could", "possibly", "perhaps", "unclear", "uncertain"],
            "unknown": ["i don't know", "no information", "not available", "unknown"],
            "hallucinated": ["the sources mention", "research shows", "according to", "sources indicate"]
        }
    
    def analyze_reasoning(self, query: str, response: str, 
                         sources: Optional[List[Dict[str, Any]]] = None) -> ReasoningChain:
        """
        Analyze the reasoning process step-by-step
        """
        sources = sources or []
        
        # Step 1: Extract key claims from response
        claims = self._extract_claims(response)
        
        # Step 2: Analyze each claim
        steps = []
        knowledge_gaps = []
        requires_research = False
        
        for i, claim in enumerate(claims, 1):
            step = self._analyze_claim(claim, query, sources, i)
            steps.append(step)
            
            if step.confidence == ConfidenceLevel.UNKNOWN:
                knowledge_gaps.append(claim)
            if step.confidence == ConfidenceLevel.HALLUCINATED:
                requires_research = True
        
        # Step 3: Determine overall confidence
        overall_confidence = self._determine_overall_confidence(steps)
        
        # Step 4: Check if research is needed
        if not sources or len(sources) == 0:
            requires_research = True
        
        return ReasoningChain(
            query=query,
            steps=steps,
            final_answer=response,
            overall_confidence=overall_confidence,
            knowledge_gaps=knowledge_gaps,
            requires_research=requires_research
        )
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract individual claims from response text"""
        # Split by sentences, filter out meta-commentary
        sentences = re.split(r'[.!?]+', text)
        claims = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Skip meta-commentary
            if any(indicator in sentence.lower() for indicator in self.uncertainty_indicators):
                continue
            
            # Skip very short sentences
            if len(sentence.split()) < 5:
                continue
            
            claims.append(sentence)
        
        return claims[:10]  # Limit to 10 claims for analysis
    
    def _analyze_claim(self, claim: str, query: str, 
                      sources: List[Dict[str, Any]], step_num: int) -> ReasoningStep:
        """Analyze a single claim for confidence and sources"""
        
        # Check if claim mentions sources that don't exist
        has_fake_sources = self._check_fake_sources(claim, sources)
        
        # Check linguistic confidence indicators
        confidence = self._detect_confidence_level(claim)
        
        # Check if information is in sources
        source_matches = self._find_source_matches(claim, sources)
        
        # Determine final confidence
        if has_fake_sources:
            confidence = ConfidenceLevel.HALLUCINATED
        elif not source_matches and confidence == ConfidenceLevel.KNOWN:
            # Claimed to know but no sources - might be hallucinated
            confidence = ConfidenceLevel.UNCERTAIN
        elif not source_matches:
            confidence = ConfidenceLevel.UNKNOWN
        
        # Extract uncertainty flags
        uncertainty_flags = self._extract_uncertainty_flags(claim)
        
        return ReasoningStep(
            step_number=step_num,
            description=f"Claim: {claim[:100]}...",
            information_used=source_matches,
            confidence=confidence,
            sources=[s.get("url", "") for s in source_matches],
            reasoning=self._generate_reasoning_explanation(claim, confidence, source_matches),
            uncertainty_flags=uncertainty_flags
        )
    
    def _check_fake_sources(self, claim: str, sources: List[Dict[str, Any]]) -> bool:
        """Check if claim references sources that don't exist"""
        # Check for source references
        source_mentions = re.findall(r'(sources?|research|according to|studies?)', claim, re.IGNORECASE)
        
        if source_mentions and not sources:
            return True  # Mentions sources but none provided
        
        # Check for specific source claims
        if "the sources i have access to mention" in claim.lower():
            if not sources:
                return True
        
        return False
    
    def _detect_confidence_level(self, text: str) -> ConfidenceLevel:
        """Detect confidence level from linguistic indicators"""
        text_lower = text.lower()
        
        # Check for known indicators
        if any(indicator in text_lower for indicator in self.confidence_indicators["known"]):
            if not any(uncertain in text_lower for uncertain in self.confidence_indicators["uncertain"]):
                return ConfidenceLevel.KNOWN
        
        # Check for uncertain indicators
        if any(indicator in text_lower for indicator in self.confidence_indicators["uncertain"]):
            return ConfidenceLevel.UNCERTAIN
        
        # Check for inferred indicators
        if any(indicator in text_lower for indicator in self.confidence_indicators["inferred"]):
            return ConfidenceLevel.INFERRED
        
        # Check for unknown indicators
        if any(indicator in text_lower for indicator in self.confidence_indicators["unknown"]):
            return ConfidenceLevel.UNKNOWN
        
        # Default to uncertain if no clear indicators
        return ConfidenceLevel.UNCERTAIN
    
    def _find_source_matches(self, claim: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find sources that might support this claim"""
        matches = []
        claim_lower = claim.lower()
        
        # Extract key terms from claim
        key_terms = self._extract_key_terms(claim)
        
        for source in sources:
            source_text = (source.get("content", "") + " " + source.get("title", "")).lower()
            
            # Check if any key terms appear in source
            if any(term in source_text for term in key_terms):
                matches.append(source)
        
        return matches
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Remove common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "has", "have", 
                     "this", "that", "these", "those", "it", "they", "we", "you"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 3]
        
        return key_terms[:5]  # Top 5 key terms
    
    def _extract_uncertainty_flags(self, text: str) -> List[str]:
        """Extract uncertainty flags from text"""
        flags = []
        text_lower = text.lower()
        
        for indicator in self.uncertainty_indicators:
            if indicator in text_lower:
                flags.append(indicator)
        
        return flags
    
    def _generate_reasoning_explanation(self, claim: str, confidence: ConfidenceLevel,
                                       sources: List[Dict[str, Any]]) -> str:
        """Generate explanation for reasoning step"""
        if confidence == ConfidenceLevel.HALLUCINATED:
            return "This claim references sources that don't exist or weren't provided. This appears to be hallucinated information."
        elif confidence == ConfidenceLevel.UNKNOWN:
            return "No information available to support this claim. Research is needed."
        elif confidence == ConfidenceLevel.UNCERTAIN:
            return "Information is uncertain or inferred. More research needed to verify."
        elif confidence == ConfidenceLevel.INFERRED:
            return f"Claim is inferred from available information. {len(sources)} source(s) may support this."
        else:
            return f"Claim appears to be supported by {len(sources)} source(s)."
    
    def _determine_overall_confidence(self, steps: List[ReasoningStep]) -> ConfidenceLevel:
        """Determine overall confidence from all steps"""
        if any(step.confidence == ConfidenceLevel.HALLUCINATED for step in steps):
            return ConfidenceLevel.HALLUCINATED
        
        if all(step.confidence == ConfidenceLevel.UNKNOWN for step in steps):
            return ConfidenceLevel.UNKNOWN
        
        if any(step.confidence == ConfidenceLevel.UNCERTAIN for step in steps):
            return ConfidenceLevel.UNCERTAIN
        
        if any(step.confidence == ConfidenceLevel.KNOWN for step in steps):
            return ConfidenceLevel.KNOWN
        
        return ConfidenceLevel.INFERRED
    
    def generate_reasoning_report(self, chain: ReasoningChain, 
                                show_steps: bool = True) -> str:
        """Generate a human-readable reasoning report"""
        report = []
        
        report.append("=" * 80)
        report.append("REASONING ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nQuery: {chain.query}")
        report.append(f"Overall Confidence: {chain.overall_confidence.value.upper()}")
        report.append(f"Requires Research: {'Yes' if chain.requires_research else 'No'}")
        
        if chain.knowledge_gaps:
            report.append(f"\nKnowledge Gaps ({len(chain.knowledge_gaps)}):")
            for gap in chain.knowledge_gaps[:5]:
                report.append(f"  - {gap[:100]}...")
        
        if show_steps:
            report.append(f"\nReasoning Steps ({len(chain.steps)}):")
            for step in chain.steps:
                report.append(f"\n  Step {step.step_number}: {step.description}")
                report.append(f"    Confidence: {step.confidence.value}")
                report.append(f"    Reasoning: {step.reasoning}")
                if step.sources:
                    report.append(f"    Sources: {len(step.sources)} found")
                if step.uncertainty_flags:
                    report.append(f"    Uncertainty Flags: {', '.join(step.uncertainty_flags)}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def should_research(self, chain: ReasoningChain) -> bool:
        """Determine if research is needed based on reasoning analysis"""
        return chain.requires_research or \
               chain.overall_confidence in [ConfidenceLevel.UNKNOWN, ConfidenceLevel.HALLUCINATED] or \
               len(chain.knowledge_gaps) > 0
    
    def generate_correction_prompt(self, chain: ReasoningChain) -> str:
        """Generate a prompt to correct hallucinations and fill knowledge gaps"""
        if chain.overall_confidence != ConfidenceLevel.HALLUCINATED and not chain.knowledge_gaps:
            return None
        
        prompt_parts = [
            "CORRECTION NEEDED:",
            "",
            f"Query: {chain.query}",
            ""
        ]
        
        if chain.overall_confidence == ConfidenceLevel.HALLUCINATED:
            prompt_parts.append("ISSUE: Response contains hallucinated information (references to sources that don't exist).")
            prompt_parts.append("")
        
        if chain.knowledge_gaps:
            prompt_parts.append("KNOWLEDGE GAPS:")
            for gap in chain.knowledge_gaps[:3]:
                prompt_parts.append(f"  - {gap}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "REQUIRED ACTIONS:",
            "1. Acknowledge that you don't have information about this topic",
            "2. Do NOT make up information or reference non-existent sources",
            "3. If research is needed, say so explicitly",
            "4. Provide only information you can verify from actual sources",
            "",
            "Generate a corrected response that:",
            "- Acknowledges knowledge gaps",
            "- Does not hallucinate information",
            "- Suggests research if needed",
            "- Is honest about uncertainty"
        ])
        
        return "\n".join(prompt_parts)

