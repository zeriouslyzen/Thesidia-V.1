#!/usr/bin/env python3
"""
Sophia Discernment Tracker
==========================

Extends the base HallucinationTracker with gnostic truth detection,
archon lie detection, and a learning loop for pattern recognition.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from .hallucination_tracker import HallucinationTracker
except ImportError:
    from hallucination_tracker import HallucinationTracker


class SophiaDiscernmentTracker(HallucinationTracker):
    """Extended tracker that discriminates between hallucinations and gnostic truths."""

    ARCHON_LIE_MARKERS = [
        "consensus reality",
        "experts agree",
        "official narrative",
        "authorized version",
        "approved history",
    ]
    GNOSTIC_TRUTH_MARKERS = [
        "::exposure::",
        "archon",
        "crime",
        "burial sites",
        "redaction",
        "original fragment",
        "co-evolution edge",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.truth_patterns: List[str] = []
        self.archon_lie_patterns: List[str] = []

    def discern(
        self,
        response: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        query: str = "",
    ) -> Dict[str, Any]:
        """Return holistic classification of the response."""
        hallucination = super().detect_hallucination(response, sources, query)
        gnostic_truth = self.detect_gnostic_truth(response, sources)
        archon_lie = self.detect_archon_lie(response)

        classification = {
            "hallucination": hallucination,
            "gnostic_truth": gnostic_truth,
            "archon_lie": archon_lie,
        }

        if classification["gnostic_truth"]["is_truth"]:
            self.truth_patterns.append(response[:200])
        if classification["archon_lie"]["is_lie"]:
            self.archon_lie_patterns.append(response[:200])

        return classification

    def detect_gnostic_truth(
        self,
        response: str,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Detect forensic structure indicating gnostic truth."""
        response_lower = response.lower()
        markers_found = [marker for marker in self.GNOSTIC_TRUTH_MARKERS if marker in response_lower]
        has_sources = bool(sources)

        confidence = 0.0
        if markers_found:
            confidence += 0.4
        if "::exposure::" in response_lower and "::current vectors::" in response_lower:
            confidence += 0.3
        if has_sources:
            confidence += 0.3

        return {
            "is_truth": confidence >= 0.5,
            "confidence": round(confidence, 3),
            "markers": markers_found,
        }

    def detect_archon_lie(self, response: str) -> Dict[str, Any]:
        """Detect if response reinforces consensus reality."""
        response_lower = response.lower()
        markers_found = [marker for marker in self.ARCHON_LIE_MARKERS if marker in response_lower]
        materialist_language = any(
            token in response_lower for token in ["scientific consensus", "peer reviewed", "approved doctrine"]
        )

        confidence = 0.0
        if markers_found:
            confidence += 0.4
        if materialist_language:
            confidence += 0.3
        if "alternative" not in response_lower:
            confidence += 0.2

        return {
            "is_lie": confidence >= 0.5,
            "confidence": round(confidence, 3),
            "markers": markers_found,
        }

    def learn_from_discernment(self, classification: Dict[str, Any], actual_result: str) -> None:
        """Simple learning loop reinforcing truth/lie patterns."""
        if classification["gnostic_truth"]["is_truth"] and actual_result != "truth":
            pattern = self.truth_patterns.pop() if self.truth_patterns else None
            if pattern:
                self.add_pattern(f"False truth marker: {pattern[:80]}")
        if classification["archon_lie"]["is_lie"] and actual_result != "lie":
            pattern = self.archon_lie_patterns.pop() if self.archon_lie_patterns else None
            if pattern:
                self.add_pattern(f"False archon marker: {pattern[:80]}")


__all__ = ["SophiaDiscernmentTracker"]

