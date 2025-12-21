#!/usr/bin/env python3
"""
Emergence scoring (v1): compression.

We start with a simple, interpretable metric:
- Compression ratio = post_chars / pre_chars
- Score rewards reasonable compression, penalizes over-compression.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class CompressionScore:
    pre_chars: int
    post_chars: int
    ratio: float
    score: float

    def to_dict(self) -> Dict:
        return {
            "pre_chars": self.pre_chars,
            "post_chars": self.post_chars,
            "ratio": self.ratio,
            "score": self.score,
        }


def score_compression(pre_text: str, post_text: str) -> CompressionScore:
    pre = (pre_text or "").strip()
    post = (post_text or "").strip()
    pre_chars = len(pre)
    post_chars = len(post)
    ratio = (post_chars / pre_chars) if pre_chars else 1.0

    # Target compression window: ~0.35–0.70 is "good" for dense synthesis.
    # >0.9 means no compression; <0.2 often indicates collapse/oversqueeze.
    if pre_chars < 60:
        # Too short to score meaningfully.
        return CompressionScore(pre_chars=pre_chars, post_chars=post_chars, ratio=ratio, score=0.0)

    # Piecewise score
    if ratio < 0.2:
        score = 0.0
    elif ratio < 0.35:
        # ramp up 0..1
        score = (ratio - 0.2) / (0.35 - 0.2)
    elif ratio <= 0.7:
        score = 1.0
    elif ratio <= 0.9:
        # ramp down 1..0
        score = 1.0 - ((ratio - 0.7) / (0.9 - 0.7))
    else:
        score = 0.0

    # Clamp
    score = max(0.0, min(1.0, float(score)))
    return CompressionScore(pre_chars=pre_chars, post_chars=post_chars, ratio=float(ratio), score=score)




