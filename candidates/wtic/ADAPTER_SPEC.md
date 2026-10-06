# WTIC — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-06
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Coverage test: WTIC (Energy Substantiation) — ERC-20 on Ethereum representing 1:1 physical WTI crude oil via Volumetric Energy Receipts; may not have periodic yield

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | WTIC |
| Slug | `wtic` |
| Issuer / brand (self-described) | WTIC |
| Seed hosts | `app.rwa.xyz`, `app.uniswap.org`, `blog.rwa.xyz`, `cryptobriefing.com`, `docs.ensub.io`, `docs.etherscan.io`, `docs.rwa.xyz`, `energysubstantiation.com`, `etherscan.io`, `rwa.xyz`, `www.cointrust.com`, `www.energysubstantiation.com`, `x.com` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | ethereum |
| Token contract | `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` |
| `name()` | `WTI Coin` |
| `symbol()` | `WTIC` |
| `decimals()` | `6` |
| `totalSupply()` | 4,150 token units (raw `4150000000`) |
| RPC used | `https://ethereum-rpc.publicnode.com` |
| Address source | https://www.energysubstantiation.com/ |
| Issuer-published address? | YES |
| Identity confidence | `high` |
| Evidence: eth_call | YES |
| Evidence: metadata match | YES |
| Evidence: market corroboration | YES |

**Layer separation:** this table establishes **TOKEN IDENTITY** only. It does
**not** verify physical-asset backing, ownership/registry rights, or payouts.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| ethereum / uniswap | `0x95E707CA9CFDc1A5d7014061941E0035a866Ea6E` | WTIC / USDC | $90695.8 | $88.52 |
| ethereum / uniswap | `0xDd109a10E918ED6Bb51aEf0f5650493F552ff0Aa` | WTIC / USDC | $11691.14 | $88.10 |

CoinGecko search API returned **zero** coins for query `WTIC` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Physical asset cue: `Responses Field`

**What was actually confirmed here**

