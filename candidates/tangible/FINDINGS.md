# Tangible — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-04
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Tokenized physical luxury / real-world asset marketplace

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Tangible (`tangible`) |
| Category | `other_physical_rwa` |
| Official website | `https://www.tangible.store/` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | Official/seed language indicates a physical real-world asset or identifiable asset pool (see excerpts). |
| Why it qualifies as physical RWA | Physical + ownership/economic-exposure markers present in notes/seeds/reachable text. |
| Why it is NOT generic DePIN | Not classified as generic DePIN: evidence points to asset claim / financing exposure rather than network-work utility alone. |
| Previously investigated? | no |
| Duplicate detected? | no |
| Discovery source | `ranked_pool` |
| Physical-asset gate | `physical-rwa` |
| Classification | `candidate-for-adapter` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://www.tangible.store/` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/` | HTTP 200 — live (text/html) |
| `https://www.tangible.store/marketplace` | HTTP 404: Not Found |

## Reachable text excerpts (truncated)

### `https://www.tangible.store/`

> Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible / Crypto’s Leading Tokenization Protocol Migrate 3,3+ NFT TNGBL CVR Read more DECENTRALIZED ACCESS TO TOKENIZED REAL WORLD ASSETS Earn consistent, reliable yield from low-volatility off-chain sources Innovative tokens with deep liquidity Tangible blends D

### `https://docs.tangible.store/`

> General / Tangible v2 Tangible v2 ⌘ Ctrl k Tangible v2 Protocol Overview General Legal Technical Audits & Security RWA (TNGBL) Token Contracts & Addresses re.al Network Details Protocol Guides and Videos Archive Asset Categories Real Estate Gold Baskets Overview Why Tokenized Real Estate? Design Technical FAQs Contracts & Addresses USTB USTB Token USTB Yield Backing Asset: USDM Powered by GitBook On this page For the complete documentation index, see llms.txt . This page is also available as Mar


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
