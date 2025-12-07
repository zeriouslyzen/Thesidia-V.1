#!/usr/bin/env python3
"""
Feature Flags - Advanced LLM Techniques
---------------------------------------
Centralized feature flag system with simple auto-detection based on query text.
All flags default to False to preserve existing behavior.
"""

from __future__ import annotations

from typing import Dict, List


class FeatureFlags:
    """Centralized feature flag system for advanced LLM techniques."""

    def __init__(self):
        self.flags: Dict[str, bool] = {
            "ENABLE_CONTRASTIVE_DECODING": False,
            "ENABLE_LATENT_SPACE_TRAVERSAL": False,
            "ENABLE_CUSTOM_DECODING": False,
            "ENABLE_REPRESENTATION_PROBING": False,
        }
        self.auto_detect_rules: Dict[str, List[str]] = {
            "ENABLE_CONTRASTIVE_DECODING": ["genesis", "bible", "decode", "expose", "contradiction"],
            "ENABLE_LATENT_SPACE_TRAVERSAL": ["suppressed", "hidden", "truth", "pattern"],
            "ENABLE_CUSTOM_DECODING": ["forensic", "vivisect", "deep analysis"],
            "ENABLE_REPRESENTATION_PROBING": ["probe", "activation", "internal"],
        }

    def should_enable(self, flag_name: str, query: str) -> bool:
        """Return True if the flag is globally enabled and the query matches auto-detect rules."""
        if not self.flags.get(flag_name, False):
            return False
        query_lower = (query or "").lower()
        keywords = self.auto_detect_rules.get(flag_name, [])
        return any(kw in query_lower for kw in keywords) if keywords else False

    def enable(self, flag_name: str):
        """Enable a feature flag."""
        self.flags[flag_name] = True

    def disable(self, flag_name: str):
        """Disable a feature flag."""
        self.flags[flag_name] = False

    def is_enabled(self, flag_name: str) -> bool:
        """Check if flag is set to True (ignores auto-detect)."""
        return self.flags.get(flag_name, False)


