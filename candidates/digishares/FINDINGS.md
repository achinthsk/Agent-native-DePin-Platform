# DigiShares — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Real-estate / alternative-asset tokenization platform

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | DigiShares (`digishares`) |
| Category | `real_estate` |
| Official website | `https://www.digishares.io/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Not independently confirmed in this pass. |
| Why it qualifies as physical RWA | Physical-asset gate result: `unclear`. |
| Why it is NOT generic DePIN | Gate did not assign generic-depin; still not sufficient for unqualified physical-RWA promotion without more evidence. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `pool_match` |
| Physical-asset gate | `unclear` |
| Classification | `insufficient-information` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://www.digishares.io/` | HTTP 200 — live (text/html) |
| `https://www.digishares.io/platform` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://www.digishares.io/`

> Tokenize real estate and real-world assets: issue digital securities, manage investors, and enable peer-to-peer trading. Tokenize real estate and real-world assets: issue digital securities, manage investors, and enable peer-to-peer trading. DigiShares / Asset Tokenization Platform Loading… Products DigiShares Launch Fast, compliant token issuance DigiShares Standard Full-featured tokenization & trading DigiShares Advanced Custom white-label marketplaces View all products Pricing Plans & Pricing


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
