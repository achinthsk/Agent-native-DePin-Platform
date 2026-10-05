# Blocksquare — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Real-estate tokenization protocol / property exposure

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | Blocksquare |
| Slug | `blocksquare` |
| Issuer / brand (self-described) | Blocksquare |
| Seed hosts | `app.blocksquare.io`, `blocksquare.gitbook.io`, `blocksquare.io`, `blog.blocksquare.io`, `docs.blocksquare.io` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | ethereum |
| Token contract | `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` |
| `name()` | `BlocksquareToken` |
| `symbol()` | `BST` |
| `decimals()` | `18` |
| `totalSupply()` | 69,263,162 token units (raw `69263162304034291754603810`) |
| RPC used | `https://ethereum-rpc.publicnode.com` |
| Address source | https://docs.blocksquare.io/about |
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
| ethereum / uniswap | `0x0E85fB1be698E777F2185350b4A52E5eE8DF51A6` | BST / WETH | $48653.28 | $0.01178 |
| ethereum / uniswap | `0x1779b347046e36f411380b8a6618036b023f70263043ae80f566463707b40c4b` | BST / ETH | $34723.08 | $0.01198 |

CoinGecko search returned hit(s): Blocksquare (BST) — still not proof of underlying-asset verification.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Physical asset cue: `estate property`
- Fractional ownership of underlying real-world assets (docs/marketing)

**What was actually confirmed here**

- Token eth_call identity confirmed on **ethereum** at `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` (BlocksquareToken/BST).
- DexScreener reports 2 pair(s) for the probed token (market context only).
- 20/22 research URLs reachable in this pass.
- Physical asset layer: `unverified`; economic right: `partially-verified` (`fractional_ownership`); revenue: `partially-verified`; payout: `unverified` (0 on-chain tx samples; 0 metadata records).
- **No** independently corroborated physical-asset identity (filings/registries) was confirmed.
- **No** machine-queryable payout/distribution surface with on-chain confirmation was established.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | Fractional ownership of underlying real-world assets (docs/marketing) | **no** |
| Token supply | matches eth_call | yes |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` | eth_call + market metadata | Identity / supply only |
| Distribution / Safe / vault | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Payout observability:** No verified payout/harvest event ABI + confirmed historical txs for this candidate’s underlying economics in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://blocksquare.io/tokenize/` | HTTP 200 — live (text/html) |
| `https://app.blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://blog.blocksquare.io/` | HTTP 200 — live (text/html) |
| `https://blocksquare.io/whitepaper` | HTTP 200 — live (text/html) |
| `https://blocksquare.io/whitepaper.pdf` | HTTP 200 — live (text/html) |
| `https://blocksquare.io/llm/blocksquare-llm-knowledge-base.html` | HTTP 200 — live (text/html) |
| `https://blocksquare.gitbook.io/blocksquare-docs/llms.txt` | HTTP 404: Not Found |
| `https://blocksquare.gitbook.io/blocksquare-docs/` | HTTP 404: Not Found |
| `https://blocksquare.gitbook.io/blocksquare-docs.md` | HTTP 200 — live (text/markdown) |
| `https://docs.blocksquare.io/research` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/about` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/press-kit` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/infrastructure/tokenization-protocol` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/infrastructure/marketplaces-platform` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/infrastructure/liquidity-engine` | HTTP 200 — live (text/html) |
| `https://docs.blocksquare.io/certified-partners/tokenization-service` | HTTP 200 — live (text/html) |
| `https://blog.blocksquare.io/article/blocksquare-heads-to-token-2049-week-to-connect-asian-capital-with-european-real-estate/` | HTTP 200 — live (text/html) |
| `https://blog.blocksquare.io/article/asian-investors-european-real-estate-tokenization/` | HTTP 200 — live (text/html) |
| `https://blog.blocksquare.io/article/security-tokens-real-estate-market-2034/` | HTTP 200 — live (text/html) |
| `https://blog.blocksquare.io/article/new-oceanpoint-tokenized-real-estate-platform/` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search returned hit(s): Blocksquare (BST) — still not proof of underlying-asset verification. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `app.blocksquare.io`, `blocksquare.gitbook.io`, `blocksquare.io`, `blog.blocksquare.io`, `docs.blocksquare.io`

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

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `token-data-only`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