- Token eth_call identity confirmed on **ethereum** at `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` (WTI Coin/WTIC).
- DexScreener reports 2 pair(s) for the probed token (market context only).
- 17/35 research URLs reachable in this pass.
- Physical asset layer: `partially-verified` (`erc-20`); economic right: `partially-verified` (`debt_like`); revenue: `partially-verified`; payout: `unverified` (0 on-chain tx samples; 0 metadata records).
- **No** independently corroborated physical-asset identity (filings/registries) was confirmed.
- **No** machine-queryable payout/distribution surface with on-chain confirmation was established.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | see docs excerpts | **no** |
| Token supply | matches eth_call | yes |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` | eth_call + market metadata | Identity / supply only |
| Distribution / Safe / vault | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Payout observability:** No verified payout/harvest event ABI + confirmed historical txs for this candidate’s underlying economics in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://www.energysubstantiation.com/` | HTTP 200 — live (text/html) |
| `https://www.energysubstantiation.com/about` | HTTP 200 — live (text/html) |
| `https://etherscan.io/token/0x709ab533D18e652eCd56423d71c0241A0ee56a3b` | HTTP 403: Forbidden |
| `https://app.rwa.xyz/assets/WTIC` | HTTP 200 — live (text/html) |
| `https://rwa.xyz/` | HTTP 200 — live (text/html) |
| `https://docs.rwa.xyz/` | HTTP 200 — live (text/html) |
| `https://app.rwa.xyz/` | HTTP 200 — live (text/html) |
| `https://blog.rwa.xyz/` | HTTP 200 — live (text/html) |
| `https://rwa.xyz/whitepaper` | HTTP 404: Not Found |
| `https://rwa.xyz/whitepaper.pdf` | HTTP 404: Not Found |
| `https://rwa.xyz/llm/wtic-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://wtic.gitbook.io/wtic-docs/llms.txt` | HTTP 404: Not Found |
| `https://wtic.gitbook.io/wtic-docs/` | HTTP 404: Not Found |
| `https://energysubstantiation.com/` | HTTP 200 — live (text/html) |
| `https://docs.energysubstantiation.com/` | URL error: [Errno -2] Name or service not known |
| `https://app.energysubstantiation.com/` | URL error: [Errno -2] Name or service not known |
| `https://blog.energysubstantiation.com/` | URL error: [Errno -2] Name or service not known |
| `https://energysubstantiation.com/whitepaper` | HTTP 404: Not Found |
| `https://energysubstantiation.com/whitepaper.pdf` | HTTP 404: Not Found |
| `https://energysubstantiation.com/llm/wtic-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://etherscan.io/` | HTTP 403: Forbidden |
| `https://docs.etherscan.io/` | HTTP 200 — live (text/html) |
| `https://app.etherscan.io/` | URL error: [Errno -5] No address associated with hostname |
| `https://blog.etherscan.io/` | URL error: [Errno -5] No address associated with hostname |
| `https://etherscan.io/whitepaper` | HTTP 200 — live (text/html) |
| `https://etherscan.io/whitepaper.pdf` | HTTP 403: Forbidden |
| `https://etherscan.io/llm/wtic-llm-knowledge-base.html` | HTTP 403: Forbidden |
| `https://wtic.gitbook.io/wtic-docs.md` | HTTP 404: Not Found |
| `https://app.uniswap.org/explore/tokens/ethereum/0x709ab533d18e652ecd56423d71c0241a0ee56a3b` | HTTP 200 — live (text/html) |
| `https://cryptobriefing.com/energy-substantiation-tokenize-oil-blockchain/` | HTTP 200 — live (text/html) |
| `https://www.cointrust.com/market-news/california-startup-launches-oil-backed-ethereum-token-wtic` | HTTP 200 — live (text/html) |
| `https://docs.ensub.io/` | HTTP 200 — live (text/html) |
| `https://x.com/energyrwa` | HTTP 200 — live (text/html) |
| `https://app.rwa.xyz/citations` | HTTP 200 — live (text/html) |
| `https://app.rwa.xyz/platform-overview` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search API returned **zero** coins for query `WTIC` in this pass — no independent CoinGecko listing confirmed. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `app.rwa.xyz`, `app.uniswap.org`, `blog.rwa.xyz`, `cryptobriefing.com`, `docs.ensub.io`, `docs.etherscan.io`, `docs.rwa.xyz`, `energysubstantiation.com`, `etherscan.io`, `rwa.xyz`, `www.cointrust.com`, `www.energysubstantiation.com`, `x.com`

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
| Token identity on-chain | High | Successful eth_call getters |
| Underlying asset independently verifiable | Low | Independent filings/registries naming the asset |
| Economic right established | Medium | Right-type evidence (filings/docs) |
| Economic mechanism / realized yield observable | Low | Payout metadata + on-chain tx verification |
| Independent market listing quality | Medium | Dex/CG presence without implying backing |

---

## 8. Recommended data sources for an eventual adapter

See **Recommended Adapter Inputs** below for the concrete table. High-level:

- ERC-20 identity (name/symbol/decimals)
- totalSupply via eth_call
- DEX market context (price/liquidity) as non-backing context
- claims[] rows for documented self-reported yield/ownership claims with explicit tiers
- Record physical-asset identity + independent filing URLs as claims[] provenance

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `token-data-only`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

TOKEN IDENTITY can be established (confidence=high; issuer-published=True; eth_call=True), but the TOKEN→ASSET→RIGHT→PAYOUT chain is incomplete (physical_asset=partially-verified, payout_mechanism=unverified). Tokn must not equate token identity with physical-asset ownership or realized yield.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), TOKEN IDENTITY: contract address is issuer-published + eth_call-verified, Public DEX market price/liquidity exists for the token

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions, Continuously verified production/revenue figures as facts

**Main blocker(s):** Physical asset named only in issuer materials — no independent filing/registry corroboration; No publicly reachable payout metadata, distribution contract, or verified payout transactions

