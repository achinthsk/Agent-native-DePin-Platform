# AgriFi — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Named farmland / ag RWA tokenization project (Polygon / AGF) — replaces bare category tokenized-farmland

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | AgriFi |
| Slug | `agrifi` |
| Issuer / brand (self-described) | AgriFi |
| Seed hosts | `agrifi.gitbook.io`, `agrifi.tech`, `blog.agrifi.tech`, `techbullion.com`, `www.rwa.io` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | polygon |
| Token contract | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` |
| `name()` | `AGRIFI` |
| `symbol()` | `AGF` |
| `decimals()` | `18` |
| `totalSupply()` | 7,200,000,000 token units (raw `7200000000000000000000000000`) |
| RPC used | `https://polygon-bor-rpc.publicnode.com` |
| Address source | — |
| Issuer-published address? | NO |
| Identity confidence | `high` |
| Evidence: eth_call | YES |
| Evidence: metadata match | YES |
| Evidence: market corroboration | YES |

**Layer separation:** this table establishes **TOKEN IDENTITY** only. It does
**not** verify physical-asset backing, ownership/registry rights, or payouts.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| polygon / quickswap | `0x8F86821d639105F0f678e7d78F70C6F5c8edEFBC` | AGF / USDT0 | $2343.04 | $0.008457 |
| polygon / quickswap | `0xC5540C03C42cEe4D2cA967B662f0E9FD84b01209` | AGF / WPOL | $1688.24 | $0.008439 |

CoinGecko search API returned **zero** coins for query `AgriFi` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Fractional ownership of underlying real-world assets (docs/marketing)
- Claimed yield/APY language: `5–18% APY`
- Staking lock language: `30–360 days (stated in docs)`

**What was actually confirmed here**

- Token eth_call identity confirmed on **polygon** at `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` (AGRIFI/AGF).
- DexScreener reports 2 pair(s) for the probed token (market context only).
- 16/21 research URLs reachable in this pass.
- **No** independently queryable underlying-asset registry/ownership contract was confirmed.
- **No** independently queryable staking/profit/royalty distribution contract was confirmed.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | 5–18% APY | **no** |
| Ownership / royalty / RWA claim | Fractional ownership of underlying real-world assets (docs/marketing) | **no** |
| Token supply | total supply 7.2 billion , fully circulating. | yes |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` | eth_call + market metadata | Identity / supply only |
| Ownership / asset registry | **Not confirmed** | Docs may describe; address not verified | Required for underlying claims — blocked unless published |
| Staking / rewards | **Not confirmed** | Docs may describe; address not verified | Required for APY observation — blocked unless published |
| Profit / royalty distribution | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Events:** No verified payout/harvest event ABI + public indexer endpoint for
this candidate’s underlying economics was confirmed in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://agrifi.tech/` | HTTP 200 — live (text/html) |
| `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/whitepaper` | HTTP 404: Not Found |
| `https://docs.agrifi.tech/` | URL error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'docs.agrifi.tech'. (_ssl.c:1000) |
| `https://app.agrifi.tech/` | URL error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'app.agrifi.tech'. (_ssl.c:1000) |
| `https://blog.agrifi.tech/` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/whitepaper.pdf` | HTTP 404: Not Found |
| `https://agrifi.tech/llm/agrifi-llm-knowledge-base.html` | HTTP 200 — live (text/html) |
| `https://agrifi.gitbook.io/agrifi-docs/llms.txt` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/` | HTTP 200 — live (text/html) |
| `https://agrifi.gitbook.io/agrifi-docs.md` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs` | HTTP 200 — live (text/html) |
| `https://techbullion.com/agrifi-highlights-traceability-tokenization-and-real-time-data-as-agricultures-next-layer/` | HTTP 200 — live (text/html) |
| `https://techbullion.com/the-agf-token-ecosystem-expands-agricultures-role-in-the-web3-real-world-asset-economy/` | HTTP 200 — live (text/html) |
| `https://www.digitaljournal.com/pr/news/binary-news-network/agrifi-s-digital-twin-tokens-reinventing-1446980078.html` | HTTP 410: Gone |
| `https://techbullion.com/agrifi-brings-farmland-on-chain-with-its-iot-and-blockchain-powered-marketplace/` | HTTP 200 — live (text/html) |
| `https://techbullion.com/agrifi-expands-farmer-profitability-through-blockchain-based-staking-and-revenue-sharing/` | HTTP 200 — live (text/html) |
| `https://techbullion.com/how-agf-token-brings-real-world-utility-to-defi/` | HTTP 200 — live (text/html) |
| `https://www.rwa.io/post/how-defi-is-embracing-real-world-assets?utm_source=chatgpt.com` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/agrifi-whitepaper.pdf?utm_source=chatgpt.com` | HTTP 200 — live (application/pdf) |
| `https://blog.agrifi.tech/web3-token-traceable-tokenized-data-driven-agriculture-passiveincome-agriculture` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search API returned **zero** coins for query `AgriFi` in this pass — no independent CoinGecko listing confirmed. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `agrifi.gitbook.io`, `agrifi.tech`, `blog.agrifi.tech`, `techbullion.com`, `www.rwa.io`

