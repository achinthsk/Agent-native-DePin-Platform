# Energy Web — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Energy infrastructure decentralization — may be utility/DePIN not asset claim; investigate carefully

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Energy Web (`energy-web`) |
| Category | `energy` |
| Official website | `https://www.energyweb.org/` |
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
| `https://www.energyweb.org/` | HTTP 200 — live (text/html) |
| `https://docs.energyweb.org/` | HTTP 200 — live (text/html) |
| `https://www.energyweb.org/technology` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://www.energyweb.org/`

> Energy Web builds rule-digitization tools and decentralized verification infrastructure for energy and environmental markets. Energy Web builds rule-digitization tools and decentralized verification infrastructure for energy and environmental markets. Energy Web · Digitize rules. Verify claims. Accelerate decarbonization. Skip to content Home Protocol Solutions Ecosystem Open verification infrastructure Digitize rules. Verify claims. Accelerate decarbonization. Energy Web builds rule digitizatio

### `https://docs.energyweb.org/`

> Welcome to Energy Web&#x27;s documentation site. You will find here information about all our solutions, technologies and services! Welcome to Energy Web&#x27;s documentation site. You will find here information about all our solutions, technologies and services! Documentation Overview / Energy Web Documentation Energy Web Documentation ⌘ Ctrl k Energy Web Ecosystem Launchpad by Energy Web EWC Validator Documentation Community Ressources Legacy documentation Energy Web Documentation Documentatio


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
