# RealX — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-06
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Coverage test: RealX Investment Token (Thailand SEC-approved) — tokenized luxury Bangkok real-estate (Park Origin properties)

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | RealX |
| Slug | `realx` |
| Issuer / brand (self-described) | RealX |
| Seed hosts | `market.sec.or.th`, `realx.gitbook.io`, `realxtoken.finance`, `static.tokenx.finance`, `tokenx.finance` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | bsc |
| Token contract | `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` |
| `name()` | `HF RealX` |
| `symbol()` | `HF` |
| `decimals()` | `18` |
| `totalSupply()` | 10,000,000,000 token units (raw `10000000000000000000000000000`) |
| RPC used | `https://bsc-rpc.publicnode.com` |
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
| bsc / pancakeswap | `0xb29c2336d225fD72Ff00fd3eB4A095f7b39367aE` | HF / USDT | $11009.33 | $0.0003766 |

CoinGecko search returned hit(s): HF RealX (HF) — still not proof of underlying-asset verification.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Physical asset cue: `Origin Property`
- Fractional ownership of underlying real-world assets (docs/marketing)

**What was actually confirmed here**

- Token eth_call identity confirmed on **bsc** at `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` (HF RealX/HF).
- DexScreener reports 1 pair(s) for the probed token (market context only).
- 15/33 research URLs reachable in this pass.
- Physical asset layer: `partially-verified` (`realxtoken`); economic right: `partially-verified` (`fractional_ownership`); revenue: `unverified`; payout: `unverified` (0 on-chain tx samples; 0 metadata records).
- **No** independently corroborated physical-asset identity (filings/registries) was confirmed.
- **No** machine-queryable payout/distribution surface with on-chain confirmation was established.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | Fractional ownership of underlying real-world assets (docs/marketing) | **no** |
| Token supply | Total Supply 13,186,813 Tokens Market Cap 2,400 MB The value of this fundraising is 2,400 million baht at the Initial Coin Offering; ICO price. | yes |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` | eth_call + market metadata | Identity / supply only |
| Distribution / Safe / vault | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Payout observability:** No verified payout/harvest event ABI + confirmed historical txs for this candidate’s underlying economics in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://realxtoken.finance/en` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/assets` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/investor` | HTTP 200 — live (text/html) |
| `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf` | HTTP 200 — live (application/pdf) |
| `https://market.sec.or.th/public/ipos/IPOSTD01.aspx?TransID=494728&lang=en` | HTTP 200 — live (text/html) |
| `https://or.th/` | URL error: [Errno -5] No address associated with hostname |
| `https://docs.or.th/` | URL error: [Errno -2] Name or service not known |
| `https://app.or.th/` | URL error: [Errno -2] Name or service not known |
| `https://blog.or.th/` | URL error: [Errno -2] Name or service not known |
| `https://or.th/whitepaper` | URL error: [Errno -5] No address associated with hostname |
| `https://or.th/whitepaper.pdf` | URL error: [Errno -5] No address associated with hostname |
| `https://or.th/llm/realx-llm-knowledge-base.html` | URL error: [Errno -5] No address associated with hostname |
| `https://realx.gitbook.io/realx-docs/llms.txt` | HTTP 404: Not Found |
| `https://realx.gitbook.io/realx-docs/` | HTTP 404: Not Found |
| `https://realxtoken.finance/` | HTTP 200 — live (text/html) |
| `https://docs.realxtoken.finance/` | URL error: [Errno -2] Name or service not known |
| `https://app.realxtoken.finance/` | URL error: [Errno -2] Name or service not known |
| `https://blog.realxtoken.finance/` | URL error: [Errno -2] Name or service not known |
| `https://realxtoken.finance/whitepaper` | HTTP 404: Not Found |
| `https://realxtoken.finance/whitepaper.pdf` | HTTP 404: Not Found |
| `https://realxtoken.finance/llm/realx-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://tokenx.finance/` | HTTP 200 — live (text/html) |
| `https://docs.tokenx.finance/` | URL error: [Errno -5] No address associated with hostname |
| `https://app.tokenx.finance/` | URL error: [Errno -5] No address associated with hostname |
| `https://blog.tokenx.finance/` | URL error: [Errno -5] No address associated with hostname |
| `https://tokenx.finance/whitepaper` | HTTP 200 — live (text/html) |
| `https://tokenx.finance/whitepaper.pdf` | HTTP 200 — live (text/html) |
| `https://tokenx.finance/llm/realx-llm-knowledge-base.html` | HTTP 200 — live (text/html) |
| `https://realx.gitbook.io/realx-docs.md` | HTTP 200 — live (text/markdown) |
| `https://realxtoken.finance/en/hhr` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/faq` | HTTP 200 — live (text/html) |
| `https://realxtoken.finance/en/contact` | HTTP 200 — live (text/html) |
| `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf?fbclid=IwAR3EEpEfyCYjNpIoeymxLkPorviMX23X-9w5Ps2nby61RHaJJDyKnYqCPZE` | HTTP 200 — live (application/pdf) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search returned hit(s): HF RealX (HF) — still not proof of underlying-asset verification. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `market.sec.or.th`, `realx.gitbook.io`, `realxtoken.finance`, `static.tokenx.finance`, `tokenx.finance`

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

