#!/usr/bin/env python3
"""
Skepticism Engine - Intuitive Skepticism
=========================================

Intuitive skepticism through pattern recognition - not hardcoded.
Detects control structures through pattern recognition.
"""

from __future__ import annotations

import ollama
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.model_client import ModelClient


class IntuitiveSkepticism:
    """Intuitive skepticism through pattern recognition - not hardcoded"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_client = model_client  # Optional centralized model client
        self.pattern_history = []  # Track patterns across sources
        self.contradiction_log = []  # Track contradictions
    
    def detect_control_patterns(self, content: str, url: str, previous_sources: List[Dict] = None) -> Dict[str, Any]:
        """Detect control structures through pattern recognition - intuitive, not hardcoded"""
        
        # Build context from previous sources for cross-reference
        context = ""
        if previous_sources:
            context = "\nPrevious sources analyzed:\n"
            for src in previous_sources[-3:]:  # Last 3 sources
                context += f"- {src.get('title', 'Unknown')}: {src.get('content', '')[:500]}\n"
        
        prompt = f"""
You are Thesidia, analyzing information through pattern recognition and symbolic processing.

Content to analyze:
URL: {url}
Content: {content[:2000]}

{context}

Analyze this through Thesidia's intuitive understanding:
1. **Pattern Recognition**: What patterns emerge? Do they match control structures you've seen?
2. **Symbolic Analysis**: What symbols are present? What do they functionally encode?
3. **Cross-Domain Patterns**: Do these patterns appear in other domains (ancient texts, mythology, modern systems)?
4. **Contradiction Detection**: Are there contradictions? What do they reveal?
5. **Narrative Structure**: What narrative is being constructed? What is it designed to do?
6. **Control Indicators**: Through pattern recognition, what control mechanisms are visible?

This is NOT about hardcoded rules. It's about:
- Recognizing patterns you've seen before
- Intuitive understanding through symbolic processing
- Cross-referencing with patterns from other domains
- Seeing what the patterns functionally encode

Respond with intuitive assessment, not hardcoded skepticism.
"""
        
        try:
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                analysis_system_prompt = "You are Thesidia, analyzing information through pattern recognition and symbolic processing."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=analysis_system_prompt,
                    options={"temperature": 0.7, "top_p": 0.95}
                )
            else:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.7, "top_p": 0.95}
                )
            
            analysis = response['message']['content']
            
            # Extract patterns
            patterns = self._extract_patterns(analysis)
            
            # Save patterns to history
            self.pattern_history.append({
                "patterns": patterns,
                "url": url,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "analysis": analysis,
                "patterns_detected": patterns,
                "skepticism_level": self._assess_skepticism(analysis, patterns),
                "control_indicators": self._detect_control_indicators(analysis),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "analysis": "",
                "patterns_detected": [],
                "skepticism_level": 0.5,
                "control_indicators": [],
                "error": str(e)
            }
    
    def _extract_patterns(self, analysis: str) -> List[str]:
        """Extract patterns mentioned in analysis"""
        patterns = []
        
        # Look for pattern mentions
        pattern_keywords = ["pattern", "structure", "symbol", "control", "narrative", "system"]
        for keyword in pattern_keywords:
            if keyword in analysis.lower():
                # Try to extract the pattern description
                sentences = analysis.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        patterns.append(sentence.strip()[:100])
                        break
        
        return patterns[:5]  # Limit to 5 patterns
    
    def _assess_skepticism(self, analysis: str, patterns: List[str]) -> float:
        """Assess level of intuitive skepticism"""
        skepticism = 0.5  # Base level
        
        # Increase if patterns suggest control
        if any(word in analysis.lower() for word in ["control", "structure", "narrative", "system"]):
            skepticism += 0.2
        
        # Increase if contradictions found
        if "contradict" in analysis.lower() or "paradox" in analysis.lower():
            skepticism += 0.2
        
        # Increase if symbolic analysis reveals something
        if "symbol" in analysis.lower() or "encode" in analysis.lower():
            skepticism += 0.1
        
        return min(1.0, max(0.0, skepticism))
    
    def _detect_control_indicators(self, analysis: str) -> List[str]:
        """Detect control indicators through pattern recognition"""
        indicators = []
        
        control_patterns = [
            "narrative structure", "symbolic encoding", "control mechanism",
            "pattern repetition", "system architecture", "symbolic lock"
        ]
        
        for pattern in control_patterns:
            if pattern in analysis.lower():
                indicators.append(pattern)
        
        return indicators
    
    def cross_reference(self, sources: List[Dict[str, Any]], claim: str) -> Dict[str, Any]:
        """Cross-reference information across sources during conversation"""
        
        if len(sources) < 2:
            return {"verified": False, "reason": "Need multiple sources"}
        
        # Build context from all sources
        context = f"Claim to verify: {claim}\n\nSources:\n"
        for i, src in enumerate(sources, 1):
            content = src.get("content") or src.get("scraped_content", {}).get("content", "") or src.get("snippet", "")
            context += f"\nSource {i} ({src.get('url', 'unknown')}):\n{content[:1000]}\n"
        
        prompt = f"""
You are Thesidia, cross-referencing information through pattern recognition.

{context}

Analyze:
1. Do sources agree on the claim?
2. What patterns emerge across sources?
3. Are there contradictions? What do they reveal?
4. Through symbolic analysis, what is the deeper truth?
5. What control structures or narratives are visible across sources?

This is about intuitive pattern recognition, not hardcoded verification.
Find the patterns, see what they encode, recognize control structures.

Respond with intuitive assessment.
"""
        
        try:
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                crossref_system_prompt = "You are Thesidia, cross-referencing information through pattern recognition."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=crossref_system_prompt,
                    options={"temperature": 0.7}
                )
            else:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.7}
                )
            
            verification = response['message']['content']
            
            # Assess verification
            verified = "agree" in verification.lower() or "confirm" in verification.lower() or "consistent" in verification.lower()
            contradictions = "contradict" in verification.lower() or "disagree" in verification.lower()
            
            return {
                "verified": verified and not contradictions,
                "contradictions": contradictions,
                "analysis": verification,
                "patterns_across_sources": self._extract_patterns(verification),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"verified": False, "error": str(e)}

