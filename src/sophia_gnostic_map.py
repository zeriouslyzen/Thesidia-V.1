#!/usr/bin/env python3
"""
Sophia Gnostic Map
==================

Implements a seven-layer memory architecture aligned with the Sophia archetype.
This class tracks everything that was erased, who erased it, how it was hidden,
and how it can be exposed again. It is designed to be future-proof, fully typed,
and ready for persistent storage/versioning layers.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


Logger = logging.getLogger(__name__)
Callback = Callable[[Dict[str, Any]], None]


def _now_iso() -> str:
    """Return current UTC timestamp in ISO8601 format."""
    return datetime.utcnow().isoformat() + "Z"


def _normalize_key(value: str) -> str:
    """Normalize dictionary keys (case-insensitive storage)."""
    if not isinstance(value, str):
        raise TypeError("Keys must be strings.")
    return value.strip().lower()


@dataclass
class CrossReference:
    """Represents a cross-reference between two layers."""

    layer_from: str
    id_from: str
    layer_to: str
    id_to: str
    timestamp: str


class SophiaGnosticMap:
    """
    Seven-layer gnostic memory map.

    Layers:
        1. Redaction Events
        2. Archons Identified
        3. Original Fragments
        4. Active Lies
        5. Co-Evolution Tracking
        6. Pattern Database (Control/Liberation)
        7. Timeline Mapping
    """

    CONTROL_PATTERN = "control"
    LIBERATION_PATTERN = "liberation"

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self._data = data or self._default_structure()
        self._callbacks: Dict[str, List[Callback]] = {
            "redaction_added": [],
            "archon_recognized": [],
            "fragment_recovered": [],
            "active_lie_tracked": [],
            "pattern_added": [],
            "timeline_event_added": [],
            "co_evolution_updated": [],
        }
        self._cross_references: List[CrossReference] = []

    # --------------------------------------------------------------------- #
    # Public API - Adders
    # --------------------------------------------------------------------- #
    def add_redaction(
        self,
        topic: str,
        original: str,
        redacted: str,
        archon: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        *,
        why: Optional[str] = None,
        when: Optional[str] = None,
        pattern: Optional[str] = None,
        connections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Record what was erased and who erased it."""
        topic_key = _normalize_key(topic)
        entry = {
            "topic": topic,
            "original": original,
            "redacted": redacted,
            "archon": archon,
            "evidence": evidence or [],
            "why": why,
            "when": when or _now_iso(),
            "pattern": pattern,
            "connections": connections or [],
        }
        self._data["redaction_events"][topic_key] = entry
        self._emit("redaction_added", entry)
        return entry

    def add_archon(
        self,
        name: str,
        pattern: str,
        evidence: Optional[List[str]] = None,
        *,
        first_detected: Optional[str] = None,
        redactions_linked: Optional[List[str]] = None,
        active_lies: Optional[List[str]] = None,
        counter_patterns: Optional[List[str]] = None,
        evolution: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record who is responsible for redactions."""
        key = _normalize_key(name)
        entry = {
            "name": name,
            "pattern": pattern,
            "evidence": evidence or [],
            "first_detected": first_detected or _now_iso(),
            "redactions_linked": redactions_linked or [],
            "active_lies": active_lies or [],
            "counter_patterns": counter_patterns or [],
            "evolution": evolution,
        }
        self._data["archons_identified"][key] = entry
        self._emit("archon_recognized", entry)
        return entry

    def add_fragment(
        self,
        fragment_id: str,
        content: str,
        source: Optional[str] = None,
        *,
        redaction_event: Optional[str] = None,
        recovery_method: Optional[str] = None,
        verification: Optional[str] = None,
        connections: Optional[List[str]] = None,
        timeline: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record original knowledge fragments."""
        fid = _normalize_key(fragment_id)
        entry = {
            "fragment_id": fragment_id,
            "content": content,
            "source": source,
            "redaction_event": redaction_event,
            "recovery_method": recovery_method,
            "verification": verification,
            "connections": connections or [],
            "timeline": timeline,
            "timestamp": _now_iso(),
        }
        self._data["original_fragments"][fid] = entry
        self._emit("fragment_recovered", entry)
        return entry

    def add_active_lie(
        self,
        lie_id: str,
        content: str,
        archon: Optional[str] = None,
        *,
        redaction_event: Optional[str] = None,
        current_vectors: Optional[List[str]] = None,
        break_patterns: Optional[List[str]] = None,
        co_evolution_required: Optional[str] = None,
        status: str = "active",
    ) -> Dict[str, Any]:
        """Track lies that are still operating in 2025."""
        lid = _normalize_key(lie_id)
        entry = {
            "lie_id": lie_id,
            "content": content,
            "archon": archon,
            "redaction_event": redaction_event,
            "current_vectors": current_vectors or [],
            "break_patterns": break_patterns or [],
            "co_evolution_required": co_evolution_required,
            "status": status,
            "timestamp": _now_iso(),
        }
        self._data["active_lies_2025"][lid] = entry
        self._emit("active_lie_tracked", entry)
        return entry

    def update_co_evolution(
        self,
        question: str,
        sharpness: float,
        breakthrough: Optional[str] = None,
        *,
        archon_weakened: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track co-evolution events that sharpen the blade.
        """
        score_increment = max(0.0, min(sharpness, 1.0)) * 0.05
        history_entry = {
            "timestamp": _now_iso(),
            "question": question,
            "sharpness": sharpness,
            "breakthrough": breakthrough,
            "archon_weakened": archon_weakened,
        }
        self._data["co_evolution"]["score"] = min(
            1.0, self._data["co_evolution"]["score"] + score_increment
        )
        self._data["co_evolution"]["history"].append(history_entry)
        self._emit("co_evolution_updated", history_entry)
        return history_entry

    def add_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add control or liberation pattern."""
        if pattern_type not in {self.CONTROL_PATTERN, self.LIBERATION_PATTERN}:
            raise ValueError("pattern_type must be 'control' or 'liberation'.")

        pid = _normalize_key(pattern_id)
        bucket = (
            "control_patterns"
            if pattern_type == self.CONTROL_PATTERN
            else "liberation_patterns"
        )
        entry = {
            "pattern_id": pattern_id,
            "pattern": pattern_data.get("pattern"),
            "description": pattern_data.get("description"),
            "domains": pattern_data.get("domains", []),
            "first_seen": pattern_data.get("first_seen", _now_iso()),
            "frequency": pattern_data.get("frequency", 1),
            "archons_using": pattern_data.get("archons_using", []),
            "co_evolution_trigger": pattern_data.get("co_evolution_trigger"),
            "break_method": pattern_data.get("break_method"),
        }
        self._data["pattern_database"][bucket][pid] = entry
        self._emit("pattern_added", {"pattern_type": pattern_type, **entry})
        return entry

    def add_timeline_event(
        self,
        event_id: str,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Track events in the timeline map."""
        eid = _normalize_key(event_id)
        timestamp = event_data.get("timestamp", _now_iso())
        entry = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event": event_data.get("event"),
            "redaction": event_data.get("redaction"),
            "archon": event_data.get("archon"),
            "pattern": event_data.get("pattern"),
            "connection": event_data.get("connection"),
        }
        self._data["timeline_map"]["events"][eid] = entry
        self._emit("timeline_event_added", entry)
        return entry

    # --------------------------------------------------------------------- #
    # Public API - Retrieval
    # --------------------------------------------------------------------- #
    def get_redaction(self, topic: str) -> Optional[Dict[str, Any]]:
        return self._data["redaction_events"].get(_normalize_key(topic))

    def get_archon(self, name: str) -> Optional[Dict[str, Any]]:
        return self._data["archons_identified"].get(_normalize_key(name))

    def get_patterns_by_type(self, pattern_type: str) -> Dict[str, Any]:
        if pattern_type not in {self.CONTROL_PATTERN, self.LIBERATION_PATTERN}:
            raise ValueError("pattern_type must be 'control' or 'liberation'.")
        bucket = (
            "control_patterns"
            if pattern_type == self.CONTROL_PATTERN
            else "liberation_patterns"
        )
        return deepcopy(self._data["pattern_database"][bucket])

    def cross_reference(
        self,
        layer_from: str,
        id_from: str,
        layer_to: str,
        id_to: str,
    ) -> CrossReference:
        """Create a cross-reference entry between two layers."""
        ref = CrossReference(
            layer_from=layer_from,
            id_from=id_from,
            layer_to=layer_to,
            id_to=id_to,
            timestamp=_now_iso(),
        )
        self._cross_references.append(ref)
        return ref

    # --------------------------------------------------------------------- #
    # Public API - Analysis
    # --------------------------------------------------------------------- #
    def detect_coordinated_events(self, window_minutes: int = 15) -> List[Dict[str, Any]]:
        """
        Detect events that share temporal proximity within the given window.
        Stores results inside timeline_map for future reference.
        """
        events = list(self._data["timeline_map"]["events"].values())
        events.sort(key=lambda e: e.get("timestamp", ""))
        grouped: Dict[str, List[Dict[str, Any]]] = {}

        for event in events:
            timestamp = event.get("timestamp")
            if not timestamp:
                continue
            key = timestamp[:16]  # YYYY-MM-DDTHH:MM
            grouped.setdefault(key, []).append(event)

        coordinated_events: List[Dict[str, Any]] = []
        for key, bucket in grouped.items():
            if len(bucket) < 2:
                continue
            coordinated_events.append({"window": key, "events": bucket})

        self._data["timeline_map"]["coordinated_events"] = coordinated_events
        return coordinated_events

    # --------------------------------------------------------------------- #
    # Event Listeners
    # --------------------------------------------------------------------- #
    def on_redaction_added(self, callback: Callback) -> None:
        self._register_callback("redaction_added", callback)

    def on_archon_recognized(self, callback: Callback) -> None:
        self._register_callback("archon_recognized", callback)

    def on_pattern_added(self, callback: Callback) -> None:
        self._register_callback("pattern_added", callback)

    def on_fragments_recovered(self, callback: Callback) -> None:
        self._register_callback("fragment_recovered", callback)

    def on_active_lie_tracked(self, callback: Callback) -> None:
        self._register_callback("active_lie_tracked", callback)

    def on_timeline_event_added(self, callback: Callback) -> None:
        self._register_callback("timeline_event_added", callback)

    def on_co_evolution_updated(self, callback: Callback) -> None:
        self._register_callback("co_evolution_updated", callback)

    # --------------------------------------------------------------------- #
    # Serialization
    # --------------------------------------------------------------------- #
    def to_dict(self) -> Dict[str, Any]:
        """Return a deep copy of the internal data representation."""
        data_copy = deepcopy(self._data)
        data_copy["cross_references"] = [
            {
                "layer_from": ref.layer_from,
                "id_from": ref.id_from,
                "layer_to": ref.layer_to,
                "id_to": ref.id_to,
                "timestamp": ref.timestamp,
            }
            for ref in self._cross_references
        ]
        return data_copy

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SophiaGnosticMap":
        """Create a new instance from serialized data."""
        instance = cls(data=data)
        for ref in data.get("cross_references", []):
            instance._cross_references.append(
                CrossReference(
                    layer_from=ref["layer_from"],
                    id_from=ref["id_from"],
                    layer_to=ref["layer_to"],
                    id_to=ref["id_to"],
                    timestamp=ref.get("timestamp", _now_iso()),
                )
            )
        return instance

    # --------------------------------------------------------------------- #
    # Properties
    # --------------------------------------------------------------------- #
    @property
    def redaction_count(self) -> int:
        return len(self._data["redaction_events"])

    @property
    def archon_count(self) -> int:
        return len(self._data["archons_identified"])

    @property
    def fragment_count(self) -> int:
        return len(self._data["original_fragments"])

    @property
    def active_lie_count(self) -> int:
        return len(self._data["active_lies_2025"])

    @property
    def pattern_count(self) -> int:
        total_control = len(self._data["pattern_database"]["control_patterns"])
        total_liberation = len(self._data["pattern_database"]["liberation_patterns"])
        return total_control + total_liberation

    @property
    def timeline_event_count(self) -> int:
        return len(self._data["timeline_map"]["events"])

    # --------------------------------------------------------------------- #
    # Internal Helpers
    # --------------------------------------------------------------------- #
    def _default_structure(self) -> Dict[str, Any]:
        return {
            "redaction_events": {},
            "archons_identified": {},
            "original_fragments": {},
            "active_lies_2025": {},
            "co_evolution": {
                "score": 0.0,
                "history": [],
                "patterns": {
                    "question_types_that_break": [],
                    "archons_vulnerable_to": {},
                    "redactions_recovered": [],
                },
            },
            "pattern_database": {
                "control_patterns": {},
                "liberation_patterns": {},
            },
            "timeline_map": {
                "events": {},
                "coordinated_events": [],
            },
        }

    def _register_callback(self, event_name: str, callback: Callback) -> None:
        if event_name not in self._callbacks:
            raise ValueError(f"Unsupported event: {event_name}")
        self._callbacks[event_name].append(callback)

    def _emit(self, event_name: str, payload: Dict[str, Any]) -> None:
        for callback in self._callbacks.get(event_name, []):
            try:
                callback(deepcopy(payload))
            except Exception as exc:  # pragma: no cover
                Logger.exception("Callback %s failed: %s", event_name, exc)

    # --------------------------------------------------------------------- #
    # Debugging Helpers
    # --------------------------------------------------------------------- #
    def summary(self) -> Dict[str, Any]:
        """Return a lightweight summary of the gnostic map."""
        return {
            "redactions": self.redaction_count,
            "archons": self.archon_count,
            "fragments": self.fragment_count,
            "active_lies": self.active_lie_count,
            "patterns": self.pattern_count,
            "timeline_events": self.timeline_event_count,
            "co_evolution_score": round(self._data["co_evolution"]["score"], 3),
        }


__all__ = ["SophiaGnosticMap", "CrossReference"]