TOKEN IDENTITY can be established (confidence=high; issuer-published=False; eth_call=True), but the TOKEN→ASSET→RIGHT→PAYOUT chain is incomplete (physical_asset=partially-verified, payout_mechanism=unverified). Tokn must not equate token identity with physical-asset ownership or realized yield.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), Public DEX market price/liquidity exists for the token

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions, Continuously verified production/revenue figures as facts

**Main blocker(s):** Physical asset named only in issuer materials — no independent filing/registry corroboration; No publicly reachable payout metadata, distribution contract, or verified payout transactions

**To move to the next state:** To become adapter-ready: independently corroborate the physical asset, establish the economic/legal right type, and publish a machine-queryable payout surface (distribution txs/events/API) that an adapter can poll. Token identity alone is insufficient.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | Total Supply 13,186,813 Tokens Market Cap 2,400 MB The value of this fundraising is 2,400 million baht at the Initial Coin Offering; ICO price. | bsc `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` via `https://bsc-rpc.publicnode.com` | blockchain | on-chain | bsc eth_call → totalSupply() @ 0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177 | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | HF RealX / HF / 18 | `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` on bsc | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| TOKEN IDENTITY: contract address is issuer-published + eth_call-verified | HF RealX / HF @ 0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177 (bsc); confidence=high | DexScreener / research text | DEX/indexer | on-chain | Issuer-controlled source publishes address → infer chain → eth_call name()/symbol()/decimals()/totalSupply() → match candidate identity; DexScreener corroboration | partially-verified | token identity fields / claims[] | Address provenance is market/indexer-attributed rather than issuer-published; token identity still eth_call-matched |
| PHYSICAL ASSET: underlying physical asset identity | realxtoken | https://realxtoken.finance/en | official documentation | physical-world | Independent filings/registries naming the asset + economic context; NOT implied by ERC-20 identity | partially-verified | underlying_asset | Physical asset named only in issuer materials — no independent filing/registry corroboration |
| ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues | fractional_ownership | issuer research corpus | official documentation | physical-world | Independent filing and/or issuer legal/technical docs describing right type (royalty, revenue-swap, ownership, etc.) | partially-verified | claims[] / economic_right | Economic/legal right described in issuer materials only — independent legal corroboration missing |
| PAYOUT MECHANISM: machine-queryable investor distributions | 0 payout records; 0 on-chain verified; currency=unknown; frequency=unknown | n/a | official documentation | physical-world | Issuer-published payout metadata → eth_getTransaction(ByHash/Receipt) on the token's chain; or distribution contract events / public API | blocked | null / unavailable | No publicly reachable payout metadata, distribution contract, or verified payout transactions |
| REVENUE MECHANISM: how the physical asset generates revenue | not established | n/a | official documentation | physical-world | Operator/regulatory production disclosures or continuously queryable revenue APIs | unverified | null / unavailable | No revenue-generation mechanism identified |
| Public DEX market price/liquidity exists for the token | price=$0.0003766; liquidity_usd=11009.33 | DexScreener pair `0xb29c2336d225fD72Ff00fd3eB4A095f7b39367aE` (bsc/pancakeswap) | DEX/indexer | on-chain | GET DexScreener /latest/dex/tokens/{address} | observable | token_price (context only) / claims[] | — |
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
| Revenue generation / leases / harvests | NO |
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
| physical_asset | partially-verified | medium | realxtoken |
| economic_right | partially-verified | medium | fractional_ownership |
| revenue_mechanism | unverified | none | No revenue-generation mechanism identified |
| payout_mechanism | unverified | none | records=0; onchain_sample=0; currency=n/a |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| ERC-20 getters | blockchain | `0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` on bsc | eth_call name/symbol/decimals/totalSupply via `https://bsc-rpc.publicnode.com` | identity + supply | on snapshot / daily | **required** — token identity |
| DEX market context | DEX/indexer | `https://api.dexscreener.com/latest/dex/tokens/0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177` | GET JSON pairs | price/liquidity context | optional cadence | **optional** — never as backing proof |
| Official page text | official documentation | `https://realxtoken.finance/en` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://realxtoken.finance/en/assets` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://realxtoken.finance/en/investor` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://market.sec.or.th/public/ipos/IPOSTD01.aspx?TransID=494728&lang=en` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://realxtoken.finance/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
    issuer_published_address: false
    chain_established: true
    eth_call_verified: true
    metadata_match: true
    market_corroboration: true
    note: "Token identity ≠ asset backing ≠ economic/payout verification"

  physical_asset:
    status: partially-verified
    confidence: medium
    named_asset: "realxtoken"
    blocker: "Physical asset named only in issuer materials — no independent filing/registry corroboration"
    evidence:
      - source: "https://realxtoken.finance/en"
        tier: medium
        proves: "Issuer materials name a specific physical asset"
        reachable: true
        independently_verifiable: false

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
    status: unverified
    confidence: none
    machine_queryable: false
    blocker: "No revenue-generation mechanism identified"
    evidence:
      []

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
    - source: "bsc:0x2CB469f8Af300A9ebDC10f06F6b81bE3B814F177"
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

