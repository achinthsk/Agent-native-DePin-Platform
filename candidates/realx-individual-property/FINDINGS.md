# RealX — individual property — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Curated pipeline test: RealX named/individual property FRAX tokens (India)

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | RealX — individual property (`realx-individual-property`) |
| Category | `real_estate` |
| Official website | `https://realx.in/` |
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
| `https://realx.in/` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/real-estate-tokenization-india-guide/` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://realx.in/`

> RealX Marketplace - we are obsessed with bringing quality investment opportunities to everyone. We have broken the access barrier and brought this down, so everyone can digitally invest in quality Real Estate RealX Marketplace - we are obsessed with bringing quality investment opportunities to everyone. We have broken the access barrier and brought this down, so everyone can digitally invest in quality Real Estate RealX

### `https://wassup.realx.in/real-estate-tokenization-india-guide/`

> Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Real Estate Tokenization In India: Investor’s Complete Guide Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey December 6, 2025 April 23, 2026 Real Estate Tokenization Explained:


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
