"""
Persistent candidate state for discovery.

State is stored in scheduler/candidate_state.json and always re-synced from
the filesystem (candidates/*/FINDINGS.md, ADAPTER_SPEC.md, storage/) so a
fresh checkout of main remembers already-researched assets even when
next_index is stale or discovery PRs were never merged.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path(__file__).resolve().parent / "candidate_state.json"
POOL_PATH = Path(__file__).resolve().parent / "discovery_pool.json"
CANDIDATES_DIR = REPO_ROOT / "candidates"
STORAGE_DIR = REPO_ROOT / "storage"

CLASSIFICATION_RE = re.compile(
    r"\*\*Classification:\s*`([^`]+)`\*\*", re.IGNORECASE
)
READINESS_RE = re.compile(
    r"^\s*status:\s*(adapter-ready|token-data-only|blocked)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Lifecycle states for discovery/research/adapters.
VALID_STATES = (
    "undiscovered",
    "discovered",
    "researching",
    "researched",
    "candidate-for-adapter",
    "adapter-ready",
    "blocked",
    "rejected",
    "adapter-built",
    "live",
)

# Once in these states, discovery must not select as a "new" candidate.
ALREADY_INVESTIGATED_STATES = frozenset(
    {
        "researched",
        "candidate-for-adapter",
        "adapter-ready",
        "blocked",
        "rejected",
        "adapter-built",
        "live",
        "researching",
        "discovered",
    }
)

FINDINGS_TO_STATE = {
    "candidate-for-adapter": "candidate-for-adapter",
    "not-yet-investable": "rejected",
    "wrong-model": "rejected",
    "insufficient-information": "researched",
}


def empty_state() -> dict[str, Any]:
    return {
        "description": (
            "Durable discovery candidate state. Synced from candidates/*/ "
            "and storage/ on every discovery run so unmerged pointer advances "
            "cannot re-select already-investigated assets."
        ),
        "updated_at": None,
        "recent_categories": [],
        "candidates": {},
    }


def load_state() -> dict[str, Any]:
    if not STATE_PATH.is_file():
        return empty_state()
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if "candidates" not in data:
        data["candidates"] = {}
    if "recent_categories" not in data:
        data["recent_categories"] = []
    return data


def save_state(state: dict[str, Any]) -> None:
    state["updated_at"] = date.today().isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def load_pool() -> dict[str, Any]:
    if not POOL_PATH.is_file():
        return {
            "description": "Replenishable physical-RWA discovery pool",
            "candidates": [],
        }
    return json.loads(POOL_PATH.read_text(encoding="utf-8"))


def save_pool(pool: dict[str, Any]) -> None:
    POOL_PATH.write_text(json.dumps(pool, indent=2) + "\n", encoding="utf-8")


def normalize_name(name: str) -> str:
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def host_key(url: str) -> str | None:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return None
    if host.startswith("www."):
        host = host[4:]
    return host or None


def read_findings_classification(slug: str) -> str | None:
    path = CANDIDATES_DIR / slug / "FINDINGS.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    m = CLASSIFICATION_RE.search(text)
    return m.group(1).strip() if m else None


def read_adapter_readiness(slug: str) -> str | None:
    path = CANDIDATES_DIR / slug / "ADAPTER_SPEC.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    m = READINESS_RE.search(text)
    return m.group(1).strip().lower() if m else None


def sync_state_from_filesystem(state: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Rebuild/refresh candidate records from durable repo artifacts.

    This is the persistence backbone: even if backlog next_index is stale and
    discovery PRs were never merged, existing FINDINGS.md means "already
    investigated" and must not be rediscovered.
    """
    state = state or load_state()
    cands: dict[str, Any] = state.setdefault("candidates", {})

    if CANDIDATES_DIR.is_dir():
        for child in sorted(CANDIDATES_DIR.iterdir()):
            if not child.is_dir():
                continue
            slug = child.name
            findings = child / "FINDINGS.md"
            if not findings.is_file():
                continue
            classification = read_findings_classification(slug)
            readiness = read_adapter_readiness(slug)
            rec = cands.get(slug) or {
                "slug": slug,
                "display_name": slug,
                "category": "other_physical_rwa",
                "domains": [],
                "aliases": [],
                "token_addresses": [],
            }
            if classification:
                rec["findings_classification"] = classification
                rec["state"] = FINDINGS_TO_STATE.get(classification, "researched")
            else:
                rec["state"] = "researched"
            if readiness:
                rec["adapter_readiness"] = readiness
                if readiness == "adapter-ready":
                    rec["state"] = "adapter-ready"
                elif readiness == "blocked" and rec.get("state") == "candidate-for-adapter":
                    # Keep candidate-for-adapter disposition; readiness is research detail
                    pass
            rec["has_findings"] = True
            rec["has_adapter_spec"] = (child / "ADAPTER_SPEC.md").is_file()
            rec["investigated"] = True
            cands[slug] = rec

    # Live snapshots under storage/
    if STORAGE_DIR.is_dir():
        for child in sorted(STORAGE_DIR.iterdir()):
            if not child.is_dir():
                continue
            asset_id = child.name
            # Map known live platforms
            if asset_id.startswith("glow-"):
                key = "glow-protocol"
            elif asset_id.startswith("realt-"):
                key = "realt-platform"
            elif asset_id.startswith("elmnts"):
                key = "elmnts"
            else:
                key = asset_id
            rec = cands.get(key) or {"slug": key, "display_name": key}
            rec["state"] = "live"
            rec["live_asset_id"] = asset_id
            rec["investigated"] = True
            cands[key] = rec

    # Rebuild recent_categories from *new-format* FINDINGS (Discovery summary)
    # when empty so a fresh checkout still prefers category diversity without
    # letting legacy category-probes / wrong-model DePIN rows dominate.
    if not state.get("recent_categories"):
        rebuilt: list[str] = []
        if CANDIDATES_DIR.is_dir():
            dated: list[tuple[str, str]] = []
            for child in CANDIDATES_DIR.iterdir():
                findings = child / "FINDINGS.md"
                if not findings.is_file():
                    continue
                text = findings.read_text(encoding="utf-8")
                if "## Discovery summary" not in text:
                    continue
                m = re.search(r"\|\s*Category\s*\|\s*`([^`]+)`", text)
                if not m:
                    continue
                # Prefer date investigated for ordering
                dm = re.search(r"\*\*Date investigated:\*\*\s*([0-9-]+)", text)
                dated.append((dm.group(1) if dm else "1970-01-01", m.group(1)))
            dated.sort()
            rebuilt = [c for _, c in dated]
        state["recent_categories"] = rebuilt[-20:]

    state["candidates"] = cands
    return state


