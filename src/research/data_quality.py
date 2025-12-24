#!/usr/bin/env python3
"""
Data Quality System
===================

Data quality filtering, enrichment, and intuitive skepticism.
Extracted from thesidia_hybrid_adaptive.py as part of Phase 0 modular refactoring.
"""

from __future__ import annotations

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Optional dependencies
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class IntuitiveSkepticism:
    """Intuitive skepticism through pattern recognition - not hardcoded"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_client = model_client
        self.patterns_learned = []
        self.cross_reference_history = []
    
    def detect_control_patterns(self, content: str, url: str, previous_sources: List[Dict] = None) -> Dict[str, Any]:
        """Detect control structures through pattern recognition - intuitive, not hardcoded"""
        
        # Cross-reference with previous sources if available
        cross_ref_context = ""
        if previous_sources:
            cross_ref_context = f"""
Previous sources for cross-reference:
{chr(10).join(f"- {s.get('url', 'unknown')}: {s.get('content', '')[:200]}" for s in previous_sources[:3])}
"""
        
        prompt = f"""
Analyze this content using intuitive pattern recognition to detect any control or manipulation structures:

URL: {url}
Content: {content[:2000]}
{cross_ref_context}

Tasks:
1. Look for patterns that suggest information control
2. Identify any repetitive narratives or unusual omissions
3. Cross-reference with other sources for consistency
4. Trust your pattern recognition - if something feels off, note it

Respond in JSON:
{{
    "analysis": "Your intuitive analysis",
    "patterns_detected": ["pattern1", "pattern2"],
    "control_indicators": ["indicator1", "indicator2"],
    "skepticism_level": 0.0-1.0,
    "cross_reference_notes": "Notes from comparing sources"
}}
"""
        
        try:
            if self.model_client:
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base="You are Thesidia, using intuitive pattern recognition to detect control structures in information.",
                    options={"temperature": 0.5}
                )
            elif OLLAMA_AVAILABLE:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.5}
                )
            else:
                # No model available - return neutral assessment
                return {
                    "analysis": "Model not available for analysis",
                    "patterns_detected": [],
                    "control_indicators": [],
                    "skepticism_level": 0.5,
                    "cross_reference_notes": ""
                }
            
            analysis_text = response['message']['content']
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    patterns = self._extract_patterns(analysis_text)
                    result["patterns_detected"] = result.get("patterns_detected", []) + patterns
                    self.patterns_learned.extend(patterns)
                    return result
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # Fallback: extract patterns manually
            patterns = self._extract_patterns(analysis_text)
            skepticism = self._assess_skepticism(analysis_text, patterns)
            
            result = {
                "analysis": analysis_text[:500],
                "patterns_detected": patterns,
                "control_indicators": self._detect_control_indicators(analysis_text),
                "skepticism_level": skepticism
            }
            
            self.patterns_learned.extend(patterns)
            return result
            
        except Exception as e:
            return {
                "analysis": f"Pattern analysis error: {str(e)}",
                "patterns_detected": [],
                "control_indicators": [],
                "skepticism_level": 0.5
            }
    
    def _extract_patterns(self, analysis: str) -> List[str]:
        """Extract patterns mentioned in analysis"""
        patterns = []
        
        # Look for pattern-related words
        pattern_indicators = ["pattern", "repetition", "narrative", "omission", "inconsistency"]
        sentences = analysis.split(".")
        
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in pattern_indicators):
                # Extract the pattern description
                pattern_text = sentence.strip()[:100]
                if pattern_text and len(pattern_text) > 10:
                    patterns.append(pattern_text)
        
        return patterns[:5]  # Limit to 5 patterns
    
    def _assess_skepticism(self, analysis: str, patterns: List[str]) -> float:
        """Assess level of intuitive skepticism"""
        base_skepticism = 0.3
        
        # Increase skepticism based on patterns found
        base_skepticism += len(patterns) * 0.1
        
        # Increase if analysis mentions concerning words
        concerning_words = ["suspicious", "unusual", "control", "manipulation", "propaganda"]
        for word in concerning_words:
            if word in analysis.lower():
                base_skepticism += 0.1
        
        return min(1.0, base_skepticism)
    
    def _detect_control_indicators(self, analysis: str) -> List[str]:
        """Detect control indicators through pattern recognition"""
        indicators = []
        
        control_words = {
            "propaganda": "Potential propaganda detected",
            "bias": "Potential bias detected",
            "censored": "Possible censorship",
            "omitted": "Information omission",
            "narrative": "Controlled narrative"
        }
        
        for word, indicator in control_words.items():
            if word in analysis.lower():
                indicators.append(indicator)
        
        return indicators
    
    def cross_reference(self, sources: List[Dict[str, Any]], claim: str) -> Dict[str, Any]:
        """Cross-reference information across sources during conversation"""
        
        prompt = f"""
Cross-reference this claim across multiple sources:

Claim: {claim}

Sources:
{chr(10).join(f"Source {i+1} ({s.get('url', 'unknown')}): {s.get('content', '')[:500]}" for i, s in enumerate(sources[:5]))}

