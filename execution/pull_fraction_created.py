#!/usr/bin/env python3
"""Pull all FractionCreated logs for OffchainFractions (mainnet)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from eth_utils import keccak
from web3 import Web3

DATA = Path(__file__).resolve().parent / "artifacts"
OUT = DATA / "fraction_created_raw.json"
ADDR = Web3.to_checksum_address("0x80EA852448c2807BeAe321deC7c603990209F7db")
DEPLOY = 23_483_114
TOPIC = "0x" + keccak(
    text="FractionCreated(bytes32,address,address,uint256,uint256,uint48,address,bool,uint256,address)"
).hex()


def ser(lg):
    data = lg["data"]
    if hasattr(data, "hex"):
        h = data.hex()
        data = "0x" + h if not h.startswith("0x") else h
    topics = []
    for t in lg["topics"]:
        h = t.hex()
        if not h.startswith("0x"):
            h = "0x" + h
        topics.append(h)
    tx = lg["transactionHash"].hex()
    if not tx.startswith("0x"):
        tx = "0x" + tx
    return {
        "blockNumber": lg["blockNumber"],
        "txHash": tx,
        "topics": topics,
        "data": data,
        "logIndex": lg["logIndex"],
    }


def main() -> int:
    rpc_big = "https://eth.drpc.org"
    rpc_small = "https://1rpc.io/eth"
    w3big = Web3(Web3.HTTPProvider(rpc_big, request_kwargs={"timeout": 90}))
    w3small = Web3(Web3.HTTPProvider(rpc_small, request_kwargs={"timeout": 60}))
    latest = w3big.eth.block_number
    out = []
    fr = DEPLOY
    chunk = 3000
    print(f"pulling FractionCreated {DEPLOY}..{latest}")
    while fr <= latest:
        to = min(latest, fr + chunk - 1)
        try:
            logs = w3big.eth.get_logs(
                {"address": ADDR, "fromBlock": fr, "toBlock": to, "topics": [TOPIC]}
            )
            out.extend(logs)
            if chunk < 3000:
                chunk = min(3000, chunk + 500)
        except Exception as e:
            print(f"big fail {fr}-{to}: {e}; fallback 25")
            sub = fr
            while sub <= to:
                sub_to = min(to, sub + 24)
                ok = False
                for _ in range(4):
                    try:
                        logs = w3small.eth.get_logs(
                            {
                                "address": ADDR,
                                "fromBlock": sub,
                                "toBlock": sub_to,
                                "topics": [TOPIC],
                            }
                        )
                        out.extend(logs)
                        ok = True
                        break
                    except Exception:
                        try:
                            logs = w3big.eth.get_logs(
                                {
                                    "address": ADDR,
                                    "fromBlock": sub,
                                    "toBlock": sub_to,
                                    "topics": [TOPIC],
                                }
                            )
                            out.extend(logs)
                            ok = True
                            break
                        except Exception:
                            time.sleep(0.4)
                if not ok:
                    print("SKIP", sub, sub_to)
                sub = sub_to + 1
            chunk = 500
        if fr % 100000 < chunk:
            print(f"@{to} n={len(out)}", flush=True)
        fr = to + 1
        time.sleep(0.02)

    DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "deploy_block": DEPLOY,
        "latest": latest,
        "count": len(out),
        "logs": [ser(x) for x in out],
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"wrote {OUT} count={len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