TOKEN IDENTITY can be established (confidence=high; issuer-published=True; eth_call=True), but the TOKEN→ASSET→RIGHT→PAYOUT chain is incomplete (physical_asset=unverified, payout_mechanism=unverified). Tokn must not equate token identity with physical-asset ownership or realized yield.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), TOKEN IDENTITY: contract address is issuer-published + eth_call-verified, Public DEX market price/liquidity exists for the token

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions, Continuously verified production/revenue figures as facts

**Main blocker(s):** No specific physical asset identity established from research sources; No publicly reachable payout metadata, distribution contract, or verified payout transactions

**To move to the next state:** To become adapter-ready: independently corroborate the physical asset, establish the economic/legal right type, and publish a machine-queryable payout surface (distribution txs/events/API) that an adapter can poll. Token identity alone is insufficient.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | BST supply (docs or market) | ethereum `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` via `https://ethereum-rpc.publicnode.com` | blockchain | on-chain | ethereum eth_call → totalSupply() @ 0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | BlocksquareToken / BST / 18 | `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` on ethereum | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| TOKEN IDENTITY: contract address is issuer-published + eth_call-verified | BlocksquareToken / BST @ 0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a (ethereum); confidence=high | https://docs.blocksquare.io/about | official documentation | on-chain | Issuer-controlled source publishes address → infer chain → eth_call name()/symbol()/decimals()/totalSupply() → match candidate identity; DexScreener corroboration | verified | token identity fields / claims[] | — |
| PHYSICAL ASSET: underlying physical asset identity | estate property | n/a | official documentation | physical-world | Independent filings/registries naming the asset + economic context; NOT implied by ERC-20 identity | blocked | null / unavailable | No specific physical asset identity established from research sources |
| ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues | fractional_ownership | issuer research corpus | official documentation | physical-world | Independent filing and/or issuer legal/technical docs describing right type (royalty, revenue-swap, ownership, etc.) | partially-verified | claims[] / economic_right | Economic/legal right described in issuer materials only — independent legal corroboration missing |
| PAYOUT MECHANISM: machine-queryable investor distributions | 0 payout records; 0 on-chain verified; currency=unknown; frequency=unknown | n/a | official documentation | physical-world | Issuer-published payout metadata → eth_getTransaction(ByHash/Receipt) on the token's chain; or distribution contract events / public API | blocked | null / unavailable | No publicly reachable payout metadata, distribution contract, or verified payout transactions |
| REVENUE MECHANISM: how the physical asset generates revenue | described | https://blog.blocksquare.io/ | official documentation | physical-world | Operator/regulatory production disclosures or continuously queryable revenue APIs | partially-verified | claims[] (context) | Revenue mechanism described only by issuer; not independently queryable |
| Public DEX market price/liquidity exists for the token | price=$0.01178; liquidity_usd=48653.28 | DexScreener pair `0x0E85fB1be698E777F2185350b4A52E5eE8DF51A6` (ethereum/uniswap) | DEX/indexer | on-chain | GET DexScreener /latest/dex/tokens/{address} | observable | token_price (context only) / claims[] | — |
| DEX liquidity proves underlying-asset liquidity / backing | implied by marketing sometimes | DexScreener | DEX/indexer | self-reported | No valid verification — category error | blocked | null / unavailable | Market liquidity ≠ physical/underlying liquidity |
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
| physical_asset | unverified | none | No specific physical asset identity established from research sources |
| economic_right | partially-verified | medium | fractional_ownership |
| revenue_mechanism | partially-verified | low | Revenue mechanism described only by issuer; not independently queryable |
| payout_mechanism | unverified | none | records=0; onchain_sample=0; currency=n/a |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| ERC-20 getters | blockchain | `0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` on ethereum | eth_call name/symbol/decimals/totalSupply via `https://ethereum-rpc.publicnode.com` | identity + supply | on snapshot / daily | **required** — token identity |
| DEX market context | DEX/indexer | `https://api.dexscreener.com/latest/dex/tokens/0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a` | GET JSON pairs | price/liquidity context | optional cadence | **optional** — never as backing proof |
| Official page text | official documentation | `https://blocksquare.io/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://docs.blocksquare.io/` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://blocksquare.io/tokenize/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://app.blocksquare.io/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://blog.blocksquare.io/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://blocksquare.io/whitepaper` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
  researched_at: "2026-10-05T17:53Z"

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
    status: unverified
    confidence: none
    named_asset: ""
    blocker: "No specific physical asset identity established from research sources"
    evidence:
      []

  economic_right:
    status: partially-verified
    confidence: medium
    right_type: "fractional_ownership"
    blocker: "Economic/legal right described in issuer materials only — independent legal corroboration missing"
    evidence:
      - source: "issuer research corpus"
        tier: medium
        proves: "Issuer/docs language indicates `fractional_ownership`"
        reachable: true
        independently_verifiable: false

  revenue_mechanism:
    status: partially-verified
    confidence: low
    machine_queryable: false
    blocker: "Revenue mechanism described only by issuer; not independently queryable"
    evidence:
      - source: "https://blog.blocksquare.io/"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://docs.blocksquare.io/certified-partners/tokenization-service"
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
    - source: "ethereum:0x509A38b7a1cC0dcd83Aa9d06214663D9eC7c7F4a"
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
    - "No specific physical asset identity established from research sources"
    - "No publicly reachable payout metadata, distribution contract, or verified payout transactions"

  recommended_adapter_scope:
    - "ERC-20 identity (name/symbol/decimals)"
    - "totalSupply via eth_call"
    - "DEX market context (price/liquidity) as non-backing context"
    - "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"

  prohibited_outputs:
    - "Verified underlying-asset ownership / registry identity"
    - "Observed staking APY as a verified fact"
    - "Realized underlying revenue/yield distributions"
    - "Continuously verified production/revenue figures as facts"
