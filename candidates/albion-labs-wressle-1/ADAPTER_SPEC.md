# Albion Labs — tokenized Wressle-1 oil royalty — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Curated pipeline test: Albion Labs tokenized Wressle-1 oil royalty on Base (ALB-WR1-R1 / ALB-WR1-R2). Physical oil/gas royalty / revenue interest — not generic DePIN.

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | Albion Labs — tokenized Wressle-1 oil royalty |
| Slug | `albion-labs-wressle-1` |
| Issuer / brand (self-described) | Albion Labs — tokenized Wressle-1 oil royalty |
| Seed hosts | `albion.exchange`, `albionlabs.org`, `app.co.uk`, `basescan.org`, `blog.github.com`, `docs.basescan.org`, `docs.github.com`, `github.com`, `raw.githubusercontent.com`, `www.albionlabs.org`, `www.lse.co.uk` |

### Token / chain (live probe)

No ERC-20 (or equivalent) contract was confirmed via live `eth_call` in this pass for a token identity matching this project. Marketing may describe a token, but without a confirmed address + successful RPC getters, Tokn cannot treat token identity as verified.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

CoinGecko search API returned **zero** coins for query `Albion Labs — tokenized Wressle-1 oil royalty` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Official pages describe a capital-style product; see excerpts.

**What was actually confirmed here**

- 29/66 research URLs reachable in this pass.
- **No** independently queryable underlying-asset registry/ownership contract was confirmed.
- **No** independently queryable staking/profit/royalty distribution contract was confirmed.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | see docs excerpts | **no** |
| Token supply | not confirmed | **no** |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `not confirmed` | not confirmed | Identity / supply only |
| Ownership / asset registry | **Not confirmed** | Docs may describe; address not verified | Required for underlying claims — blocked unless published |
| Staking / rewards | **Not confirmed** | Docs may describe; address not verified | Required for APY observation — blocked unless published |
| Profit / royalty distribution | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Events:** No verified payout/harvest event ABI + public indexer endpoint for
this candidate’s underlying economics was confirmed in this research pass.

---