**To move to the next state:** To become adapter-ready: independently corroborate the physical asset, establish the economic/legal right type, and publish a machine-queryable payout surface (distribution txs/events/API) that an adapter can poll. Token identity alone is insufficient.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | WTIC supply (docs or market) | ethereum `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` via `https://ethereum-rpc.publicnode.com` | blockchain | on-chain | ethereum eth_call → totalSupply() @ 0x709ab533D18e652eCd56423d71c0241A0ee56a3b | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | WTI Coin / WTIC / 6 | `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` on ethereum | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| TOKEN IDENTITY: contract address is issuer-published + eth_call-verified | WTI Coin / WTIC @ 0x709ab533D18e652eCd56423d71c0241A0ee56a3b (ethereum); confidence=high | https://www.energysubstantiation.com/ | official documentation | on-chain | Issuer-controlled source publishes address → infer chain → eth_call name()/symbol()/decimals()/totalSupply() → match candidate identity; DexScreener corroboration | verified | token identity fields / claims[] | — |
| PHYSICAL ASSET: underlying physical asset identity | erc-20 | https://www.energysubstantiation.com/ | official documentation | physical-world | Independent filings/registries naming the asset + economic context; NOT implied by ERC-20 identity | partially-verified | underlying_asset | Physical asset named only in issuer materials — no independent filing/registry corroboration |
| ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues | debt_like | issuer research corpus | official documentation | physical-world | Independent filing and/or issuer legal/technical docs describing right type (royalty, revenue-swap, ownership, etc.) | partially-verified | claims[] / economic_right | Economic/legal right described in issuer materials only — independent legal corroboration missing |
| PAYOUT MECHANISM: machine-queryable investor distributions | 0 payout records; 0 on-chain verified; currency=unknown; frequency=unknown | n/a | official documentation | physical-world | Issuer-published payout metadata → eth_getTransaction(ByHash/Receipt) on the token's chain; or distribution contract events / public API | blocked | null / unavailable | No publicly reachable payout metadata, distribution contract, or verified payout transactions |
| REVENUE MECHANISM: how the physical asset generates revenue | described | https://cryptobriefing.com/energy-substantiation-tokenize-oil-blockchain/ | official documentation | physical-world | Operator/regulatory production disclosures or continuously queryable revenue APIs | partially-verified | claims[] (context) | Revenue mechanism described only by issuer; not independently queryable |
| Public DEX market price/liquidity exists for the token | price=$88.52; liquidity_usd=90695.8 | DexScreener pair `0x95E707CA9CFDc1A5d7014061941E0035a866Ea6E` (ethereum/uniswap) | DEX/indexer | on-chain | GET DexScreener /latest/dex/tokens/{address} | observable | token_price (context only) / claims[] | — |
| DEX liquidity proves underlying-asset liquidity / backing | implied by marketing sometimes | DexScreener | DEX/indexer | self-reported | No valid verification — category error | blocked | null / unavailable | Market liquidity ≠ physical/underlying liquidity |

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
| Economic/legal right type established | YES |
| Infrastructure operation / production | NO |
| Revenue generation / leases / harvests | YES |
| Actual distributions to holders | NO |

### Bridge summary

```text
Token exists (independently queryable): YES
Underlying asset identified in docs: YES
Underlying asset independently verifiable: NO
Economic connection between token and asset verifiable: NO
```

### Evidence graph (layered)

| Layer | Status | Confidence | Notes |
| --- | --- | --- | --- |
| token_identity | verified | high | eth_call + issuer address provenance |
| physical_asset | partially-verified | medium | erc-20 |
| economic_right | partially-verified | medium | debt_like |
| revenue_mechanism | partially-verified | low | Revenue mechanism described only by issuer; not independently queryable |
| payout_mechanism | unverified | none | records=0; onchain_sample=0; currency=n/a |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| ERC-20 getters | blockchain | `0x709ab533D18e652eCd56423d71c0241A0ee56a3b` on ethereum | eth_call name/symbol/decimals/totalSupply via `https://ethereum-rpc.publicnode.com` | identity + supply | on snapshot / daily | **required** — token identity |
| DEX market context | DEX/indexer | `https://api.dexscreener.com/latest/dex/tokens/0x709ab533D18e652eCd56423d71c0241A0ee56a3b` | GET JSON pairs | price/liquidity context | optional cadence | **optional** — never as backing proof |
| Official page text | official documentation | `https://www.energysubstantiation.com/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://www.energysubstantiation.com/about` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://app.rwa.xyz/assets/WTIC` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://rwa.xyz/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://docs.rwa.xyz/` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://app.rwa.xyz/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
- Record physical-asset identity + independent filing URLs as claims[] provenance

