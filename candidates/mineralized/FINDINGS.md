# Mineralized — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Mining / mineral-rights adjacent tokenization project

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Mineralized (`mineralized`) |
| Category | `mining` |
| Official website | `https://mineralized.io/` |
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
| `https://mineralized.io/` | URL error: [Errno -2] Name or service not known |
| `https://mineralized.io/#how-it-works` | URL error: [Errno -2] Name or service not known |

## Reachable text excerpts (truncated)

_No reachable seed returned extractable text._


## Classification rationale

**`insufficient-information`**

None of the seed URLs returned usable content during this scheduled cycle. Retry with better primary sources before any stronger disposition.

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
