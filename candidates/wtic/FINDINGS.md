# WTIC — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-06
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Coverage test: WTIC (Energy Substantiation) — ERC-20 on Ethereum representing 1:1 physical WTI crude oil via Volumetric Energy Receipts; may not have periodic yield

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | WTIC (`wtic`) |
| Category | `energy` |
| Official website | `https://www.energysubstantiation.com/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `backlog_match` |
| Physical-asset gate | `physical-rwa` |
| Classification | `candidate-for-adapter` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://www.energysubstantiation.com/` | HTTP 200 — live (text/html) |
| `https://www.energysubstantiation.com/about` | HTTP 200 — live (text/html) |
| `https://etherscan.io/token/0x709ab533D18e652eCd56423d71c0241A0ee56a3b` | HTTP 403: Forbidden |
| `https://app.rwa.xyz/assets/WTIC` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://www.energysubstantiation.com/`

> WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. Energy Substantiation — WTIC / Tokenized Oil WTIC How It Works Suppliers About Us FAQ Transparency Contact Us Oil, Tokenized. WTIC is a RWA token with 1:1 backing by barrels of West Texas Intermed

### `https://www.energysubstantiation.com/about`

> Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Meet the team, advisors, and board members behind WTIC. Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Meet the team, advisors, and board members behind WTIC. About Us — Energy Substantiation WTIC How It Works Suppliers About Us FAQ Transparency Contact Us About Us Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Our first product, WTIC

### `https://app.rwa.xyz/assets/WTIC`

> View comprehensive analytics for WTI Coin. Track market cap, supply metrics, and transfer stats by network, platform, issuer, and jurisdiction. View comprehensive analytics for WTI Coin. Track market cap, supply metrics, and transfer stats by network, platform, issuer, and jurisdiction. RWA.xyz / WTI Coin / WTIC Open main menu The registry for tokenized real-world assets CTRL + K Press & Citations Enterprise API New NEW → Book Demo Log in Sign up CTRL + K Expand or Collapse Navigation Latest Hom


## Classification rationale

**`candidate-for-adapter`**

Reachable seeds describe a capital / ownership / royalty-style path tied to a physical-RWA thesis without clear operator-hardware requirements. This is a **first-pass** signal only — a human must greenlight any adapter work separately. No adapter is created by this cycle.

## Can the four scores be computed?

**No.** Discovery does not invent scores. An adapter + real `storage/`
snapshot would be required first, and only after a human greenlights
adapter work for a `candidate-for-adapter` disposition.

## What would need to change for this to become scoreable

1. Human review of this FINDINGS.md.
2. If promoted: a dedicated adapter under `adapters/` (SourceError
   discipline; no fabrication).
3. At least one real snapshot under `storage/<asset-id>/`.
4. Confirmation that payout / claim mechanics fit this project's
   capital-provision bar — or keep `wrong-model` / `not-yet-investable`
   / `insufficient-information` as the honest outcome.

## Scheduler notes

- One candidate per cycle (this file).
- Already-investigated slugs (existing FINDINGS.md / candidate state) are
  skipped on future discovery runs even if `next_index` is stale.
- Output is intended to land as a PR for human merge — nothing auto-merges.