```

---

## Appendix — reachable excerpts (truncated)

### `https://blocksquare.io/`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

### `https://docs.blocksquare.io/`

> Introduction / Blocksquare Docs Blocksquare Docs ⌘ Ctrl k Blocksquare Docs Introduction Research About Press Kit Infrastructure Tokenization protocol Marketplaces platform Liquidity engine Certified Partners Tokenization service Operating your marketplace Setup instructions Pricing Partner network Legal BST token ℹ️ Token overview 💹 Exchanges 📳 Price feeds ⚛️ Blocksquare DAO FAQ General questions Tokenization protocol Marketplace operators End users For Developers Revenue Distribution Contract Security Powered by GitBook On this page For the complete documentation index, see llms.txt . This pa

### `https://blocksquare.io/tokenize/`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

### `https://app.blocksquare.io/`

> Dashboard

### `https://blog.blocksquare.io/`

> / Blog Website All ℹ️ Updates 🦄 Oceanpoint 🗞 Interviews Regional Hubs Oceanpoint Prepares Instant Liquidity for Income-Producing European Real Estate New liquidity infrastructure is designed to connect stablecoin capital with tokenised real estate through a shared, real-yield liquidity layer Julia Buchholz · October 2, 2026 Blocksquare Heads to TOKEN2049 Week to Connect Asian Capital with European Real Estate Blocksquare will be in Singapore from October 5–10, 2026, offering investors, real estate businesses, and liquidity partners a closer look at new routes into tokenized property markets. J

### `https://blocksquare.io/whitepaper`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

### `https://blocksquare.io/whitepaper.pdf`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

### `https://blocksquare.io/llm/blocksquare-llm-knowledge-base.html`

> Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Built on Ethereum and IPFS, any single real estate property can be converted into 100,000 tokens, either partially or in full, providing investors a transparent and standardised digitalisation process. Blocksquare / Tokenization infrastructure for real estate.

