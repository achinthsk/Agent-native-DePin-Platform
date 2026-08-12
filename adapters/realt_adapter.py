#!/usr/bin/env python3
"""
RealT property adapter — pulls public property metadata and weekly rent
history, then maps into asset-v1.schema.json (schema_version 1.1.0).

Sources (see adapters/FINDINGS.md Part C):
  1. https://api.realtoken.community/v1/token  — property list / token price
  2. https://ehpst.duckdns.org/realt_rent_tracker/ — weekly rent/yield history
     derived from RealT's publicly available master rent files
  3. Gnosis eth_call — confirm ERC-20 token metadata on-chain

Does NOT invent realized yields from marketing blogs. Does NOT use KYC-gated
RealT portfolio endpoints.

Usage:
  python3 adapters/realt_adapter.py --address 0xFe17C3C0B6F38cF3bD8bA872bEE7a18Ab16b43fB
  python3 adapters/realt_adapter.py --name Ardmore
  python3 adapters/realt_adapter.py --all --limit 2
  python3 adapters/realt_adapter.py --address 0xFe17... --dry-run
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv
from eth_abi import decode
from eth_utils import keccak
from web3 import Web3

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import require_valid, write_snapshot  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

DEFAULT_REALT_API = "https://api.realtoken.community"
DEFAULT_RENT_TRACKER = "https://ehpst.duckdns.org/realt_rent_tracker"
DEFAULT_GNOSIS_RPC = "https://rpc.gnosischain.com"
# RealT public launch ~ April 2019 (first PPM series).
REALT_PROTOCOL_GENESIS = datetime(2019, 4, 1, tzinfo=timezone.utc)
SECONDS_PER_MONTH = 30.4375 * 24 * 3600
HTTP_RETRIES = 4
HTTP_TIMEOUT = 45


class SourceError(Exception):
    """Raised when a required live source is unreachable or returns bad data."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def months_between(start: datetime, end: datetime) -> int:
    return max(0, int((end - start).total_seconds() / SECONDS_PER_MONTH))


def http_get(url: str, retries: int = HTTP_RETRIES, accept: str = "application/json") -> bytes:
    last_err: Exception | None = None
    headers = {
        "Accept": accept,
        "User-Agent": (
            "Mozilla/5.0 (compatible; realt-adapter/1.0; +https://github.com/achinthsk/"
            "Agent-native-DePin-Platform)"
        ),
        "Referer": f"{DEFAULT_REALT_API}/",
    }
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                return resp.read()
        except (HTTPError, URLError, TimeoutError) as e:
            last_err = e
            code = getattr(e, "code", None)
            print(
                f"[ERROR] GET {url} attempt {attempt}/{retries} failed: {e}",
                file=sys.stderr,
            )
            # Cloudflare 403 / rate-limit — back off harder.
            if attempt < retries:
                time.sleep(3.0 * attempt if code == 403 else 1.5 * attempt)
    raise SourceError(f"HTTP GET failed after {retries} retries: {url}: {last_err}")


def http_get_json(url: str) -> Any:
    raw = http_get(url)
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise SourceError(f"Non-JSON response from {url}: {e}; body={raw[:200]!r}") from e


def fetch_token_list(api_base: str) -> list[dict[str, Any]]:
    url = f"{api_base.rstrip('/')}/v1/token"
    data = http_get_json(url)
    if not isinstance(data, list) or not data:
        raise SourceError(f"Unexpected token list payload from {url}")
    print(f"[OK] RealT community API: {len(data)} tokens from {url}")
    return data


def select_tokens(
    tokens: list[dict[str, Any]],
    address: str | None,
    name: str | None,
    pull_all: bool,
    limit: int | None,
) -> list[dict[str, Any]]:
    active = [
        t
        for t in tokens
        if not str(t.get("fullName", "")).startswith("OLD-")
        and (t.get("gnosisContract") or t.get("xDaiContract") or t.get("ethereumContract"))
        and t.get("productType") in (None, "real_estate_rental")
    ]
    # Prefer explicit real_estate_rental; if productType missing, keep.
    active = [
        t
        for t in active
        if t.get("productType") == "real_estate_rental" or t.get("productType") is None
    ]

    if address:
        addr = address.lower()
        matches = [
            t
            for t in tokens
            if addr
            in {
                str(t.get("gnosisContract") or "").lower(),
                str(t.get("xDaiContract") or "").lower(),
                str(t.get("ethereumContract") or "").lower(),
                str(t.get("uuid") or "").lower(),
            }
        ]
        if not matches:
            raise SourceError(f"No token matching address {address} in community API list")
        return matches[:1]

    if name:
        needle = name.lower()
        matches = [
            t
            for t in tokens
            if needle in str(t.get("fullName", "")).lower()
            or needle in str(t.get("shortName", "")).lower()
            or needle in str(t.get("symbol", "")).lower()
        ]
        matches = [t for t in matches if not str(t.get("fullName", "")).startswith("OLD-")]
        if not matches:
            raise SourceError(f"No token matching name {name!r}")
        return matches[:1]

    if pull_all:
        out = active
        if limit is not None:
            out = out[:limit]
        if not out:
            raise SourceError("No active real_estate_rental tokens found in API list")
        return out

    raise SourceError("Specify --address, --name, or --all")


