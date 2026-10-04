# Blocksquare — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Real-estate tokenization protocol / property exposure

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Blocksquare (`blocksquare`) |
| Category | `real_estate` |
| Official website | `https://blocksquare.io/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `ranked_pool` |
| Physical-asset gate | `physical-rwa` |
| Classification | `candidate-for-adapter` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://blocksquare.io/tokenize/` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://blocksquare.io/`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

### `https://docs.blocksquare.io/`

> Introduction / Blocksquare Docs Blocksquare Docs ⌘ Ctrl k Blocksquare Docs Introduction Research About Press Kit Infrastructure Tokenization protocol Marketplaces platform Liquidity engine Certified Partners Tokenization service Operating your marketplace Setup instructions Pricing Partner network Legal BST token ℹ️ Token overview 💹 Exchanges 📳 Price feeds ⚛️ Blocksquare DAO FAQ General questions Tokenization protocol Marketplace operators End users For Developers Revenue Distribution Contract S

### `https://blocksquare.io/tokenize/`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.


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