## 5. Public APIs / indexers (reachability)

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
| `https://albion.exchange/` | HTTP 200 — live (text/html) |
| `https://docs.albion.exchange/` | URL error: [Errno -2] Name or service not known |
| `https://app.albion.exchange/` | URL error: [Errno -2] Name or service not known |
| `https://blog.albion.exchange/` | URL error: [Errno -2] Name or service not known |
| `https://albion.exchange/whitepaper` | HTTP 404: Not Found |
| `https://albion.exchange/whitepaper.pdf` | HTTP 404: Not Found |
| `https://albion.exchange/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://albionlabstokenizedwressle1oilroyalty.gitbook.io/albionlabstokenizedwressle1oilroyalty-docs/llms.txt` | HTTP 404: Not Found |
| `https://albionlabstokenizedwressle1oilroyalty.gitbook.io/albionlabstokenizedwressle1oilroyalty-docs/` | HTTP 404: Not Found |
| `https://albionlabs.org/` | HTTP 200 — live (text/html) |
| `https://docs.albionlabs.org/` | URL error: [Errno -2] Name or service not known |
| `https://app.albionlabs.org/` | URL error: [Errno -2] Name or service not known |
| `https://blog.albionlabs.org/` | URL error: [Errno -2] Name or service not known |
| `https://albionlabs.org/whitepaper` | HTTP 200 — live (text/html) |
| `https://albionlabs.org/whitepaper.pdf` | HTTP 200 — live (text/html) |
| `https://albionlabs.org/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | HTTP 200 — live (text/html) |
| `https://basescan.org/` | HTTP 403: Forbidden |
| `https://docs.basescan.org/` | HTTP 200 — live (text/html) |
| `https://app.basescan.org/` | URL error: [Errno -5] No address associated with hostname |
| `https://blog.basescan.org/` | URL error: [Errno -5] No address associated with hostname |
| `https://basescan.org/whitepaper` | HTTP 403: Forbidden |
| `https://basescan.org/whitepaper.pdf` | HTTP 403: Forbidden |
| `https://basescan.org/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | HTTP 403: Forbidden |
| `https://github.com/` | HTTP 200 — live (text/html) |
| `https://docs.github.com/` | HTTP 200 — live (text/html) |
| `https://app.github.com/` | URL error: [Errno -5] No address associated with hostname |
| `https://blog.github.com/` | HTTP 200 — live (text/html) |
| `https://github.com/whitepaper` | HTTP 200 — live (text/html) |
| `https://github.com/whitepaper.pdf` | HTTP 406: Not Acceptable |
| `https://github.com/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://co.uk/` | URL error: [Errno -5] No address associated with hostname |
| `https://docs.co.uk/` | URL error: [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1000) |
| `https://app.co.uk/` | HTTP 200 — live (text/html) |
| `https://blog.co.uk/` | URL error: _ssl.c:983: The handshake operation timed out |
| `https://co.uk/whitepaper` | URL error: [Errno -5] No address associated with hostname |
| `https://co.uk/whitepaper.pdf` | URL error: [Errno -5] No address associated with hostname |
| `https://co.uk/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | URL error: [Errno -5] No address associated with hostname |
| `https://githubusercontent.com/` | URL error: [Errno -5] No address associated with hostname |
| `https://docs.githubusercontent.com/` | HTTP 500: Domain Not Found |
| `https://app.githubusercontent.com/` | HTTP 500: Domain Not Found |
| `https://blog.githubusercontent.com/` | HTTP 500: Domain Not Found |
| `https://githubusercontent.com/whitepaper` | URL error: [Errno -5] No address associated with hostname |
| `https://githubusercontent.com/whitepaper.pdf` | URL error: [Errno -5] No address associated with hostname |
| `https://githubusercontent.com/llm/albion-labs-tokenized-wressle-1-oil-royalty-llm-knowledge-base.html` | URL error: [Errno -5] No address associated with hostname |
| `https://albionlabstokenizedwressle1oilroyalty.gitbook.io/albionlabstokenizedwressle1oilroyalty-docs.md` | HTTP 404: Not Found |
| `https://docs.basescan.org/llms.txt` | HTTP 200 — live (text/html) |
| `https://etherscan.io/api/pricing` | HTTP 403: Forbidden |
| `https://docs.basescan.org/set-up-your-api-key` | HTTP 200 — live (text/html) |
| `https://docs.basescan.org/introduction` | HTTP 200 — live (text/html) |
| `https://docs.basescan.org/build-with-ai/introduction` | HTTP 200 — live (text/html) |
| `https://docs.basescan.org/endpoint-overview` | HTTP 200 — live (text/html) |
| `https://docs.basescan.org/metadata/introduction` | HTTP 200 — live (text/html) |
| `https://docs.github.com` | HTTP 200 — live (text/html) |
| `https://github.com/resources/whitepapers` | HTTP 200 — live (text/html) |
| `https://docs.github.com/en` | HTTP 200 — live (text/html) |
| `https://docs.github.com/en/get-started` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search API returned **zero** coins for query `Albion Labs — tokenized Wressle-1 oil royalty` in this pass — no independent CoinGecko listing confirmed. |
| Public EVM RPC eth_call | No successful project-matched token probe |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `albion.exchange`, `albionlabs.org`, `app.co.uk`, `basescan.org`, `blog.github.com`, `docs.basescan.org`, `docs.github.com`, `github.com`, `raw.githubusercontent.com`, `www.albionlabs.org`, `www.lse.co.uk`

**Independent / market:** DexScreener (if pairs match); CoinGecko as noted.
Independent market metadata is **not** independent underlying-asset verification.

**Conflicts / tensions**

- No hard textual conflict isolated beyond marketing vs evidence gaps.

---

## 7. Per-claim confidence

| Claim | Confidence now | Why |
| --- | --- | --- |
| Public project web presence | High | Reachable official HTTP surfaces |
| Capital-style (non-operator) marketing path | Medium-high | Discovery already classified `candidate-for-adapter` — first-pass only |
| Token identity on-chain | Low | No matched token probe |
| Underlying asset independently verifiable | Low | Ownership/registry contract reachability |
| Economic mechanism / realized yield observable | Low | Distribution/staking contract reachability |
| Independent market listing quality | Low | Dex/CG presence without implying backing |

---

## 8. Recommended data sources for an eventual adapter

See **Recommended Adapter Inputs** below for the concrete table. High-level:

- Do not implement an adapter yet — research only until identity is confirmed

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `blocked`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

Even a minimum useful verification surface could not be established: no confirmed token eth_call identity matched to the project and no independently queryable underlying/payout source. Marketing pages alone are insufficient.

**What can currently be verified:** none beyond marketing reachability

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions, Any on-chain token identity fields

