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

### Implausibly high yields score worse, not better

The yield curve saturates near ~20% (maps to 100 component points). Without
a further rule, a genuine ~22% and a suspicious 70% claim would both sit at
the ceiling. After mapping through the curve, if the yield used for that
component exceeds `implausibility_threshold_pct` (default 30%), multiply by
`max(0, 1 − implausibility_penalty_per_pp * (pct − threshold))`. Past the
believable range for these asset classes, more yield is treated as a red
flag on this axis, not as “even better.” Threshold and rate live in
`weights.yaml`.

Every score object also includes `"direction": "higher_is_better"` so agents
consuming the JSON do not have to read this document to know the scale
convention (including on `insufficient_data` returns).

### Hand-check expectations

- **Glow:** both yields null → **insufficient data** (not 0).
- **Elmnts:** both yields null → **insufficient data**.
- **RealT:** realized 9.225%, advertised null → a **moderate positive**
  yield score from realized alone (roughly mid-range on a 0–20% curve;
  ~51/100 on the current curve). Well below the implausibility threshold,
  so unchanged by that penalty.
- **Synthetic check:** a 70% realized claim should score **worse** on
  `yield_score` than a believable high yield (e.g. 18%), not tie at 100.

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
| `payout_mechanism_type` | See subsection below. Category risk of how payout is funded — **not** an issuer-misconduct flag. | Medium |
| Emission-token peak decline | See subsection below. **Additive** to the flat category penalty: magnitude of already-realized token drawdown when verifiable pool history exists. | Medium |
| Advertised−realized gap | If both yields present and gap > 0 → safer score falls via a multiplicative penalty (same shape as yield). If either yield is null, this penalty is skipped entirely — never treated as a zero gap. | Applied after the weighted average when computable |

### Payout-mechanism category risk

Measures **structural exposure by `payout_mechanism_type`**, not whether any
specific protocol “did something wrong.”

| `payout_mechanism_type` | Treatment | Points (safer ↑) |
| --- | --- | ---: |
| `direct-revenue-share` | **Omit** this component (no newly-minted-token price leg on the payout) | — |
| `fixed-interest` | **Omit** (same rationale) | — |
| `token-emission-reward` | Include — financer’s realized USD return depends on the protocol token’s market price holding up, even if the physical asset performs | **30** |

**Why 30 (evidence basis):** direct on-chain pulls in
`scoring/GLW_PRICE_EMISSIONS_FINDINGS.md` (not aggregators) show that for the
current `token-emission-reward` asset (Glow / GLW):

1. Weekly MinerPool mint aggregates sit near the documented fixed
   infrastructure schedule (median ≈187k GLW/week vs claimed 175k) across
   dozens of weeks — ongoing newly minted supply is real.
2. Uniswap V2 GLW–USDG pool
   (`0x6FA09ffC45F1dDC95c1bc192956717042f142c5d`, resolved via
   `factory.getPair`) Sync-derived price fell from a sample peak ≈ **3.95**
   (2025-01-08) to ≈ **0.23** (2026-08 spot) — about **−94%** — while those
   emissions continued.

That combination is the inherent category risk: mint schedule and token
market price are independent of (and can diverge from) physical performance.
Severity 30 is material (comparable to other structural weak mappings in
this axis) but not a “zero out the asset” hammer, and it applies to **any**
future `token-emission-reward` asset, not as a Glow-specific penalty.

The flat category score alone treats a token that held steady and one that
collapsed identically. The next component covers realized magnitude.

### Emission-token peak-decline risk (additive)

**Intent:** when a `token-emission-reward` asset has **real, verifiable,
directly-pulled** pool price history, score how far the payout token has
already fallen from its observed historical peak. This is **additive** to
the flat `payout_mechanism_type` component — category risk stays; this
layers on realized drawdown.

**When it applies**

| Condition | Treatment |
| --- | --- |
| Not `token-emission-reward` | **Omit** (RealT / Elmnts / etc.) |
| `token-emission-reward` but no reliable peak+current in the scoring price-history registry | **Omit** — never invent 0% decline / full marks |
| `token-emission-reward` with registry entry from direct pool Sync / `getReserves` (same standard as `GLW_PRICE_EMISSIONS_FINDINGS.md`, not aggregators) | Include |