def fetch_rent_history(tracker_base: str, query: str) -> dict[str, Any]:
    """
    POST to the public rent tracker token form; parse Chart.js weekly
    annualized-yield series from the HTML response.
    """
    base = tracker_base.rstrip("/")
    form_url = f"{base}/token"
    last_err: Exception | None = None
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [
                (
                    "User-Agent",
                    "Mozilla/5.0 (compatible; realt-adapter/1.0)",
                )
            ]
            form_html = opener.open(form_url, timeout=HTTP_TIMEOUT).read().decode("utf-8", "ignore")
            m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', form_html)
            if not m:
                raise SourceError("Rent tracker form CSRF token not found")
            csrf = m.group(1)
            body = urllib.parse.urlencode({"csrf_token": csrf, "address": query}).encode()
            req = urllib.request.Request(form_url, data=body, method="POST")
            resp = opener.open(req, timeout=120)
            html = resp.read().decode("utf-8", "ignore")
            labels_m = re.search(r"labels:\s*(\[[^\]]+\])", html)
            data_m = re.search(r"data:\s*(\[[0-9eE+.\s,\-]+\])", html)
            if not labels_m or not data_m:
                raise SourceError(
                    "Rent tracker response missing Chart.js labels/data "
                    f"(query={query!r}, html_len={len(html)})"
                )
            labels = json.loads(labels_m.group(1).replace("'", '"'))
            series = json.loads(data_m.group(1))
            if len(labels) != len(series) or not labels:
                raise SourceError(
                    f"Rent tracker series length mismatch: labels={len(labels)} data={len(series)}"
                )
            txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
            title_m = re.search(
                r"Distributed rent for token\s+(.+?)\s+Annual yield weekly evolution",
                txt,
            )
            print(
                f"[OK] Rent tracker: {len(labels)} weeks "
                f"({labels[0]} → {labels[-1]}) for query={query!r}"
            )
            return {
                "labels": labels,
                "annual_yield_pct_weekly": series,
                "title": title_m.group(1).strip() if title_m else None,
                "source_url": form_url,
            }
        except (HTTPError, URLError, TimeoutError, SourceError, json.JSONDecodeError) as e:
            last_err = e
            print(
                f"[ERROR] Rent tracker attempt {attempt}/{HTTP_RETRIES} failed: {e}",
                file=sys.stderr,
            )
            if attempt < HTTP_RETRIES:
                time.sleep(1.5 * attempt)
    raise SourceError(f"Rent tracker failed after retries for {query!r}: {last_err}")


def compute_realized_yield(
    weekly_annualized_pct: list[float], token_price: float
) -> dict[str, Any]:
    if token_price <= 0:
        raise SourceError(f"Invalid token_price={token_price}")
    n = len(weekly_annualized_pct)
    if n == 0:
        raise SourceError("Empty weekly yield series")
    mean_yield = sum(weekly_annualized_pct) / n
    positive = [y for y in weekly_annualized_pct if y > 0]
    weekly_rent = [(y / 100.0) * token_price / 52.0 for y in weekly_annualized_pct]
    years = n / 52.0
    # Equivalent check: (sum rents / price) / years * 100 == mean_yield
    equiv = (sum(weekly_rent) / token_price) / years * 100.0
    return {
        "realized_yield_pct": round(mean_yield, 4),
        "equiv_check": round(equiv, 4),
        "weeks_observed": n,
        "completed_payout_cycles": len(positive),
        "avg_weekly_rent_usd": round(sum(weekly_rent) / n, 6),
        "total_rent_usd_per_token": round(sum(weekly_rent), 6),
        "years_observed": round(years, 4),
    }


