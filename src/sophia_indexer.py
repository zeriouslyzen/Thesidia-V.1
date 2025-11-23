#!/usr/bin/env python3
"""
Sophia Indexer
==============

Handles fast lookup of conversations, patterns, archons, and redactions by
maintaining lightweight inverted indexes.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional, Set, Union


IndexDict = DefaultDict[str, Set[str]]


class SophiaIndexer:
    """Maintains inverted indexes for Sophia's conversation memory."""

    INDEX_TYPES = ("topic", "pattern", "archon", "redaction")

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self.base_dir = Path(base_dir)
        self.index_root = self.base_dir / "data" / "thesidia_sophia_memory" / "conversations" / "indexed"
        self.index_root.mkdir(parents=True, exist_ok=True)

        self._indexes: Dict[str, IndexDict] = {
            name: defaultdict(set) for name in self.INDEX_TYPES
        }
        self._load_indexes()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def index(self, session_id: str, data: Dict[str, Iterable[str]]) -> None:
        """Index a conversation by various facets."""
        topics = data.get("topics", [])
        patterns = data.get("patterns", [])
        archons = data.get("archons", [])
        redactions = data.get("redactions", [])

        self._index_values("topic", session_id, topics)
        self._index_values("pattern", session_id, patterns)
        self._index_values("archon", session_id, archons)
        self._index_values("redaction", session_id, redactions)

        self._save_indexes()

    def query(self, *, index_type: str, term: str) -> List[str]:
        """Query an index by term."""
        index_type = index_type.lower()
        if index_type not in self._indexes:
            raise ValueError(f"Unsupported index type: {index_type}")
        key = term.strip().lower()
        return sorted(self._indexes[index_type].get(key, []))

    def rebuild(self) -> None:
        """Clear and rebuild indexes (placeholder for future batch rebuild)."""
        for index in self._indexes.values():
            index.clear()
        self._save_indexes()

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #
    def _index_values(self, index_type: str, session_id: str, values: Iterable[str]) -> None:
        if not values:
            return
        index = self._indexes[index_type]
        for value in values:
            key = value.strip().lower()
            if key:
                index[key].add(session_id)

    def _load_indexes(self) -> None:
        for index_type in self.INDEX_TYPES:
            path = self._index_path(index_type)
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            index = self._indexes[index_type]
            for key, sessions in payload.items():
                index[key].update(sessions)

    def _save_indexes(self) -> None:
        for index_type in self.INDEX_TYPES:
            path = self._index_path(index_type)
            serializable = {key: sorted(list(values)) for key, values in self._indexes[index_type].items()}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def _index_path(self, index_type: str) -> Path:
        return self.index_root / f"by_{index_type}.json"


__all__ = ["SophiaIndexer"]