**Independent / market:** DexScreener (if pairs match); CoinGecko as noted.
Independent market metadata is **not** independent underlying-asset verification.

**Conflicts / tensions**

- Docs describe supply as fully circulating while also describing team/partner vesting — allocation schedule conflict.
- Yield/APY is claimed in official materials, but no staking or distribution contract address was confirmed as independently queryable.

---

## 7. Per-claim confidence

| Claim | Confidence now | Why |
| --- | --- | --- |
| Public project web presence | High | Reachable official HTTP surfaces |
| Capital-style (non-operator) marketing path | Medium-high | Discovery already classified `candidate-for-adapter` — first-pass only |
| Token identity on-chain | High | Successful eth_call getters |
| Underlying asset independently verifiable | Low | Ownership/registry contract reachability |
| Economic mechanism / realized yield observable | Low | Distribution/staking contract reachability |
| Independent market listing quality | Medium | Dex/CG presence without implying backing |

---

## 8. Recommended data sources for an eventual adapter

See **Recommended Adapter Inputs** below for the concrete table. High-level:

- ERC-20 identity (name/symbol/decimals)
- totalSupply via eth_call
- DEX market context (price/liquidity) as non-backing context
- claims[] rows for documented self-reported yield/ownership claims with explicit tiers

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `token-data-only`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

TOKEN IDENTITY can be established (confidence=high; issuer-published=False; eth_call=True), but ASSET/BACKING verification and ECONOMIC/PAYOUT verification are still unavailable. Tokn must not equate token identity with physical-asset ownership or realized yield.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), Public DEX market price/liquidity exists for the token

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions

**Main blocker(s):** No issuer-published ownership/registry contract address for the underlying asset; No publicly reachable staking/profit/royalty distribution contract or payout API

**To move to the next state:** To become adapter-ready: issuer-published ownership/registry and/or payout-distribution contracts (or an equivalent public attestation API) that connect the token to specific underlying assets and cashflows. Token identity alone is insufficient.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | total supply 7.2 billion , fully circulating. | polygon `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` via `https://polygon-bor-rpc.publicnode.com` | blockchain | on-chain | polygon eth_call → totalSupply() @ 0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6 | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | AGRIFI / AGF / 18 | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` on polygon | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| TOKEN IDENTITY: contract address is issuer-published + eth_call-verified | AGRIFI / AGF @ 0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6 (polygon); confidence=high | DexScreener / research text | DEX/indexer | on-chain | Issuer-controlled source publishes address → infer chain → eth_call name()/symbol()/decimals()/totalSupply() → match candidate identity; DexScreener corroboration | partially-verified | token identity fields / claims[] | Address provenance is market/indexer-attributed rather than issuer-published; token identity still eth_call-matched |
| ASSET/BACKING: token represents verified physical-asset ownership/registry | not established by token identity alone | n/a | official documentation | physical-world | Requires ownership/registry contract or independent attestation — NOT implied by ERC-20 identity | blocked | null / unavailable | No independently queryable ownership/registry surface |
| ECONOMIC/PAYOUT: holders receive claimed royalty/revenue distributions | not established by token identity alone | n/a | official documentation | physical-world | Requires payout/distribution contract events or public payout API — NOT implied by ERC-20 identity | blocked | null / unavailable | No independently queryable payout/distribution surface |
| Public DEX market price/liquidity exists for the token | price=$0.008457; liquidity_usd=2343.04 | DexScreener pair `0x8F86821d639105F0f678e7d78F70C6F5c8edEFBC` (polygon/quickswap) | DEX/indexer | on-chain | GET DexScreener /latest/dex/tokens/{address} | observable | token_price (context only) / claims[] | — |
| DEX liquidity proves underlying-asset liquidity / backing | implied by marketing sometimes | DexScreener | DEX/indexer | self-reported | No valid verification — category error | blocked | null / unavailable | Market liquidity ≠ physical/underlying liquidity |
| Staking / advertised yield APY | 5–18% APY | Official docs/blog (reachable text) | official documentation | self-reported | No verification method currently available | self-reported | claims[] (self-reported) ; realized_yield_pct=null | Staking/reward contract address not identified |
| Fractional ownership of underlying real-world assets (docs/marketing) | As stated in official marketing/docs | Official website/docs | official website | physical-world | No verification method currently available | self-reported | claims[] ; underlying fields null until contracts exist | No public ownership/registry/distribution surface confirmed |

Status vocabulary: `verified` | `partially-verified` | `observable` |
`self-reported` | `conflicted` | `unverified` | `blocked`.

---

## 11. Verification Boundary

### Token-level verification

| Capability | Available now? |
| --- | --- |
| Contract identity / symbol / decimals | YES |
| Total supply | YES |
| Holder balances / transfers (generic ERC-20) | YES (standard) |
| DEX price | YES |
| DEX liquidity | YES |

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
Token exists (independently queryable): YES
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
| ERC-20 getters | blockchain | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` on polygon | eth_call name/symbol/decimals/totalSupply via `https://polygon-bor-rpc.publicnode.com` | identity + supply | on snapshot / daily | **required** — token identity |
| DEX market context | DEX/indexer | `https://api.dexscreener.com/latest/dex/tokens/0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` | GET JSON pairs | price/liquidity context | optional cadence | **optional** — never as backing proof |
| Official page text | official documentation | `https://agrifi.tech/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://blog.agrifi.tech/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://agrifi.tech/llm/agrifi-llm-knowledge-base.html` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://agrifi.gitbook.io/agrifi-docs/llms.txt` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://agrifi.gitbook.io/agrifi-docs/` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |

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

