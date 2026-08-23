"""Append-only run status log for scheduler jobs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_DIR = Path(__file__).resolve().parent / "status"
STATUS_LOG = STATUS_DIR / "status_log.jsonl"


def utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def append_status(
    *,
    job: str,
    status: str,
    started_at: str,
    finished_at: str | None = None,
    error: str | None = None,
    details: dict[str, Any] | None = None,
) -> Path:
    """
    Append one JSON object per line. Always creates the directory.
    Called on success and failure — never silent.

    status: "success" | "failure"
    """
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    finished = finished_at or utc_now_iso()
    payload: dict[str, Any] = {
        "job": job,
        "status": status,
        "started_at": started_at,
        "finished_at": finished,
        "logged_at": utc_now_iso(),
    }
    if error:
        payload["error"] = error
    if details:
        payload["details"] = details
    with STATUS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")
    print(f"[STATUS] appended {STATUS_LOG} :: {job}={status}")
    return STATUS_LOG


def read_status_tail(n: int = 20) -> list[dict[str, Any]]:
    if not STATUS_LOG.exists():
        return []
    lines = STATUS_LOG.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-n:]:
        if line.strip():
            out.append(json.loads(line))
    return out
