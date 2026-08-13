#!/usr/bin/env python3
"""
Four-axis scoring engine for Yield Opportunity schema instances.

Scores are independent: yield_score, risk_score, liquidity_score,
data_confidence_score. Missing yield inputs produce insufficient_data —
never a fabricated 0 or imputed average.

Weights: scoring/weights.yaml (never hardcoded here).
Methodology: scoring/METHODOLOGY.md

Usage:
  python scoring/engine.py
  python scoring/engine.py --latest-only
  python scoring/engine.py --prove
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
STORAGE_DIR = ROOT / "storage"
WEIGHTS_PATH = Path(__file__).resolve().parent / "weights.yaml"

# Explicit in every score object so agents need not read METHODOLOGY.md.
DIRECTION = "higher_is_better"

sys.path.insert(0, str(ROOT / "adapters"))
from common import validate_instance  # noqa: E402


def load_weights(path: Path = WEIGHTS_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def parse_iso_utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def dig(obj: dict[str, Any], dotted: str) -> Any:
    """Resolve dotted path like yield_profile.advertised_yield_pct."""
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def curve_interp(
    value: float,
    points: list[dict[str, float]],
    x_key: str,
    y_key: str = "score",
) -> float:
    """Piecewise-linear interpolate a list of {x_key, score} dicts."""
    pts = sorted((float(p[x_key]), float(p[y_key])) for p in points)
    if value <= pts[0][0]:
        return pts[0][1]
    if value >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= value <= x1:
            if x1 == x0:
                return y1
            t = (value - x0) / (x1 - x0)
            return y0 + t * (y1 - y0)
    return pts[-1][1]


def weighted_mean(parts: list[tuple[float, float]]) -> float | None:
    """parts = [(points, weight), ...]. Renormalize over present parts."""
    if not parts:
        return None
    tw = sum(w for _, w in parts)
    if tw <= 0:
        return None
    return sum(p * w for p, w in parts) / tw


def map_yield_pct(pct: float, yw: dict[str, Any]) -> tuple[float, dict[str, Any] | None]:
    """
    Map a yield % through the curve, then apply implausibility haircut if
    past the configured threshold. Returns (points, implausibility_meta|None).
    """
    base = clamp(curve_interp(pct, yw["curve_points"], "pct"))
    threshold = float(yw["implausibility_threshold_pct"])
    rate = float(yw["implausibility_penalty_per_pp"])
    if pct <= threshold:
        return base, None
    excess = pct - threshold
    multiplier = max(0.0, 1.0 - rate * excess)
    return clamp(base * multiplier), {
        "threshold_pct": threshold,
        "excess_pp": round(excess, 4),
        "multiplier": round(multiplier, 4),
    }


# ---------------------------------------------------------------------------
# Yield
# ---------------------------------------------------------------------------

def score_yield(asset: dict[str, Any], w: dict[str, Any]) -> dict[str, Any]:
    yw = w["yield"]
    yp = asset.get("yield_profile") or {}
    adv = yp.get("advertised_yield_pct")
    real = yp.get("realized_yield_pct")
    inputs = {
        "yield_profile.advertised_yield_pct": adv,
        "yield_profile.realized_yield_pct": real,
    }

    # REQUIREMENT 2 / METHODOLOGY: both null → insufficient_data (never fabricate)
    if adv is None and real is None:
        return {
            "value": None,
            "insufficient_data": True,
            "direction": DIRECTION,
            "reason": (
                "both yield_profile.advertised_yield_pct and "
                "yield_profile.realized_yield_pct are null"
            ),
            "inputs": inputs,
        }

    if real is not None and adv is None:
        pts, impl = map_yield_pct(float(real), yw)
        out: dict[str, Any] = {
            "value": round(pts, 2),
            "insufficient_data": False,
            "direction": DIRECTION,
            "mode": "realized_only",
            "inputs": inputs,
        }
        if impl is not None:
            out["implausibility"] = impl
        return out

    if adv is not None and real is None:
        mapped, impl = map_yield_pct(float(adv), yw)
        discounted = mapped * float(yw["advertised_only_discount"])
        out = {
            "value": round(clamp(discounted), 2),
            "insufficient_data": False,
            "direction": DIRECTION,
            "mode": "advertised_only",
            "advertised_only_discount": float(yw["advertised_only_discount"]),
            "inputs": inputs,
        }
        if impl is not None:
            out["implausibility"] = impl
        return out

    # both present
    adv_f = float(adv)
    real_f = float(real)
    gap = adv_f - real_f  # positive = advertised overshoot
    real_pts, real_impl = map_yield_pct(real_f, yw)
    adv_pts, adv_impl = map_yield_pct(adv_f, yw)
    base = (
        float(yw["weight_realized"]) * real_pts
        + float(yw["weight_advertised"]) * adv_pts
    )
    k = float(yw["gap_penalty_per_pp"])
    if gap > 0:
        multiplier = max(0.0, 1.0 - k * gap)
    else:
        multiplier = 1.0
    value = clamp(base * multiplier)
    out = {
        "value": round(value, 2),
        "insufficient_data": False,
        "direction": DIRECTION,
        "mode": "both",
        "gap_pp": round(gap, 4),
        "gap_multiplier": round(multiplier, 4),
        "inputs": inputs,
    }
    impl_bits = {}
    if real_impl is not None:
        impl_bits["realized"] = real_impl
    if adv_impl is not None:
        impl_bits["advertised"] = adv_impl
    if impl_bits:
        out["implausibility"] = impl_bits
    return out


# ---------------------------------------------------------------------------
# Risk (higher = safer)
# ---------------------------------------------------------------------------

def score_risk(asset: dict[str, Any], w: dict[str, Any]) -> dict[str, Any]:
    rw = w["risk"]
    verification = asset.get("verification") or {}
    maturity = asset.get("maturity") or {}
    exposure = asset.get("exposure") or {}
    yp = asset.get("yield_profile") or {}

    tier = verification.get("verification_tier")
    protocol_age = maturity.get("protocol_age_months")
    asset_age = maturity.get("asset_age_months")
    cycles = maturity.get("completed_payout_cycles")
    exposure_type = exposure.get("exposure_type")
    adv = yp.get("advertised_yield_pct")
    real = yp.get("realized_yield_pct")

    inputs: dict[str, Any] = {
        "verification.verification_tier": tier,
        "maturity.protocol_age_months": protocol_age,
        "maturity.asset_age_months": asset_age,
        "maturity.completed_payout_cycles": cycles,
        "exposure.exposure_type": exposure_type,
        "yield_profile.advertised_yield_pct": adv,
        "yield_profile.realized_yield_pct": real,
    }

    parts: list[tuple[float, float]] = []
    components: dict[str, Any] = {}

    tier_scores = rw["verification_tier_scores"]
    if tier is not None and tier in tier_scores:
        pts = float(tier_scores[tier])
        parts.append((pts, float(rw["weight_verification_tier"])))
        components["verification_tier"] = pts

    if protocol_age is not None:
        pts = curve_interp(float(protocol_age), rw["protocol_age_curve"], "months")
        parts.append((pts, float(rw["weight_protocol_age"])))
        components["protocol_age_months"] = round(pts, 2)

    if asset_age is not None:
        pts = curve_interp(float(asset_age), rw["asset_age_curve"], "months")
        parts.append((pts, float(rw["weight_asset_age"])))
        components["asset_age_months"] = round(pts, 2)

    if cycles is not None:
        pts = curve_interp(float(cycles), rw["payout_cycles_curve"], "cycles")
        parts.append((pts, float(rw["weight_completed_payout_cycles"])))
        components["completed_payout_cycles"] = round(pts, 2)

    exp_scores = rw["exposure_type_scores"]
    if exposure_type is not None and exposure_type in exp_scores:
        pts = float(exp_scores[exposure_type])
        parts.append((pts, float(rw["weight_exposure_type"])))
        components["exposure_type"] = pts

    if not parts:
        return {
            "value": None,
            "insufficient_data": True,
            "direction": DIRECTION,
            "reason": "no risk inputs populated",
            "inputs": inputs,
            "components": components,
        }

    value = weighted_mean(parts)
    assert value is not None

    # Gap penalty: only when BOTH yields present. Positive gap (advertised >
    # realized) multiplies the score down — same shape as yield_score.
    # Missing either yield → skip (never invent a 0 gap).
    gap_meta: dict[str, Any] | None = None
    if adv is not None and real is not None:
        gap = float(adv) - float(real)
        k = float(rw["gap_penalty_per_pp"])
        if gap > 0:
            multiplier = max(0.0, 1.0 - k * gap)
        else:
            multiplier = 1.0
        value = value * multiplier
        gap_meta = {"gap_pp": round(gap, 4), "multiplier": round(multiplier, 4)}
        components["advertised_realized_gap"] = gap_meta

    return {
        "value": round(clamp(value), 2),
        "insufficient_data": False,
        "direction": DIRECTION,
        "inputs": inputs,
        "components": components,
    }


# ---------------------------------------------------------------------------
# Liquidity
# ---------------------------------------------------------------------------

def _whitelist_restricted(asset: dict[str, Any]) -> bool:
    """METHODOLOGY: RealT / KYC-whitelist cues must haircut open-market enum."""
    if asset.get("source_platform") == "realt":
        return True
    blob = " ".join(
        [
            str(asset.get("description_text") or ""),
            str(dig(asset, "verification.verification_notes") or ""),
        ]
    ).lower()
    cues = ("whitelist", "kyc", "transferability requires")
    return any(c in blob for c in cues)


def score_liquidity(asset: dict[str, Any], w: dict[str, Any]) -> dict[str, Any]:
    lw = w["liquidity"]
    liq = asset.get("liquidity") or {}
    exit_type = liq.get("exit_type")
    lockup = liq.get("lockup_period_weeks")
    exit_days = liq.get("estimated_time_to_exit_days")

    inputs: dict[str, Any] = {
        "liquidity.exit_type": exit_type,
        "liquidity.lockup_period_weeks": lockup,
        "liquidity.estimated_time_to_exit_days": exit_days,
        "source_platform": asset.get("source_platform"),
    }

    parts: list[tuple[float, float]] = []
    components: dict[str, Any] = {}

    exit_scores = lw["exit_type_scores"]
    if exit_type is not None and exit_type in exit_scores:
        pts = float(exit_scores[exit_type])
        parts.append((pts, float(lw["weight_exit_type"])))
        components["exit_type"] = pts

    # Lockup length: use when non-null (especially meaningful for fixed-lockup)
    if lockup is not None:
        pts = curve_interp(float(lockup), lw["lockup_curve"], "weeks")
        parts.append((pts, float(lw["weight_lockup"])))
        components["lockup_period_weeks"] = round(pts, 2)

    if exit_days is not None:
        pts = curve_interp(float(exit_days), lw["time_to_exit_curve"], "days")
        parts.append((pts, float(lw["weight_time_to_exit"])))
        components["estimated_time_to_exit_days"] = round(pts, 2)

    if not parts:
        return {
            "value": None,
            "insufficient_data": True,
            "direction": DIRECTION,
            "reason": "no liquidity inputs populated",
            "inputs": inputs,
            "components": components,
        }

    base = weighted_mean(parts)
    assert base is not None

    haircut_applied = False
    haircut = 1.0
    if _whitelist_restricted(asset):
        haircut = float(lw["whitelist_haircut"])
        haircut_applied = True
        components["whitelist_restriction_haircut"] = haircut

    return {
        "value": round(clamp(base * haircut), 2),
        "insufficient_data": False,
        "direction": DIRECTION,
        "inputs": inputs,
        "components": components,
        "whitelist_haircut_applied": haircut_applied,
    }


# ---------------------------------------------------------------------------
# Data confidence
# ---------------------------------------------------------------------------

def _field_present(asset: dict[str, Any], dotted: str) -> bool:
    val = dig(asset, dotted)
    if val is None:
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    return True


def score_data_confidence(asset: dict[str, Any], w: dict[str, Any]) -> dict[str, Any]:
    dw = w["data_confidence"]
    verification = asset.get("verification") or {}
    tier = verification.get("verification_tier")
    retrieval = asset.get("retrieval_method")
    pulled = asset.get("data_pulled_at")

    checklist: list[str] = list(dw["completeness_fields"])
    null_fields: list[str] = []
    populated = 0
    for field in checklist:
        if _field_present(asset, field):
            populated += 1
        else:
            null_fields.append(field)
    total = len(checklist)
    completeness_pts = 100.0 * (populated / total) if total else 0.0

    age_days: float | None = None
    fresh_pts: float | None = None
    if pulled:
        age_days = (
            datetime.now(timezone.utc) - parse_iso_utc(str(pulled))
        ).total_seconds() / 86400.0
        fresh_pts = curve_interp(age_days, dw["freshness_curve"], "days")

    inputs: dict[str, Any] = {
        "verification.verification_tier": tier,
        "retrieval_method": retrieval,
        "data_pulled_at": pulled,
        "completeness_populated": populated,
        "completeness_total": total,
        "completeness_null_fields": null_fields,
        "snapshot_age_days": round(age_days, 3) if age_days is not None else None,
    }

    parts: list[tuple[float, float]] = []
    components: dict[str, Any] = {}

    tier_scores = dw["verification_tier_scores"]
    if tier is not None and tier in tier_scores:
        pts = float(tier_scores[tier])
        parts.append((pts, float(dw["weight_verification_tier"])))
        components["verification_tier"] = pts

    ret_scores = dw["retrieval_method_scores"]
    if retrieval is not None and retrieval in ret_scores:
        pts = float(ret_scores[retrieval])
        parts.append((pts, float(dw["weight_retrieval_method"])))
        components["retrieval_method"] = pts

    parts.append((completeness_pts, float(dw["weight_completeness"])))
    components["completeness"] = round(completeness_pts, 2)

    if fresh_pts is not None:
        parts.append((fresh_pts, float(dw["weight_freshness"])))
        components["freshness"] = round(fresh_pts, 2)

    value = weighted_mean(parts)
    assert value is not None
    return {
        "value": round(clamp(value), 2),
        "insufficient_data": False,
        "direction": DIRECTION,
        "inputs": inputs,
        "components": components,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def score_asset(
    asset: dict[str, Any], snapshot_path: str, weights: dict[str, Any]
) -> dict[str, Any]:
    return {
        "asset_id": asset.get("asset_id"),
        "source_platform": asset.get("source_platform"),
        "snapshot_file": snapshot_path,
        "schema_version": asset.get("schema_version"),
        "scored_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "weights_version": weights.get("version"),
        "yield_score": score_yield(asset, weights),
        "risk_score": score_risk(asset, weights),
        "liquidity_score": score_liquidity(asset, weights),
        "data_confidence_score": score_data_confidence(asset, weights),
    }


def discover_snapshots(storage: Path = STORAGE_DIR) -> list[Path]:
    if not storage.is_dir():
        return []
    return sorted(p for p in storage.rglob("*.json") if p.is_file())


def score_storage(
    storage: Path = STORAGE_DIR,
    weights_path: Path = WEIGHTS_PATH,
    *,
    latest_only: bool = False,
) -> list[dict[str, Any]]:
    weights = load_weights(weights_path)
    paths = discover_snapshots(storage)
    by_asset: dict[str, list[tuple[Path, dict[str, Any]]]] = {}

    for path in paths:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            validate_instance(raw)
        except Exception as exc:  # noqa: BLE001
            print(f"skip invalid {path}: {exc}", file=sys.stderr)
            continue
        aid = str(raw.get("asset_id", path.parent.name))
        by_asset.setdefault(aid, []).append((path, raw))

    results: list[dict[str, Any]] = []
    for aid, items in sorted(by_asset.items()):
        items_sorted = sorted(items, key=lambda t: t[0].name)
        chosen = [items_sorted[-1]] if latest_only else items_sorted
        for path, raw in chosen:
            rel = (
                str(path.relative_to(ROOT))
                if path.is_relative_to(ROOT)
                else str(path)
            )
            results.append(score_asset(raw, rel, weights))
    return results


def run_gap_proof(weights: dict[str, Any]) -> dict[str, Any]:
    """
    Part C: clone latest RealT snapshot in memory, widen advertised−realized
    gap, show risk_score worsens. Does not write anything under storage/.
    """
    realt_dir = STORAGE_DIR / "realt-0xfe17c3c0b6f38cf3bd8ba872bee7a18ab16b43fb"
    snaps = sorted(realt_dir.glob("*.json")) if realt_dir.is_dir() else []
    if not snaps:
        raise SystemExit("no RealT snapshot found for gap proof")
    path = snaps[-1]
    base = json.loads(path.read_text(encoding="utf-8"))
    validate_instance(base)

    before = score_risk(base, weights)

    mutated = copy.deepcopy(base)
    realized = float(mutated["yield_profile"]["realized_yield_pct"])
    # Hard positive gap: advertised far above realized
    mutated["yield_profile"]["advertised_yield_pct"] = realized + 15.0
    after = score_risk(mutated, weights)

    return {
        "snapshot_file": str(path.relative_to(ROOT)),
        "before": {
            "advertised_yield_pct": base["yield_profile"].get("advertised_yield_pct"),
            "realized_yield_pct": base["yield_profile"].get("realized_yield_pct"),
            "risk_score_value": before["value"],
            "risk_components": before.get("components"),
        },
        "after_synthetic_gap": {
            "advertised_yield_pct": mutated["yield_profile"]["advertised_yield_pct"],
            "realized_yield_pct": mutated["yield_profile"]["realized_yield_pct"],
            "gap_pp": 15.0,
            "risk_score_value": after["value"],
            "risk_components": after.get("components"),
        },
        "risk_delta": round((after["value"] or 0) - (before["value"] or 0), 2),
        "note": "Synthetic mutation was in-memory only; storage/ unchanged.",
    }


def run_implausibility_proof(weights: dict[str, Any]) -> dict[str, Any]:
    """
    Fix 2: 70% realized should score worse than a believable 18%, not tie at
    the curve ceiling. In-memory only — storage/ unchanged.
    """
    realt_dir = STORAGE_DIR / "realt-0xfe17c3c0b6f38cf3bd8ba872bee7a18ab16b43fb"
    snaps = sorted(realt_dir.glob("*.json")) if realt_dir.is_dir() else []
    if not snaps:
        raise SystemExit("no RealT snapshot found for implausibility proof")
    path = snaps[-1]
    base = json.loads(path.read_text(encoding="utf-8"))
    validate_instance(base)

    believable = copy.deepcopy(base)
    believable["yield_profile"]["realized_yield_pct"] = 18.0
    believable["yield_profile"]["advertised_yield_pct"] = None

    implausible = copy.deepcopy(base)
    implausible["yield_profile"]["realized_yield_pct"] = 70.0
    implausible["yield_profile"]["advertised_yield_pct"] = None

    y_believable = score_yield(believable, weights)
    y_implausible = score_yield(implausible, weights)

    return {
        "snapshot_file_cloned": str(path.relative_to(ROOT)),
        "believable_18pct": {
            "realized_yield_pct": 18.0,
            "yield_score": y_believable,
        },
        "implausible_70pct": {
            "realized_yield_pct": 70.0,
            "yield_score": y_implausible,
        },
        "implausible_worse_than_believable": (
            (y_implausible["value"] or 0) < (y_believable["value"] or 0)
        ),
        "note": "Synthetic mutation was in-memory only; storage/ unchanged.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Yield Opportunity snapshots")
    parser.add_argument(
        "--latest-only",
        action="store_true",
        help="Score only the newest snapshot per asset_id",
    )
    parser.add_argument(
        "--prove",
        action="store_true",
        help="Also run Part C proofs (gap test in-memory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSON payload to this path",
    )
    args = parser.parse_args()

    results = score_storage(latest_only=args.latest_only)
    payload: dict[str, Any] = {"scores": results}

    if args.prove:
        weights = load_weights()
        latest = score_storage(latest_only=True)
        by_id = {r["asset_id"]: r for r in latest}
        glow = by_id.get("glow-farm-1")
        elmnts = by_id.get("elmnts-chevron-mineral-rights-fund-public-marketing")
        realt = by_id.get("realt-0xfe17c3c0b6f38cf3bd8ba872bee7a18ab16b43fb")

        payload["proofs"] = {
            "glow_yield_insufficient_data": {
                "asset_id": "glow-farm-1",
                "yield_score": glow["yield_score"] if glow else None,
                "code_path": (
                    "score_yield(): if both yield_profile.advertised_yield_pct "
                    "and yield_profile.realized_yield_pct are None, return "
                    "value=None and insufficient_data=True before any numeric "
                    "mapping — never fabricates 0 or an imputed average."
                ),
            },
            "realt_vs_elmnts_same_tier_different_outcomes": {
                "elmnts": {
                    "verification_tier": (
                        elmnts["risk_score"]["inputs"][
                            "verification.verification_tier"
                        ]
                        if elmnts
                        else None
                    ),
                    "yield_score": elmnts["yield_score"] if elmnts else None,
                    "risk_score": elmnts["risk_score"]["value"] if elmnts else None,
                    "liquidity_score": (
                        elmnts["liquidity_score"]["value"] if elmnts else None
                    ),
                    "data_confidence_score": (
                        elmnts["data_confidence_score"]["value"] if elmnts else None
                    ),
                    "completeness_populated": (
                        elmnts["data_confidence_score"]["inputs"][
                            "completeness_populated"
                        ]
                        if elmnts
                        else None
                    ),
                    "completeness_total": (
                        elmnts["data_confidence_score"]["inputs"][
                            "completeness_total"
                        ]
                        if elmnts
                        else None
                    ),
                },
                "realt": {
                    "verification_tier": (
                        realt["risk_score"]["inputs"][
                            "verification.verification_tier"
                        ]
                        if realt
                        else None
                    ),
                    "yield_score": realt["yield_score"] if realt else None,
                    "risk_score": realt["risk_score"]["value"] if realt else None,
                    "liquidity_score": (
                        realt["liquidity_score"]["value"] if realt else None
                    ),
                    "data_confidence_score": (
                        realt["data_confidence_score"]["value"] if realt else None
                    ),
                    "completeness_populated": (
                        realt["data_confidence_score"]["inputs"][
                            "completeness_populated"
                        ]
                        if realt
                        else None
                    ),
                    "completeness_total": (
                        realt["data_confidence_score"]["inputs"][
                            "completeness_total"
                        ]
                        if realt
                        else None
                    ),
                },
            },
            "advertised_realized_gap_moves_risk": run_gap_proof(weights),
            "implausible_yield_scores_worse_than_believable": (
                run_implausibility_proof(weights)
            ),
        }

    text = json.dumps(payload, indent=2, sort_keys=False)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
