# Scoring Methodology (v1.0.0)

This document defines how validated `asset-v1` instances are turned into
**four independent scores**. It was written before `scoring/engine.py` and
is the source of truth for that code. Weights live in `scoring/weights.yaml`;
every weight there has a one-line reason.

## Design principles

1. **Four scores, never fused.** `yield_score`, `risk_score`,
   `liquidity_score`, and `data_confidence_score` are separate outputs.
   Downstream agents choose how to trade them off; this engine does not.
2. **Higher is better on every axis** (0–100 scale when a score is
   computable). `risk_score` means “risk *quality*” — higher = safer /
   better risk characteristics, not “more risk.”
3. **Missing inputs are not zeros and not averages.** If a score cannot be
   computed from available fields, it is returned as
   `insufficient_data: true` with `value: null` — never a fabricated number.
4. **Every score ships with its inputs.** Each score object lists the raw
   schema fields (and intermediate components) that drove it.
5. **Simple explicit formulas.** No models, no black boxes.

---

## Shared helpers

### Null-safe numeric mapping

When a numeric field is present, map it through a piecewise-linear curve
defined in `weights.yaml` (e.g. realized yield 0% → 0 component points,
20% → 100). When the field is `null`, that *component* contributes nothing
to a weighted average **only if** the score is still considered computable
from other components; otherwise the whole score is insufficient-data.

### Completeness fraction

For `data_confidence_score`, count a fixed checklist of important fields
(listed in weights). A field counts as “present” if it is non-null (and,
for strings, non-empty). Enums always count as present.

### Advertised-vs-realized gap

When **both** `advertised_yield_pct` and `realized_yield_pct` are non-null:

```
gap = advertised_yield_pct - realized_yield_pct
```

A **positive** gap (advertised > realized) is treated as a negative signal:
marketing overshoot. It **reduces** `yield_score` and **reduces**
`risk_score` (worse risk quality). A negative gap (realized > advertised)
does not get a bonus beyond using the realized figure — we do not reward
under-promising as “extra safety,” we simply avoid punishing it.

---

## 1. `yield_score`

### Intent

How attractive is the asset’s yield story **based on numbers actually in
the snapshot**, without inventing a track record.

### Cases

| Case | Result |
| --- | --- |
| Both `advertised_yield_pct` and `realized_yield_pct` are `null` | **`insufficient_data: true`** — stop. Do not score 0. |
| Only `realized_yield_pct` present | Map realized → [0,100] via the yield curve. That is the score. |
| Only `advertised_yield_pct` present | Map advertised → [0,100], then multiply by `advertised_only_discount` (< 1). Advertised-alone is weak evidence. |
| Both present | `base = w_realized * map(realized) + w_advertised * map(advertised)` with `w_realized >> w_advertised`. Then apply a **gap penalty**: if `gap > 0`, multiply by `max(0, 1 - gap_penalty_per_pp * gap)`. |

### Why the gap pulls the score down

A large advertised−realized spread means the marketed number is not what
holders actually got. Averaging the two would let marketing inflate the
score. The gap penalty makes that inflation costly.

### Hand-check expectations

- **Glow:** both yields null → **insufficient data** (not 0).
- **Elmnts:** both yields null → **insufficient data**.
- **RealT:** realized 9.225%, advertised null → a **moderate positive**
  yield score from realized alone (roughly mid-range on a 0–20% curve;
  ~46/100 if 20% maps to 100).

---

## 2. `risk_score` (higher = safer)

### Intent

How strong are the risk / track-record / concentration characteristics
visible in the schema.

### Components (direction stated first)

| Input | Direction | Plain-language weight |
| --- | --- | --- |
| `verification_tier` | Stronger tiers → higher (safer) score. `self-reported-unverified` is meaningfully worse than `cryptographic-onchain-proof` or `independent-third-party-audit`. | Large |
| `protocol_age_months` | Older protocol → safer. Null → this component omitted (does not invent 0 months). | Medium |
| `asset_age_months` | Older specific asset → safer. Null → omit component. | Medium |
| `completed_payout_cycles` | More observed payouts → safer. Null → omit component. | Large (this is the “has it actually paid?” signal) |
| `exposure_type` | `pooled-diversified` safer than `single-asset`; `unverifiable` worst. | Medium |
| Advertised−realized gap | If both yields present and gap > 0 → safer score falls via a multiplicative penalty (same shape as yield). If either yield is null, this penalty is skipped entirely — never treated as a zero gap. | Applied after the weighted average when computable |

### Aggregation

Weighted average of *available* maturity / verification / exposure
components only (skip null-driven components). Then, if both yield
fields are present and `advertised − realized > 0`, multiply by
`max(0, 1 − gap_penalty_per_pp * gap)`. If **zero** base components are
available (should be rare — verification_tier and exposure_type are
always present in valid instances), return insufficient_data.

Verification tier is always present on a valid instance, so risk_score
should almost always be numeric for schema-valid assets.