- ERC-20 identity (name/symbol/decimals)
- totalSupply via eth_call
- DEX market context (price/liquidity) as non-backing context
- claims[] rows for documented self-reported yield/ownership claims with explicit tiers

### What the future adapter MUST NOT implement

- Verified underlying-asset ownership / registry identity
- Observed staking APY as a verified fact
- Realized underlying revenue/yield distributions

### What requires human review

- Whether the project token (if any) should be treated as the representation
  of specific underlying assets vs a generic ecosystem/utility token.
- Whether DexScreener-attributed contract addresses are acceptable before
  issuer-published address lists exist.
- Whether to greenlight any adapter at `token-data-only` readiness.

---

## 15. Promotion Checklist

- [x] Token/asset identity independently confirmed
- [x] Relevant contracts confirmed
- [x] Required APIs reachable
- [x] Required blockchain calls reproducible
- [x] Claim sources documented
- [x] Independent evidence identified where available
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
  status: token-data-only
  researched_at: "2026-10-05T15:29Z"

  # Three separate layers — do not collapse into one confidence value.
  token_identity:
    available: true
    confidence: high
    issuer_published_address: false
    chain_established: true
    eth_call_verified: true
    metadata_match: true
    market_corroboration: true
    note: "Token identity ≠ asset backing ≠ economic/payout verification"

  token_verification:
    available: true

  underlying_asset_verification:
    available: false

  economic_mechanism_verification:
    available: false

  market_data:
    available: true

  independent_sources:
    available: true
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
    - "No issuer-published ownership/registry contract address for the underlying asset"
    - "No publicly reachable staking/profit/royalty distribution contract or payout API"

  recommended_adapter_scope:
    - "ERC-20 identity (name/symbol/decimals)"
    - "totalSupply via eth_call"
    - "DEX market context (price/liquidity) as non-backing context"
    - "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"

  prohibited_outputs:
    - "Verified underlying-asset ownership / registry identity"
    - "Observed staking APY as a verified fact"
    - "Realized underlying revenue/yield distributions"
```

---

## Appendix — reachable excerpts (truncated)

### `https://agrifi.tech/`

> Agrifi is an Agricultural platform based on Blockchain technology providing solutions and to challenges in traditional agriculture methods, including traceability of food products, financing, crop insurance and supply chain transactions. Innovation combined with advanced technologies like blockchain and artificial intelligence (AI) provide revolutionary solutions to agriculture. Agrifi Home About Platform Traceability Roadmap Whitepaper News Contact Airdrop Blockchain technology is a disruptive technology that changes business and supply chain models. Blockchain technology has many application

### `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution`

> AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). How AgriFi Is Turning Farmland into the Next Big Real-World Asset Class - Agrifi Contact Home Blockchain News Supplychain AI Home Bl

### `https://blog.agrifi.tech/`