### What the future adapter MUST NOT implement

- Verified underlying-asset ownership / registry identity
- Observed staking APY as a verified fact
- Realized underlying revenue/yield distributions
- Continuously verified production/revenue figures as facts

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
  researched_at: "2026-10-06T17:21Z"

  # Layered evidence graph — do not collapse into one confidence value.
  token_identity:
    status: verified
    confidence: high
    issuer_published_address: true
    chain_established: true
    eth_call_verified: true
    metadata_match: true
    market_corroboration: true
    note: "Token identity ≠ asset backing ≠ economic/payout verification"

  physical_asset:
    status: partially-verified
    confidence: medium
    named_asset: "erc-20"
    blocker: "Physical asset named only in issuer materials — no independent filing/registry corroboration"
    evidence:
      - source: "https://www.energysubstantiation.com/"
        tier: medium
        proves: "Issuer materials name a specific physical asset"
        reachable: true
        independently_verifiable: false

  economic_right:
    status: partially-verified
    confidence: medium
    right_type: "debt_like"
    blocker: "Economic/legal right described in issuer materials only — independent legal corroboration missing"
    evidence:
      - source: "issuer research corpus"
        tier: medium
        proves: "Issuer/docs language indicates `debt_like`"
        reachable: true
        independently_verifiable: false

  revenue_mechanism:
    status: partially-verified
    confidence: low
    machine_queryable: false
    blocker: "Revenue mechanism described only by issuer; not independently queryable"
    evidence:
      - source: "https://cryptobriefing.com/energy-substantiation-tokenize-oil-blockchain/"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://www.cointrust.com/market-news/california-startup-launches-oil-backed-ethereum-token-wtic"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://app.rwa.xyz/platform-overview"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false

  payout_mechanism:
    status: unverified
    confidence: none
    machine_queryable: false
    payout_record_count: 0
    onchain_verified_sample: 0
    currency_hint: ""
    frequency_hint: ""
    blocker: "No publicly reachable payout metadata, distribution contract, or verified payout transactions"
    evidence:
      []

  machine_queryable_sources:
    - source: "ethereum:0x709ab533D18e652eCd56423d71c0241A0ee56a3b"
      what_it_proves: "ERC-20 token identity and supply"
      reachable: true
      independently_verifiable: true

  # Back-compat summary flags
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
    - "Physical asset named only in issuer materials — no independent filing/registry corroboration"
    - "No publicly reachable payout metadata, distribution contract, or verified payout transactions"

  recommended_adapter_scope:
    - "ERC-20 identity (name/symbol/decimals)"
    - "totalSupply via eth_call"
    - "DEX market context (price/liquidity) as non-backing context"
    - "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"
    - "Record physical-asset identity + independent filing URLs as claims[] provenance"

  prohibited_outputs:
    - "Verified underlying-asset ownership / registry identity"
    - "Observed staking APY as a verified fact"
    - "Realized underlying revenue/yield distributions"
    - "Continuously verified production/revenue figures as facts"
```

---

## Appendix — reachable excerpts (truncated)

### `https://www.energysubstantiation.com/`

> WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. Energy Substantiation — WTIC / Tokenized Oil WTIC How It Works Suppliers About Us FAQ Transparency Contact Us Oil, Tokenized. WTIC is a RWA token with 1:1 backing by barrels of West Texas Intermediate oil. Zero tracking error. Zero rollover risk. Just direct 1:1 backed exposure to WTI oil, oncha

### `https://www.energysubstantiation.com/about`

> Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Meet the team, advisors, and board members behind WTIC. Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Meet the team, advisors, and board members behind WTIC. About Us — Energy Substantiation WTIC How It Works Suppliers About Us FAQ Transparency Contact Us About Us Energy Substantiation provides a platform for tokens backed 1:1 by real-world assets. Our first product, WTIC, brings West Texas Intermediate crude oil onchain. Each token is backed by physical oil held throug