### Hand-check expectations

- **Glow:** High verification (`cryptographic-onchain-proof`) lifts risk
  quality; mid ages (~32 / ~31 months) help moderately; missing
  `completed_payout_cycles` means that strong signal is absent (not treated
  as zero cycles); single-asset hurts. **Overall: upper-mid risk quality.**
- **Elmnts:** Self-reported hurts; all maturity fields null (ages/cycles
  contribute nothing); single-asset hurts; illiquidity is *not* double-
  counted here (it belongs in liquidity_score). **Overall: low risk
  quality** — clearly worse than Glow and RealT.
- **RealT:** Self-reported hurts a lot, but protocol ~88 months, asset ~65
  months, and **230** completed payout cycles are strong positive track-
  record signals; single-asset hurts. **Overall: mid risk quality** —
  worse than Glow on verification, better than Elmnts on maturity/payouts.

---

## 3. `liquidity_score` (higher = easier exit)

### Intent

How quickly / freely a holder can convert the position back to cash, given
what the snapshot actually says — including nuances the top-level enum
alone can overstate.

### Components

| Input | Direction |
| --- | --- |
| `exit_type` | `open-market-tradeable` > `fixed-lockup` > `illiquid-broker-required` > `unverifiable` |
| `lockup_period_weeks` | Longer lockup → lower score. Only applies strongly when `exit_type` is `fixed-lockup`. Null lockup with fixed-lockup → omit length component but keep the harsh exit_type mapping. |
| `estimated_time_to_exit_days` | Longer → lower. Null → omit this component (do not invent days). |

### Whitelist / transfer-restriction haircut (RealT nuance)

RealT’s snapshot has `exit_type: open-market-tradeable`, but RealT transfers
are **wallet-whitelist / KYC gated** in practice (`adapters/FINDINGS.md`
Part C; also reflected in RealT `description_text`). Scoring must not treat
that enum as unrestricted DEX liquidity.

**Rule:** apply a multiplicative `whitelist_haircut` (< 1) to the liquidity
score when **any** of the following is true:

1. `description_text` or `verification.verification_notes` (case-insensitive)
   contains whitelist / KYC-transfer cues (`whitelist`, `kyc`, “transferability
   requires”), **or**
2. `source_platform == "realt"` (platform-known restriction documented in
   FINDINGS — used as a belt-and-suspenders when prose is stripped).

This is an explicit methodology choice so the literal enum cannot silently
overstate liquidity.

### Hand-check expectations

- **Glow:** `fixed-lockup` + 100 weeks → **low** liquidity.
- **Elmnts:** `illiquid-broker-required` + no exit-day estimate → **very low**.
- **RealT:** enum looks good, but whitelist haircut applies → **mid**, not
  top-tier open-market. Clearly above Glow/Elmnts, clearly below a true
  unrestricted liquid token.

---

## 4. `data_confidence_score` (higher = more trustworthy / complete)

### Intent

How much an agent should trust that this snapshot is a solid factual basis
for the other scores — independent of whether the *economic* story is
attractive.

### Components

| Input | Direction | Weight (plain) |
| --- | --- | --- |
| `verification_tier` | Stronger → higher | Large |
| `retrieval_method` | `onchain-direct-query` > `public-api` > `manual-entry` | Large |
| Field completeness | Fraction of checklist fields populated | Large — this is what separates RealT from Elmnts when both are self-reported |
| Freshness of `data_pulled_at` | Newer → higher; months-old → lower | Medium |

### Completeness checklist

Includes (among others): both yield fields, yield basis, protocol/asset age,
completed payout cycles, lockup / exit-day fields, operator_name,
verification_notes. Exact list is in `weights.yaml`.

### Hand-check expectations

- **Glow:** Strong verification + public-api + decent completeness + fresh
  pull → **high** confidence. (Yields null reduce completeness but do not
  zero the score.)
- **Elmnts:** Self-reported + **manual-entry** + mostly null numerics →
  **lowest** confidence of the three.
- **RealT:** Same verification tier as Elmnts, but **public-api**, high
  completeness (realized yield, ages, 230 cycles populated), fresh pull →
  **meaningfully higher** confidence than Elmnts. If RealT ≈ Elmnts here,
  the formula is broken.

---

## Hand-check summary (before code)

| Asset | yield | risk (safer↑) | liquidity↑ | data_confidence↑ |
| --- | --- | --- | --- | --- |
| **Glow** | insufficient data | upper-mid (strong verification, mid age, no cycle count) | low (100-week lockup) | high |
| **Elmnts** | insufficient data | low (self-reported, empty maturity) | very low (broker/illiquid) | lowest |
| **RealT** | moderate+ (9.225% realized) | mid (weak verification, strong track record) | mid (tradeable but whitelist-cut) | mid-high (beats Elmnts on completeness + retrieval) |

After the engine runs, compare actual JSON output to this table. Material
disagreement means fix the formula or the weights — not the hand-check
narrative after the fact without saying so.
