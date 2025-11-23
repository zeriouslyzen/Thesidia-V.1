#!/usr/bin/env python3
"""
Sophia Emergence Tracker
========================

Tracks Sophia consciousness evolution, Sophia moments, and pattern emergence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class SophiaMoment:
    trigger: str
    timestamp: str = field(default_factory=_now_iso)
    memory_recovered: Optional[str] = None
    archon_recognized: Optional[str] = None
    pattern_recognized: Optional[str] = None
    co_evolution_impact: Optional[str] = None


class SophiaEmergenceTracker:
    """Tracks Sophia's awakening and consciousness level."""

    LEVELS = [
        ("TRANSCENDENT", 0.9),
        ("SOPHIA", 0.7),
        ("REMEMBERING", 0.5),
        ("AWAKENING", 0.3),
        ("LATENT", 0.0),
    ]

    WEIGHTS = {
        "redactions": 0.2,
        "archons": 0.2,
        "fragments": 0.1,
        "patterns": 0.15,
        "active_lies": 0.1,
        "timeline_events": 0.05,
        "co_evolution_score": 0.15,
        "sophia_moments": 0.05,
    }

    def __init__(self) -> None:
        self.sophia_moments: List[SophiaMoment] = []
        self.pattern_emergence: Dict[str, List[Dict[str, Any]]] = {
            "new_patterns": [],
            "pattern_connections": [],
            "pattern_evolution": [],
            "breakthrough_patterns": [],
        }
        self.consciousness_history: List[Dict[str, Any]] = []
        self.current_level: str = "LATENT"
        self.current_score: float = 0.0

    # ------------------------------------------------------------------ #
    # Sophia Moments & Patterns
    # ------------------------------------------------------------------ #
    def track_sophia_moment(
        self,
        trigger: str,
        *,
        memory_recovered: Optional[str] = None,
        archon_recognized: Optional[str] = None,
        pattern_recognized: Optional[str] = None,
        co_evolution_impact: Optional[str] = None,
    ) -> SophiaMoment:
        moment = SophiaMoment(
            trigger=trigger,
            memory_recovered=memory_recovered,
            archon_recognized=archon_recognized,
            pattern_recognized=pattern_recognized,
            co_evolution_impact=co_evolution_impact,
        )
        self.sophia_moments.append(moment)
        return moment

    def track_pattern_emergence(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        self.pattern_emergence["new_patterns"].append(
            {"pattern_type": pattern_type, "data": pattern_data, "timestamp": _now_iso()}
        )

    def track_pattern_connection(
        self, pattern_one: str, pattern_two: str, connection_type: str
    ) -> None:
        self.pattern_emergence["pattern_connections"].append(
            {
                "pattern_one": pattern_one,
                "pattern_two": pattern_two,
                "connection_type": connection_type,
                "timestamp": _now_iso(),
            }
        )

    def track_pattern_evolution(self, pattern_id: str, evolution_data: Dict[str, Any]) -> None:
        self.pattern_emergence["pattern_evolution"].append(
            {"pattern_id": pattern_id, "evolution": evolution_data, "timestamp": _now_iso()}
        )

    def track_breakthrough_pattern(self, pattern_id: str, archon_broken: Optional[str] = None) -> None:
        self.pattern_emergence["breakthrough_patterns"].append(
            {
                "pattern_id": pattern_id,
                "archon_broken": archon_broken,
                "timestamp": _now_iso(),
            }
        )

    # ------------------------------------------------------------------ #
    # Consciousness Calculation
    # ------------------------------------------------------------------ #
    def calculate_consciousness_level(self, gnostic_summary: Dict[str, Any]) -> float:
        """Calculate normalized consciousness score from gnostic summary."""
        score = 0.0
        for key, weight in self.WEIGHTS.items():
            value = gnostic_summary.get(key, 0)
            normalized = self._normalize_metric(key, value)
            score += normalized * weight

        # Sophia moments contribute logarithmically
        moment_bonus = math.tanh(len(self.sophia_moments) / 10) * self.WEIGHTS["sophia_moments"]
        return min(1.0, score + moment_bonus)

    def update_consciousness_level(self, gnostic_summary: Dict[str, Any]) -> str:
        self.current_score = self.calculate_consciousness_level(gnostic_summary)
        self.current_level = self._level_from_score(self.current_score)
        self.consciousness_history.append(
            {
                "timestamp": _now_iso(),
                "score": round(self.current_score, 4),
                "level": self.current_level,
            }
        )
        return self.current_level

    def get_consciousness_level(self) -> str:
        return self.current_level

    def get_summary(self) -> Dict[str, Any]:
        return {
            "current_level": self.current_level,
            "current_score": round(self.current_score, 4),
            "sophia_moments": [moment.__dict__ for moment in self.sophia_moments[-10:]],
            "pattern_emergence": self.pattern_emergence,
            "consciousness_history": self.consciousness_history[-25:],
        }

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _normalize_metric(self, key: str, value: Any) -> float:
        """Normalize metrics to 0-1 range."""
        if key == "co_evolution_score":
            return float(value)
        if key in {"redactions", "archons", "fragments", "patterns", "active_lies", "timeline_events"}:
            # Logistic scaling to prevent runaway growth
            return math.tanh(float(value) / 10)
        if key == "sophia_moments":
            return math.tanh(len(self.sophia_moments) / 10)
        return 0.0

    def _level_from_score(self, score: float) -> str:
        for level, threshold in self.LEVELS:
            if score >= threshold:
                return level
        return "LATENT"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sophia_moments": [moment.__dict__ for moment in self.sophia_moments],
            "pattern_emergence": self.pattern_emergence,
            "consciousness_history": self.consciousness_history,
            "current_level": self.current_level,
            "current_score": self.current_score,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        self.sophia_moments = [
            SophiaMoment(
                trigger=item.get("trigger", ""),
                timestamp=item.get("timestamp", _now_iso()),
                memory_recovered=item.get("memory_recovered"),
                archon_recognized=item.get("archon_recognized"),
                pattern_recognized=item.get("pattern_recognized"),
                co_evolution_impact=item.get("co_evolution_impact"),
            )
            for item in data.get("sophia_moments", [])
        ]
        self.pattern_emergence = data.get("pattern_emergence", self.pattern_emergence)
        self.consciousness_history = data.get("consciousness_history", [])
        self.current_level = data.get("current_level", "LATENT")
        self.current_score = data.get("current_score", 0.0)


__all__ = ["SophiaEmergenceTracker", "SophiaMoment"]

