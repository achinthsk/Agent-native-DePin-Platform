#!/usr/bin/env python3
"""
Glow Launchpad execution constructor (Part B) — non-custodial, Anvil-safe.

Constructs unsigned transaction calldata for optional GLW acquisition +
approve + OffchainFractions.buyFractions after enforcing every Part A gate
in code. Never signs. Never holds keys. Never broadcasts to real mainnet.

Broadcast is only allowed when the connected chain is an Anvil/Hardhat
dev chain (chain_id 31337). There is no code path that sends a signed tx
to Ethereum mainnet (chain_id 1).

Usage:
  python3 execution/glow_execute.py quote \\
      --creator 0x2b57... --fraction-id 0x51ab... \\
      --steps 1 --buyer 0xYourAgent \\
      --rpc http://127.0.0.1:8545
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eth_abi import encode
from eth_utils import keccak, to_checksum_address
from web3 import Web3

REPO = Path(__file__).resolve().parent
ABI_DIR = REPO / "abis"

OFFCHAIN_FRACTIONS = to_checksum_address(
    "0x80EA852448c2807BeAe321deC7c603990209F7db"
)
GLW = to_checksum_address("0xf4fbC617A5733EAAF9af08E1Ab816B103388d8B6")
USDG = to_checksum_address("0xe010ec500720bE9EF3F82129E7eD2Ee1FB7955F2")
UNISWAP_V2_ROUTER = to_checksum_address(
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
)

MIN_FILL_RATIO = 0.90
MAX_TIME_TO_EXPIRY_SECONDS = 7 * 24 * 3600

DEFAULT_MAX_SLIPPAGE_BPS = 100  # 1.00% — not Glow's 5%
HARD_MAX_SLIPPAGE_BPS = 200  # absolute ceiling 2.00%

DEFAULT_MAX_GLW_WEI = 50_000 * 10**18
DEFAULT_MAX_STEPS = 25

ANVIL_CHAIN_IDS = {31337}


@dataclass
class Refusal:
    refused: bool = True
    reason_code: str = ""
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": False,
            "refused": True,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "details": self.details,
            "transactions": None,
        }


@dataclass
class UnsignedTx:
    to: str
    data: str
    value: str = "0x0"
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_abi(name: str) -> list:
    return json.loads((ABI_DIR / name).read_text())


def connect(rpc: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 60}))
    if not w3.is_connected():
        raise SystemExit(f"Cannot connect to RPC: {rpc}")
    return w3


def assert_not_mainnet_broadcast(w3: Web3, rpc: str) -> None:
    chain_id = int(w3.eth.chain_id)
    if chain_id == 1:
        raise RuntimeError(
            "REFUSE_BROADCAST: connected chain_id=1 (Ethereum mainnet). "
            "This Part B package constructs calldata only and will not "
            "broadcast to real mainnet. Use an Anvil mainnet fork "
            "(chain_id 31337) for demos."
        )
    if chain_id not in ANVIL_CHAIN_IDS:
        raise RuntimeError(
            f"REFUSE_BROADCAST: chain_id={chain_id} is not an Anvil/dev chain. "
            "Only Anvil forks are permitted for sending transactions in this PR."
        )


def fetch_fraction(w3: Web3, creator: str, fraction_id: str) -> dict[str, Any] | None:
    """Independent on-chain verification — never trust Hub alone."""
    contract = w3.eth.contract(
        address=OFFCHAIN_FRACTIONS, abi=_load_abi("offchain_fractions.json")
    )
    creator_cs = to_checksum_address(creator)
    fid = bytes.fromhex(fraction_id[2:] if fraction_id.startswith("0x") else fraction_id)
    if len(fid) != 32:
        raise ValueError("fraction_id must be bytes32")
    data = contract.functions.getFraction(creator_cs, fid).call()
    (
        token,
        expiration,
        manually_closed,
        min_shares,
        use_cf,
        claimed,
        step,
        to,
        sold_steps,
        total_steps,
        closer,
    ) = data
    if int(token, 16) == 0 and int(total_steps) == 0:
        return None
    return {
        "token": to_checksum_address(token),
        "expiration": int(expiration),
        "manuallyClosed": bool(manually_closed),
        "minSharesToRaise": int(min_shares),
        "useCounterfactualAddress": bool(use_cf),
        "claimedFromMinSharesToRaise": bool(claimed),
        "step": int(step),
        "to": to_checksum_address(to) if int(to, 16) else to,
        "soldSteps": int(sold_steps),
        "totalSteps": int(total_steps),
        "closer": closer,
        "creator": creator_cs,
        "id": "0x" + fid.hex(),
    }


def evaluate_gates(
    fraction: dict[str, Any] | None,
    *,
    now_ts: int,
    steps_to_buy: int,
    max_steps: int,
    max_cost_wei: int,
    hub_committed: bool | None,
    chain_id: int,
) -> Refusal | None:
    if fraction is None:
        return Refusal(
            reason_code="fraction_not_on_chain",
            reason=(
                "getFraction returned empty FractionData. Hub isCommittedOnChain "
                "alone is insufficient — refusing construction."
            ),
            details={"hub_committed_hint": hub_committed},
        )

    if hub_committed is False:
        return Refusal(
            reason_code="hub_not_committed",
            reason="Hub isCommittedOnChain is false; Part B v1 refuses.",
            details={},
        )

    if fraction["manuallyClosed"]:
        return Refusal(
            reason_code="manually_closed",
            reason="Fraction is manuallyClosed on-chain.",
            details={"manuallyClosed": True},
        )

    if fraction["soldSteps"] >= fraction["totalSteps"]:
        return Refusal(
            reason_code="no_inventory",
            reason="No remaining steps (soldSteps >= totalSteps).",
            details={
                "soldSteps": fraction["soldSteps"],
                "totalSteps": fraction["totalSteps"],
            },
        )

    min_shares = fraction["minSharesToRaise"]
    if min_shares <= 0:
        return Refusal(
            reason_code="insufficient_data",
            reason="minSharesToRaise is zero — cannot evaluate fill gate.",
            details={"minSharesToRaise": min_shares},
        )

    fill_ratio = fraction["soldSteps"] / min_shares
    tte = fraction["expiration"] - now_ts

    if fill_ratio < MIN_FILL_RATIO:
        return Refusal(
            reason_code="fill_below_threshold",
            reason=(
                f"Fill ratio {fill_ratio:.4f} < required {MIN_FILL_RATIO:.2f} "
                f"(soldSteps/minSharesToRaise)."
            ),
            details={
                "soldSteps": fraction["soldSteps"],
                "minSharesToRaise": min_shares,
                "fill_ratio": fill_ratio,
                "required_min_fill_ratio": MIN_FILL_RATIO,
            },
        )

    if tte <= 0:
        return Refusal(
            reason_code="expired",
            reason="Fraction expiration is not in the future.",
            details={"expiration": fraction["expiration"], "now": now_ts, "tte": tte},
        )

    if tte > MAX_TIME_TO_EXPIRY_SECONDS:
        return Refusal(
            reason_code="expiry_too_far",
            reason=(
                f"timeToExpiry {tte}s > max {MAX_TIME_TO_EXPIRY_SECONDS}s "
                f"({MAX_TIME_TO_EXPIRY_SECONDS // 86400} days)."
            ),
            details={
                "time_to_expiry_seconds": tte,
                "max_time_to_expiry_seconds": MAX_TIME_TO_EXPIRY_SECONDS,
                "expiration": fraction["expiration"],
                "now": now_ts,
            },
        )

    if steps_to_buy <= 0:
        return Refusal(
            reason_code="invalid_steps",
            reason="steps_to_buy must be > 0.",
            details={"steps_to_buy": steps_to_buy},
        )

    remaining = fraction["totalSteps"] - fraction["soldSteps"]
    if steps_to_buy > remaining:
        return Refusal(
            reason_code="steps_exceed_inventory",
            reason="Requested steps exceed remaining inventory.",
            details={"steps_to_buy": steps_to_buy, "remaining": remaining},
        )

    if steps_to_buy > max_steps:
        return Refusal(
            reason_code="steps_exceed_soft_cap",
            reason=f"steps_to_buy {steps_to_buy} exceeds soft cap {max_steps}.",
            details={"steps_to_buy": steps_to_buy, "max_steps": max_steps},
        )

    # Mainnet / non-dev: GLW only. Anvil may use a mock ERC-20 for demos
    # because mainnet GLW transfers are allowlist-restricted.
    if fraction["token"].lower() != GLW.lower() and chain_id not in ANVIL_CHAIN_IDS:
        return Refusal(
            reason_code="unsupported_payment_token",
            reason=(
                f"Part B v1 on non-dev chains only supports GLW payment; "
                f"on-chain token is {fraction['token']}."
            ),
            details={"token": fraction["token"], "expected": GLW, "chain_id": chain_id},
        )

    cost = steps_to_buy * fraction["step"]
    if cost > max_cost_wei:
        return Refusal(
            reason_code="cost_exceeds_soft_cap",
            reason=f"Token cost {cost} wei exceeds soft cap {max_cost_wei}.",
            details={"cost_wei": cost, "max_cost_wei": max_cost_wei, "token": fraction["token"]},
        )

    return None


def build_buy_fractions_tx(
    creator: str,
    fraction_id: str,
    steps_to_buy: int,
    min_steps_to_buy: int,
    refund_to: str,
    credit_to: str,
    use_cf_refund: bool = False,
) -> UnsignedTx:
    selector = keccak(
        text="buyFractions(address,bytes32,uint256,uint256,address,address,bool)"
    )[:4]
    fid = bytes.fromhex(
        fraction_id[2:] if fraction_id.startswith("0x") else fraction_id
    )
    data = selector + encode(
        ["address", "bytes32", "uint256", "uint256", "address", "address", "bool"],
        [
            to_checksum_address(creator),
            fid,
            steps_to_buy,
            min_steps_to_buy,
            to_checksum_address(refund_to),
            to_checksum_address(credit_to),
            use_cf_refund,
        ],
    )
    return UnsignedTx(
        to=OFFCHAIN_FRACTIONS,
        data="0x" + data.hex(),
        description=(
            f"OffchainFractions.buyFractions(creator={creator}, id={fraction_id}, "
            f"steps={steps_to_buy}, minSteps={min_steps_to_buy})"
        ),
    )


def build_swap_usdg_to_glw(
    w3: Web3,
    *,
    buyer: str,
    glw_needed: int,
    usdg_budget: int,
    slippage_bps: int,
    deadline_ts: int,
) -> tuple[UnsignedTx, UnsignedTx] | Refusal:
    if slippage_bps > HARD_MAX_SLIPPAGE_BPS:
        return Refusal(
            reason_code="slippage_above_hard_cap",
            reason=(
                f"Requested slippage {slippage_bps} bps exceeds hard cap "
                f"{HARD_MAX_SLIPPAGE_BPS} bps (Glow's 5%/500 bps is explicitly rejected)."
            ),
            details={
                "slippage_bps": slippage_bps,
                "hard_max_slippage_bps": HARD_MAX_SLIPPAGE_BPS,
                "glow_default_rejected_bps": 500,
            },
        )
    if slippage_bps < 0:
        return Refusal(
            reason_code="invalid_slippage",
            reason="slippage_bps must be >= 0.",
            details={"slippage_bps": slippage_bps},
        )

    router = w3.eth.contract(
        address=UNISWAP_V2_ROUTER, abi=_load_abi("uniswap_v2_router.json")
    )
    path = [USDG, GLW]
    try:
        amounts = router.functions.getAmountsOut(usdg_budget, path).call()
    except Exception as e:
        return Refusal(
            reason_code="insufficient_data",
            reason=f"Uniswap V2 quote failed: {e}",
            details={"path": path, "usdg_budget": usdg_budget},
        )
    quoted_glw = int(amounts[-1])
    if quoted_glw < glw_needed:
        return Refusal(
            reason_code="swap_quote_below_needed",
            reason=(
                f"Quote yields {quoted_glw} GLW wei < needed {glw_needed} "
                f"for USDG budget {usdg_budget}."
            ),
            details={
                "quoted_glw_wei": quoted_glw,
                "glw_needed_wei": glw_needed,
                "usdg_budget_wei": usdg_budget,
            },
        )

    slipped = quoted_glw * (10_000 - slippage_bps) // 10_000
    amount_out_min = max(glw_needed, slipped)

    sel_approve = keccak(text="approve(address,uint256)")[:4]
    approve_data = sel_approve + encode(
        ["address", "uint256"], [UNISWAP_V2_ROUTER, usdg_budget]
    )
    approve_tx = UnsignedTx(
        to=USDG,
        data="0x" + approve_data.hex(),
        description=f"USDG.approve(UniswapV2Router, {usdg_budget})",
    )

    sel_swap = keccak(
        text="swapExactTokensForTokens(uint256,uint256,address[],address,uint256)"
    )[:4]
    swap_data = sel_swap + encode(
        ["uint256", "uint256", "address[]", "address", "uint256"],
        [usdg_budget, amount_out_min, path, to_checksum_address(buyer), deadline_ts],
    )
    swap_tx = UnsignedTx(
        to=UNISWAP_V2_ROUTER,
        data="0x" + swap_data.hex(),
        description=(
            f"UniswapV2.swapExactTokensForTokens(USDG→GLW, amountOutMin={amount_out_min}, "
            f"slippage_bps={slippage_bps})"
        ),
    )
    return approve_tx, swap_tx


def construct_intent(
    w3: Web3,
    *,
    creator: str,
    fraction_id: str,
    buyer: str,
    steps_to_buy: int,
    min_steps_to_buy: int | None = None,
    hub_committed: bool | None = True,
    max_steps: int = DEFAULT_MAX_STEPS,
    max_glw_wei: int = DEFAULT_MAX_GLW_WEI,
    slippage_bps: int = DEFAULT_MAX_SLIPPAGE_BPS,
    include_swap_if_needed: bool = False,
    usdg_budget: int | None = None,
    now_ts: int | None = None,
) -> dict[str, Any]:
    now = now_ts if now_ts is not None else int(time.time())
    try:
        chain_ts = int(w3.eth.get_block("latest")["timestamp"])
        if abs(chain_ts - now) > 120:
            now = chain_ts
    except Exception:
        pass

    chain_id = int(w3.eth.chain_id)
    fraction = fetch_fraction(w3, creator, fraction_id)
    refusal = evaluate_gates(
        fraction,
        now_ts=now,
        steps_to_buy=steps_to_buy,
        max_steps=max_steps,
        max_cost_wei=max_glw_wei,
        hub_committed=hub_committed,
        chain_id=chain_id,
    )
    if refusal is not None:
        return refusal.to_dict()

    assert fraction is not None
    min_steps = min_steps_to_buy if min_steps_to_buy is not None else steps_to_buy
    if min_steps <= 0 or min_steps > steps_to_buy:
        return Refusal(
            reason_code="invalid_min_steps",
            reason="min_steps_to_buy must be in [1, steps_to_buy].",
            details={"min_steps_to_buy": min_steps, "steps_to_buy": steps_to_buy},
        ).to_dict()

    if slippage_bps > HARD_MAX_SLIPPAGE_BPS:
        return Refusal(
            reason_code="slippage_above_hard_cap",
            reason=(
                f"Configured slippage {slippage_bps} bps exceeds hard cap "
                f"{HARD_MAX_SLIPPAGE_BPS} bps (Glow 500 bps rejected)."
            ),
            details={"slippage_bps": slippage_bps},
        ).to_dict()

    cost = steps_to_buy * fraction["step"]
    buyer_cs = to_checksum_address(buyer)
    payment_token = to_checksum_address(fraction["token"])
    txs: list[dict[str, Any]] = []
    notes: list[str] = []

    if payment_token.lower() != GLW.lower():
        notes.append(
            f"Dev-chain exception: payment token {payment_token} (not mainnet GLW)."
        )

    token_contract = w3.eth.contract(address=payment_token, abi=_load_abi("erc20.json"))
    token_bal = int(token_contract.functions.balanceOf(buyer_cs).call())

    if token_bal < cost:
        if payment_token.lower() != GLW.lower():
            return Refusal(
                reason_code="insufficient_token_balance",
                reason=(
                    f"Buyer token balance {token_bal} < required {cost} "
                    f"for {payment_token}."
                ),
                details={"balance": token_bal, "required": cost, "token": payment_token},
            ).to_dict()
        if not include_swap_if_needed:
            return Refusal(
                reason_code="insufficient_glw_balance",
                reason=(
                    f"Buyer GLW balance {token_bal} < required {cost}. "
                    "Re-run with --include-swap and --usdg-budget, or fund GLW on the fork."
                ),
                details={"glw_balance": token_bal, "glw_required": cost},
            ).to_dict()
        if usdg_budget is None or usdg_budget <= 0:
            return Refusal(
                reason_code="insufficient_data",
                reason="Swap requested but usdg_budget not provided.",
                details={},
            ).to_dict()
        swap_result = build_swap_usdg_to_glw(
            w3,
            buyer=buyer_cs,
            glw_needed=cost - token_bal,
            usdg_budget=usdg_budget,
            slippage_bps=slippage_bps,
            deadline_ts=now + 600,
        )
        if isinstance(swap_result, Refusal):
            return swap_result.to_dict()
        approve_usdg, swap_tx = swap_result
        txs.append(approve_usdg.to_dict())
        txs.append(swap_tx.to_dict())
        notes.append(
            f"Included USDG→GLW swap with amountOutMin hard floor; "
            f"slippage_bps={slippage_bps} (Glow 500 bps default rejected)."
        )

    sel_approve = keccak(text="approve(address,uint256)")[:4]
    approve_data = sel_approve + encode(
        ["address", "uint256"], [OFFCHAIN_FRACTIONS, cost]
    )
    txs.append(
        UnsignedTx(
            to=payment_token,
            data="0x" + approve_data.hex(),
            description=f"token.approve(OffchainFractions, {cost}) token={payment_token}",
        ).to_dict()
    )
    txs.append(
        build_buy_fractions_tx(
            creator=fraction["creator"],
            fraction_id=fraction["id"],
            steps_to_buy=steps_to_buy,
            min_steps_to_buy=min_steps,
            refund_to=buyer_cs,
            credit_to=buyer_cs,
            use_cf_refund=False,
        ).to_dict()
    )
    notes.append(
        "Underfill after expiry requires manual claimRefund — not auto. "
        "Platform does not sign or broadcast these txs."
    )

    fill_ratio = fraction["soldSteps"] / fraction["minSharesToRaise"]
    return {
        "ok": True,
        "refused": False,
        "reason_code": None,
        "fraction": {
            "creator": fraction["creator"],
            "id": fraction["id"],
            "token": fraction["token"],
            "soldSteps": fraction["soldSteps"],
            "totalSteps": fraction["totalSteps"],
            "minSharesToRaise": fraction["minSharesToRaise"],
            "step": fraction["step"],
            "expiration": fraction["expiration"],
            "fill_ratio": fill_ratio,
            "time_to_expiry_seconds": fraction["expiration"] - now,
            "manuallyClosed": fraction["manuallyClosed"],
        },
        "gates": {
            "getFraction_ok": True,
            "min_fill_ratio": MIN_FILL_RATIO,
            "max_time_to_expiry_seconds": MAX_TIME_TO_EXPIRY_SECONDS,
            "max_slippage_bps": HARD_MAX_SLIPPAGE_BPS,
            "configured_slippage_bps": slippage_bps,
            "max_cost_wei": max_glw_wei,
            "max_steps": max_steps,
        },
        "intent": {
            "buyer": buyer_cs,
            "steps_to_buy": steps_to_buy,
            "min_steps_to_buy": min_steps,
            "cost_wei": cost,
            "payment_token": payment_token,
        },
        "transactions": txs,
        "notes": notes,
        "broadcast_policy": (
            "UNSIGNED ONLY. No mainnet broadcast path exists in this module. "
            "Demo sends must use Anvil fork (chain_id 31337) via demo_anvil_fork.py."
        ),
        "constructed_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def cmd_quote(args: argparse.Namespace) -> int:
    w3 = connect(args.rpc)
    result = construct_intent(
        w3,
        creator=args.creator,
        fraction_id=args.fraction_id,
        buyer=args.buyer,
        steps_to_buy=args.steps,
        min_steps_to_buy=args.min_steps,
        hub_committed=None if args.hub_committed is None else args.hub_committed,
        max_steps=args.max_steps,
        max_glw_wei=args.max_glw_wei,
        slippage_bps=args.slippage_bps,
        include_swap_if_needed=args.include_swap,
        usdg_budget=args.usdg_budget,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 2


def cmd_construct(args: argparse.Namespace) -> int:
    return cmd_quote(args)


def cmd_safety_check(args: argparse.Namespace) -> int:
    w3 = connect(args.rpc)
    chain_id = int(w3.eth.chain_id)
    report: dict[str, Any] = {
        "rpc": args.rpc,
        "chain_id": chain_id,
        "is_mainnet": chain_id == 1,
        "anvil_dev_chain": chain_id in ANVIL_CHAIN_IDS,
    }
    try:
        assert_not_mainnet_broadcast(w3, args.rpc)
        report["broadcast_allowed_here"] = True
        report["note"] = "Dev/Anvil chain — demo send permitted."
    except RuntimeError as e:
        report["broadcast_allowed_here"] = False
        report["refuse_reason"] = str(e)
    print(json.dumps(report, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Glow Part B unsigned tx constructor")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_rpc(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--rpc",
            default=os.environ.get("ETH_RPC_URL", "https://eth.drpc.org"),
            help="Ethereum JSON-RPC (mainnet eth_call OK; broadcast only on Anvil)",
        )

    def add_intent_args(sp: argparse.ArgumentParser) -> None:
        add_rpc(sp)
        sp.add_argument("--creator", required=True)
        sp.add_argument("--fraction-id", required=True)
        sp.add_argument("--buyer", required=True)
        sp.add_argument("--steps", type=int, required=True)
        sp.add_argument("--min-steps", type=int, default=None)
        sp.add_argument(
            "--hub-committed",
            type=lambda s: s.lower() in ("1", "true", "yes"),
            default=True,
        )
        sp.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
        sp.add_argument("--max-glw-wei", type=int, default=DEFAULT_MAX_GLW_WEI)
        sp.add_argument(
            "--slippage-bps",
            type=int,
            default=DEFAULT_MAX_SLIPPAGE_BPS,
            help=f"Default {DEFAULT_MAX_SLIPPAGE_BPS}; hard max {HARD_MAX_SLIPPAGE_BPS}",
        )
        sp.add_argument("--include-swap", action="store_true")
        sp.add_argument("--usdg-budget", type=int, default=None)

    q = sub.add_parser("quote", help="Evaluate gates; print unsigned txs or refusal")
    add_intent_args(q)
    q.set_defaults(func=cmd_quote)

    c = sub.add_parser("construct", help="Same as quote")
    add_intent_args(c)
    c.set_defaults(func=cmd_construct)

    s = sub.add_parser("safety-check", help="Show whether broadcast would be refused")
    add_rpc(s)
    s.set_defaults(func=cmd_safety_check)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
