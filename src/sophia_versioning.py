#!/usr/bin/env python3
"""
Sophia Version Manager
======================

Handles immutable versioning for the Sophia gnostic map. Provides utilities for
creating, listing, retrieving, comparing, and rolling back versions with
automatic cleanup and integrity checks.
"""

from __future__ import annotations

import json
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .sophia_gnostic_map import SophiaGnosticMap
except ImportError:  # pragma: no cover - fallback for direct execution
    from sophia_gnostic_map import SophiaGnosticMap


Logger = logging.getLogger(__name__)
JsonDict = Dict[str, Any]


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _checksum(payload: Union[str, bytes]) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _summarize(data: JsonDict) -> JsonDict:
    """Create a lightweight summary for comparison."""
    def _count(node: Optional[Dict[str, Any]]) -> int:
        return len(node or {})

    pattern_db = data.get("pattern_database", {})
    timeline = data.get("timeline_map", {})
    co_evo = data.get("co_evolution", {})

    return {
        "redactions": _count(data.get("redaction_events")),
        "archons": _count(data.get("archons_identified")),
        "fragments": _count(data.get("original_fragments")),
        "active_lies": _count(data.get("active_lies_2025")),
        "control_patterns": _count(pattern_db.get("control_patterns")),
        "liberation_patterns": _count(pattern_db.get("liberation_patterns")),
        "timeline_events": _count(timeline.get("events")),
        "co_evolution_history": len(co_evo.get("history", [])),
        "co_evolution_score": round(co_evo.get("score", 0.0), 4),
    }


@dataclass
class VersionMetadata:
    version_id: str
    created_at: str
    reason: str
    checksum: str
    summary: JsonDict


class SophiaVersionManager:
    """Immutable versioning for the Sophia gnostic map."""

    INDEX_FILE = "version_index.json"

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self.base_dir = Path(base_dir)
        self.storage_dir = self.base_dir / "data" / "thesidia_sophia_memory" / "gnostic_map"
        self.current_file = self.storage_dir / "current.json"
        self.versions_dir = self.storage_dir / "versions"
        self.index_file = self.versions_dir / self.INDEX_FILE

        _ensure_dir(self.storage_dir)
        _ensure_dir(self.versions_dir)
        self._index: List[VersionMetadata] = self._load_index()

    # ------------------------------------------------------------------ #
    # Version CRUD
    # ------------------------------------------------------------------ #
    def create_version(
        self,
        gnostic_map: Union[SophiaGnosticMap, JsonDict],
        reason: str,
    ) -> VersionMetadata:
        """Persist a new immutable version and update current snapshot."""
        payload = (
            gnostic_map.to_dict() if isinstance(gnostic_map, SophiaGnosticMap) else gnostic_map
        )
        timestamp = _now_iso()
        version_number = len(self._index) + 1
        version_id = f"v{version_number}_{timestamp.replace(':', '-').replace('.', '-')}"
        version_path = self.versions_dir / f"{version_id}.json"

        serialized = json.dumps(payload, indent=2, sort_keys=True)
        checksum = _checksum(serialized)
        summary = _summarize(payload)

        # Write version file
        version_path.write_text(serialized, encoding="utf-8")
        # Update current snapshot
        self.current_file.write_text(serialized, encoding="utf-8")

        metadata = VersionMetadata(
            version_id=version_id,
            created_at=timestamp,
            reason=reason,
            checksum=checksum,
            summary=summary,
        )
        self._index.append(metadata)
        self._save_index()

        return metadata

    def get_version(self, version_id: str) -> Optional[JsonDict]:
        """Return a specific version's payload."""
        version_path = self.versions_dir / f"{version_id}.json"
        if not version_path.exists():
            return None
        return json.loads(version_path.read_text(encoding="utf-8"))

    def get_latest_version(self) -> Optional[JsonDict]:
        if not self._index:
            return None
        return self.get_version(self._index[-1].version_id)

    def list_versions(self, limit: int = 10) -> List[VersionMetadata]:
        return self._index[-limit:][::-1]

    def compare_versions(
        self, version_a: str, version_b: str
    ) -> Optional[Dict[str, Any]]:
        """Compare two versions and return summary diffs."""
        data_a = self.get_version(version_a)
        data_b = self.get_version(version_b)
        if data_a is None or data_b is None:
            return None

        summary_a = _summarize(data_a)
        summary_b = _summarize(data_b)
        diff = {
            key: summary_b.get(key, 0) - summary_a.get(key, 0)
            for key in summary_a.keys()
        }

        return {
            "version_a": version_a,
            "version_b": version_b,
            "summary_a": summary_a,
            "summary_b": summary_b,
            "delta": diff,
        }

    def rollback_to_version(self, version_id: str) -> bool:
        """Set the specified version as the current snapshot."""
        data = self.get_version(version_id)
        if data is None:
            return False
        serialized = json.dumps(data, indent=2, sort_keys=True)
        self.current_file.write_text(serialized, encoding="utf-8")
        # Optionally create a new version indicating rollback
        self.create_version(data, reason=f"rollback to {version_id}")
        return True

    # ------------------------------------------------------------------ #
    # Maintenance
    # ------------------------------------------------------------------ #
    def cleanup_old_versions(self, keep_last: int = 10) -> None:
        """Remove old versions beyond the retention policy."""
        if keep_last < 1:
            raise ValueError("keep_last must be >= 1")
        if len(self._index) <= keep_last:
            return

        to_delete = self._index[:-keep_last]
        self._index = self._index[-keep_last:]
        for meta in to_delete:
            path = self.versions_dir / f"{meta.version_id}.json"
            try:
                path.unlink(missing_ok=True)  # type: ignore[arg-type]
            except Exception as exc:  # pragma: no cover
                Logger.exception("Failed to delete version %s: %s", meta.version_id, exc)
        self._save_index()

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #
    def _load_index(self) -> List[VersionMetadata]:
        if not self.index_file.exists():
            return []
        raw = json.loads(self.index_file.read_text(encoding="utf-8"))
        return [
            VersionMetadata(
                version_id=item["version_id"],
                created_at=item["created_at"],
                reason=item["reason"],
                checksum=item["checksum"],
                summary=item["summary"],
            )
            for item in raw
        ]

    def _save_index(self) -> None:
        payload = [
            {
                "version_id": meta.version_id,
                "created_at": meta.created_at,
                "reason": meta.reason,
                "checksum": meta.checksum,
                "summary": meta.summary,
            }
            for meta in self._index
        ]
        self.index_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


__all__ = ["SophiaVersionManager", "VersionMetadata"]