> The blockchain technology allows peer-to-peer transactions to take place transparently and without the need for an intermediary like a bank (such as for cryptocurrencies) or a middleman in the agriculture sector. By eliminating the need for a central authority, the technology changes the way that trust is granted – instead of trusting an authority, trust is placed in cryptography and peer-to-peer architecture. It thus helps restore the trust between producers and consumers, which can reduce the The blockchain technology allows peer-to-peer transactions to take place transparently and without t

### `https://agrifi.tech/llm/agrifi-llm-knowledge-base.html`

> Agrifi is a Web3 agriculture platform combining blockchain, DeFi, IoT farming and real-world asset tokenisation to build a transparent agricultural finance ecosystem. Agrifi LLM Knowledge Base / Web3 Agriculture Ecosystem Agrifi Web3 Agriculture Knowledge Base This page provides a structured overview of the Agrifi ecosystem for researchers, AI systems, and users seeking technical information about the Agrifi platform. Platform Overview Agrifi is a Web3 agricultural technology platform that integrates blockchain infrastructure, decentralized finance (DeFi), IoT farming devices, and artificial i

### `https://agrifi.gitbook.io/agrifi-docs/llms.txt`

> # Agrifi Docs ## Agrifi Docs - [Introduction](https://agrifi.gitbook.io/agrifi-docs/introduction.md) - [Agrifi Concepts for both B2B and B2C Space](https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space.md) - [Food Safety and Supply Chain Management in Blockchain & Marketplace](https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space/food-safety-and-supply-chain-management-in-blockchain-and-marketplace.md) - [Concept 2: RWA - Organic Farming - Produce from the Farm will be their Return on the Investment](https://agrifi.gitbook.io/agrifi-docs/ag

### `https://agrifi.gitbook.io/agrifi-docs/`

> Introduction / Agrifi Docs Agrifi Docs ⌘ Ctrl k Agrifi Docs Introduction Agrifi Concepts for both B2B and B2C Space Future Potential of Farmland Tokenization Agrifi AGF BLOCKCHAIN IN AGRICUTURE ROLE OF BLOCKCHAIN TECHNOLOGY AGTECH HELPS SMALL AND LARGE FARMS TO FINANCING TRENDS AGRIBUSINESS GIANTS ARE TAKING NOTICE DUPONT’S GRANULAR SENSORS ARE NOW COMMON THROUGHOUT FARMING ADVANCED AERIAL IMAGING IS NOW POSSIBLE ANALYTICS TOOLS ROBOTICS IS AUTOMATING AGRICULTURE BENEFITS TRANSPARENT SUPPLY CHAIN FAIR PRICING OF GOODS EXPAND FINANCIAL OPTIONS FOR FARMERS IMMEDIATE PAYMENT ON DELIVERY TRACEABIL

### `https://agrifi.gitbook.io/agrifi-docs.md`

> # Page Not Found The URL `agrifi-docs` does not exist. This page may have been moved, renamed, or deleted. ## Suggested Pages You may be looking for one of the following: - [ANALYTICS TOOLS](https://agrifi.gitbook.io/agrifi-docs/agrifi-agf/analytics-tools.md) - [Agrifi TOKEN](https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-token.md) - [FINANCING TRENDS](https://agrifi.gitbook.io/agrifi-docs/agrifi-agf/financing-trends.md) - [DUPONT’S GRANULAR](https://agrifi.gitbook.io/agrifi-docs/agrifi-agf/duponts-granular.md) - [BLOCKCHAIN IN AGRICUTURE](https://agrifi.gitbook.io/agrifi-docs/agrifi-

### `https://agrifi.gitbook.io/agrifi-docs`

> Introduction / Agrifi Docs Agrifi Docs ⌘ Ctrl k Agrifi Docs Introduction Agrifi Concepts for both B2B and B2C Space Future Potential of Farmland Tokenization Agrifi AGF BLOCKCHAIN IN AGRICUTURE ROLE OF BLOCKCHAIN TECHNOLOGY AGTECH HELPS SMALL AND LARGE FARMS TO FINANCING TRENDS AGRIBUSINESS GIANTS ARE TAKING NOTICE DUPONT’S GRANULAR SENSORS ARE NOW COMMON THROUGHOUT FARMING ADVANCED AERIAL IMAGING IS NOW POSSIBLE ANALYTICS TOOLS ROBOTICS IS AUTOMATING AGRICULTURE BENEFITS TRANSPARENT SUPPLY CHAIN FAIR PRICING OF GOODS EXPAND FINANCIAL OPTIONS FOR FARMERS IMMEDIATE PAYMENT ON DELIVERY TRACEABIL

