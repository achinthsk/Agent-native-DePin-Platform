# Glow execution (Part B) — Anvil-only

Non-custodial constructor for Glow Launchpad `buyFractions`. Enforces Part A
gates in code. **No real mainnet broadcast path.**

## Non-negotiables

1. Mainnet **fork** (Anvil) for demos — no real funds, no chain_id=1 sends.
2. Platform constructs **unsigned** calldata only; agent key signs elsewhere.
3. Gates enforced in `glow_execute.py` (not docs-only):
   - `getFraction` re-verify before construct
   - fill ≥ 90% of `minSharesToRaise` AND time-to-expiry ≤ 7 days
   - committed / not closed / inventory remaining
   - slippage hard-capped at **2%** (default **1%**); Glow’s **5% rejected**
   - soft cost / steps size caps
4. Fill gate **backtested** on real historical FractionCreated + archive
   `getFraction` — see `FILL_GATE_BACKTEST.md` (**34/34 completed**).

## Layout

| Path | Role |
| --- | --- |
| `glow_execute.py` | Unsigned tx constructor + explicit refusals |
| `demo_anvil_fork.py` | Live refuse + pass demo on Anvil fork |
| `backtest_fill_gate.py` | Historical 90%/7d backtest |
| `pull_fraction_created.py` | Pull FractionCreated logs |
| `FILL_GATE_BACKTEST.md` | Backtest write-up |
| `artifacts/` | Pulled logs, backtest JSON, demo result |
| `contracts/MockERC20.*` | Fork-only payment token (GLW transfers allowlisted) |

## Commands

```bash
# Quote / construct (eth_call OK on mainnet RPC; still unsigned)
python3 execution/glow_execute.py quote \
  --rpc https://eth.drpc.org \
  --creator 0x2b57E1bF5071c6579F2145b367EEC34f8729AA9C \
  --fraction-id 0x51ab76b04053b16422787348785f051b636f7b0e066ffc9bcf4bab5b2116c53d \
  --buyer 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 \
  --steps 1

# Safety: prove broadcast refused on mainnet RPC
python3 execution/glow_execute.py safety-check --rpc https://eth.drpc.org

# Historical backtest
python3 execution/pull_fraction_created.py   # once
python3 execution/backtest_fill_gate.py

# Live Anvil demo (refuse + pass + mainnet broadcast refusal)
anvil --fork-url "$ETH_RPC_URL" --port 8545 --chain-id 31337
python3 execution/demo_anvil_fork.py --rpc http://127.0.0.1:8545
```

## Broadcast policy

`glow_execute.assert_not_mainnet_broadcast` raises on chain_id 1.
`demo_anvil_fork.py` is the only sender; it requires Anvil chain_id 31337 and
signs with Anvil’s public test keys only.

Pass-case note: the fork demo uses a deployed `MockERC20` as the fraction
payment token because mainnet GLW rejects arbitrary `transfer`/`transferFrom`
(custom error). Gates, `getFraction`, and `buyFractions` are still exercised
against the real OffchainFractions contract on the fork.
