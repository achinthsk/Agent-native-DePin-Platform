"""
Shared query / filter / lookup for scored assets.

Both MCP and REST call this module. Score values come only from
scoring.engine — this file never recomputes or overrides them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY_PATH = ROOT / "scoring" / "METHODOLOGY.md"
WEIGHTS_PATH = ROOT / "scoring" / "weights.yaml"

import sys

sys.path.insert(0, str(ROOT))
from scoring.engine import score_storage  # noqa: E402

SortField = Literal[
    "asset_id",
    "risk_score",
    "liquidity_score",
    "yield_score",
    "data_confidence_score",
    "snapshot_age_days",
]

NOTES_LIST = [
    "Scores computed live from storage snapshots via scoring.engine.",
    "Descriptive and comparative only — not investment advice.",
]

NOTES_DETAIL = [
    "Descriptive scored snapshot data only — not investment advice.",
]

NOTES_METHODOLOGY = [
    "Methodology text is informational. Score values always come from scoring.engine.",
]


def _load_snapshot(snapshot_file: str) -> dict[str, Any]:
    path = ROOT / snapshot_file
    return json.loads(path.read_text(encoding="utf-8"))


def _jurisdiction_eligibility(
    regulatory: dict[str, Any],
    holder_jurisdiction: str | None,
) -> dict[str, Any]:
    restricted = list(regulatory.get("restricted_jurisdictions") or [])
    permitted = list(regulatory.get("permitted_jurisdictions") or [])

    if holder_jurisdiction is None:
        return {
            "queried_jurisdiction": None,
            "eligibility": "unknown",
        }

    code = holder_jurisdiction.upper()
    if code in restricted:
        return {"queried_jurisdiction": code, "eligibility": "restricted"}
    if permitted and code not in permitted:
        return {
            "queried_jurisdiction": code,
            "eligibility": "not_listed_in_permitted",
        }
    if not permitted and not restricted:
        # Schema rule: both empty ⇒ unknown, not worldwide clearance.
        return {"queried_jurisdiction": code, "eligibility": "unknown"}
    return {"queried_jurisdiction": code, "eligibility": "eligible"}


def _enrich(
    scored: dict[str, Any],
    *,
    holder_jurisdiction: str | None = None,
) -> dict[str, Any]:
    """Attach identity/regulatory fields from the scored snapshot. Scores untouched."""
    snap = _load_snapshot(scored["snapshot_file"])
    regulatory = snap.get("regulatory") or {}
    conf = scored.get("data_confidence_score") or {}
    age = (conf.get("inputs") or {}).get("snapshot_age_days")

    return {
        "asset_id": scored.get("asset_id"),
        "name": snap.get("name"),
        "asset_class": snap.get("asset_class"),
        "source_platform": scored.get("source_platform") or snap.get("source_platform"),
        "schema_version": scored.get("schema_version") or snap.get("schema_version"),
        "snapshot_file": scored.get("snapshot_file"),
        "data_pulled_at": snap.get("data_pulled_at"),
        "snapshot_age_days": age,
        "regulatory": {
            "regulatory_wrapper": regulatory.get("regulatory_wrapper"),
            "accreditation_required": regulatory.get("accreditation_required"),
            "restricted_jurisdictions": list(
                regulatory.get("restricted_jurisdictions") or []
            ),
            "permitted_jurisdictions": list(
                regulatory.get("permitted_jurisdictions") or []
            ),
        },
        "jurisdiction_note": _jurisdiction_eligibility(regulatory, holder_jurisdiction),
        "yield_score": scored.get("yield_score"),
        "risk_score": scored.get("risk_score"),
        "liquidity_score": scored.get("liquidity_score"),
        "data_confidence_score": scored.get("data_confidence_score"),
        "weights_version": scored.get("weights_version"),
        "scored_at": scored.get("scored_at"),
    }


def _score_value(asset: dict[str, Any], field: str) -> float | None:
    if field == "asset_id":
        return None
    if field == "snapshot_age_days":
        age = asset.get("snapshot_age_days")
        return float(age) if age is not None else None
    obj = asset.get(field) or {}
    if obj.get("insufficient_data"):
        return None
    val = obj.get("value")
    return float(val) if val is not None else None


def _passes_min_score(asset: dict[str, Any], key: str, minimum: float | None) -> bool:
    if minimum is None:
        return True
    obj = asset.get(key) or {}
    if obj.get("insufficient_data") or obj.get("value") is None:
        return False
    return float(obj["value"]) >= float(minimum)


def list_scored_assets(
    *,
    asset_class: str | None = None,
    min_risk_score: float | None = None,
    min_liquidity_score: float | None = None,
    holder_jurisdiction: str | None = None,
    include_unknown_jurisdiction: bool = True,
    regulatory_wrapper: str | None = None,
    sort_by: SortField = "asset_id",
    sort_desc: bool = False,
    latest_only: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    limit = max(1, min(int(limit), 200))
    offset = max(0, int(offset))

    raw = score_storage(latest_only=latest_only)
    assets = [
        _enrich(s, holder_jurisdiction=holder_jurisdiction) for s in raw
    ]

    if asset_class is not None:
        assets = [a for a in assets if a.get("asset_class") == asset_class]

    if regulatory_wrapper is not None:
        assets = [
            a
            for a in assets
            if (a.get("regulatory") or {}).get("regulatory_wrapper")
            == regulatory_wrapper
        ]

    assets = [
        a
        for a in assets
        if _passes_min_score(a, "risk_score", min_risk_score)
        and _passes_min_score(a, "liquidity_score", min_liquidity_score)
    ]

    if holder_jurisdiction is not None:
        allowed = {"eligible"}
        if include_unknown_jurisdiction:
            allowed.add("unknown")
        assets = [
            a
            for a in assets
            if (a.get("jurisdiction_note") or {}).get("eligibility") in allowed
        ]

    reverse = bool(sort_desc)

    def sort_key_stable(a: dict[str, Any]) -> tuple:
        if sort_by == "asset_id":
            return (0, a.get("asset_id") or "")
        val = _score_value(a, sort_by)
        missing = val is None
        # Design: nulls last when descending, first when ascending.
        if reverse:
            return (1 if missing else 0, -(val or 0.0), a.get("asset_id") or "")
        return (0 if missing else 1, val or 0.0, a.get("asset_id") or "")

    assets_sorted = sorted(assets, key=sort_key_stable)

    total = len(assets_sorted)
    page = assets_sorted[offset : offset + limit]

    return {
        "query": {
            "asset_class": asset_class,
            "min_risk_score": min_risk_score,
            "min_liquidity_score": min_liquidity_score,
            "holder_jurisdiction": holder_jurisdiction,
            "include_unknown_jurisdiction": include_unknown_jurisdiction,
            "regulatory_wrapper": regulatory_wrapper,
            "sort_by": sort_by,
            "sort_desc": sort_desc,
            "latest_only": latest_only,
            "limit": limit,
            "offset": offset,
        },
        "total_matched": total,
        "limit": limit,
        "offset": offset,
        "assets": page,
        "notes": list(NOTES_LIST),
    }


def get_scored_asset(
    asset_id: str,
    *,
    latest_only: bool = True,
    holder_jurisdiction: str | None = None,
) -> dict[str, Any]:
    raw = score_storage(latest_only=False)
    matches = [s for s in raw if s.get("asset_id") == asset_id]
    if not matches:
        return {
            "asset": None,
            "assets": [],
            "error": f"No scored snapshot found for asset_id={asset_id!r}",
            "notes": list(NOTES_DETAIL),
        }

    matches_sorted = sorted(matches, key=lambda s: s.get("snapshot_file") or "")
    if latest_only:
        chosen = matches_sorted[-1]
        return {
            "asset": _enrich(chosen, holder_jurisdiction=holder_jurisdiction),
            "notes": list(NOTES_DETAIL),
        }

    return {
        "assets": [
            _enrich(s, holder_jurisdiction=holder_jurisdiction)
            for s in matches_sorted
        ],
        "notes": list(NOTES_DETAIL),
    }


def _methodology_summary() -> dict[str, Any]:
    return {
        "four_scores": [
            {
                "name": "yield_score",
                "direction": "higher_is_better",
                "summary": (
                    "Maps advertised/realized yield through a curve; null both "
                    "yields → insufficient_data; gap and implausibility penalties apply."
                ),
            },
            {
                "name": "risk_score",
                "direction": "higher_is_better",
                "summary": (
                    "Risk quality (safer ↑) from verification_tier, ages, payout "
                    "cycles, exposure_type; positive advertised−realized gap "
                    "multiplies the score down."
                ),
            },
            {
                "name": "liquidity_score",
                "direction": "higher_is_better",
                "summary": (
                    "exit_type, lockup, time-to-exit; whitelist/KYC haircut when "
                    "transfer restrictions apply (e.g. RealT)."
                ),
            },
            {
                "name": "data_confidence_score",
                "direction": "higher_is_better",
                "summary": (
                    "verification_tier, retrieval_method, field completeness, "
                    "and freshness of data_pulled_at (surfaced as snapshot_age_days)."
                ),
            },
        ],
        "null_handling": (
            "A missing numeric input is never treated as zero and never imputed "
            "from other assets. Yield with both fields null returns "
            "insufficient_data."
        ),
        "no_master_score": (
            "The four scores are never blended into one master number."
        ),
        "weights_path": "scoring/weights.yaml",
        "methodology_path": "scoring/METHODOLOGY.md",
    }


def get_scoring_methodology(
    format: Literal["markdown", "summary"] = "markdown",
) -> dict[str, Any]:
    if format == "summary":
        content: Any = _methodology_summary()
    else:
        content = METHODOLOGY_PATH.read_text(encoding="utf-8")

    return {
        "format": format,
        "weights_path": "scoring/weights.yaml",
        "methodology_path": "scoring/METHODOLOGY.md",
        "content": content,
        "notes": list(NOTES_METHODOLOGY),
    }