Input: `decline_pct = 100 × (1 − current_price / peak_price)` from the
registry file `scoring/token_emission_price_history.yaml` (machine-readable
sibling of the findings doc — engine reads that file, does not hardcode
prices and does not re-fetch RPC on every score run).

**Piecewise curve** (`decline_pct` → risk points, safer ↑):

| Decline from peak | Points | Plain-language reason |
| ---: | ---: | --- |
| 0% | 100 | No realized market damage beyond the flat category score |
| 25% | 80 | Noticeable drawdown; still mostly intact vs peak |
| 50% | 50 | Half of peak USD value gone — meaningfully worse |
| 75% | 25 | Severe; most peak value destroyed |
| 90% | 10 | Near-wipe of peak value |
| 95% | 5 | Floor band for extreme collapses |
| 100% | 0 | Token worthless vs its own peak |

Piecewise-linear between knots (same interpolator as age/cycle curves).

**Glow hand-check (predict before code):** findings peak **3.954479**
(2025-01-08 Sync sample) and spot **0.2305** → decline ≈
`100 × (1 − 0.2305/3.954479)` ≈ **94.17%**. Interpolating 90→95 on the
curve → component points ≈ **5.8**. With `weight_emission_token_peak_decline:
0.12` and prior risk weights scaled ×0.88 to free that weight, Glow’s
overall `risk_score` should fall from the post-category baseline **~62.7**
to roughly **54–55** (about **−8 points** more). RealT and Elmnts omit both
emission components → **unchanged**.

**Known data gap (do not paper over):** tracked mint destinations in
findings (MinerPool + Grants + VetoCouncil) are a **partial** mint ledger
for the scanned window — they are not reconciled to `totalSupply()` /
full circulating supply. Peak-decline scoring uses **pool price path
only**; it does not assume mint destinations sum to supply.

Weights: pre-existing risk component weights (including
`weight_payout_mechanism`) scaled by 0.88 so
`weight_emission_token_peak_decline: 0.12` fits without unaccounted-for
total weight.

### Aggregation

Weighted average of *available* maturity / verification / exposure /
payout-mechanism / emission-peak-decline components only (skip null-driven
components and omit unmapped payout types / missing price history). Then,
if both yield fields are present and `advertised − realized > 0`, multiply
by `max(0, 1 − gap_penalty_per_pp * gap)`. If **zero** base components are
available (should be rare — verification_tier and exposure_type are
always present in valid instances), return insufficient_data.

Verification tier is always present on a valid instance, so risk_score
should almost always be numeric for schema-valid assets.

### Hand-check expectations

- **Glow:** High verification lifts risk quality; mid ages help; missing
  cycles omit that signal; single-asset hurts; flat `token-emission-reward`
  (30) plus **~94% peak decline (~5.8 pts)** both pull down. **Predict
  overall risk ≈ 54–55** (from post-category ~62.7).
- **Elmnts:** `direct-revenue-share` + no emission price history → both new
  components omitted → **risk_score unchanged**. **Overall: low.**
- **RealT:** same omit path → **risk_score unchanged**. **Overall: mid.**

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
| **Glow** | insufficient data | **predict ≈54–55** after additive peak-decline on top of category penalty (was ~62.7 post-category) | low (100-week lockup) | high |
| **Elmnts** | insufficient data | low — **unchanged** (omits emission components) | very low (broker/illiquid) | lowest |
| **RealT** | moderate+ (9.225% realized) | mid — **unchanged** | mid (tradeable but whitelist-cut) | mid-high (beats Elmnts on completeness + retrieval) |
| **Implausible yield (e.g. 70%)** | worse than a believable high yield (e.g. 18%), not equal at the curve ceiling | — | — | — |

After the engine runs, compare actual JSON output to this table. Material
disagreement means fix the formula or the weights — not the hand-check
narrative after the fact without saying so.
