# Albion ALB-WR1-R1/R2 — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Curated pipeline test: Albion Labs Wressle-1 well royalty tokens ALB-WR1-R1/R2

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Albion ALB-WR1-R1/R2 (`albion-alb-wr1`) |
| Category | `energy` |
| Official website | `https://www.albionlabs.org/` |
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
| `https://www.albionlabs.org/` | HTTP 200 — live (text/html) |
| `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf` | HTTP 200 — live (application/pdf) |
| `https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://www.albionlabs.org/`

> Albion — The Energy Protocol Albion — The Energy Protocol

### `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf`

> %PDF-1.4 %���� 1 0 obj <</Title (Albion Labs whitepaper) /Producer (Skia/PDF m142 Google Docs Renderer)>> endobj 3 0 obj <</ca 1 /BM /Normal>> endobj 10 0 obj <</N 3 /Filter /FlateDecode /Length 296>> stream x�}��J�`� kA�A� \��h���X\[�V�4M�؟�������&.ހ�e(��%���o$����{x�/�@$�*�N�s˥�Q� S�L��eZ}����K�}^�'7��v���!y�.�'��V��>�����s<���^�(���F�>���7�V�=���f���WtV�%J��-�جS�#LQ�"��'IB� EN��Py�zfISP�Y��H)����� ���@� &/C�~�{ �e�6�����1]shE�H� ��0W��'�9�]�Y�?����bM��4 �?��K� endstr

### `https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html`

> Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Home Home About Us Advertise With Us Investor Relations What's New Share Prices Share Prices Financial Diary Commodities UK Industry Sectors Aquis Stock Exchange Share Prices Euronext Share Prices US Share Prices UK Indices FTSE 100 FTSE 250 FTSE All-Share FTSE Small Cap FTSE 350 FTSE AIM All-Share Share Riser


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