**Main blocker(s):** No independently confirmed token contract via eth_call; No issuer-published ownership/registry contract address for the underlying asset; No independent market/indexer surface confirming asset identity

**To move to the next state:** Publish contract addresses / public APIs for token identity and economic mechanism, then re-run the research agent.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Public capital-product identity / investability surface | Marketing site describes investable product | https://www.albionlabs.org/; https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf; https://www.albionlabs.org/terms.html; https://github.com/albionlabs/tokenlist/blob/main/README.md; https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json; https://raw.githubusercontent.com | official website | self-reported | No independent contract/API verification method found | blocked | null / unavailable | No confirmed token, registry, or payout API |

Status vocabulary: `verified` | `partially-verified` | `observable` |
`self-reported` | `conflicted` | `unverified` | `blocked`.

---

## 11. Verification Boundary

### Token-level verification

| Capability | Available now? |
| --- | --- |
| Contract identity / symbol / decimals | NO |
| Total supply | NO |
| Holder balances / transfers (generic ERC-20) | NO |
| DEX price | NO |
| DEX liquidity | NO |

### Underlying-asset verification

| Capability | Available now? |
| --- | --- |
| Physical / real-world asset identity | NO |
| Asset ownership / registry | NO |
| Infrastructure operation / production | NO |
| Revenue generation / leases / harvests | NO |
| Actual distributions to holders | NO |

### Bridge summary

```text
Token exists (independently queryable): NO
Underlying asset identified in docs: YES
Underlying asset independently verifiable: NO
Economic connection between token and asset verifiable: NO
```

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| Official page text | official documentation | `https://www.albionlabs.org/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://www.albionlabs.org/terms.html` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://github.com/albionlabs/tokenlist/blob/main/README.md` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://raw.githubusercontent.com/albionlabs/tokenlist/main/README.md` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

---

## 13. Sources Not Suitable for Verification

| Source / pattern | Why unsuitable |
| --- | --- |
| Marketing slogans without contracts/APIs | Self-reported; not independently queryable |
| Unnamed ownership/staking/profit contracts | Described in docs but address missing |
| DEX liquidity as proof of underlying-asset liquidity/backing | Category error |
| Project's own unverified API (if any) as independent verification | Same trust domain as issuer |
| Unextracted PDF bytes as confirmation of a specific numeric claim | PDF may be reachable without text verification |
| Unrelated DEX tickers sharing a short symbol | Symbol collision risk |

---

## 14. Adapter Implementation Boundary

### What the future adapter SHOULD implement

- Do not implement an adapter yet — research only until identity is confirmed

### What the future adapter MUST NOT implement

- Verified underlying-asset ownership / registry identity
- Observed staking APY as a verified fact
- Realized underlying revenue/yield distributions
- Any on-chain token identity fields

### What requires human review

- Whether the project token (if any) should be treated as the representation
  of specific underlying assets vs a generic ecosystem/utility token.
- Whether DexScreener-attributed contract addresses are acceptable before
  issuer-published address lists exist.
- Whether to greenlight any adapter at `blocked` readiness.

---

## 15. Promotion Checklist

- [ ] Token/asset identity independently confirmed
- [ ] Relevant contracts confirmed
- [x] Required APIs reachable
- [ ] Required blockchain calls reproducible
- [x] Claim sources documented
- [ ] Independent evidence identified where available
- [x] Conflicts documented
- [x] Verification boundary defined
- [x] Claims mapped to evidence
- [x] Unknown values explicitly preserved
- [x] Adapter outputs defined
- [ ] Schema compatibility checked
- [ ] Scoring impact understood
- [ ] Snapshot reproducibility confirmed
- [ ] Human review completed

`[x]` = demonstrated in this research pass. `[ ]` = not demonstrated (human /
adapter phase).

---

## 16. Human decision gate

This file does **not** authorize adapter work. Next steps for a human:

1. Review [`FINDINGS.md`](./FINDINGS.md) + this `ADAPTER_SPEC.md`.
2. Decide whether to greenlight a bespoke adapter (manual, like Glow/RealT/Elmnts).
3. If greenlit: implement **only** the SHOULD list; keep MUST NOT as null/unavailable.
4. If not greenlit: leave as research-only; no code.

---

## 17. Machine-readable summary (research only)

Not consumed by scoring/schema. For humans and future tooling only.

