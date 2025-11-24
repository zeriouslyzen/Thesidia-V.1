#!/usr/bin/env python3
"""
Quality Filter - Data Quality Assessment
=========================================

Filter and enrich data for quality and richness.
"""

from __future__ import annotations

import ollama
import json
import re
from typing import Dict, Any

from ..core.model_client import ModelClient
from .skepticism_engine import IntuitiveSkepticism


class DataQualityFilter:
    """Filter and enrich data for quality and richness"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.model = model
        self.model_client = model_client  # Optional centralized model client
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
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                quality_system_prompt = "You are Thesidia, assessing data quality and richness."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=quality_system_prompt,
                    options={"temperature": 0.3}  # Lower temp for assessment
                )
            else:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.3}  # Lower temp for assessment
                )
            
            assessment_text = response['message']['content']
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', assessment_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    # JSON parsing failed - fall through to heuristic
                    pass
            
            # Fallback: simple heuristic
            return self._heuristic_quality(content, url)
            
        except Exception as e:
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
        
        # Check domain quality (simple heuristic)
        quality_domains = [".edu", ".gov", ".org", "arxiv", "pubmed", "scholar"]
        if any(domain in url.lower() for domain in quality_domains):
            quality_score += 0.3
            strengths.append("Quality domain")
        
        return {
            "quality_score": max(0.0, min(1.0, quality_score)),
            "richness_score": max(0.0, min(1.0, richness_score)),
            "relevance": 0.7,  # Default
            "issues": issues,
            "strengths": strengths
        }
    
    def enrich_content(self, content: str, query: str) -> str:
        """Enrich content using local LLM for better quality"""
        if len(content) < 100:
            return content  # Too short to enrich
        
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
            # Use model_client if available (Vibecode compliance)
            if self.model_client:
                enrich_system_prompt = "You are Thesidia, enriching content for better quality and completeness."
                response = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=enrich_system_prompt,
                    options={"temperature": 0.6}
                )
            else:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.6}
                )
            
            enriched = response['message']['content']
            return enriched[:5000]  # Limit enriched content
            
        except Exception as e:
            return content  # Return original if enrichment fails