Tasks:
1. Check if claim is supported by multiple sources
2. Identify any contradictions
3. Note any suspicious patterns (same wording across sources, etc.)
4. Trust your intuition about information quality

Respond in JSON:
{{
    "verification_status": "verified/partial/unverified/contradicted",
    "supporting_sources": ["url1", "url2"],
    "contradicting_sources": ["url3"],
    "patterns_noted": ["pattern1"],
    "confidence": 0.0-1.0,
    "notes": "Your analysis"
}}
"""
        
        try:
            if self.model_client:
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base="You are Thesidia, cross-referencing information with intuitive skepticism.",
                    options={"temperature": 0.4}
                )
            elif OLLAMA_AVAILABLE:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.4}
                )
            else:
                return {
                    "verification_status": "unverified",
                    "supporting_sources": [],
                    "contradicting_sources": [],
                    "patterns_noted": [],
                    "confidence": 0.5,
                    "notes": "Model not available for cross-reference"
                }
            
            verification_text = response['message']['content']
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', verification_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    self.cross_reference_history.append({
                        "claim": claim,
                        "result": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    return result
                except (json.JSONDecodeError, ValueError):
                    pass
            
            # Fallback
            return {
                "verification_status": "partial",
                "notes": verification_text[:500],
                "confidence": 0.5
            }
            
        except Exception as e:
            return {
                "verification_status": "error",
                "notes": str(e),
                "confidence": 0.0
            }


class DataQualityFilter:
    """Filter and enrich data for quality and richness"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_client = model_client
        self.skepticism_engine = IntuitiveSkepticism(model, model_client=model_client)
    
    def assess_quality(self, content: str, url: str) -> Dict[str, Any]:
        """Assess data quality using local LLM"""
        if not content or len(content) < 50:
            return {"quality_score": 0.0, "issues": ["Content too short"], "richness": 0.0}
        
        prompt = f"""
Assess the quality and richness of this web content:

URL: {url}
Content: {content[:2000]}

Rate on:
1. Quality (0-1): Accuracy, reliability, depth
2. Richness (0-1): Information density, detail, completeness
3. Relevance: How relevant to typical queries
4. Issues: Any problems (bias, spam, low quality, etc.)

Respond in JSON:
{{
    "quality_score": 0.0-1.0,
    "richness_score": 0.0-1.0,
    "relevance": 0.0-1.0,
    "issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"]
}}
"""
        try:
            if self.model_client:
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base="You are Thesidia, assessing data quality and richness.",
                    options={"temperature": 0.3}
                )
            elif OLLAMA_AVAILABLE:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.3}
                )
            else:
                return self._heuristic_quality(content, url)
            
            assessment_text = response['message']['content']
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except (json.JSONDecodeError, ValueError):
                    pass
            
            return self._heuristic_quality(content, url)
            
        except Exception:
            return self._heuristic_quality(content, url)
    
    def _heuristic_quality(self, content: str, url: str) -> Dict[str, Any]:
        """Heuristic quality assessment"""
        quality_score = 0.5
        richness_score = 0.5
        issues = []
        strengths = []
        
        # Check length
        if len(content) < 200:
            quality_score -= 0.2
            issues.append("Very short content")
        elif len(content) > 2000:
            richness_score += 0.2
            strengths.append("Detailed content")
        
        # Check for spam indicators
        spam_words = ["click here", "buy now", "limited time", "act now"]
        if any(word in content.lower() for word in spam_words):
            quality_score -= 0.3
            issues.append("Possible spam")
        
        # Check for quality indicators
        quality_indicators = ["research", "study", "analysis", "evidence", "data", "source"]
        if any(word in content.lower() for word in quality_indicators):
            quality_score += 0.2
            strengths.append("Contains research/evidence")
        
        # Check domain quality
        quality_domains = [".edu", ".gov", ".org", "arxiv", "pubmed", "scholar"]
        if any(domain in url.lower() for domain in quality_domains):
            quality_score += 0.3
            strengths.append("Quality domain")
        
        return {
            "quality_score": max(0.0, min(1.0, quality_score)),
            "richness_score": max(0.0, min(1.0, richness_score)),
            "relevance": 0.7,
            "issues": issues,
            "strengths": strengths
        }
    
    def enrich_content(self, content: str, query: str) -> str:
        """Enrich content using local LLM for better quality"""
        if len(content) < 100:
            return content
        
        prompt = f"""
Enrich and improve this web content for better quality and completeness:

Original Query: {query}
Content: {content[:3000]}

Tasks:
1. Extract key information
2. Fill in missing context
3. Clarify ambiguous statements
4. Add relevant connections
5. Maintain accuracy (don't add false information)

Return enriched content that is more complete and useful.
"""
        
        try:
            if self.model_client:
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base="You are Thesidia, enriching content for better quality and completeness.",
                    options={"temperature": 0.6}
                )
            elif OLLAMA_AVAILABLE:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.6}
                )
            else:
                return content
            
            enriched = response['message']['content']
            return enriched[:5000]
            
        except Exception:
            return content
