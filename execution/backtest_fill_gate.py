#!/usr/bin/env python3
"""
Historical backtest of Part B fill/expiry gates against real on-chain
OffchainFractions state (archive eth_call getFraction).

Gate under test (Clarification D):
  soldSteps / minSharesToRaise >= 0.90
  AND 0 < timeToExpiry <= 7 days
  AND not manuallyClosed AND soldSteps < totalSteps

Universe: every FractionCreated on mainnet OffchainFractions since deploy.
Outcome: completed vs expired/closed underfilled (still-open excluded from
completion-rate denominator).

Usage:
  python3 execution/backtest_fill_gate.py
  python3 execution/backtest_fill_gate.py --rpc https://eth.drpc.org
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from eth_abi import decode, encode
from eth_utils import keccak
from web3 import Web3

REPO = Path(__file__).resolve().parent
DATA = REPO / "artifacts"
CREATED_PATH = DATA / "fraction_created_raw.json"
OUT_PATH = DATA / "fill_gate_backtest.json"
PROGRESS_PATH = DATA / "fill_gate_backtest.progress.json"

OFFCHAIN_FRACTIONS = Web3.to_checksum_address(
    "0x80EA852448c2807BeAe321deC7c603990209F7db"
)
GET_FRACTION_SEL = keccak(text="getFraction(address,bytes32)")[:4]
FRAC_TYPES = [
    "(address,uint48,bool,uint256,bool,bool,uint256,address,uint256,uint256,address)"
]
CREATE_DATA_TYPES = [
    "uint256",
    "uint256",
    "uint48",
    "address",
    "bool",
    "uint256",
    "address",
]

MIN_FILL_RATIO = 0.90
MAX_TIME_TO_EXPIRY = 7 * 24 * 3600
DEPLOY_BLOCK = 23_483_114


def decode_created(lg: dict) -> dict:
    fid = lg["topics"][1]
    token = "0x" + lg["topics"][2][-40:]
    owner = Web3.to_checksum_address("0x" + lg["topics"][3][-40:] )
    raw = bytes.fromhex(lg["data"][2:] if lg["data"].startswith("0x") else lg["data"])
    step, total_steps, expiration, to, _use_cf, min_shares, closer = decode(
        CREATE_DATA_TYPES, raw
    )
    return {
        "id": fid,
        "token": Web3.to_checksum_address(token),
        "creator": owner,
        "createBlock": lg["blockNumber"],
        "createTx": lg["txHash"],
        "step": int(step),
        "totalSteps": int(total_steps),
        "expiration": int(expiration),
        "minSharesToRaise": int(min_shares),
        "to": to,
        "closer": closer,
    }


def get_fraction_at(w3: Web3, creator: str, fid_hex: str, block: int) -> dict | None:
    fid = bytes.fromhex(fid_hex[2:])
    data = GET_FRACTION_SEL + encode(
        ["address", "bytes32"], [Web3.to_checksum_address(creator), fid]
    )
    raw = w3.eth.call({"to": OFFCHAIN_FRACTIONS, "data": data}, block_identifier=block)
    if not raw or len(raw) < 32:
        return None
    (tup,) = decode(FRAC_TYPES, raw)
    (
        token,
        expiration,
        manually_closed,
        min_shares,
        _use_cf,
        claimed,
        step,
        _to,
        sold_steps,
        total_steps,
        closer,
    ) = tup
    if int(token, 16) == 0 and total_steps == 0:
        return None
    return {
        "token": token,
        "expiration": int(expiration),
        "manuallyClosed": bool(manually_closed),
        "minSharesToRaise": int(min_shares),
        "claimedFromMinSharesToRaise": bool(claimed),
        "step": int(step),
        "soldSteps": int(sold_steps),
        "totalSteps": int(total_steps),
        "closer": closer,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default="https://eth.drpc.org")
    ap.add_argument("--limit", type=int, default=0, help="Optional cap for smoke tests")
    args = ap.parse_args()

    if not CREATED_PATH.exists():
        raise SystemExit(f"Missing {CREATED_PATH}; pull FractionCreated logs first.")

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": 60}))
    latest = w3.eth.block_number
    latest_ts = int(w3.eth.get_block(latest)["timestamp"])
    print(
        f"[backtest] latest={latest} ts={latest_ts} "
        f"({datetime.fromtimestamp(latest_ts, tz=timezone.utc).isoformat()})"
    )

    created = json.loads(CREATED_PATH.read_text())
    fractions = [decode_created(lg) for lg in created["logs"]]
    uniq: dict[tuple[str, str], dict] = {}
    for f in fractions:
        uniq[(f["creator"].lower(), f["id"])] = f
    fractions = list(uniq.values())
    if args.limit:
        fractions = fractions[: args.limit]
    print(f"[backtest] unique fractions={len(fractions)}")

    block_cache: dict[int, int] = {}

    def block_at_or_before(ts: int) -> int:
        if ts in block_cache:
            return block_cache[ts]
        if ts >= latest_ts:
            block_cache[ts] = latest
            return latest
        est = latest - int((latest_ts - ts) / 12)
        est = max(DEPLOY_BLOCK, min(latest, est))
        lo2, hi2 = max(DEPLOY_BLOCK, est - 10_000), min(latest, est + 10_000)
        while lo2 < hi2:
            mid = (lo2 + hi2 + 1) // 2
            for attempt in range(4):
                try:
                    bts = int(w3.eth.get_block(mid)["timestamp"])
                    break
                except Exception:
                    time.sleep(0.3 * (attempt + 1))
            else:
                raise RuntimeError(f"get_block failed at {mid}")
            if bts <= ts:
                lo2 = mid
            else:
                hi2 = mid - 1
        block_cache[ts] = lo2
        return lo2

    results: list[dict] = []
    # Resume if progress exists
    if PROGRESS_PATH.exists():
        prev = json.loads(PROGRESS_PATH.read_text())
        results = prev.get("results", [])
        done_ids = {(r.get("creator", "").lower(), r.get("id")) for r in results if "id" in r}
        print(f"[backtest] resuming with {len(results)} prior results")
    else:
        done_ids = set()

    for i, f in enumerate(fractions):
        key = (f["creator"].lower(), f["id"])
        if key in done_ids:
            continue
        exp = f["expiration"]
        try:
            create_ts = int(w3.eth.get_block(f["createBlock"])["timestamp"])
        except Exception as e:
            results.append({"id": f["id"], "creator": f["creator"], "error": f"create_ts: {e}"})
            continue

        # Sparse samples: create, each day in last 7d, near-expiry, now
        offsets = [MAX_TIME_TO_EXPIRY, 6 * 86400, 5 * 86400, 4 * 86400, 3 * 86400, 2 * 86400, 86400, 12 * 3600, 1]
        sample_ts = sorted(
            {
                create_ts,
                *[max(create_ts, exp - o) for o in offsets],
                min(exp, latest_ts),
                latest_ts,
            }
        )

        samples = []
        passed_gate = False
        first_pass = None
        for ts in sample_ts:
            try:
                blk = block_at_or_before(ts)
            except Exception as e:
                samples.append({"ts": ts, "error": str(e)})
                continue
            if blk < f["createBlock"]:
                continue
            try:
                fr = get_fraction_at(w3, f["creator"], f["id"], blk)
            except Exception as e:
                samples.append({"ts": ts, "block": blk, "error": str(e)})
                time.sleep(0.2)
                continue
            if fr is None:
                samples.append({"ts": ts, "block": blk, "missing": True})
                continue
            min_s = fr["minSharesToRaise"] or f["minSharesToRaise"]
            fill = (fr["soldSteps"] / min_s) if min_s else 0.0
            tte = fr["expiration"] - ts
            gate = (
                fill >= MIN_FILL_RATIO
                and 0 < tte <= MAX_TIME_TO_EXPIRY
                and not fr["manuallyClosed"]
                and fr["soldSteps"] < fr["totalSteps"]
            )
            row = {
                "ts": ts,
                "block": blk,
                "soldSteps": fr["soldSteps"],
                "totalSteps": fr["totalSteps"],
                "minShares": min_s,
                "fill": round(fill, 6),
                "tte": tte,
                "gate": gate,
                "manuallyClosed": fr["manuallyClosed"],
                "claimed": fr["claimedFromMinSharesToRaise"],
            }
            samples.append(row)
            if gate and not passed_gate:
                passed_gate = True
                first_pass = row

        fr_now = None
        fr_exp = None
        try:
            fr_now = get_fraction_at(w3, f["creator"], f["id"], latest)
            exp_blk = block_at_or_before(min(exp, latest_ts))
            fr_exp = get_fraction_at(w3, f["creator"], f["id"], exp_blk)
        except Exception as e:
            results.append(
                {
                    "id": f["id"],
                    "creator": f["creator"],
                    "error": f"terminal: {e}",
                    "samples": samples,
                }
            )
            continue

        if (
            latest_ts < exp
            and fr_now
            and not fr_now["manuallyClosed"]
            and fr_now["soldSteps"] < fr_now["totalSteps"]
            and fr_now["soldSteps"] < fr_now["minSharesToRaise"]
            and not fr_now["claimedFromMinSharesToRaise"]
        ):
            outcome = "still_open"
        else:
            ref = fr_exp or fr_now
            if ref is None:
                outcome = "missing"
            elif (
                ref["soldSteps"] >= ref["minSharesToRaise"]
                or ref["claimedFromMinSharesToRaise"]
                or ref["soldSteps"] >= ref["totalSteps"]
            ):
                outcome = "completed"
            elif ref["manuallyClosed"] and ref["soldSteps"] < ref["minSharesToRaise"]:
                outcome = "closed_underfilled"
            elif latest_ts >= exp and ref["soldSteps"] < ref["minSharesToRaise"]:
                outcome = "expired_underfilled"
            else:
                outcome = "other"

        results.append(
            {
                "id": f["id"],
                "creator": f["creator"],
                "createBlock": f["createBlock"],
                "expiration": exp,
                "minSharesToRaise": f["minSharesToRaise"],
                "totalSteps": f["totalSteps"],
                "passed_gate_90_7d": passed_gate,
                "first_pass": first_pass,
                "outcome": outcome,
                "final_sold": (fr_now or {}).get("soldSteps"),
                "final_min": (fr_now or {}).get("minSharesToRaise"),
                "samples": samples,
            }
        )

        if (len(results) % 5) == 0:
            PROGRESS_PATH.write_text(json.dumps({"results": results}))
            print(f"  progress {len(results)}/{len(fractions)}", flush=True)
        time.sleep(0.03)

    terminal = [
        r
        for r in results
        if r.get("outcome")
        in ("completed", "expired_underfilled", "closed_underfilled")
    ]
    passed = [r for r in terminal if r.get("passed_gate_90_7d")]
    passed_completed = [r for r in passed if r["outcome"] == "completed"]
    passed_failed = [
        r
        for r in passed
        if r["outcome"] in ("expired_underfilled", "closed_underfilled")
    ]
    errors = [r for r in results if "error" in r]

    summary = {
        "method": (
            "Archive eth_call OffchainFractions.getFraction sampled at create, "
            "each day in the final 7d before expiration, near-expiry, and latest. "
            "Universe = all FractionCreated events pulled from mainnet logs."
        ),
        "rpc": args.rpc,
        "pulled_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "min_fill_ratio": MIN_FILL_RATIO,
        "max_time_to_expiry_seconds": MAX_TIME_TO_EXPIRY,
        "fractions_created_unique": len(fractions),
        "results_ok": len(results) - len(errors),
        "errors": len(errors),
        "still_open": sum(1 for r in results if r.get("outcome") == "still_open"),
        "terminal_completed": sum(1 for r in terminal if r["outcome"] == "completed"),
        "terminal_expired_underfilled": sum(
            1 for r in terminal if r["outcome"] == "expired_underfilled"
        ),
        "terminal_closed_underfilled": sum(
            1 for r in terminal if r["outcome"] == "closed_underfilled"
        ),
        "gate_passers_among_terminal": len(passed),
        "gate_passers_that_completed": len(passed_completed),
        "gate_passers_that_failed": len(passed_failed),
        "completion_rate_given_gate": (
            (len(passed_completed) / len(passed)) if passed else None
        ),
        "all_gate_passers_including_open": sum(
            1 for r in results if r.get("passed_gate_90_7d")
        ),
        "note": (
            "completion_rate_given_gate is the primary metric: among terminal "
            "fractions that at some sampled time satisfied the 90%/7d gate, "
            "what share eventually reached minSharesToRaise."
        ),
    }

    OUT_PATH.write_text(json.dumps({"summary": summary, "results": results}, indent=2))
    if PROGRESS_PATH.exists():
        PROGRESS_PATH.unlink()
    print(json.dumps(summary, indent=2))
    print(f"[backtest] wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
