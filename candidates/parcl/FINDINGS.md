# Parcl — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Real-estate price exposure / property market synthetic — verify physical-asset claim carefully

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Parcl (`parcl`) |
| Category | `real_estate` |
| Official website | `https://www.parcl.co/` |
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
| `https://www.parcl.co/` | HTTP 200 — live (text/html) |
| `https://docs.parcl.co/` | HTTP 200 — live (text/html) |
| `https://app.parcl.co/` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://www.parcl.co/`

> Live home prices, seller stress and underwater equity for every U.S. market - 20,000+ price feeds down to the zip, updated daily. Parcl prices 1,578,062 active listings every day. Free to search. Live home prices, seller stress and underwater equity for every U.S. market - 20,000+ price feeds down to the zip, updated daily. Parcl prices 1,578,062 active listings every day. Free to search. U.S. Housing Market, Live - US Home Prices +0.1% 1Y, MSI 5.79, Price Cuts 43.1% / Parcl U.S. ▲ 0.1% YoY MSI 

### `https://docs.parcl.co/`

> Parcl v3 / Parcl Docs ⌘ Ctrl k Parcl v3 Protocol Overview Addresses Security Links v2 (archive) Powered by GitBook On this page For the complete documentation index, see llms.txt . This page is also available as Markdown . Copy On this page Parcl v3 Parcl v3 is a perpetuals exchange designed for real estate synthetics. It supports cross margined perps trading on various real estate markets. LPs add liquidity to a single LP pool per exchange where they take on trader PnL as well as earn trading f

### `https://app.parcl.co/`

> Unlock global real estate investment opportunities with Parcl, your gateway to smarter, faster, and simpler deals. Revolutionize your portfolio with our innovative platform designed to simplify and accelerate the investment process. Start with Parcl today and transform your approach to real estate investing, making it more accessible and efficient than ever before. Unlock global real estate investment opportunities with Parcl, your gateway to smarter, faster, and simpler deals. Revolutionize you


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