```yaml
adapter_readiness:
  status: blocked
  researched_at: "2026-10-05T15:22Z"

  token_verification:
    available: false

  underlying_asset_verification:
    available: false

  economic_mechanism_verification:
    available: false

  market_data:
    available: false

  independent_sources:
    available: false
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
    - "No independently confirmed token contract via eth_call"
    - "No issuer-published ownership/registry contract address for the underlying asset"
    - "No independent market/indexer surface confirming asset identity"

  recommended_adapter_scope:
    - "Do not implement an adapter yet — research only until identity is confirmed"

  prohibited_outputs:
    - "Verified underlying-asset ownership / registry identity"
    - "Observed staking APY as a verified fact"
    - "Realized underlying revenue/yield distributions"
    - "Any on-chain token identity fields"
```

---

## Appendix — reachable excerpts (truncated)

### `https://www.albionlabs.org/`

> Albion — The Energy Protocol Albion — The Energy Protocol

### `https://www.albionlabs.org/Albion-Labs-Whitepaper.pdf`

> [PDF reachable — 200000 bytes fetched; binary not fully text-extracted by this agent]

### `https://www.albionlabs.org/terms.html`

> Terms of Service - Albion ← Back Terms of Service Last updated: December 2025 1. Acceptance of Terms By accessing and using the Albion platform, you accept and agree to be bound by these Terms of Service. If you do not agree to these terms, you may not use our services. 2. User Eligibility You must be at least 18 years old and legally capable of entering into binding contracts. You must also comply with all applicable laws and regulations in your jurisdiction. 3. Investment Terms All investments are subject to specific terms outlined in the respective token offering documents. Past performance

### `https://github.com/albionlabs/tokenlist/blob/main/README.md`

> <!DOCTYPE html> <html lang="en" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark" data-a11y-animated-images="system" data-a11y-link-underlines="true" > <head> <meta charset="utf-8"> <link rel="dns-prefetch" href="https://github.githubassets.com"> <link rel="dns-prefetch" href="https://avatars.githubusercontent.com"> <link rel="dns-prefetch" href="https://github-cloud.s3.amazonaws.com"> <link rel="dns-prefetch" href="https://user-images.githubusercontent.com/"> <link rel="preconnect" href="https://github.githubassets.com" crossorigin> <link rel="preconnect" href="https://av

### `https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json`

> { "name": "Albion Labs Token List", "logoURI": "https://raw.githubusercontent.com/albionlabs/tokenlist/main/assets/albion-logo.svg", "keywords": ["albion", "royalty", "energy", "tokenized", "wressle", "oil"], "timestamp": "2026-02-21T15:25:00.000Z", "version": { "major": 1, "minor": 0, "patch": 0 }, "tokens": [ { "chainId": 8453, "address": "0xf836a500910453A397084ADe41321ee20a5AAde1", "name": "Wressle-1 Royalty Community Preview", "symbol": "ALB-WR1-R1", "decimals": 18, "logoURI": "https://raw.githubusercontent.com/albionlabs/tokenlist/main/assets/r1-token-logo.svg", "tags": ["royalty", "ener

### `https://raw.githubusercontent.com/albionlabs/tokenlist/main/README.md`

> # Albion Labs Token List Standard [Uniswap tokenlist](https://tokenlists.org/) format for Albion royalty tokens on Base. ## Tokens / Symbol / Name / Royalty Share / Contract / /--------/------/---------------/----------/ / ALB-WR1-R1 / Wressle-1 Community Preview / 2.5% of 4.5% / [`0xf836a500...`](https://basescan.org/token/0xf836a500910453A397084ADe41321ee20a5AAde1) / / ALB-WR1-R2 / Wressle-1 Investor Preview / 7.5% of 4.5% / [`0x1d57246f...`](https://basescan.org/token/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7) / ## Usage ### Raindex / DEX Integration Add to your `settings.yaml`: ```yaml us

### `https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html`

> Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Home Home About Us Advertise With Us Investor Relations What's New Share Prices Share Prices Financial Diary Commodities UK Industry Sectors Aquis Stock Exchange Share Prices Euronext Share Prices US Share Prices UK Indices FTSE 100 FTSE 250 FTSE All-Share FTSE Small Cap FTSE 350 FTSE AIM All-Share Share Risers Georgina Energy (GEX) +25.68% Tech Minerals (MNTL) +25.00% Macau Property (MPO) +24.07% Tern (TERN

### `https://albion.exchange`

> 

