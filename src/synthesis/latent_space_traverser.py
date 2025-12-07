#!/usr/bin/env python3
"""
Latent Space Traverser
======================
Discovers latent axes (e.g., truth axes) and performs simple vector arithmetic
for pattern exploration. Designed to degrade gracefully when embeddings are
unavailable.
"""

from __future__ import annotations

from typing import List, Optional, Dict
import math

from ..support.embeddings import EmbeddingGenerator


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def _add(vec1: List[float], vec2: List[float]) -> List[float]:
    return [a + b for a, b in zip(vec1, vec2)]


def _sub(vec1: List[float], vec2: List[float]) -> List[float]:
    return [a - b for a, b in zip(vec1, vec2)]


def _scale(vec: List[float], factor: float) -> List[float]:
    return [a * factor for a in vec]


class LatentSpaceTraverser:
    """Traverse embedding space to reveal latent axes and suppressed knowledge."""

    def __init__(self, model: str = "clean-mistral:latest"):
        self.embedder = EmbeddingGenerator(model=model)

    def discover_truth_axis(self, positive: str, negative: str) -> Optional[List[float]]:
        """Return vector representing direction(positive - negative)."""
        pos = self.embedder.get_embedding(positive)
        neg = self.embedder.get_embedding(negative)
        if pos and neg and len(pos) == len(neg):
            return _sub(pos, neg)
        return None

    def apply_axis(self, text: str, axis: List[float], strength: float = 1.0) -> Optional[List[float]]:
        """Apply axis to text embedding to bias toward that direction."""
        base = self.embedder.get_embedding(text)
        if base and axis and len(base) == len(axis):
            return _add(base, _scale(axis, strength))
        return None

    def interpolate_concepts(self, concept1: str, concept2: str, steps: int = 5) -> List[List[float]]:
        """Linear interpolation between two concept embeddings."""
        emb1 = self.embedder.get_embedding(concept1)
        emb2 = self.embedder.get_embedding(concept2)
        if not emb1 or not emb2 or len(emb1) != len(emb2):
            return []
        interpolations: List[List[float]] = []
        for i in range(steps + 1):
            alpha = i / steps
            interpolations.append([a * (1 - alpha) + b * alpha for a, b in zip(emb1, emb2)])
        return interpolations

    def find_suppressed_direction(self, query: str, official_narrative: str) -> Optional[List[float]]:
        """Heuristic: direction from official narrative back toward raw query."""
        q_emb = self.embedder.get_embedding(query)
        o_emb = self.embedder.get_embedding(official_narrative)
        if q_emb and o_emb and len(q_emb) == len(o_emb):
            return _sub(q_emb, o_emb)
        return None

    def summarize_axis(self, axis: Optional[List[float]], probes: Dict[str, str]) -> Dict[str, float]:
        """
        Score how aligned probe texts are with an axis via cosine similarity.
        Returns mapping of probe label -> similarity.
        """
        if not axis:
            return {}
        scores: Dict[str, float] = {}
        for label, text in probes.items():
            emb = self.embedder.get_embedding(text)
            if emb and len(emb) == len(axis):
                scores[label] = _cosine_similarity(emb, axis)
        return scores


