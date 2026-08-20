# Fill-gate backtest results (real on-chain history)

**Date:** 2026-08-20  
**Gate under test:** Clarification D — `soldSteps / minSharesToRaise ≥ 0.90`
AND `0 < timeToExpiry ≤ 7 days` (plus not closed, inventory remaining).

## Method (real data, not synthetic)

1. Pulled every `FractionCreated` log from mainnet `OffchainFractions`
   `0x80EA8524…F7db` since deploy block `23483114`
   → **155 unique fractions** (`artifacts/fraction_created_raw.json`).
2. For each fraction, archive `eth_call` of `getFraction(creator, id)` at
   create time, each day in the final 7 days before expiration, near-expiry,
   and latest (`execution/backtest_fill_gate.py`).
3. Marked a fraction as **gate-passer** if any sample satisfied the 90%/7d
   gate while still open.
4. Terminal outcome from archive state at expiry / latest:
   - `completed` = `soldSteps ≥ minSharesToRaise` (or claimed flag / full sell)
   - `expired_underfilled` / `closed_underfilled` = missed threshold

## Results

| Metric | Value |
| --- | --- |
| Fractions created (unique) | **155** |
| Still open at pull | 2 |
| Terminal completed | 144 |
| Terminal expired underfilled | 8 |
| Terminal closed underfilled | 1 |
| Gate-passers among terminal | **34** |
| Gate-passers that completed | **34** |
| Gate-passers that failed | **0** |
| **Completion rate given gate** | **100% (34/34)** |

Source JSON: `artifacts/fill_gate_backtest.json` (`summary` object).

## Interpretation

On this historical sample, **every** terminal fraction that at some sampled
time reached ≥90% fill with ≤7 days to expiry **did complete**. None of the
9 underfilled failures ever passed the gate in the sampled windows (they
died at low fill and/or long runway).

**Verdict:** Keep **90% + 7 days** as the Part B v1 hard gate. The backtest
does **not** show the policy is “meaningfully weaker than expected.” It is
supportive. Residual risk remains (sampling granularity; future regime
change) — do not claim zero refund risk.

## Reproduce

```bash
python3 execution/pull_fraction_created.py
python3 execution/backtest_fill_gate.py --rpc https://eth.drpc.org
```
