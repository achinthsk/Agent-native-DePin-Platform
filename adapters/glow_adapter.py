#!/usr/bin/env python3
"""
Glow farm adapter — pulls real data from currently reachable sources and
maps it into asset-v1.schema.json instances.

Primary sources (see adapters/FINDINGS.md):
  1. GCA public HTTP API  — farm registry / capacity / location / init time
  2. Ethereum eth_call    — MinerPoolAndGCA weekly reward-bucket state

Does NOT use the documented Control API (control-api.glowlabs.org is NXDOMAIN
as of the investigation date). Does NOT invent realized yields.

Usage:
  python3 adapters/glow_adapter.py --farm-id 1
  python3 adapters/glow_adapter.py --all --limit 3
  python3 adapters/glow_adapter.py --farm-id 1 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from eth_abi import decode, encode
from eth_utils import keccak
from web3 import Web3

# Allow `python3 adapters/glow_adapter.py` from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import write_snapshot  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")

# Guarded Launch addresses from glowlabs-org/glow-contracts README / glow-utils.
GCA_AND_MINER_POOL = Web3.to_checksum_address(
    "0x6Fa8C7a89b22bf3212392b778905B12f3dBAF5C4"
)
GLW_TOKEN = Web3.to_checksum_address("0xf4fbC617A5733EAAF9af08E1Ab816B103388d8B6")

DEFAULT_GCA_BASE = "http://95.217.194.59:35015"
DEFAULT_RPC = "https://eth.drpc.org"
TIMESLOT_SECONDS = 300  # GCA backend: timeslots are 5 minutes
SECONDS_PER_MONTH = 30.4375 * 24 * 3600
HTTP_RETRIES = 3
HTTP_TIMEOUT = 30


class SourceError(Exception):
    """Raised when a required live source is unreachable or returns bad data."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def http_get_json(url: str, retries: int = HTTP_RETRIES) -> Any:
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"Accept": "application/json", "User-Agent": "glow-adapter/1.0"})
            with urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                body = resp.read()
            return json.loads(body.decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
            last_err = e
            print(
                f"[ERROR] HTTP GET {url} attempt {attempt}/{retries} failed: {e}",
                file=sys.stderr,
            )
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise SourceError(f"RPC/HTTP call failed after {retries} retries: {url}: {last_err}")


def eth_call(
    w3: Web3,
    address: str,
    signature: str,
    arg_types: list[str] | None = None,
    args: list[Any] | None = None,
    out_types: list[str] | None = None,
    retries: int = HTTP_RETRIES,
) -> Any:
    selector = keccak(text=signature)[:4]
    data = selector
    if arg_types:
        data += encode(arg_types, args or [])
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            raw = w3.eth.call({"to": address, "data": data})
            if out_types is None:
                return raw
            return decode(out_types, raw)
        except Exception as e:  # noqa: BLE001 — surface whatever web3 raises
            last_err = e
            print(
                f"[ERROR] eth_call {signature} attempt {attempt}/{retries} failed: {e}",
                file=sys.stderr,
            )
            if attempt < retries:
                time.sleep(1.5 * attempt)
    raise SourceError(
        f"RPC call timed out/failed after {retries} retries: {signature}: {last_err}"
    )


def connect_rpc(rpc_url: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": HTTP_TIMEOUT}))
    try:
        block = w3.eth.block_number
    except Exception as e:  # noqa: BLE001
        raise SourceError(f"Ethereum RPC unreachable at {rpc_url}: {e}") from e
    print(f"[OK] Connected to Ethereum RPC; latest block={block}")
    return w3


def fetch_equipment(gca_base: str) -> dict[str, dict[str, Any]]:
    url = f"{gca_base.rstrip('/')}/api/v1/equipment"
    payload = http_get_json(url)
    details = payload.get("EquipmentDetails")
    if not isinstance(details, dict) or not details:
        raise SourceError(f"GCA equipment response missing EquipmentDetails: {url}")
    print(f"[OK] GCA equipment: {len(details)} farms from {url}")
    return details


def fetch_onchain_protocol_state(w3: Web3) -> dict[str, Any]:
    genesis = eth_call(w3, GCA_AND_MINER_POOL, "GENESIS_TIMESTAMP()", out_types=["uint256"])[0]
    current_bucket = eth_call(w3, GCA_AND_MINER_POOL, "currentBucket()", out_types=["uint256"])[0]
    glw_symbol = eth_call(w3, GLW_TOKEN, "symbol()", out_types=["string"])[0]
    glw_name = eth_call(w3, GLW_TOKEN, "name()", out_types=["string"])[0]

    # Sample a recent finalized bucket to prove reward roots are queryable.
    sample_bucket_id = max(int(current_bucket) - 2, 0)
    finalized = eth_call(
        w3,
        GCA_AND_MINER_POOL,
        "isBucketFinalized(uint256)",
        ["uint256"],
        [sample_bucket_id],
        ["bool"],
    )[0]
    global_state = eth_call(
        w3,
        GCA_AND_MINER_POOL,
        "bucketGlobalState(uint256)",
        ["uint256"],
        [sample_bucket_id],
        ["uint128", "uint64", "uint64"],
    )
    total_new_gcc, total_glw_weight, total_grc_weight = global_state

    chain_now = w3.eth.get_block("latest")["timestamp"]
    print(
        f"[OK] On-chain MinerPoolAndGCA: genesis={genesis}, currentBucket={current_bucket}, "
        f"sampleBucket={sample_bucket_id} finalized={finalized}, "
        f"GLW symbol={glw_symbol}"
    )
    return {
        "genesis_timestamp": int(genesis),
        "current_bucket": int(current_bucket),
        "chain_now": int(chain_now),
        "glw_symbol": glw_symbol,
        "glw_name": glw_name,
        "sample_bucket_id": int(sample_bucket_id),
        "sample_bucket_finalized": bool(finalized),
        "sample_total_new_gcc": int(total_new_gcc),
        "sample_total_glw_weight": int(total_glw_weight),
        "sample_total_grc_weight": int(total_grc_weight),
    }


def months_between(start_ts: int, end_ts: int) -> int:
    if end_ts < start_ts:
        return 0
    return int((end_ts - start_ts) / SECONDS_PER_MONTH)


def capacity_mw(capacity_milliwatts: int) -> float:
    # GCA README: milliwatts are the power unit.
    return capacity_milliwatts / 1_000_000_000.0


def build_instance(
    farm_id: str,
    farm: dict[str, Any],
    protocol: dict[str, Any],
    gca_base: str,
    pulled_at: str,
) -> dict[str, Any]:
    init_slot = int(farm["Initialization"])
    asset_start = protocol["genesis_timestamp"] + init_slot * TIMESLOT_SECONDS
    protocol_age = months_between(protocol["genesis_timestamp"], protocol["chain_now"])
    asset_age = months_between(asset_start, protocol["chain_now"])
    cap_mw = capacity_mw(int(farm["Capacity"]))
    lat = farm.get("Latitude")
    lon = farm.get("Longitude")

    # Realized yield: NOT computed. Farm→delegator GLW attribution is not
    # publicly recoverable (merkle leaves use payout wallets; Control API down).
    yield_reason = (
        "realized_yield_pct is null because farm-level GLW emissions to this farm's "
        "delegators are not publicly attributable from currently reachable sources. "
        "MinerPoolAndGCA weekly reports store merkle roots whose leaves are "
        "(payoutWallet, glwRewardsWeight, grcRewardsWeight); this adapter observed "
        f"on-chain bucket {protocol['sample_bucket_id']} "
        f"(finalized={protocol['sample_bucket_finalized']}, "
        f"totalGLWRewardsWeight={protocol['sample_total_glw_weight']}) but cannot map "
        "those weights to farm ShortID "
        f"{farm_id} or to delegator positions. The Glow Control API "
        "(control-api.glowlabs.org), which the official SDK documents for "
        "/farms/{{id}}/weekly-rewards, returned NXDOMAIN at investigation time. "
        "advertised_yield_pct is also null: no marketed yield percentage is present "
        "on the GCA equipment endpoint or in on-chain view getters queried here."
    )

    verification_notes = (
        "Weekly GCA carbon-credit / reward reports are posted on-chain to MinerPoolAndGCA "
        f"({GCA_AND_MINER_POOL}) as merkle roots (BucketSubmission / bucket()), which anyone "
        "can eth_call. That is the cryptographic on-chain proof this tier refers to. "
        "Physical electricity/output figures for this farm originate from the public GCA "
        "equipment/device-stats API and from GCA reports — this adapter did not independently "
        "re-verify satellite or AI imagery for this pull."
    )

    name = f"Glow Solar Farm #{farm_id}"
    description = (
        f"Glow-protocol solar installation ShortID={farm_id}, reported capacity "
        f"{cap_mw:.6f} MW (from GCA Capacity={farm['Capacity']} milliwatts), "
        f"coordinates lat={lat}, lon={lon}. "
        f"Protocol token is {protocol['glw_name']} ({protocol['glw_symbol']}). "
        "Holders who finance a farm's protocol deposit earn GLW token-emission rewards "
        "over the protocol's vesting window; they do not receive a direct cash cut of "
        "this farm's electricity revenue (100% of electricity revenue is contributed to "
        "Glow's shared incentive pool per Glow public docs). "
        f"On-chain genesis={protocol['genesis_timestamp']}, "
        f"currentBucket={protocol['current_bucket']}."
    )

    # Lockup: Glow public docs describe a 100-week vesting window for protocol-deposit
    # financers. That figure is NOT returned by an on-chain getter we called; if you
    # need strictly on-chain-only lockup, treat this field as documentation-sourced.
    # We still record it as the protocol's stated contractual vesting, with the source
    # called out here rather than silently omitting the well-documented parameter.
    instance: dict[str, Any] = {
        "schema_version": "1.0.0",
        "asset_id": f"glow-farm-{farm_id}",
        "source_platform": "glow",
        "asset_class": "solar-depin",
        "name": name,
        "description_text": description,
        "source_url": f"{gca_base.rstrip('/')}/api/v1/equipment",
        "data_pulled_at": pulled_at,
        # Farm identity comes from the GCA public API; on-chain enrichment is also performed.
        "retrieval_method": "public-api",
        "payout_mechanism": {
            "payout_mechanism_type": "token-emission-reward",
            "payout_currency": "native-protocol-token",
            "payout_frequency": "weekly",
        },
        "yield_profile": {
            "advertised_yield_pct": None,
            "realized_yield_pct": None,
            "yield_calculation_basis": yield_reason,
            "yield_last_computed_at": pulled_at,
        },
        "verification": {
            "verification_tier": "cryptographic-onchain-proof",
            "verification_notes": verification_notes,
        },
        "maturity": {
            "protocol_age_months": protocol_age,
            "protocol_age_months_unknown_reason": None,
            "asset_age_months": asset_age,
            "asset_age_months_unknown_reason": None,
            # Cannot count farm-specific completed payout cycles without farm→leaf mapping.
            "completed_payout_cycles": None,
            "completed_payout_cycles_unknown_reason": (
                "Farm-specific completed payout cycles are not observable from the GCA "
                "equipment endpoint or from MinerPoolAndGCA bucket global state alone. "
                "Weekly buckets exist protocol-wide "
                f"(currentBucket={protocol['current_bucket']}), but this adapter cannot "
                "prove how many finalized buckets included this farm ShortID in a reward "
                "merkle tree without Control API weekly-rewards data or decoded leaves."
            ),
            "protocol_version": "Glow Guarded Launch / MinerPoolAndGCA",
        },
        # lockup_period_weeks=100 comes from Glow public docs on protocol-deposit
        # financer vesting (e.g. glow.org blog); it is not read from an on-chain
        # getter in this adapter.
        "liquidity": {
            "exit_type": "fixed-lockup",
            "lockup_period_weeks": 100,
            "lockup_period_weeks_unknown_reason": None,
            "estimated_time_to_exit_days": None,
            "estimated_time_to_exit_days_unknown_reason": (
                "Contractual vesting is documented as 100 weeks, but practical "
                "time-to-exit after (or during) vesting was not observed from GCA "
                "or on-chain data in this pull — no public order-book / redemption "
                "latency figure was available."
            ),
        },
        "regulatory": {
            "regulatory_wrapper": "unregistered-onchain-token",
            "accreditation_required": False,
            # Both empty = jurisdictional eligibility unknown (per schema), not "unrestricted".
            "restricted_jurisdictions": [],
            "permitted_jurisdictions": [],
        },
        "exposure": {
            "exposure_type": "single-asset",
            "underlying_reference": f"Glow GCA farm ShortID {farm_id}",
            "operator_name": None,
            "operator_track_record_notes": (
                "GCA /api/v1/equipment does not publish an operator legal name for this "
                f"ShortID. Debt={farm.get('Debt')} cents, ProtocolFee={farm.get('ProtocolFee')} "
                "cents as reported by the GCA server (not independently audited by this adapter)."
            ),
        },
    }
    return instance


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pull Glow farm data into asset-v1 snapshots")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--farm-id", help="GCA ShortID of a single farm (e.g. 1)")
    g.add_argument("--all", action="store_true", help="Pull all farms from GCA equipment")
    p.add_argument("--limit", type=int, default=None, help="With --all, cap number of farms")
    p.add_argument("--dry-run", action="store_true", help="Validate and print JSON; do not write storage/")
    p.add_argument(
        "--gca-base",
        default=os.getenv("GCA_API_BASE", DEFAULT_GCA_BASE),
        help="GCA API base URL (or set GCA_API_BASE)",
    )
    p.add_argument(
        "--rpc-url",
        default=os.getenv("ETH_RPC_URL", DEFAULT_RPC),
        help="Ethereum HTTPS RPC URL (or set ETH_RPC_URL in .env)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    pulled_at = utc_now_iso()
    print(f"[START] Glow adapter pull at {pulled_at}")

    try:
        w3 = connect_rpc(args.rpc_url)
        protocol = fetch_onchain_protocol_state(w3)
        equipment = fetch_equipment(args.gca_base)
    except SourceError as e:
        print(f"[FATAL] Source unreachable — aborting with no writes: {e}", file=sys.stderr)
        return 1

    if args.farm_id:
        farm_ids = [str(args.farm_id)]
        if farm_ids[0] not in equipment:
            print(
                f"[FATAL] Farm ShortID {farm_ids[0]} not found in GCA equipment "
                f"({len(equipment)} farms loaded).",
                file=sys.stderr,
            )
            return 1
    else:
        farm_ids = sorted(equipment.keys(), key=lambda x: int(x) if x.isdigit() else x)
        if args.limit is not None:
            farm_ids = farm_ids[: args.limit]

    written = 0
    for fid in farm_ids:
        farm = equipment[fid]
        instance = build_instance(fid, farm, protocol, args.gca_base, pulled_at)
        print(json.dumps(instance, indent=2))
        if args.dry_run:
            # Still validate even on dry-run.
            from common import require_valid

            require_valid(instance, f"dry-run {instance['asset_id']}")
        else:
            write_snapshot(instance)
            written += 1

    if not args.dry_run and written == 0:
        print("[FATAL] No snapshots written.", file=sys.stderr)
        return 1

    print(f"[DONE] farms_processed={len(farm_ids)} snapshots_written={written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
