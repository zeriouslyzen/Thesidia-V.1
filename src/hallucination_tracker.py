#!/usr/bin/env python3
"""
Hallucination Tracker
=====================

Original hallucination detection and quarantine logic extracted from
`thesidia_hybrid_adaptive.py` for reuse across Sophia modules.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional


class HallucinationTracker:
    """Track and quarantine hallucinations."""

    def __init__(self) -> None:
        self.hallucinations: List[Dict[str, Any]] = []
        self.quarantine_list: List[Dict[str, Any]] = []
        self.patterns_detected: List[str] = []

    def detect_hallucination(
        self,
        response: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        query: str = "",
    ) -> Dict[str, Any]:
        """Detect potential hallucinations in response."""
        indicators = {
            "made_up_person": False,
            "unverified_fact": False,
            "fake_source": False,
            "no_uncertainty": False,
            "confidence_score": 0.0,
            "quarantine": False,
        }

        response_lower = response.lower()
        person_patterns = [
            r'dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'professor\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'archaeologist\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'researcher\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        discovery_words = ["discovered", "found", "uncovered", "revealed", "identified", "made", "unearthed"]

        found_persons = []
        for pattern in person_patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE)
            for match in matches:
                person_name = match.group(1)
                start_pos = match.end()
                snippet = response_lower[start_pos:start_pos + 300]
                if any(word in snippet for word in discovery_words):
                    found_persons.append((person_name, match.start()))

        if found_persons:
            for person_name, _ in found_persons:
                verified = False
                if sources:
                    for source in sources:
                        content = (
                            source.get("content", "")
                            or source.get("scraped_content", {}).get("content", "")
                            or ""
                        ).lower()
                        if person_name.lower() in content:
                            verified = True
                            break
                if not verified:
                    indicators["made_up_person"] = True
                    indicators["confidence_score"] += 0.5
                    break

        if sources:
            claims = self._extract_claims(response)
            verified_claims = 0
            for claim in claims:
                for source in sources:
                    content = (
                        source.get("content", "")
                        or source.get("scraped_content", {}).get("content", "")
                        or ""
                    ).lower()
                    if claim.lower()[:50] in content:
                        verified_claims += 1
                        break

            if claims and verified_claims / len(claims) < 0.5:
                indicators["unverified_fact"] = True
                indicators["confidence_score"] += 0.3

        uncertainty_markers = ["couldn't find", "not found", "don't know", "no information", "uncertain", "unclear", "couldn't verify"]
        if not any(marker in response_lower for marker in uncertainty_markers):
            indicators["no_uncertainty"] = True
            indicators["confidence_score"] += 0.2

        if sources:
            valid_hosts = ["http", "https", "www", "://" ]
            for source in sources:
                url = source.get("url", "")
                if url and not any(token in url for token in valid_hosts):
                    indicators["fake_source"] = True
                    indicators["confidence_score"] += 0.3
                    break

        if indicators["confidence_score"] > 0.5:
            indicators["quarantine"] = True

        return indicators

    def quarantine_response(
        self,
        response: str,
        indicators: Dict[str, Any],
        query: str,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        entry = {
            "response": response,
            "indicators": indicators,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": sources or []
        }
        self.quarantine_list.append(entry)
        self.hallucinations.append(entry)

    def get_quarantine_summary(self) -> Dict[str, Any]:
        summary = {
            "total_quarantined": len(self.quarantine_list),
            "by_type": {
                "made_up_person": 0,
                "unverified_fact": 0,
                "fake_source": 0,
                "no_uncertainty": 0
            },
            "average_confidence": 0.0
        }
        if not self.quarantine_list:
            return summary

        total_confidence = 0.0
        for entry in self.quarantine_list:
            indicators = entry.get("indicators", {})
            if indicators.get("made_up_person"):
                summary["by_type"]["made_up_person"] += 1
            if indicators.get("unverified_fact"):
                summary["by_type"]["unverified_fact"] += 1
            if indicators.get("fake_source"):
                summary["by_type"]["fake_source"] += 1
            if indicators.get("no_uncertainty"):
                summary["by_type"]["no_uncertainty"] += 1
            total_confidence += indicators.get("confidence_score", 0.0)

        summary["average_confidence"] = total_confidence / len(self.quarantine_list)
        return summary

    def add_pattern(self, pattern: str):
        if pattern not in self.patterns_detected:
            self.patterns_detected.append(pattern)

    def _extract_claims(self, text: str) -> List[str]:
        claims = []
        for sentence in text.split("."):
            if any(char.isdigit() for char in sentence):
                claims.append(sentence.strip())
        return claims[:5]


__all__ = ["HallucinationTracker"]