def is_already_investigated(slug: str, state: dict[str, Any]) -> bool:
    if (CANDIDATES_DIR / slug / "FINDINGS.md").is_file():
        return True
    rec = (state.get("candidates") or {}).get(slug) or {}
    if rec.get("investigated"):
        return True
    if rec.get("state") in ALREADY_INVESTIGATED_STATES:
        return True
    if rec.get("skip"):
        return True
    return False


def upsert_candidate_record(
    state: dict[str, Any],
    *,
    slug: str,
    display_name: str,
    category: str | None = None,
    domains: list[str] | None = None,
    aliases: list[str] | None = None,
    status: str = "undiscovered",
    physical_class: str | None = None,
    findings_classification: str | None = None,
    discovery_source: str | None = None,
    notes: str | None = None,
    token_addresses: list[str] | None = None,
) -> dict[str, Any]:
    cands = state.setdefault("candidates", {})
    rec = cands.get(slug) or {"slug": slug}
    rec["slug"] = slug
    rec["display_name"] = display_name
    if category:
        rec["category"] = category
    if domains is not None:
        rec["domains"] = sorted(set(domains))
    if aliases is not None:
        rec["aliases"] = sorted({normalize_name(a) for a in aliases if a})
    if status:
        rec["state"] = status
    if physical_class:
        rec["physical_class"] = physical_class
    if findings_classification:
        rec["findings_classification"] = findings_classification
    if discovery_source:
        rec["discovery_source"] = discovery_source
    if notes is not None:
        rec["notes"] = notes
    if token_addresses is not None:
        rec["token_addresses"] = sorted({a.lower() for a in token_addresses if a})
    cands[slug] = rec
    return rec


def mark_investigated(
    state: dict[str, Any],
    *,
    slug: str,
    display_name: str,
    findings_classification: str,
    category: str | None,
    physical_class: str | None,
    discovery_source: str | None,
    domains: list[str] | None = None,
) -> None:
    mapped = FINDINGS_TO_STATE.get(findings_classification, "researched")
    upsert_candidate_record(
        state,
        slug=slug,
        display_name=display_name,
        category=category,
        domains=domains,
        status=mapped,
        physical_class=physical_class,
        findings_classification=findings_classification,
        discovery_source=discovery_source,
    )
    rec = state["candidates"][slug]
    rec["investigated"] = True
    rec["has_findings"] = True
    if category:
        recent = list(state.get("recent_categories") or [])
        recent.append(category)
        state["recent_categories"] = recent[-20:]
