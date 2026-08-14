"""Request log store for the owner dashboard (separate from API responses)."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_db_path: Path | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_request_log_db(path: Path) -> None:
    global _db_path
    path.parent.mkdir(parents=True, exist_ok=True)
    _db_path = path
    with _lock, sqlite3.connect(path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                caller TEXT NOT NULL,
                method TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                query_params TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _conn() -> sqlite3.Connection:
    if _db_path is None:
        raise RuntimeError("request log DB not initialized")
    return sqlite3.connect(_db_path)


def log_request(
    *,
    caller: str,
    method: str,
    endpoint: str,
    query_params: dict[str, Any] | None = None,
) -> None:
    payload = json.dumps(query_params or {}, sort_keys=True, default=str)
    with _lock, _conn() as conn:
        conn.execute(
            """
            INSERT INTO request_log (ts, caller, method, endpoint, query_params)
            VALUES (?, ?, ?, ?, ?)
            """,
            (_utc_now(), caller, method, endpoint, payload),
        )
        conn.commit()


def recent_requests(limit: int = 200) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 1000))
    with _lock, _conn() as conn:
        rows = conn.execute(
            """
            SELECT ts, caller, method, endpoint, query_params
            FROM request_log
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    out: list[dict[str, Any]] = []
    for ts, caller, method, endpoint, query_params in rows:
        try:
            params = json.loads(query_params)
        except json.JSONDecodeError:
            params = {"raw": query_params}
        out.append(
            {
                "ts": ts,
                "caller": caller,
                "method": method,
                "endpoint": endpoint,
                "query_params": params,
            }
        )
    return out
