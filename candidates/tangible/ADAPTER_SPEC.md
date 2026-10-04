# Tangible — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-04
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Tokenized physical luxury / real-world asset marketplace

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | Tangible |
| Slug | `tangible` |
| Issuer / brand (self-described) | Tangible |
| Seed hosts | `discord.gg`, `docs.tangible.store`, `tangible.gitbook.io`, `tangible.store`, `www.tangible.store` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | polygon |
| Token contract | `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` |
| `name()` | `Tangible` |
| `symbol()` | `TNGBL` |
| `decimals()` | `18` |
| `totalSupply()` | 33,239,046 token units (raw `33239046220193681475092859`) |
| RPC used | `https://polygon-bor-rpc.publicnode.com` |

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| polygon / uniswap | `0xDC8a5c5975726235402cFac9B28268EEccd42813` | TNGBL / DAI | $23.89 | $0.4388 |

CoinGecko search returned hit(s): Tangible (TNGBL) — still not proof of underlying-asset verification.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Official pages describe a capital-style product; see excerpts.

**What was actually confirmed here**

- Token eth_call identity confirmed on **polygon** at `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` (Tangible/TNGBL).
- DexScreener reports 1 pair(s) for the probed token (market context only).
- 15/21 research URLs reachable in this pass.
- **No** independently queryable underlying-asset registry/ownership contract was confirmed.
- **No** independently queryable staking/profit/royalty distribution contract was confirmed.

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
| Primary token (probed) | `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` | eth_call + market metadata | Identity / supply only |
| Ownership / asset registry | **Not confirmed** | Docs may describe; address not verified | Required for underlying claims — blocked unless published |
| Staking / rewards | **Not confirmed** | Docs may describe; address not verified | Required for APY observation — blocked unless published |
| Profit / royalty distribution | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Events:** No verified payout/harvest event ABI + public indexer endpoint for
this candidate’s underlying economics was confirmed in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://www.tangible.store/` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/` | HTTP 200 — live (text/html) |
| `https://www.tangible.store/marketplace` | HTTP 404: Not Found |
| `https://tangible.store/` | HTTP 200 — live (text/html) |
| `https://app.tangible.store/` | URL error: [Errno -2] Name or service not known |
| `https://blog.tangible.store/` | URL error: [Errno -2] Name or service not known |
| `https://tangible.store/whitepaper` | HTTP 404: Not Found |
| `https://tangible.store/whitepaper.pdf` | HTTP 404: Not Found |
| `https://tangible.store/llm/tangible-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://tangible.gitbook.io/tangible-docs/llms.txt` | HTTP 200 — live (text/html) |
| `https://tangible.gitbook.io/tangible-docs/` | HTTP 200 — live (text/html) |
| `https://tangible.gitbook.io/tangible-docs.md` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/rwa-tngbl-token` | HTTP 200 — live (text/html) |
| `https://discord.gg/realrwa` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/legal` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/technical` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/audits-and-security` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/contracts-and-addresses` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/re.al-network-details` | HTTP 200 — live (text/html) |
| `https://docs.tangible.store/protocol-overview/protocol-guides-and-videos` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search returned hit(s): Tangible (TNGBL) — still not proof of underlying-asset verification. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `discord.gg`, `docs.tangible.store`, `tangible.gitbook.io`, `tangible.store`, `www.tangible.store`

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

Token-level (and possibly market) facts can be independently queried, but the underlying real-world / economic mechanism claims lack published, queryable contracts or independent attestations. Tokn must not equate token verification with infrastructure verification.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), Public DEX market price/liquidity exists for the token

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions

**Main blocker(s):** No issuer-published ownership/registry contract address for the underlying asset

**To move to the next state:** To become adapter-ready: issuer-published ownership/registry and/or payout-distribution contracts (or an equivalent public attestation API) that connect the token to specific underlying assets and cashflows.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | TNGBL supply (docs or market) | polygon `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` via `https://polygon-bor-rpc.publicnode.com` | blockchain | on-chain | polygon eth_call → totalSupply() @ 0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007 | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | Tangible / TNGBL / 18 | `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` on polygon | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| Contract address is issuer-published | 0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007 | DexScreener metadata match and/or docs (see research) | DEX/indexer | on-chain | Compare issuer docs address list to probed address; if docs omit address, provenance is only market metadata | partially-verified | claims[] (provenance note) | Issuer docs may not publish the address; treat DexScreener attribution as supporting until docs confirm |
| Public DEX market price/liquidity exists for the token | price=$0.4388; liquidity_usd=23.89 | DexScreener pair `0xDC8a5c5975726235402cFac9B28268EEccd42813` (polygon/uniswap) | DEX/indexer | on-chain | GET DexScreener /latest/dex/tokens/{address} | observable | token_price (context only) / claims[] | — |
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
| ERC-20 getters | blockchain | `0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` on polygon | eth_call name/symbol/decimals/totalSupply via `https://polygon-bor-rpc.publicnode.com` | identity + supply | on snapshot / daily | **required** — token identity |
| DEX market context | DEX/indexer | `https://api.dexscreener.com/latest/dex/tokens/0x49e6A20f1BBdfEeC2a8222E052000BbB14EE6007` | GET JSON pairs | price/liquidity context | optional cadence | **optional** — never as backing proof |
| Official page text | official documentation | `https://www.tangible.store/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://docs.tangible.store/` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://tangible.store/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://tangible.gitbook.io/tangible-docs/llms.txt` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://tangible.gitbook.io/tangible-docs/` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |
| Official page text | official documentation | `https://tangible.gitbook.io/tangible-docs.md` | HTTP GET + text extract | claim language / product description | on research refresh | **required** for claims[] sourcing (self-reported) |

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
  researched_at: "2026-10-04T10:47Z"

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

