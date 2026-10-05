# Albion Labs — tokenized Wressle-1 oil royalty — candidate investigation

**Classification: `candidate-for-adapter`**

**Date investigated:** 2026-10-05
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: Curated pipeline test: Albion Labs tokenized Wressle-1 oil royalty on Base (ALB-WR1-R1 / ALB-WR1-R2). Physical oil/gas royalty / revenue interest — not generic DePIN.

---

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | Albion Labs — tokenized Wressle-1 oil royalty (`albion-labs-wressle-1`) |
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
| Classification | `candidate-for-adapter` |

---

## What was checked

Seed URLs were fetched live in this cycle
(ranked physical-RWA pool / backlog).

| Source | Result |
| --- | --- |
| `https://www.albionlabs.org/` | HTTP 200 — live (text/html) |
| `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf` | HTTP 200 — live (application/pdf) |
| `https://www.albionlabs.org/terms.html` | HTTP 200 — live (text/html) |
| `https://github.com/albionlabs/tokenlist/blob/main/README.md` | HTTP 200 — live (text/html) |
| `https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/tokenlist/main/README.md` | HTTP 200 — live (text/plain) |
| `https://basescan.org/token/0xf836a500910453A397084ADe41321ee20a5AAde1` | HTTP 403: Forbidden |
| `https://basescan.org/token/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` | HTTP 403: Forbidden |
| `https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html` | HTTP 200 — live (text/html) |
| `https://albion.exchange` | HTTP 200 — live (text/html) |

## Reachable text excerpts (truncated)

### `https://www.albionlabs.org/`

> Albion — The Energy Protocol Albion — The Energy Protocol

### `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf`

> %PDF-1.4 %���� 1 0 obj <</Title (Albion Labs whitepaper) /Producer (Skia/PDF m142 Google Docs Renderer)>> endobj 3 0 obj <</ca 1 /BM /Normal>> endobj 10 0 obj <</N 3 /Filter /FlateDecode /Length 296>> stream x�}��J�`� kA�A� \��h���X\[�V�4M�؟�������&.ހ�e(��%���o$����{x�/�@$�*�N�s˥�Q� S�L��eZ}����K�}^�'7��v���!y�.�'��V��>�����s<���^�(���F�>���7�V�=���f���WtV�%J��-�جS�#LQ�"��'IB� EN��Py�zfISP�Y��H)����� ���@� &/C�~�{ �e�6�����1]shE�H� ��0W��'�9�]�Y�?����bM��4 �?��K� endstr

### `https://www.albionlabs.org/terms.html`

> Terms of Service - Albion ← Back Terms of Service Last updated: December 2025 1. Acceptance of Terms By accessing and using the Albion platform, you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, you may not use our services. 2. User Eligibility You must be at least 18 years old and legally capable of entering into binding contracts. You must also comply with all applicable laws and regulations in your jurisdiction. 3. Investment Terms All investments

### `https://github.com/albionlabs/tokenlist/blob/main/README.md`

> Albion Labs token list for Raindex and other DEX integrations - tokenlist/README.md at main · albionlabs/tokenlist Albion Labs token list for Raindex and other DEX integrations - albionlabs/tokenlist tokenlist/README.md at main · albionlabs/tokenlist · GitHub Skip to content Navigation Menu Sign in Appearance settings Platform AI CODE CREATION GitHub Copilot Write better code with AI GitHub Copilot app Direct agents from issue to merge MCP Registry Integrate external tools DEVELOPER WORKFLOWS Ac

### `https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json`

> { "name": "Albion Labs Token List", "logoURI": "https://raw.githubusercontent.com/albionlabs/tokenlist/main/assets/albion-logo.svg", "keywords": ["albion", "royalty", "energy", "tokenized", "wressle", "oil"], "timestamp": "2026-02-21T15:25:00.000Z", "version": { "major": 1, "minor": 0, "patch": 0 }, "tokens": [ { "chainId": 8453, "address": "0xf836a500910453A397084ADe41321ee20a5AAde1", "name": "Wressle-1 Royalty Community Preview", "symbol": "ALB-WR1-R1", "decimals": 18, "logoURI": "https://raw.

### `https://raw.githubusercontent.com/albionlabs/tokenlist/main/README.md`

> # Albion Labs Token List Standard [Uniswap tokenlist](https://tokenlists.org/) format for Albion royalty tokens on Base. ## Tokens / Symbol / Name / Royalty Share / Contract / /--------/------/---------------/----------/ / ALB-WR1-R1 / Wressle-1 Community Preview / 2.5% of 4.5% / [`0xf836a500...`](https://basescan.org/token/0xf836a500910453A397084ADe41321ee20a5AAde1) / / ALB-WR1-R2 / Wressle-1 Investor Preview / 7.5% of 4.5% / [`0x1d57246f...`](https://basescan.org/token/0x1d57246fd0ba134d7cc78d

### `https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html`

> Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Home Home About Us Advertise With Us Investor Relations What's New Share Prices Share Prices Financial Diary Commodities UK Industry Sectors Aquis Stock Exchange Share Prices Euronext Share Prices US Share Prices UK Indices FTSE 100 FTSE 250 FTSE All-Share FTSE Small Cap FTSE 350 FTSE AIM All-Share Share Riser

### `https://albion.exchange`

> 


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