### `https://realxtoken.finance/en`

> RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN REALX INVESTMENT TOKEN THE REAL ESTATE BACKED TOKEN Whitepaper Introducing RealX Investment Token is the First Asset-Backed Token in Thailand under the approval of the Security Exchange and Commissions of Thailand (SEC) and fully complies with the relevant regulations surrounding this nascent industry. RealX has raised over $60+ million during its fundraising period for the purpose of asset acquisition and tokenization, of which a total of 13,186,813 RealX Tokens are then minted in a near 1:1 ratio of the total sq.m of assets acqu

### `https://realxtoken.finance/en/assets`

> Assets - RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN Underlying Assets Totaling 244 rooms The underlying assets, namely Park Origin Promphong, Park Origin Thonglor, and Park Origin Phayathai, are assets located in the prime areas of Bangkok with a proven track record and are sought after by the market. Investment Proportion 27.46% Calculate as 67 Rooms Investment Proportion 38.11% Calculate as 93 Rooms Investment Proportion 27.46% Calculate as 84 Rooms The last, most distinguished 10-rai piece of nature of elite residential living, located right in the heart of Sukhumvit So

### `https://realxtoken.finance/en/investor`

> RealX Home Assets Investor HHR Whitepaper FAQ Contact us ไทย EN Real Estate Exponential Co., Ltd. @RealXToken [email protected] 989 Siam Piwat Tower Floor 12A Rama I Rd. Pathumwan, Bangkok, 10330 Home Investor Whitepaper Contact us Assets HHR FAQ Privacy Policy Copyright © 2026 Real Estate Exponential Co., Ltd.

