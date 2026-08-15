"""Self-serve API key issuance and lookup (SQLite)."""

from __future__ import annotations

import secrets
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

_lock = threading.Lock()
_db_path: Path | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_keys_db(path: Path) -> None:
    global _db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    _db_path = path
    with _lock, sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                api_key TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _conn() -> sqlite3.Connection:
    if _db_path is None:
        raise RuntimeError("keys DB not initialized")
    return sqlite3.connect(_db_path)


def issue_key() -> dict[str, str]:
    """Mint a fresh key immediately — no approval gate."""
    key = "ysk_" + secrets.token_urlsafe(24)
    created = _utc_now()
    with _lock, _conn() as conn:
        conn.execute(
            "INSERT INTO api_keys (api_key, created_at) VALUES (?, ?)",
            (key, created),
        )
        conn.commit()
    return {"api_key": key, "created_at": created}


def key_exists(api_key: str) -> bool:
    if not api_key:
        return False
    with _lock, _conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM api_keys WHERE api_key = ? LIMIT 1",
            (api_key,),
        ).fetchone()
    return row is not None
