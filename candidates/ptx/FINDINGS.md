# PTX — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-09-11
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Named mining-royalty issuer (Net Smelter Royalty tokenization) — replaces bare category mining-royalty-tokenization

---

## What was checked

Seed URLs were fetched live in this cycle
(backlog / matched seeds).

| Source | Result |
| --- | --- |
| `https://ptxtoken.com/` | HTTP 200 — live (text/html) |
| `https://ptxtoken.com/#how-it-works` | HTTP 200 — live (text/html) |
| `https://ptxtoken.com/#nsr` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://ptxtoken.com/`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

### `https://ptxtoken.com/#how-it-works`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

### `https://ptxtoken.com/#nsr`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue


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
