# xU3O8 — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Curated pipeline test: tokenized physical uranium (U3O8 / yellowcake) fractional ownership

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | xU3O8 (`xu3o8`) |
| Category | `other_physical_rwa` |
| Official website | `https://uranium.io/en` |
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
| `https://uranium.io/en` | HTTP 200 — live (text/html) |
| `https://help.uranium.io/en/articles/10110492-what-is-xu3o8` | HTTP 200 — live (text/html) |
| `https://help.uranium.io/en/articles/10711639-where-is-the-physical-uranium-ore-concentrate-u3o8-stored` | HTTP 200 — live (text/html) |
| `https://app.uranium.io/en/polygon` | HTTP 403: Forbidden |

## Reachable text excerpts (truncated)

### `https://uranium.io/en`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Invest in uranium / U3O8 / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Buy Own Trade uranium xU3O8 powers your ownership and trading of physical uranium (U3O8) Buy Uranium Powered by Featured in Featured in Power your portfolio with uranium (Value of $100 invested) S&P 500 vs urani

### `https://help.uranium.io/en/articles/10110492-what-is-xu3o8`

> What is xU3O8? / xU3O8 Help Center Skip to main content Search for articles... All Collections General Questions What is xU3O8? What is xU3O8? December 2, 2024 xU3O8 enables investors to own and trade U3O8 in an investment friendly and transparent manner by administering fractional ownership of physical uranium in the form of a smart contract ledger. Each xU3O8 represents a unit of ownership of U3O8 held by Archax as a custodian for investors. This novel blockchain-based ownership register lever

### `https://help.uranium.io/en/articles/10711639-where-is-the-physical-uranium-ore-concentrate-u3o8-stored`

> Where is the physical uranium ore concentrate (U3O8) stored? / xU3O8 Help Center Skip to main content Search for articles... All Collections General Questions Where is the physical uranium ore concentrate (U3O8) stored? Where is the physical uranium ore concentrate (U3O8) stored? March 5, 2025 The physical uranium ore concentrate (U3O8) is securely stored at regulated storage facility, operated by Cameco, one of the three globally recognized uranium conversion and storage providers. The uranium 


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
