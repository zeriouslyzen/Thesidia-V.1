#!/usr/bin/env python3
"""
SynthesisPressureStage

Goal: force dense synthesis by extracting atomic claims, flagging contradictions,
and compressing the draft into a tighter, higher-signal response.

This is intentionally heuristic-first to stay fast and deterministic; an LLM-backed
mode can be added later behind THESIDIA_SYNTHESIS_PRESSURE_MODE=llm.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_BULLET_LINE = re.compile(r"^\s*(?:[-*•]|\d+[\).])\s+")


@dataclass(frozen=True)
class PressureMeta:
    enabled: bool
    mode: str
    pre_chars: int
    post_chars: int
    compression_ratio: float
    claims_count: int
    contradictions_count: int


class SynthesisPressureStage:
    """
    Heuristic synthesis pressure stage.

    Strategy:
    - Split into candidate sentences/lines.
    - Extract "claims" as normalized sentence units (rough but useful).
    - Identify simple contradiction patterns (negations and numeric conflicts).
    - Compress: keep a small set of highest-signal sentences + any explicitly-marked unknowns.
    """

    def __init__(self, mode: str = "heuristic"):
        self.mode = mode

    def apply(
        self,
        query: str,
        draft_response: str,
        *,
        max_chars: int = 1200,
    ) -> Tuple[str, PressureMeta]:
        pre = (draft_response or "").strip()
        pre_len = len(pre)
        if not pre:
            meta = PressureMeta(
                enabled=True,
                mode=self.mode,
                pre_chars=0,
                post_chars=0,
                compression_ratio=1.0,
                claims_count=0,
                contradictions_count=0,
            )
            return "", meta

        # Extract units
        units = self._extract_units(pre)
        claims = self._extract_claims(units)
        contradictions = self._detect_contradictions(claims)

        # Build compressed response
        compressed = self._compress(query=query, units=units, max_chars=max_chars)
        post_len = len(compressed)
        ratio = (post_len / pre_len) if pre_len else 1.0

        meta = PressureMeta(
            enabled=True,
            mode=self.mode,
            pre_chars=pre_len,
            post_chars=post_len,
            compression_ratio=ratio,
            claims_count=len(claims),
            contradictions_count=len(contradictions),
        )
        return compressed, meta

    def _extract_units(self, text: str) -> List[str]:
        # Prefer preserving bullets as units; otherwise sentence split.
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        bulletish = [ln for ln in lines if _BULLET_LINE.match(ln)]
        if len(bulletish) >= max(2, len(lines) // 4):
            return bulletish
        # sentence split fallback
        return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]

    def _extract_claims(self, units: List[str]) -> List[str]:
        claims: List[str] = []
        for u in units:
            norm = self._normalize_claim(u)
            if not norm:
                continue
            # drop extremely short / non-informational
            if len(norm) < 12:
                continue
            claims.append(norm)
        return claims

    def _normalize_claim(self, s: str) -> str:
        s = _BULLET_LINE.sub("", s).strip()
        s = re.sub(r"\s+", " ", s)
        return s

    def _detect_contradictions(self, claims: List[str]) -> List[Dict[str, str]]:
        # Heuristic: same subject phrase with negation flip or different numeric value.
        contradictions: List[Dict[str, str]] = []
        indexed: Dict[str, List[str]] = {}

        for c in claims:
            key = self._topic_key(c)
            indexed.setdefault(key, []).append(c)

        for key, group in indexed.items():
            if len(group) < 2:
                continue
            # negation conflict
            for a in group:
                for b in group:
                    if a == b:
                        continue
                    if self._negation_conflict(a, b) or self._numeric_conflict(a, b):
                        contradictions.append({"topic": key, "a": a, "b": b})
                        break
                if contradictions and contradictions[-1].get("topic") == key:
                    break
        return contradictions

    def _topic_key(self, c: str) -> str:
        # take leading ~6 words as a crude topic signature
        words = re.findall(r"[a-zA-Z0-9']+", c.lower())
        return " ".join(words[:6]) if words else c.lower()[:40]

    def _negation_conflict(self, a: str, b: str) -> bool:
        na = bool(re.search(r"\b(not|never|no)\b", a.lower()))
        nb = bool(re.search(r"\b(not|never|no)\b", b.lower()))
        if na == nb:
            return False
        # if most words overlap, treat as conflict
        wa = set(re.findall(r"[a-zA-Z0-9']+", a.lower()))
        wb = set(re.findall(r"[a-zA-Z0-9']+", b.lower()))
        if not wa or not wb:
            return False
        overlap = len(wa & wb) / max(1, min(len(wa), len(wb)))
        return overlap >= 0.6

    def _numeric_conflict(self, a: str, b: str) -> bool:
        nums_a = re.findall(r"\b\d+(?:\.\d+)?\b", a)
        nums_b = re.findall(r"\b\d+(?:\.\d+)?\b", b)
        if not nums_a or not nums_b:
            return False
        if nums_a == nums_b:
            return False
        # consider conflict if high word overlap and different numbers
        wa = set(re.findall(r"[a-zA-Z0-9']+", a.lower()))
        wb = set(re.findall(r"[a-zA-Z0-9']+", b.lower()))
        overlap = len(wa & wb) / max(1, min(len(wa), len(wb)))
        return overlap >= 0.7

    def _compress(self, query: str, units: List[str], max_chars: int) -> str:
        # Score by presence of mechanistic / evidential language.
        score_words = [
            "because", "therefore", "mechanism", "evidence", "data", "measure",
            "causes", "causal", "rate", "signal", "model", "hypothesis", "predict",
            "unknown", "uncertain", "i don't know", "we don't know",
        ]
        q = (query or "").strip()
        ranked = []
        for u in units:
            low = u.lower()
            score = 0
            score += sum(2 for w in score_words if w in low)
            score += 2 if any(ch.isdigit() for ch in u) else 0
            score += 1 if len(u) > 80 else 0
            # slight preference for direct answers (avoid long preambles)
            score += 1 if not low.startswith(("hey", "hi", "alright", "ok", "so")) else 0
            ranked.append((score, u))

        ranked.sort(key=lambda t: t[0], reverse=True)

        kept: List[str] = []
        total = 0

        # Always keep first unit if nothing else
        if ranked:
            for _, u in ranked:
                if u in kept:
                    continue
                # stopwords: skip obvious filler
                if len(u.strip()) < 10:
                    continue
                if total + len(u) + 2 > max_chars and kept:
                    continue
                kept.append(u.strip())
                total += len(u) + 2
                if total >= max_chars:
                    break

        # Shape final: short intro that anchors to the query, then bullets if multi-unit.
        if not kept:
            return units[0].strip()[:max_chars]

        if len(kept) == 1:
            return kept[0][:max_chars].strip()

        # Build bullet summary
        header = ""
        if q and len(q) <= 140:
            header = f"{q}\n\n"
        bullets = "\n".join(f"- {self._normalize_claim(k)}" for k in kept)
        out = (header + bullets).strip()
        return out[:max_chars].strip()




