# AgriFi — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-09-12
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Named farmland / ag RWA tokenization project (Polygon / AGF) — replaces bare category tokenized-farmland

---

## What was checked

Seed URLs were fetched live in this cycle
(backlog / matched seeds).

| Source | Result |
| --- | --- |
| `https://agrifi.tech/` | HTTP 200 — live (text/html) |
| `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/whitepaper` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://agrifi.tech/`

> Agrifi is an Agricultural platform based on Blockchain technology providing solutions and to challenges in traditional agriculture methods, including traceability of food products, financing, crop insurance and supply chain transactions. Innovation combined with advanced technologies like blockchain and artificial intelligence (AI) provide revolutionary solutions to agriculture. Agrifi Home About Platform Traceability Roadmap Whitepaper News Contact Airdrop Blockchain technology is a disruptive 

### `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution`

> AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). How AgriFi Is Turning Farmland i


## Classification rationale

**`candidate-for-adapter`**

Reachable seeds describe a capital / ownership / royalty-style path without clear operator-hardware requirements. This is a **first-pass** signal only — a human must greenlight any adapter work separately. No adapter is created by this cycle.

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
- Output is intended to land as a PR for human merge — nothing auto-merges.
