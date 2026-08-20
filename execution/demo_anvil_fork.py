#!/usr/bin/env python3
"""
Anvil mainnet-fork demo for Part B.

Demonstrates:
  1. REFUSE — real live Hub listing that fails fill/expiry gates
  2. PASS   — fork-local fraction (≥90% fill, ≤7d expiry) using a mock
              ERC-20 payment token (mainnet GLW transfers are allowlist-
              restricted; storage-deal alone cannot make transferFrom work)
  3. Mainnet broadcast refusal on chain_id 1

Signing uses Anvil's well-known local test keys only — never a real key.
glow_execute.py constructs unsigned calldata; this script is the agent-side
signer for the fork demo only.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from eth_account import Account
from eth_utils import to_checksum_address
from web3 import Web3

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
import glow_execute as gx  # noqa: E402

ANVIL_KEY0 = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ANVIL_KEY1 = "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d"
ANVIL_ADDR0 = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

REAL_REFUSE_CREATOR = "0x2b57E1bF5071c6579F2145b367EEC34f8729AA9C"
REAL_REFUSE_ID = (
    "0x51ab76b04053b16422787348785f051b636f7b0e066ffc9bcf4bab5b2116c53d"
)

MOCK_ARTIFACT = REPO / "contracts" / "MockERC20.json"


def load_abi(name: str):
    return json.loads((REPO / "abis" / name).read_text())


def send_unsigned(w3: Web3, account, unsigned: dict, nonce: int) -> str:
    gx.assert_not_mainnet_broadcast(w3, w3.provider.endpoint_uri)
    tx = {
        "to": to_checksum_address(unsigned["to"]),
        "data": unsigned["data"],
        "value": int(unsigned.get("value", "0x0"), 16),
        "nonce": nonce,
        "chainId": int(w3.eth.chain_id),
        "gas": 800_000,
        "maxFeePerGas": w3.to_wei(50, "gwei"),
        "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
    }
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    txh = w3.eth.send_raw_transaction(raw)
    receipt = w3.eth.wait_for_transaction_receipt(txh)
    if receipt.status != 1:
        raise RuntimeError(f"tx failed: {txh.hex()} status={receipt.status}")
    return txh.hex()


def send_built(w3: Web3, account, built: dict) -> str:
    gx.assert_not_mainnet_broadcast(w3, w3.provider.endpoint_uri)
    signed = account.sign_transaction(built)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    txh = w3.eth.send_raw_transaction(raw)
    receipt = w3.eth.wait_for_transaction_receipt(txh)
    if receipt.status != 1:
        raise RuntimeError(f"tx failed: {txh.hex()} status={receipt.status}")
    return txh.hex()


def deploy_mock_erc20(w3: Web3, deployer_acct) -> tuple[str, any]:
    if not MOCK_ARTIFACT.exists():
        raise SystemExit(
            f"Missing {MOCK_ARTIFACT}. Compile with forge first "
            "(see execution/README.md)."
        )
    art = json.loads(MOCK_ARTIFACT.read_text())
    bytecode = art["bytecode"]["object"]
    abi = art["abi"]
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(deployer_acct.address)
    tx = contract.constructor().build_transaction(
        {
            "from": deployer_acct.address,
            "nonce": nonce,
            "chainId": int(w3.eth.chain_id),
            "gas": 1_500_000,
            "maxFeePerGas": w3.to_wei(50, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        }
    )
    txh = send_built(w3, deployer_acct, tx)
    receipt = w3.eth.get_transaction_receipt(txh)
    addr = to_checksum_address(receipt["contractAddress"])
    return addr, w3.eth.contract(address=addr, abi=abi)


def demo_refuse(w3: Web3) -> dict:
    print("\n=== DEMO 1: REFUSE real underfilled listing ===")
    result = gx.construct_intent(
        w3,
        creator=REAL_REFUSE_CREATOR,
        fraction_id=REAL_REFUSE_ID,
        buyer=ANVIL_ADDR0,
        steps_to_buy=1,
        hub_committed=True,
    )
    print(json.dumps(result, indent=2))
    assert result.get("refused") is True
    assert result.get("reason_code") in ("fill_below_threshold", "expiry_too_far")
    print(f"[PASS] refused with reason_code={result['reason_code']}")
    return result


def demo_pass(w3: Web3) -> dict:
    print("\n=== DEMO 2: PASS — mock-token fraction at 90% / 3d expiry ===")
    gx.assert_not_mainnet_broadcast(w3, w3.provider.endpoint_uri)
    assert int(w3.eth.chain_id) in gx.ANVIL_CHAIN_IDS

    creator_acct = Account.from_key(ANVIL_KEY0)
    buyer_acct = Account.from_key(ANVIL_KEY1)
    creator = to_checksum_address(creator_acct.address)
    buyer = to_checksum_address(buyer_acct.address)

    w3.provider.make_request("anvil_setBalance", [creator, hex(10**18 * 100)])
    w3.provider.make_request("anvil_setBalance", [buyer, hex(10**18 * 100)])

    mock_addr, mock = deploy_mock_erc20(w3, creator_acct)
    print(f"[fork] deployed MockERC20 at {mock_addr}")

    of = w3.eth.contract(
        address=gx.OFFCHAIN_FRACTIONS, abi=load_abi("offchain_fractions.json")
    )

    now = int(w3.eth.get_block("latest")["timestamp"])
    expiry = now + 3 * 24 * 3600
    fraction_id = "0x" + os.urandom(32).hex()
    total_steps = 100
    min_shares = 100
    step = 10**18
    steps_prefill = 90
    steps_buy = 1
    need = (steps_prefill + steps_buy + 5) * step

    # mint to buyer
    nonce = w3.eth.get_transaction_count(creator)
    mint_tx = mock.functions.mint(buyer, need).build_transaction(
        {
            "from": creator,
            "nonce": nonce,
            "chainId": int(w3.eth.chain_id),
            "gas": 100_000,
            "maxFeePerGas": w3.to_wei(50, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        }
    )
    send_built(w3, creator_acct, mint_tx)

    nonce = w3.eth.get_transaction_count(creator)
    create_tx = of.functions.createFraction(
        bytes.fromhex(fraction_id[2:]),
        mock_addr,
        step,
        total_steps,
        expiry,
        creator,
        False,
        min_shares,
        creator,
    ).build_transaction(
        {
            "from": creator,
            "nonce": nonce,
            "chainId": int(w3.eth.chain_id),
            "gas": 1_200_000,
            "maxFeePerGas": w3.to_wei(50, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        }
    )
    print(f"[fork] createFraction id={fraction_id} tx={send_built(w3, creator_acct, create_tx)}")

    nonce = w3.eth.get_transaction_count(buyer)
    approve = mock.functions.approve(gx.OFFCHAIN_FRACTIONS, steps_prefill * step).build_transaction(
        {
            "from": buyer,
            "nonce": nonce,
            "chainId": int(w3.eth.chain_id),
            "gas": 100_000,
            "maxFeePerGas": w3.to_wei(50, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        }
    )
    send_built(w3, buyer_acct, approve)

    nonce = w3.eth.get_transaction_count(buyer)
    buy = of.functions.buyFractions(
        creator,
        bytes.fromhex(fraction_id[2:]),
        steps_prefill,
        steps_prefill,
        buyer,
        buyer,
        False,
    ).build_transaction(
        {
            "from": buyer,
            "nonce": nonce,
            "chainId": int(w3.eth.chain_id),
            "gas": 800_000,
            "maxFeePerGas": w3.to_wei(50, "gwei"),
            "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
        }
    )
    print(f"[fork] prefill tx={send_built(w3, buyer_acct, buy)}")
    fr0 = gx.fetch_fraction(w3, creator, fraction_id)
    assert fr0 and fr0["soldSteps"] == steps_prefill, fr0
    print(f"[fork] prefilled {steps_prefill}/{total_steps} (fill={fr0['soldSteps']/fr0['minSharesToRaise']:.2f})")

    constructed = gx.construct_intent(
        w3,
        creator=creator,
        fraction_id=fraction_id,
        buyer=buyer,
        steps_to_buy=steps_buy,
        hub_committed=True,
        slippage_bps=100,
    )
    print(
        json.dumps(
            {k: constructed[k] for k in constructed if k != "transactions"}, indent=2
        )
    )
    print("transactions:", json.dumps(constructed.get("transactions"), indent=2))
    assert constructed.get("ok") is True, constructed

    nonce = w3.eth.get_transaction_count(buyer)
    sent = []
    for utx in constructed["transactions"]:
        txh = send_unsigned(w3, buyer_acct, utx, nonce)
        sent.append(txh)
        nonce += 1
        print(f"[fork] sent {utx['description']}: {txh}")

    fr = gx.fetch_fraction(w3, creator, fraction_id)
    assert fr is not None
    assert fr["soldSteps"] == steps_prefill + steps_buy
    print(
        f"[PASS] buy executed on Anvil fork; soldSteps={fr['soldSteps']} "
        f"chain_id={w3.eth.chain_id}"
    )
    return {
        "ok": True,
        "fraction_id": fraction_id,
        "creator": creator,
        "buyer": buyer,
        "payment_token": mock_addr,
        "soldSteps": fr["soldSteps"],
        "txs": sent,
        "chain_id": int(w3.eth.chain_id),
        "note": (
            "Payment token is fork-deployed MockERC20 because mainnet GLW "
            "rejects arbitrary transferFrom (allowlist)."
        ),
    }


def demo_mainnet_broadcast_refused(rpc_mainnet: str) -> None:
    print("\n=== DEMO 3: mainnet broadcast safety ===")
    w3 = Web3(Web3.HTTPProvider(rpc_mainnet, request_kwargs={"timeout": 30}))
    try:
        gx.assert_not_mainnet_broadcast(w3, rpc_mainnet)
        raise AssertionError("expected mainnet broadcast refusal")
    except RuntimeError as e:
        print(f"[PASS] {e}")


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rpc", default=os.environ.get("ANVIL_RPC", "http://127.0.0.1:8545"))
    ap.add_argument(
        "--mainnet-rpc",
        default=os.environ.get("ETH_RPC_URL", "https://eth.drpc.org"),
    )
    args = ap.parse_args()

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": 60}))
    if not w3.is_connected():
        print(
            f"Cannot connect to {args.rpc}. Start Anvil:\n"
            f"  anvil --fork-url $ETH_RPC_URL --port 8545 --chain-id 31337",
            file=sys.stderr,
        )
        return 1

    chain_id = int(w3.eth.chain_id)
    print(f"connected rpc={args.rpc} chain_id={chain_id}")
    if chain_id not in gx.ANVIL_CHAIN_IDS:
        print("REFUSING: demo requires Anvil chain_id 31337", file=sys.stderr)
        return 1

    refuse = demo_refuse(w3)
    passed = demo_pass(w3)
    demo_mainnet_broadcast_refused(args.mainnet_rpc)

    out = {
        "refuse_case": {
            "reason_code": refuse["reason_code"],
            "reason": refuse["reason"],
            "details": refuse.get("details"),
        },
        "pass_case": passed,
        "mainnet_broadcast": "refused",
    }
    out_path = REPO / "artifacts" / "anvil_demo_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
