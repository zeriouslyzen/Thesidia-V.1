#!/usr/bin/env python3
"""
Contrastive Decoder
===================
Generates multiple perspectives in parallel to surface latent contradictions
and underlying structural patterns. Designed to be optional and feature-flagged.
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional

from ..core.model_client import ModelClient


class ContrastiveDecoder:
    """Generate contrastive perspectives and extract contradictions/patterns."""

    def __init__(self, model: str = "clean-mistral:latest", model_client: Optional[ModelClient] = None):
        self.model = model
        self.model_client = model_client or ModelClient(default_model=model)

    def decode_contrastive(
        self,
        query: str,
        sources: List[Dict[str, Any]],
        enhanced_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate multiple perspectives and synthesize contradictions/patterns."""
        prompts = self._build_prompts(query, sources)
        perspectives: Dict[str, str] = {}

        for name, prompt in prompts.items():
            try:
                resp = self.model_client.chat(
                    model=self.model,
                    input_text=prompt,
                    enhanced_base=enhanced_prompt,
                    options={"temperature": temperature, "top_p": 0.9},
                )
                content = getattr(resp, "message", {}).content if hasattr(resp, "message") else resp.get("message", {}).get("content", "")
                perspectives[name] = content or ""
            except Exception as e:  # pylint: disable=broad-except
                perspectives[name] = f"[error generating {name}: {e}]"

        contradictions = self._extract_contradictions(perspectives)
        underlying_pattern = self._synthesize_pattern(perspectives)

        return {
            "perspectives": perspectives,
            "contradictions": contradictions,
            "underlying_pattern": underlying_pattern,
        }

    def _build_prompts(self, query: str, sources: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build perspective-specific prompts."""
        source_summaries = self._summarize_sources(sources)
        base = f"Query: {query}\n\nSources:\n{source_summaries}\n\n"
        return {
            "official_narrative": base + "Present the official/mainstream narrative.",
            "academic_critique": base + "Provide academic critique and analysis.",
            "historical_version": base + "Provide the historical version and context.",
            "alternative_interpretation": base + "Provide alternative or marginalized interpretations.",
            "latent_contradictions": base + "List latent contradictions across narratives.",
            "underlying_structural_pattern": base + "Extract underlying structural patterns and control structures.",
        }

    def _summarize_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Summarize sources for context."""
        lines = []
        for i, src in enumerate(sources[:3], 1):  # Limit to top 3 for brevity
            title = src.get("title", "Unknown")
            url = src.get("url", "")
            content = src.get("content") or src.get("snippet") or src.get("scraped_content", {}).get("content", "")
            lines.append(f"[Source {i}] {title} {url} :: {content[:400]}")
        return "\n".join(lines)

    def _extract_contradictions(self, perspectives: Dict[str, str]) -> List[str]:
        """Simple heuristic: look for disagreements between perspectives."""
        contradictions: List[str] = []
        official = perspectives.get("official_narrative", "").lower()
        alt = perspectives.get("alternative_interpretation", "").lower()
        critique = perspectives.get("academic_critique", "").lower()
        if official and alt and official[:200] != alt[:200]:
            contradictions.append("Alternative interpretation diverges from official narrative.")
        if official and critique and official[:200] != critique[:200]:
            contradictions.append("Academic critique diverges from official narrative.")
        latent = perspectives.get("latent_contradictions", "")
        if latent:
            contradictions.append(latent.strip())
        return [c for c in contradictions if c]

    def _synthesize_pattern(self, perspectives: Dict[str, str]) -> str:
        """Extract a simple underlying pattern statement."""
        pattern_notes = [
            perspectives.get("underlying_structural_pattern", ""),
            perspectives.get("latent_contradictions", ""),
        ]
        joined = " ".join([p for p in pattern_notes if p]).strip()
        return joined[:2000] if joined else ""