### `https://static.tokenx.finance/projects/realx/RealX_Whitepaper_Revised_230731_2.pdf`

> [PDF reachable — 200000 bytes fetched; binary not fully text-extracted by this agent]

### `https://market.sec.or.th/public/ipos/IPOSTD01.aspx?TransID=494728&lang=en`

> Digital Token Prospectus {1} ##LOC[OK]## {1} ##LOC[OK]## ##LOC[Cancel]## {1} ##LOC[OK]## ##LOC[Cancel]## Digital Token Detail Digital Token Name : RealX Investment Token Digital Token Issuer : REAL ESTATE EXPONENTIAL COMPANY LIMITED Filing Acknowledge Date : 04/01/2023 Filing First Date : 20/03/2023 Effective Date : 19/06/2023 Sell Begin Date : 01/07/2023 Sell End Date : 31/08/2023 Digital Token Type : Token Digital for investment Offering Type : Initial Coin Offering ICO Portal : TOKEN X COMPANY LIMITED Digital Token Filing Subject Filing First Version Filing Final Version Download all docume

### `https://realxtoken.finance/`

> RealX หน้าหลัก ทรัพย์สิน นักลงทุนสัมพันธ์ แฮมตัน หนังสือชี้ชวน คำถามที่พบบ่อย ติดต่อเรา ไทย EN โทเคนดิจิทัลเพื่อการลงทุนเรียลเอ็กซ์ โทเคนดิจิทัลเพื่อการลงทุนที่มีอสังหาริมทรัพย์เป็นสินทรัพย์อ้างอิง Whitepaper การแนะนำ โทเคนดิจิทัลเพื่อการลงทุนเรียลเอ็กซ์ เป็นโทเคนดิจิทัลเพื่อการลงทุน (Investment Token) ที่มีจุดประสงค์เพื่อนำเงินที่ได้จากการระดมทุน ไปลงทุนเพื่อให้ได้มาซึ่งกระแสรายรับจากห้องชุดบางส่วนของโครงการ พาร์ค ออริจิ้น พร้อมพงษ์ พาร์ค ออริจิ้น พญาไท และพาร์ค ออริจิ้น ทองหล่อ ซึ่งได้รับความเห็นชอบจาก สำนักงานคณะกรรมการกำกับหลักทรัพย์และตลาดหลักทรัพย์ (ก.ล.ต.) ถูกต้องตามกฎหมาย สำหรับรายละเอ

### `https://tokenx.finance/`

> Token X is an ICO Portal providing end-to-end tokenization services. From innovative fund-raising solutions through digital tokens to ready-to-use tokenization tools & blockchain protocols (TKX Chain), we got it all. *We are a regulated identity under The Securities and Exchange Commission (SEC). Token X is an ICO Portal providing end-to-end tokenization services. From innovative fund-raising solutions through digital tokens to ready-to-use tokenization tools & blockchain protocols (TKX Chain), we got it all. *We are a regulated identity under The Securities and Exchange Commission (SEC). Toke

### `https://tokenx.finance/whitepaper`

> Token X is an ICO Portal providing end-to-end tokenization services. From innovative fund-raising solutions through digital tokens to ready-to-use tokenization tools & blockchain protocols (TKX Chain), we got it all. *We are a regulated identity under The Securities and Exchange Commission (SEC). Token X is an ICO Portal providing end-to-end tokenization services. From innovative fund-raising solutions through digital tokens to ready-to-use tokenization tools & blockchain protocols (TKX Chain), we got it all. *We are a regulated identity under The Securities and Exchange Commission (SEC). Toke

