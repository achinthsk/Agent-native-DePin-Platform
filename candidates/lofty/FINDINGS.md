# Lofty — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Fractional real-estate property tokens

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Lofty (`lofty`) |
| Category | `real_estate` |
| Official website | `https://www.lofty.ai/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `ranked_pool` |
| Physical-asset gate | `physical-rwa` |
| Classification | `insufficient-information` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://www.lofty.ai/` | HTTP 200 — live (text/html) |
| `https://www.lofty.ai/marketplace` | HTTP 200 — live (text/html) |
| `https://docs.lofty.ai/` | URL error: [Errno -5] No address associated with hostname |

## Reachable text excerpts (truncated)

### `https://www.lofty.ai/`

> New to Lofty? Buy $50 of U.S. real estate and get $50 free. Earn daily rent and sell anytime. New to Lofty? Buy $50 of U.S. real estate and get $50 free. Earn daily rent and sell anytime. Buy Fractional Real Estate / Lofty AI Investing App About Lofty Lofty is a fractional U.S. real estate investing platform where visitors can browse property shares, learn about rental property investing, review calculators and guides, and access support for marketplace orders and account activity. The canonical

### `https://www.lofty.ai/marketplace`

> Browse U.S. rental properties on Lofty. New to Lofty? Buy $50, get $50 free. Earn daily rent and sell anytime. Browse U.S. rental properties on Lofty. New to Lofty? Buy $50, get $50 free. Earn daily rent and sell anytime. Real Estate Investing Marketplace / Lofty About Lofty Lofty is a fractional U.S. real estate investing platform where visitors can browse property shares, learn about rental property investing, review calculators and guides, and access support for marketplace orders and account


## Classification rationale

**`insufficient-information`**

Seeds were reachable but did not clearly establish either a capital-only physical-RWA path or a hard wrong-model operator requirement. Manual follow-up is required (docs deep-dive, contracts, payout shape) before a stronger classification.

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
