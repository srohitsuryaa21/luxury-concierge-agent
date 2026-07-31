"""Conversation persistence.

Deliberately a separate database from the catalogue. `catalog.db` is a build
artifact - `build_database` drops every table and reseeds it, and the file is
gitignored because it regenerates on demand. Conversations are the opposite:
they are the only data in this system that cannot be reconstructed, so they get
their own file that nothing rebuilds.

Each assistant turn stores the full structured result, not just its prose. That
is what lets a reopened conversation render the commission document again
instead of a transcript of text.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id  TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    turn             INTEGER NOT NULL,
    role             TEXT NOT NULL,
    content          TEXT NOT NULL,
    created_at       TEXT NOT NULL,
    -- Denormalised for the conversation list, so it never parses payloads.
    model            TEXT,
    region           TEXT,
    total_eur        INTEGER,
    budget_fit       TEXT,
    brief_source     TEXT,
    config_source    TEXT,
    -- The whole agent result, so a reopened turn re-renders exactly.
    payload          TEXT
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON messages(conversation_id, turn);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _title_from(brief: str, limit: int = 72) -> str:
    single_line = " ".join(brief.split())
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 1].rstrip() + "…"


class ConversationStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            # WAL lets the UI read the history list while a turn is being
            # written, which a synchronous request handler will otherwise block.
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # -- writing ------------------------------------------------------------
    def start(self, brief: str) -> str:
        conversation_id = uuid.uuid4().hex
        stamp = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) "
                "VALUES (?, ?, ?, ?)",
                (conversation_id, _title_from(brief), stamp, stamp),
            )
        return conversation_id

    def record_turn(
        self, conversation_id: str, brief: str, result: dict[str, Any]
    ) -> dict[str, Any]:
        """Append the client's brief and the agent's answer as one exchange."""
        stamp = _now()
        price = result.get("price", {})
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            row = conn.execute(
                "SELECT COALESCE(MAX(turn), 0) AS t FROM messages WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
            turn = int(row["t"]) + 1

            conn.execute(
                "INSERT INTO messages (conversation_id, turn, role, content, created_at) "
                "VALUES (?, ?, 'user', ?, ?)",
                (conversation_id, turn, brief, stamp),
            )
            conn.execute(
                "INSERT INTO messages (conversation_id, turn, role, content, created_at, "
                "model, region, total_eur, budget_fit, brief_source, config_source, payload) "
                "VALUES (?, ?, 'assistant', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    conversation_id,
                    turn,
                    result.get("summary", ""),
                    stamp,
                    (result.get("configuration") or {}).get("model"),
                    result.get("region"),
                    price.get("estimated_total"),
                    price.get("budget_fit"),
                    (result.get("provenance") or {}).get("brief"),
                    (result.get("provenance") or {}).get("configuration"),
                    json.dumps(result),
                ),
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (stamp, conversation_id),
            )
        return {"conversation_id": conversation_id, "turn": turn}

    def delete(self, conversation_id: str) -> bool:
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            cursor = conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            return cursor.rowcount > 0

    # -- reading ------------------------------------------------------------
    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT c.id, c.title, c.created_at, c.updated_at,
                       COUNT(m.id) FILTER (WHERE m.role = 'user') AS turns,
                       MAX(m.model)  AS last_model,
                       MAX(m.region) AS last_region
                FROM conversations c
                LEFT JOIN messages m ON m.conversation_id = c.id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def transcript(self, conversation_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            header = conn.execute(
                "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if header is None:
                return None
            rows = conn.execute(
                "SELECT role, content, payload, created_at FROM messages "
                "WHERE conversation_id = ? ORDER BY turn, id",
                (conversation_id,),
            ).fetchall()

        messages = []
        for row in rows:
            entry: dict[str, Any] = {
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            if row["payload"]:
                entry["result"] = json.loads(row["payload"])
            messages.append(entry)
        return {**dict(header), "messages": messages}

    def memory(self, conversation_id: str, limit: int = 12) -> list[dict[str, str]]:
        """Prior turns in the shape the agent expects for its memory window."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? "
                "ORDER BY turn DESC, id DESC LIMIT ?",
                (conversation_id, limit),
            ).fetchall()
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]
