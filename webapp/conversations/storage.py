#!/usr/bin/env python3
"""
Conversation storage abstraction.

Default implementation uses SQLite (stdlib `sqlite3`).
Designed so we can later swap to Supabase/Firebase adapters without rewriting API handlers.
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class ConversationMessage:
    role: str  # "user" | "thesidia" | "system"
    content: str
    ts_ms: int


@dataclass(frozen=True)
class ConversationRecord:
    conversation_id: str
    user_id: Optional[str]
    session_id: Optional[str]
    title: str
    preview: str
    created_at_ms: int
    updated_at_ms: int
    messages: List[ConversationMessage]


class ConversationStore:
    def upsert_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
        title: str,
        preview: str,
        messages: List[ConversationMessage],
    ) -> None:
        raise NotImplementedError

    def list_conversations(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        limit: int = 50,
    ) -> List[JsonDict]:
        """Return lightweight list for sidebar."""
        raise NotImplementedError

    def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
    ) -> Optional[JsonDict]:
        raise NotImplementedError


class SQLiteConversationStore(ConversationStore):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # Better durability defaults without killing dev perf
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    session_id TEXT,
                    title TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ts_ms INTEGER NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id, updated_at_ms);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id, updated_at_ms);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_msgs_conv ON conversation_messages(conversation_id, ts_ms);")

    def upsert_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
        title: str,
        preview: str,
        messages: List[ConversationMessage],
    ) -> None:
        now_ms = int(time.time() * 1000)
        created_ms = now_ms

        with self._conn() as conn:
            existing = conn.execute(
                "SELECT created_at_ms FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            if existing is not None:
                created_ms = int(existing["created_at_ms"])

            conn.execute(
                """
                INSERT INTO conversations (conversation_id, user_id, session_id, title, preview, created_at_ms, updated_at_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    session_id=excluded.session_id,
                    title=excluded.title,
                    preview=excluded.preview,
                    updated_at_ms=excluded.updated_at_ms;
                """,
                (conversation_id, user_id, session_id, title, preview, created_ms, now_ms),
            )

            # Replace messages (simple and robust for small chats)
            conn.execute("DELETE FROM conversation_messages WHERE conversation_id = ?", (conversation_id,))
            conn.executemany(
                """
                INSERT INTO conversation_messages (conversation_id, role, content, ts_ms)
                VALUES (?, ?, ?, ?)
                """,
                [(conversation_id, m.role, m.content, int(m.ts_ms)) for m in messages],
            )

    def list_conversations(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        limit: int = 50,
    ) -> List[JsonDict]:
        limit = max(1, min(int(limit), 200))
        where = []
        params: List[Any] = []
        if user_id:
            where.append("user_id = ?")
            params.append(user_id)
        if session_id:
            where.append("session_id = ?")
            params.append(session_id)
        clause = " AND ".join(where) if where else "1=1"

        with self._conn() as conn:
            rows = conn.execute(
                f"""
                SELECT conversation_id, title, preview, updated_at_ms
                FROM conversations
                WHERE {clause}
                ORDER BY updated_at_ms DESC
                LIMIT ?;
                """,
                (*params, limit),
            ).fetchall()
        return [
            {
                "id": r["conversation_id"],
                "title": r["title"],
                "preview": r["preview"],
                "timestamp": r["updated_at_ms"],
            }
            for r in rows
        ]

    def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
    ) -> Optional[JsonDict]:
        with self._conn() as conn:
            conv = conn.execute(
                """
                SELECT conversation_id, user_id, session_id, title, preview, created_at_ms, updated_at_ms
                FROM conversations WHERE conversation_id = ?;
                """,
                (conversation_id,),
            ).fetchone()
            if conv is None:
                return None

            # Optional scope check (prevents cross-user bleed in multi-user deployments)
            if user_id and conv["user_id"] and conv["user_id"] != user_id:
                return None
            if session_id and conv["session_id"] and conv["session_id"] != session_id:
                return None

            msgs = conn.execute(
                """
                SELECT role, content, ts_ms
                FROM conversation_messages
                WHERE conversation_id = ?
                ORDER BY ts_ms ASC, id ASC;
                """,
                (conversation_id,),
            ).fetchall()

        return {
            "id": conv["conversation_id"],
            "user_id": conv["user_id"],
            "session_id": conv["session_id"],
            "title": conv["title"],
            "preview": conv["preview"],
            "created_at": conv["created_at_ms"],
            "timestamp": conv["updated_at_ms"],
            "messages": [{"type": m["role"], "content": m["content"], "timestamp": m["ts_ms"]} for m in msgs],
        }


def build_store(base_dir: Path) -> ConversationStore:
    """
    Factory with Supabase support.
    
    Auto-detects based on SUPABASE_URL environment variable.
    Falls back to SQLite if Supabase not configured or fails.
    """
    # Import here to avoid circular dependency
    try:
        from .supabase_storage import build_store as build_supabase_store
        return build_supabase_store(base_dir=base_dir)
    except ImportError:
        # Supabase module not available, use SQLite
        print("📁 Using SQLite storage (supabase_storage not found)")
        db_path = base_dir / "data" / "conversations.sqlite3"
        return SQLiteConversationStore(db_path=db_path)




