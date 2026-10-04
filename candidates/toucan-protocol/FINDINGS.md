# Toucan Protocol — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: On-chain carbon credit / environmental asset bridging — physical-world credit exposure

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Toucan Protocol (`toucan-protocol`) |
| Category | `other_physical_rwa` |
| Official website | `https://toucan.earth/` |
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
| `https://toucan.earth/` | HTTP 200 — live (text/html) |
| `https://docs.toucan.earth/` | HTTP 200 — live (text/html) |
| `https://toucan.earth/carbon-bridge` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://toucan.earth/`

> Toucan is building carbon market infrastructure to scale the carbon removal space quickly, transparently, and efficiently. Learn more Toucan is building carbon market infrastructure to scale the carbon removal space quickly, transparently, and efficiently. Learn more Carbon credit market infrastructure / Scaling CDR space Skip to content About What we offer Team & Timeline Media Kit Biochar Pool Resources Blog CHAR pool Documentation News About What we offer Team & Timeline Media Kit Biochar Poo

### `https://docs.toucan.earth/`

> Infrastructure to accelerate global climate action. Infrastructure to accelerate global climate action. Welcome to Toucan / Toucan Documentation Toucan Documentation ⌘ Ctrl k Toucan Documentation 🌱 Introduction Welcome to Toucan Legal Disclaimer 🌏 Toucan Bridging Carbon Pools Carbon Retirements 🌿 RESOURCES Web3 concepts Carbon markets Frequently asked questions Archives Audits 💻 Developers Toucan for developers Smart contracts Subgraphs Toucan SDK Tools + examples Developer support Powered by Gi


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