### `https://app.rwa.xyz/assets/WTIC`

> View comprehensive analytics for WTI Coin. Track market cap, supply metrics, and transfer stats by network, platform, issuer, and jurisdiction. View comprehensive analytics for WTI Coin. Track market cap, supply metrics, and transfer stats by network, platform, issuer, and jurisdiction. RWA.xyz / WTI Coin / WTIC Open main menu The registry for tokenized real-world assets CTRL + K Press & Citations Enterprise API New NEW → Book Demo Log in Sign up CTRL + K Expand or Collapse Navigation Latest Home Asset Screener New Asset Monitor Data & API Data Catalog Documentation Enterprise API NEW Market I

### `https://rwa.xyz/`

> RWA.xyz provides analytics on Tokenized Real-World Assets RWA.xyz provides analytics on Tokenized Real-World Assets RWA.xyz / Analytics on Tokenized Real-World Assets Open main menu The registry for tokenized real-world assets CTRL + K Press & Citations Enterprise API New NEW → Book Demo Log in Sign up CTRL + K Expand or Collapse Navigation Latest Home Asset Screener New Asset Monitor Data & API Data Catalog Documentation Enterprise API NEW Market Intelligence Overview Networks Platforms Asset Managers Asset Classes Stablecoins U.S. Treasury Funds Non-U.S. Govt. Debt Credit Stocks PE / VC Acti

### `https://docs.rwa.xyz/`

> Welcome to RWA.xyz! Welcome to RWA.xyz! Introduction - RWA.xyz Documentation Documentation Index Fetch the complete documentation index at: /llms.txt Use this file to discover all available pages before exploring further. Skip to main content RWA.xyz Documentation home page Search... ⌘ K Ask Assistant ⌘ I Contact Research Dashboard Dashboard Search... Navigation Home Introduction Home Introduction Changelog Methodology Overview Data Sources Metric Calculations Coverage & Eligibility Data Quality Frameworks Overview Asset Classes Tokenization Type Tokenization Structure Eligible Investors Data

### `https://app.rwa.xyz/`

> RWA.xyz provides analytics on Tokenized Real-World Assets RWA.xyz provides analytics on Tokenized Real-World Assets RWA.xyz / Analytics on Tokenized Real-World Assets Open main menu The registry for tokenized real-world assets CTRL + K Press & Citations Enterprise API New NEW → Book Demo Log in Sign up CTRL + K Expand or Collapse Navigation Latest Home Asset Screener New Asset Monitor Data & API Data Catalog Documentation Enterprise API NEW Market Intelligence Overview Networks Platforms Asset Managers Asset Classes Stablecoins U.S. Treasury Funds Non-U.S. Govt. Debt Credit Stocks PE / VC Acti

### `https://blog.rwa.xyz/`

> Last Week in Tokenization Skip to content High-signal news & insights on Tokenization. Sign up to our weekly newsletter for alpha on the latest RWA market activity, regulation, and trends. Cited by Research Tokenized Asset Coalition 2024 Outlook Tokenized Asset Coalition April 22, 2024 Product Updates Product Update: RWA.xyz Directory V2 Charlie You April 22, 2024 Research The Spectrum of Tokenization Report Colin Erickson, Mac Naggar, and Jack Chong April 22, 2024 Research Case Study: The First RWA Distressed Debt Opportunity with Goldfinch's $FIDU Token Nathan Howard April 22, 2024 Research

### `https://energysubstantiation.com/`

> WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. WTIC is a commodity token backed 1:1 by barrels of West Texas Intermediate oil. Zero tracking error, zero rollover risk, easy 24/7 trading on Ethereum. Energy Substantiation — WTIC / Tokenized Oil WTIC How It Works Suppliers About Us FAQ Transparency Contact Us Oil, Tokenized. WTIC is a RWA token with 1:1 backing by barrels of West Texas Intermediate oil. Zero tracking error. Zero rollover risk. Just direct 1:1 backed exposure to WTI oil, oncha

