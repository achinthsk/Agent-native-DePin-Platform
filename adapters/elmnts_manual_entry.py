#!/usr/bin/env python3
"""
Elmnts manual-entry tool.

FINDINGS.md conclusion: there is no publicly accessible, unauthenticated
endpoint returning real Elmnts production / payout / fund data. This script
does NOT pretend to be a live API adapter. It accepts human-supplied fields
(from public marketing materials or an investor's own records), labels them
as self-reported / manual-entry, validates against asset-v1.schema.json, and
stores a timestamped snapshot under storage/.

Usage (interactive):
  python3 adapters/elmnts_manual_entry.py

Usage (non-interactive, from a prepared JSON answers file):
  python3 adapters/elmnts_manual_entry.py --from-file adapters/elmnts_manual_answers.example.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import require_valid, write_snapshot  # noqa: E402

CLOSED_ENUMS = {
    "payout_mechanism_type": [
        "direct-revenue-share",
        "token-emission-reward",
        "fixed-interest",
        "price-appreciation-only",
        "unverifiable",
    ],
    "payout_currency": ["native-protocol-token", "stablecoin", "fiat", "unverifiable"],
    "payout_frequency": [
        "continuous",
        "weekly",
        "monthly",
        "at-maturity",
        "irregular",
        "unverifiable",
    ],
    "exit_type": [
        "open-market-tradeable",
        "fixed-lockup",
        "illiquid-broker-required",
        "unverifiable",
    ],
    "regulatory_wrapper": [
        "unregistered-onchain-token",
        "reg-d-506c",
        "reg-cf",
        "reg-a",
        "licensed-fund-vault",
        "unverifiable",
    ],
    "exposure_type": ["single-asset", "pooled-diversified", "unverifiable"],
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{text}{suffix}: ").strip()
    if not value and default is not None:
        return default
    return value


def prompt_optional_number(text: str) -> float | None:
    raw = prompt(f"{text} (blank = null)")
    if raw == "":
        return None
    return float(raw)


def prompt_optional_int(text: str) -> int | None:
    raw = prompt(f"{text} (blank = null)")
    if raw == "":
        return None
    return int(raw)


def prompt_bool(text: str, default: bool = False) -> bool:
    d = "y" if default else "n"
    raw = prompt(f"{text} (y/n)", d).lower()
    return raw in ("y", "yes", "true", "1")


def prompt_enum(field: str, default: str) -> str:
    choices = CLOSED_ENUMS[field]
    print(f"  choices: {', '.join(choices)}")
    value = prompt(field, default)
    if value not in choices:
        print(f"[ERROR] '{value}' not in {choices}", file=sys.stderr)
        raise SystemExit(1)
    return value


def prompt_country_list(text: str) -> list[str]:
    raw = prompt(f"{text} (comma-separated ISO alpha-2, blank = empty)", "")
    if not raw:
        return []
    codes = [c.strip().upper() for c in raw.split(",") if c.strip()]
    for c in codes:
        if len(c) != 2 or not c.isalpha():
            print(f"[ERROR] invalid country code: {c}", file=sys.stderr)
            raise SystemExit(1)
    return codes


def collect_interactive() -> dict[str, Any]:
    print("=" * 70)
    print("Elmnts MANUAL ENTRY")
    print("No public API was found (see adapters/FINDINGS.md).")
    print("Enter values from public marketing materials or your own records.")
    print("Do not invent numbers. Leave numeric fields blank to store null.")
    print("=" * 70)

    asset_id = prompt("asset_id", "elmnts-manual-entry-01")
    name = prompt("name")
    description_text = prompt("description_text")
    source_url = prompt("source_url (URL of the marketing page / doc you used)")

    print("\n-- payout_mechanism --")
    payout_mechanism_type = prompt_enum("payout_mechanism_type", "direct-revenue-share")
    payout_currency = prompt_enum("payout_currency", "stablecoin")
    payout_frequency = prompt_enum("payout_frequency", "monthly")

    print("\n-- yield_profile --")
    advertised = prompt_optional_number("advertised_yield_pct")
    realized = prompt_optional_number("realized_yield_pct")
    if advertised is not None or realized is not None:
        basis = prompt("yield_calculation_basis (required when a yield is non-null)")
        if not basis:
            print("[ERROR] yield_calculation_basis required when a yield is set", file=sys.stderr)
            raise SystemExit(1)
    else:
        basis = prompt(
            "yield_calculation_basis (optional note; blank → null)",
            "",
        ) or None

    print("\n-- maturity --")
    protocol_age = prompt_optional_int("protocol_age_months")
    protocol_age_reason = None
    if protocol_age is None:
        protocol_age_reason = prompt(
            "protocol_age_months_unknown_reason",
            "Not published in the public materials used for this manual entry.",
        )
    asset_age = prompt_optional_int("asset_age_months")
    asset_age_reason = None
    if asset_age is None:
        asset_age_reason = prompt(
            "asset_age_months_unknown_reason",
            "Not published in the public materials used for this manual entry.",
        )
    cycles = prompt_optional_int("completed_payout_cycles")
    cycles_reason = None
    if cycles is None:
        cycles_reason = prompt(
            "completed_payout_cycles_unknown_reason",
            "No public payout history available without investor login.",
        )

    print("\n-- liquidity --")
    exit_type = prompt_enum("exit_type", "illiquid-broker-required")
    lockup = prompt_optional_int("lockup_period_weeks")
    lockup_reason = None
    if exit_type == "fixed-lockup" and lockup is None:
        lockup_reason = prompt(
            "lockup_period_weeks_unknown_reason",
            "Exit is fixed-lockup but lockup length was not stated in source materials.",
        )
    exit_days = prompt_optional_int("estimated_time_to_exit_days")
    exit_days_reason = None
    if exit_days is None:
        exit_days_reason = prompt(
            "estimated_time_to_exit_days_unknown_reason",
            "No public secondary-market timing estimate in source materials.",
        )

    print("\n-- regulatory --")
    regulatory_wrapper = prompt_enum("regulatory_wrapper", "reg-d-506c")
    accreditation_required = prompt_bool("accreditation_required", True)
    restricted = prompt_country_list("restricted_jurisdictions")
    permitted = prompt_country_list("permitted_jurisdictions")

    print("\n-- exposure --")
    exposure_type = prompt_enum("exposure_type", "single-asset")
    underlying_reference = prompt("underlying_reference")
    operator_raw = prompt("operator_name (blank = null)", "")
    operator_name = operator_raw or None
    operator_notes = prompt("operator_track_record_notes (optional)", "")

    answers = {
        "asset_id": asset_id,
        "name": name,
        "description_text": description_text,
        "source_url": source_url,
        "payout_mechanism_type": payout_mechanism_type,
        "payout_currency": payout_currency,
        "payout_frequency": payout_frequency,
        "advertised_yield_pct": advertised,
        "realized_yield_pct": realized,
        "yield_calculation_basis": basis,
        "protocol_age_months": protocol_age,
        "protocol_age_months_unknown_reason": protocol_age_reason,
        "asset_age_months": asset_age,
        "asset_age_months_unknown_reason": asset_age_reason,
        "completed_payout_cycles": cycles,
        "completed_payout_cycles_unknown_reason": cycles_reason,
        "exit_type": exit_type,
        "lockup_period_weeks": lockup,
        "lockup_period_weeks_unknown_reason": lockup_reason,
        "estimated_time_to_exit_days": exit_days,
        "estimated_time_to_exit_days_unknown_reason": exit_days_reason,
        "regulatory_wrapper": regulatory_wrapper,
        "accreditation_required": accreditation_required,
        "restricted_jurisdictions": restricted,
        "permitted_jurisdictions": permitted,
        "exposure_type": exposure_type,
        "underlying_reference": underlying_reference,
        "operator_name": operator_name,
        "operator_track_record_notes": operator_notes or None,
    }
    return answers


def build_instance(answers: dict[str, Any], pulled_at: str) -> dict[str, Any]:
    advertised = answers.get("advertised_yield_pct")
    realized = answers.get("realized_yield_pct")
    basis = answers.get("yield_calculation_basis")
    yield_computed_at = pulled_at if (advertised is not None or realized is not None) else None
    # Schema: basis + yield_last_computed_at required non-null when either yield is non-null.
    # When both yields null, basis and yield_last_computed_at may be null.
    if advertised is None and realized is None:
        # Keep an explicit null basis unless the human supplied a note.
        if basis == "":
            basis = None
        yield_computed_at = None if not answers.get("force_yield_timestamp") else pulled_at

    instance: dict[str, Any] = {
        "schema_version": "1.0.0",
        "asset_id": answers["asset_id"],
        "source_platform": "elmnts",
        "asset_class": "oil-gas-royalty",
        "name": answers["name"],
        "description_text": answers["description_text"],
        "source_url": answers["source_url"],
        "data_pulled_at": pulled_at,
        "retrieval_method": "manual-entry",
        "payout_mechanism": {
            "payout_mechanism_type": answers["payout_mechanism_type"],
            "payout_currency": answers["payout_currency"],
            "payout_frequency": answers["payout_frequency"],
        },
        "yield_profile": {
            "advertised_yield_pct": advertised,
            "realized_yield_pct": realized,
            "yield_calculation_basis": basis,
            "yield_last_computed_at": yield_computed_at if (advertised is not None or realized is not None) else (
                pulled_at if basis else None
            ),
        },
        "verification": {
            "verification_tier": "self-reported-unverified",
            "verification_notes": (
                "Manual entry. No public unauthenticated Elmnts API exposing production or "
                "payout data was found (see adapters/FINDINGS.md). Values come from human "
                "input / public marketing materials, not from a live programmatic pull."
            ),
        },
        "maturity": {
            "protocol_age_months": answers.get("protocol_age_months"),
            "protocol_age_months_unknown_reason": answers.get("protocol_age_months_unknown_reason"),
            "asset_age_months": answers.get("asset_age_months"),
            "asset_age_months_unknown_reason": answers.get("asset_age_months_unknown_reason"),
            "completed_payout_cycles": answers.get("completed_payout_cycles"),
            "completed_payout_cycles_unknown_reason": answers.get(
                "completed_payout_cycles_unknown_reason"
            ),
        },
        "liquidity": {
            "exit_type": answers["exit_type"],
            "lockup_period_weeks": answers.get("lockup_period_weeks"),
            "lockup_period_weeks_unknown_reason": answers.get("lockup_period_weeks_unknown_reason"),
            "estimated_time_to_exit_days": answers.get("estimated_time_to_exit_days"),
            "estimated_time_to_exit_days_unknown_reason": answers.get(
                "estimated_time_to_exit_days_unknown_reason"
            ),
        },
        "regulatory": {
            "regulatory_wrapper": answers["regulatory_wrapper"],
            "accreditation_required": bool(answers["accreditation_required"]),
            "restricted_jurisdictions": answers.get("restricted_jurisdictions") or [],
            "permitted_jurisdictions": answers.get("permitted_jurisdictions") or [],
        },
        "exposure": {
            "exposure_type": answers["exposure_type"],
            "underlying_reference": answers["underlying_reference"],
            "operator_name": answers.get("operator_name"),
        },
    }
    notes = answers.get("operator_track_record_notes")
    if notes:
        instance["exposure"]["operator_track_record_notes"] = notes

    # Normalize unknown_reason fields: must be null when the paired value is present.
    mat = instance["maturity"]
    for value_key, reason_key in [
        ("protocol_age_months", "protocol_age_months_unknown_reason"),
        ("asset_age_months", "asset_age_months_unknown_reason"),
        ("completed_payout_cycles", "completed_payout_cycles_unknown_reason"),
    ]:
        if mat[value_key] is not None:
            mat[reason_key] = None
        elif not mat[reason_key]:
            mat[reason_key] = "Unknown; not provided during manual entry."

    liq = instance["liquidity"]
    if liq["lockup_period_weeks"] is not None:
        liq["lockup_period_weeks_unknown_reason"] = None
    elif liq["exit_type"] != "fixed-lockup":
        liq["lockup_period_weeks_unknown_reason"] = None
    elif not liq["lockup_period_weeks_unknown_reason"]:
        liq["lockup_period_weeks_unknown_reason"] = (
            "fixed-lockup exit_type but lockup length not provided during manual entry."
        )

    if liq["estimated_time_to_exit_days"] is not None:
        liq["estimated_time_to_exit_days_unknown_reason"] = None
    elif not liq["estimated_time_to_exit_days_unknown_reason"]:
        liq["estimated_time_to_exit_days_unknown_reason"] = (
            "Unknown; not provided during manual entry."
        )

    # Fix yield_last_computed_at when basis is set but both yields null — schema allows
    # null for both basis and timestamp when yields are null. If basis is a non-empty
    # string with null yields, also set timestamp so the note is dated.
    yp = instance["yield_profile"]
    if yp["advertised_yield_pct"] is None and yp["realized_yield_pct"] is None:
        if yp["yield_calculation_basis"]:
            yp["yield_last_computed_at"] = pulled_at
        else:
            yp["yield_calculation_basis"] = None
            yp["yield_last_computed_at"] = None

    return instance


def main() -> int:
    parser = argparse.ArgumentParser(description="Elmnts manual-entry snapshot tool")
    parser.add_argument(
        "--from-file",
        help="JSON file of answers (non-interactive). See elmnts_manual_answers.example.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate/print only; do not write")
    args = parser.parse_args()

    pulled_at = utc_now_iso()
    print(f"[START] Elmnts manual entry at {pulled_at}")
    print("[NOTE] This is NOT a live API pull. See adapters/FINDINGS.md.")

    if args.from_file:
        path = Path(args.from_file)
        if not path.exists():
            print(f"[FATAL] answers file not found: {path}", file=sys.stderr)
            return 1
        with open(path, "r", encoding="utf-8") as f:
            answers = json.load(f)
    else:
        if not sys.stdin.isatty():
            print(
                "[FATAL] No TTY for interactive prompts. Pass --from-file <answers.json>.",
                file=sys.stderr,
            )
            return 1
        answers = collect_interactive()

    instance = build_instance(answers, pulled_at)
    print(json.dumps(instance, indent=2))

    if args.dry_run:
        require_valid(instance, f"dry-run {instance['asset_id']}")
    else:
        write_snapshot(instance)

    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
