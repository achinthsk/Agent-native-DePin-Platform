# xU3O8 — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-06
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Coverage test: xU3O8 — fractional beneficial ownership of physical uranium ore concentrate (U3O8 / yellowcake) in Cameco custody via Archax; may not have periodic yield

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | xU3O8 (`xu3o8`) |
| Category | `mining` |
| Official website | `https://uranium.io/en` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `backlog_match` |
| Physical-asset gate | `physical-rwa` |
| Classification | `insufficient-information` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://uranium.io/en` | HTTP 200 — live (text/html) |
| `https://uranium.io/whitepaper.pdf` | HTTP 200 — live (application/pdf) |
| `https://app.uranium.io/en/polygon` | HTTP 403: Forbidden |
| `https://uranium.io/en/proof-of-reserves` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://uranium.io/en`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Invest in uranium / U3O8 / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Buy Own Trade uranium xU3O8 powers your ownership and trading of physical uranium (U3O8) Buy Uranium Powered by Featured in Featured in Power your portfolio with uranium (Value of $100 invested) S&P 500 vs urani

### `https://uranium.io/whitepaper.pdf`

> %PDF-1.7 %���� 158 0 obj <</Linearized 1/L 3336231/O 161/E 159158/N 12/T 3332955/H [ 936 648]>> endobj xref 158 32 0000000016 00000 n 0000001584 00000 n 0000001729 00000 n 0000001765 00000 n 0000002855 00000 n 0000002969 00000 n 0000003006 00000 n 0000003634 00000 n 0000004239 00000 n 0000004645 00000 n 0000005139 00000 n 0000005587 00000 n 0000006184 00000 n 0000006555 00000 n 0000006957 00000 n 0000007342 00000 n 0000007755 00000 n 0000008010 00000 n 0000008418 00000 n 0000008673 00000 n 00000

### `https://uranium.io/en/proof-of-reserves`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Proof of Reserves / Invest in uranium / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Approved by Archax LTD on 27 November 2024 Resources Proof of Reserves Whitepaper MiCAR Whitepaper Help Center Learn Tokenize Uranium Redeem Uranium Legal Privacy & Cookie Policy Terms of Service © 


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