### `https://www.tangible.store/`

> Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible / Crypto’s Leading Tokenization Protocol Migrate 3,3+ NFT TNGBL CVR Read more DECENTRALIZED ACCESS TO TOKENIZED REAL WORLD ASSETS Earn consistent, reliable yield from low-volatility off-chain sources Innovative tokens with deep liquidity Tangible blends DeFi composability with real yield generated from off-chain sources, providing permissionless access

### `https://docs.tangible.store/`

> General / Tangible v2 Tangible v2 ⌘ Ctrl k Tangible v2 Protocol Overview General Legal Technical Audits & Security RWA (TNGBL) Token Contracts & Addresses re.al Network Details Protocol Guides and Videos Archive Asset Categories Real Estate Gold Baskets Overview Why Tokenized Real Estate? Design Technical FAQs Contracts & Addresses USTB USTB Token USTB Yield Backing Asset: USDM Powered by GitBook On this page For the complete documentation index, see llms.txt . This page is also available as Markdown . Copy On this page Protocol Overview General What is Tangible? Tangible is a tokenization pro

### `https://tangible.store/`

> Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible brings a tokenized RWAs cross-chain. Mint and redeem on re.al, bridge to deep liquidity on AMMs across DeFi. Tangible / Crypto’s Leading Tokenization Protocol Migrate 3,3+ NFT TNGBL CVR Read more DECENTRALIZED ACCESS TO TOKENIZED REAL WORLD ASSETS Earn consistent, reliable yield from low-volatility off-chain sources Innovative tokens with deep liquidity Tangible blends DeFi composability with real yield generated from off-chain sources, providing permissionless access

### `https://tangible.gitbook.io/tangible-docs/llms.txt`

> <!DOCTYPE html><html lang="en" class="notranslate" translate="no"><head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>GitBook</title> <link rel="manifest" href="/public/manifest.json"> <link rel="icon" sizes="512x512" href="/public/images/icon-512.png" media="(prefers-color-scheme: light)"> <link rel="icon" sizes="512x512" href="/public/images/icon-512-dark.png" media="(prefers-color-scheme: dark)"> <link rel="apple-touch-icon" sizes="512x512" href="/public/images/icon-ios/icon_512x512.png"> <link rel="apple-touch-icon" sizes="512x512@2x"

### `https://tangible.gitbook.io/tangible-docs/`

> GitBook GitBook

### `https://tangible.gitbook.io/tangible-docs.md`

> <!DOCTYPE html><html lang="en" class="notranslate" translate="no"><head> <meta charset="UTF-8"> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <title>GitBook</title> <link rel="manifest" href="/public/manifest.json"> <link rel="icon" sizes="512x512" href="/public/images/icon-512.png" media="(prefers-color-scheme: light)"> <link rel="icon" sizes="512x512" href="/public/images/icon-512-dark.png" media="(prefers-color-scheme: dark)"> <link rel="apple-touch-icon" sizes="512x512" href="/public/images/icon-ios/icon_512x512.png"> <link rel="apple-touch-icon" sizes="512x512@2x"

### `https://docs.tangible.store/protocol-overview/rwa-tngbl-token`

> RWA (TNGBL) Token / Tangible v2 Tangible v2 ⌘ Ctrl k Tangible v2 Protocol Overview General Legal Technical Audits & Security RWA (TNGBL) Token Contracts & Addresses re.al Network Details Protocol Guides and Videos Archive Asset Categories Real Estate Gold Baskets Overview Why Tokenized Real Estate? Design Technical FAQs Contracts & Addresses USTB USTB Token USTB Yield Backing Asset: USDM Powered by GitBook On this page For the complete documentation index, see llms.txt . This page is also available as Markdown . Copy On this page Protocol Overview RWA (TNGBL) Token Background The TNGBL token w

### `https://discord.gg/realrwa`

> Check out the Arcana 𝚫 community on Discord - hang out with 170 other members and enjoy free voice and text chat. Check out the Arcana 𝚫 community on Discord - hang out with 170 other members and enjoy free voice and text chat. Arcana 𝚫

