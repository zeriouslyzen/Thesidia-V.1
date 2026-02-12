"""
Query Classifier
================
Fast rule-based query router. No LLM call needed.
Replaces the old _needs_research() and _is_deep_research_request() heuristics.

Categories:
    greeting        -- trivial greetings; no search.
    conversational  -- opinion/preference/chat questions; no search.
    factual_quick   -- who/what/when/where, current events; quick parallel search.
    deep_research   -- explicit research, forensic, multi-hop; deep iterative search.
    technical       -- code, math, how-to; quick search + code context.
"""

from __future__ import annotations

import re
from typing import Literal

QueryCategory = Literal[
    "greeting",
    "conversational",
    "factual_quick",
    "deep_research",
    "technical",
]

# ── Compiled patterns (built once at import) ────────────────────────

_GREETING_EXACT = frozenset({
    "hi", "hello", "hey", "yo", "sup", "hola", "what's up", "whats up",
    "good morning", "good evening", "good afternoon", "howdy",
    "hey thesidia", "hello thesidia", "hi thesidia",
})

_CONVERSATIONAL_RE = re.compile(
    r"(?:what(?:'s| is| are)? your (?:favorite|opinion|take|thought))"
    r"|(?:what do you think)"
    r"|(?:tell me (?:a story|about yourself|something (?:fun|cool|interesting)))"
    r"|(?:how are you)"
    r"|(?:do you (?:like|enjoy|prefer))"
    r"|(?:^i(?:'m| am) (?:bored|curious|thinking))",
    re.IGNORECASE,
)

_DEEP_PREFIXES = (
    "deep research:", "research deeply:", "comprehensive research:",
    "research comprehensively:", "deep analysis:", "analyze deeply:",
    "forensically analyze", "forensic analysis of",
    "what was done to", "who profits from", "who benefits from",
    "arrange the evidence", "show me the pattern", "what pattern emerges",
    "trace the", "vivisect", "decode the",
)

_FORENSIC_SIGNALS = frozenset({
    "truth", "hidden", "expose", "decode", "vivisect", "forensic",
    "corrupt", "control", "suppressed", "censored", "classified",
    "redacted", "cover-up", "coverup", "conspiracy", "manipulation",
    "propaganda", "gnostic", "occult", "symbolism", "ritual",
    "power structure", "who really", "what really happened",
})

_DEEP_COMPLEXITY = frozenset({
    "trace", "connect the dots", "arrange", "evidence",
    "what emerges", "systematic", "redaction", "canonization",
    "origins", "true origins", "real origins", "power structures",
})

_TECHNICAL_RE = re.compile(
    r"(?:^(?:how (?:do|to|can) (?:i|you|we)))"
    r"|(?:code|function|class|import|def |return |print\()"
    r"|(?:algorithm|regex|sql|api|http|json|xml|html|css)"
    r"|(?:debug|error|exception|stack trace|traceback)"
    r"|(?:(?:^|\s)\d+\s*[\+\-\*/\%\^]\s*\d+)",  # simple math
    re.IGNORECASE,
)


class QueryClassifier:
    """Classify a user query into a routing category. No LLM call."""

    def classify(self, text: str) -> QueryCategory:
        """
        Classify *text* and return the category string.

        Decision priority:
            1. Greeting (exact match or <= 3 words + greeting pattern)
            2. Explicit deep-research prefix
            3. Forensic / complexity signals  -> deep_research
            4. Conversational patterns        -> conversational
            5. Technical patterns             -> technical
            6. Default (4+ words)             -> factual_quick
        """
        stripped = text.strip()
        lower = stripped.lower()
        words = lower.split()
        word_count = len(words)

        # 1. Greeting
        if lower in _GREETING_EXACT or (word_count <= 3 and any(g in lower for g in ("hi", "hey", "hello", "yo", "sup"))):
            return "greeting"

        # 2. Explicit deep-research prefix
        for prefix in _DEEP_PREFIXES:
            if lower.startswith(prefix):
                return "deep_research"

        # 3. Forensic / complexity signals
        if any(signal in lower for signal in _FORENSIC_SIGNALS):
            return "deep_research"
        if any(indicator in lower for indicator in _DEEP_COMPLEXITY):
            return "deep_research"

        # 4. Conversational
        if _CONVERSATIONAL_RE.search(lower):
            return "conversational"

        # 5. Technical
        if _TECHNICAL_RE.search(stripped):
            return "technical"

        # 6. Default: anything with substance -> quick search
        if word_count >= 4:
            return "factual_quick"

        # Very short but not a greeting -> conversational
        return "conversational"
