# Realio Network — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-07
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Real-world asset issuance network focused on real estate / alternatives

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Realio Network (`realio`) |
| Category | `real_estate` |
| Official website | `https://realio.network/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Not independently confirmed in this pass. |
| Why it qualifies as physical RWA | Physical-asset gate result: `unclear`. |
| Why it is NOT generic DePIN | Gate did not assign generic-depin; still not sufficient for unqualified physical-RWA promotion without more evidence. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `ranked_pool` |
| Physical-asset gate | `unclear` |
| Classification | `insufficient-information` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://realio.network/` | HTTP 200 — live (text/html) |
| `https://docs.realio.network/` | HTTP 200 — live (text/html) |
| `https://realio.network/ecosystem` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://realio.network/`

> Explore Realio, a Layer-1 Web3 ecosystem for issuing and managing Real-World Assets (RWAs). Fully open-source, permissionless, and all powered by native blockchain infrastructure. Explore Realio, a Layer-1 Web3 ecosystem for issuing and managing Real-World Assets (RWAs). Fully open-source, permissionless, and all powered by native blockchain infrastructure. Realio Network / Web3 Ecosystem for Digital & Real-World Assets (RWAs) Explore Projects & Apps Freehold Non-custodial wallet Districts RWA v

### `https://docs.realio.network/`

> The Realio Network is designed as a multi-chain layer 1 Web3 ecosystem focused on the issuance and management of digitally native and real-world assets across many non-EVM and EVM compatible chains. The Realio Network is designed as a multi-chain layer 1 Web3 ecosystem focused on the issuance and management of digitally native and real-world assets across many non-EVM and EVM compatible chains. Introduction / Realio Network Documentation Skip to main content Documentation GitHub Introduction EVM


## Classification rationale

**`insufficient-information`**

Capital-style language appeared, but the physical-asset relationship is still `unclear` after the relevance gate. Limited follow-up needed before candidate-for-adapter.

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