def fetch_onchain_token_meta(rpc_url: str, address: str) -> dict[str, Any] | None:
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": HTTP_TIMEOUT}))
        _ = w3.eth.block_number
        addr = Web3.to_checksum_address(address)

        def call(sig: str, out_types: list[str]) -> Any:
            data = keccak(text=sig)[:4]
            raw = w3.eth.call({"to": addr, "data": data})
            return decode(out_types, raw)

        name = call("name()", ["string"])[0]
        symbol = call("symbol()", ["string"])[0]
        decimals = call("decimals()", ["uint8"])[0]
        supply = call("totalSupply()", ["uint256"])[0]
        print(f"[OK] Gnosis eth_call {addr}: name={name!r} symbol={symbol!r}")
        return {
            "name": name,
            "symbol": symbol,
            "decimals": int(decimals),
            "total_supply_raw": int(supply),
            "total_supply": int(supply) / (10 ** int(decimals)),
        }
    except Exception as e:  # noqa: BLE001 — enrichment only; do not fail the pull
        print(f"[WARN] On-chain enrichment failed (continuing): {e}", file=sys.stderr)
        return None


def build_instance(
    token: dict[str, Any],
    rent: dict[str, Any],
    stats: dict[str, Any],
    onchain: dict[str, Any] | None,
    api_base: str,
    pulled_at: str,
) -> dict[str, Any]:
    gnosis = token.get("gnosisContract") or token.get("xDaiContract")
    eth = token.get("ethereumContract")
    contract = gnosis or eth
    price = float(token["tokenPrice"])
    labels: list[str] = rent["labels"]
    series: list[float] = rent["annual_yield_pct_weekly"]

    first_pos_idx = next((i for i, y in enumerate(series) if y > 0), 0)
    last_pos_idx = len(series) - 1 - next((i for i, y in enumerate(reversed(series)) if y > 0), 0)
    first_pos = labels[first_pos_idx]
    last_pos = labels[last_pos_idx]
    first_dt = datetime.strptime(first_pos, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    protocol_age = months_between(REALT_PROTOCOL_GENESIS, now)
    asset_age = months_between(first_dt, now)

    basis = (
        f"realized_yield_pct={stats['realized_yield_pct']} is the arithmetic mean of "
        f"{stats['weeks_observed']} weekly annualized-yield observations "
        f"({labels[0]} through {labels[-1]}) from the public RealToken rent tracker "
        f"({rent['source_url']}), which states its inputs are RealT's publicly available "
        f"weekly master rent files. Token price P=${price} USD from "
        f"{api_base.rstrip('/')}/v1/token. For each week t with annualized yield y_t%%, "
        f"implied weekly rent per token = (y_t/100)*P/52 "
        f"(period average ${stats['avg_weekly_rent_usd']}/token/week; "
        f"sum ${stats['total_rent_usd_per_token']} over {stats['years_observed']} years). "
        f"Equivalence check (sum rents / P / years * 100) = {stats['equiv_check']}. "
        f"Zero-rent weeks are included in the mean (not dropped). "
        f"Positive-rent weeks: {stats['completed_payout_cycles']} "
        f"(first positive {first_pos}, last positive {last_pos}). "
        "This is NOT copied from a marketing APY summary page."
    )

    verification_notes = (
        "Property token contract is independently queryable on Gnosis/Ethereum. "
        "Weekly USDC/xDAI rent is distributed on-chain (Gnosis airdrop / Ethereum claim), "
        "but property-level weekly amounts used for realized_yield_pct come from RealT's "
        "published master rent files as exposed by the public community rent tracker — "
        "not from eth_getLogs attribution of airdrops to this property (airdrops are not "
        "property-tagged on-chain in a decodeable way). Therefore verification_tier remains "
        "self-reported-unverified for rent figures, despite stronger on-chain evidence for "
        "token existence than platforms with no public payment history."
    )
    if onchain:
        verification_notes += (
            f" On-chain check: name={onchain['name']!r}, symbol={onchain['symbol']!r}, "
            f"totalSupply={onchain['total_supply']}."
        )

    asset_id = f"realt-{str(contract).lower()}"
    full_name = token.get("fullName") or token.get("shortName") or asset_id
    description = (
        f"RealT RealToken for {full_name} (symbol {token.get('symbol')}), an LLC-series "
        "fractional interest in a U.S. rental property. Holders receive a direct share of "
        "net rental income paid weekly in USD stablecoins (USDC on Ethereum; USDC or xDAI "
        "airdropped on Gnosis per RealT FAQ) — not a protocol-token emission. "
        f"Community API tokenPrice=${price}. Contracts: gnosis={gnosis}, ethereum={eth}. "
        "U.S. primary sales are under Reg D Rule 506(c) per RealT PPMs; non-U.S. persons "
        "may be offered under Regulation S. Transferability requires RealT whitelist/KYC."
    )

    instance: dict[str, Any] = {
        "schema_version": "1.1.0",
        "asset_id": asset_id,
        "source_platform": "realt",
        "asset_class": "real-estate-rental",
        "name": full_name,
        "description_text": description,
        "source_url": f"{api_base.rstrip('/')}/v1/token",
        "data_pulled_at": pulled_at,
        "retrieval_method": "public-api",
        "payout_mechanism": {
            "payout_mechanism_type": "direct-revenue-share",
            "payout_currency": "stablecoin",
            "payout_frequency": "weekly",
        },
        "yield_profile": {
            "advertised_yield_pct": None,
            "realized_yield_pct": stats["realized_yield_pct"],
            "yield_calculation_basis": basis,
            "yield_last_computed_at": pulled_at,
        },
        "verification": {
            "verification_tier": "self-reported-unverified",
            "verification_notes": verification_notes,
        },
        "maturity": {
            "protocol_age_months": protocol_age,
            "protocol_age_months_unknown_reason": None,
            "asset_age_months": asset_age,
            "asset_age_months_unknown_reason": None,
            "completed_payout_cycles": stats["completed_payout_cycles"],
            "completed_payout_cycles_unknown_reason": None,
        },
        "liquidity": {
            "exit_type": "open-market-tradeable",
            "lockup_period_weeks": None,
            "lockup_period_weeks_unknown_reason": None,
            "estimated_time_to_exit_days": None,
            "estimated_time_to_exit_days_unknown_reason": (
                "RealTokens can trade on Gnosis/Ethereum secondary venues (e.g. YAM, "
                "SwapCat, Levinswap) for whitelisted wallets, but order-book depth and "
                "time-to-exit were not measured in this pull."
            ),
        },
        "regulatory": {
            "regulatory_wrapper": "reg-d-506c",
            "accreditation_required": True,
            "restricted_jurisdictions": [],
            "permitted_jurisdictions": ["US"],
        },
        "exposure": {
            "exposure_type": "single-asset",
            "underlying_reference": (
                f"RealT property token {contract} ({full_name})"
            ),
            "operator_name": None,
            "operator_track_record_notes": (
                "Property management is arranged by RealT / series managers per offering "
                "documents; a specific property-manager legal name was not present on the "
                "public community API list payload used for this pull."
            ),
        },
    }
    return instance


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pull RealT property data into asset-v1 snapshots")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--address", help="Gnosis/Ethereum RealToken contract address")
    g.add_argument("--name", help="Substring match on property name/symbol (e.g. Ardmore)")
    g.add_argument("--all", action="store_true", help="Pull multiple active rental tokens")
    p.add_argument("--limit", type=int, default=None, help="With --all, cap number of properties")
    p.add_argument("--dry-run", action="store_true", help="Validate/print only; do not write")
    p.add_argument(
        "--api-base",
        default=os.getenv("REALT_API_BASE", DEFAULT_REALT_API),
        help="Community API base (or REALT_API_BASE)",
    )
    p.add_argument(
        "--rent-tracker-base",
        default=os.getenv("REALT_RENT_TRACKER_BASE", DEFAULT_RENT_TRACKER),
        help="Rent tracker base (or REALT_RENT_TRACKER_BASE)",
    )
    p.add_argument(
        "--gnosis-rpc-url",
        default=os.getenv("GNOSIS_RPC_URL", DEFAULT_GNOSIS_RPC),
        help="Gnosis HTTPS RPC (or GNOSIS_RPC_URL in .env)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    pulled_at = utc_now_iso()
    print(f"[START] RealT adapter pull at {pulled_at}")

    try:
        tokens = fetch_token_list(args.api_base)
        selected = select_tokens(tokens, args.address, args.name, args.all, args.limit)
    except SourceError as e:
        print(f"[FATAL] Source unreachable — aborting with no writes: {e}", file=sys.stderr)
        return 1

    written = 0
    for token in selected:
        contract = (
            token.get("gnosisContract")
            or token.get("xDaiContract")
            or token.get("ethereumContract")
        )
        try:
            rent = fetch_rent_history(args.rent_tracker_base, contract)
            price = float(token["tokenPrice"])
            stats = compute_realized_yield(rent["annual_yield_pct_weekly"], price)
            onchain = fetch_onchain_token_meta(args.gnosis_rpc_url, contract) if contract else None
            instance = build_instance(
                token, rent, stats, onchain, args.api_base, pulled_at
            )
        except SourceError as e:
            print(f"[FATAL] Failed for {token.get('fullName')}: {e}", file=sys.stderr)
            return 1

        print(json.dumps(instance, indent=2))
        if args.dry_run:
            require_valid(instance, f"dry-run {instance['asset_id']}")
        else:
            write_snapshot(instance)
            written += 1

    if not args.dry_run and written == 0:
        print("[FATAL] No snapshots written.", file=sys.stderr)
        return 1

    print(f"[DONE] properties_processed={len(selected)} snapshots_written={written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
