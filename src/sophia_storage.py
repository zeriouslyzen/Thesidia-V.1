#!/usr/bin/env python3
"""
Sophia Storage Manager
======================

Asynchronous storage manager responsible for persisting Sophia's multi-layer
memory architecture. Supports batch processing, background writes, and
extensible indexing hooks.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Dict, List, Optional, Union

try:  # Optional typing import to avoid circular dependency
    from typing import TYPE_CHECKING
except ImportError:  # pragma: no cover
    TYPE_CHECKING = False  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover
    from sophia_indexer import SophiaIndexer  # noqa: F401  (forward reference)


JsonDict = Dict[str, Any]


@dataclass
class StorageTask:
    """Represents a queued storage operation."""

    path: Path
    payload: JsonDict


class SophiaStorageManager:
    """Handles persistence for Sophia's multi-layer memory system."""

    def __init__(self, base_dir: Union[str, Path], async_mode: bool = True) -> None:
        self.base_dir = Path(base_dir)
        self.root = self.base_dir / "data" / "thesidia_sophia_memory"
        self.async_mode = async_mode
        self.indexer: Optional["SophiaIndexer"] = None

        self._queue: "Queue[Optional[StorageTask]]" = Queue()
        self._worker: Optional[threading.Thread] = None
        if self.async_mode:
            self._worker = threading.Thread(target=self._process_queue, daemon=True)
            self._worker.start()

        self._ensure_directories()

    # ------------------------------------------------------------------ #
    # Public API - Persistence
    # ------------------------------------------------------------------ #
    def save_gnostic_map(self, payload: JsonDict, async_mode: Optional[bool] = None) -> None:
        self._dispatch(self.paths["gnostic_map"] / "current.json", payload, async_mode)

    def load_gnostic_map(self) -> Optional[JsonDict]:
        return self._read_json(self.paths["gnostic_map"] / "current.json")

    def save_emergence_data(self, payload: JsonDict, async_mode: Optional[bool] = None) -> None:
        self._dispatch(self.paths["emergence"] / "latest.json", payload, async_mode)

    def load_emergence_data(self) -> Optional[JsonDict]:
        return self._read_json(self.paths["emergence"] / "latest.json")

    def save_discernment_data(self, payload: JsonDict, async_mode: Optional[bool] = None) -> None:
        self._dispatch(self.paths["discernment"] / "latest.json", payload, async_mode)

    def load_discernment_data(self) -> Optional[JsonDict]:
        return self._read_json(self.paths["discernment"] / "latest.json")

    def save_co_evolution(self, payload: JsonDict, async_mode: Optional[bool] = None) -> None:
        self._dispatch(self.paths["co_evolution"] / "history.json", payload, async_mode)

    def load_co_evolution(self) -> Optional[JsonDict]:
        return self._read_json(self.paths["co_evolution"] / "history.json")

    def save_conversation(
        self,
        session_id: str,
        conversation_data: JsonDict,
        async_mode: Optional[bool] = None,
    ) -> None:
        filename = f"{session_id}.json"
        self._dispatch(self.paths["conversations"] / "sessions" / filename, conversation_data, async_mode)

    def load_conversation(self, session_id: str) -> Optional[JsonDict]:
        filename = f"{session_id}.json"
        return self._read_json(self.paths["conversations"] / "sessions" / filename)

    def index_conversation(self, session_id: str, indexes: JsonDict) -> None:
        if not self.indexer:
            return
        self.indexer.index(session_id, indexes)

    def query_conversations(self, **params: Any) -> List[str]:
        if not self.indexer:
            return []
        return self.indexer.query(**params)

    def create_summary(
        self,
        period: str,
        summary_type: str,
        payload: JsonDict,
        async_mode: Optional[bool] = None,
    ) -> None:
        filename = f"{summary_type}_{period}.json"
        self._dispatch(self.paths["conversations"] / "summaries" / summary_type / filename, payload, async_mode)

    # ------------------------------------------------------------------ #
    # Queue Management
    # ------------------------------------------------------------------ #
    def shutdown(self) -> None:
        if not self.async_mode or not self._worker:
            return
        self._queue.put(None)
        self._worker.join(timeout=2)

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #
    def _dispatch(
        self,
        path: Path,
        payload: JsonDict,
        async_override: Optional[bool],
    ) -> None:
        use_async = self.async_mode if async_override is None else async_override
        if not use_async:
            self._write_json(path, payload)
            return
        self._queue.put(StorageTask(path=path, payload=payload))

    def _process_queue(self) -> None:
        while True:
            try:
                task = self._queue.get(timeout=0.1)
            except Empty:
                continue
            if task is None:
                break
            try:
                self._write_json(task.path, task.payload)
            finally:
                self._queue.task_done()

    def _write_json(self, path: Path, payload: JsonDict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _read_json(self, path: Path) -> Optional[JsonDict]:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _ensure_directories(self) -> None:
        self.paths = {
            "gnostic_map": self.root / "gnostic_map",
            "emergence": self.root / "emergence",
            "discernment": self.root / "discernment",
            "conversations": self.root / "conversations",
            "knowledge_base": self.root / "knowledge_base",
            "co_evolution": self.root / "co_evolution",
        }
        for _, directory in self.paths.items():
            directory.mkdir(parents=True, exist_ok=True)
        # Ensure nested conversation directories exist
        (self.paths["conversations"] / "sessions").mkdir(parents=True, exist_ok=True)
        (self.paths["conversations"] / "summaries" / "daily").mkdir(parents=True, exist_ok=True)
        (self.paths["conversations"] / "summaries" / "weekly").mkdir(parents=True, exist_ok=True)
        (self.paths["conversations"] / "summaries" / "monthly").mkdir(parents=True, exist_ok=True)


__all__ = ["SophiaStorageManager"]

