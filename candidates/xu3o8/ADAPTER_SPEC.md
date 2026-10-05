# xU3O8 — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Curated pipeline test: tokenized physical uranium (U3O8 / yellowcake) fractional ownership

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | xU3O8 |
| Slug | `xu3o8` |
| Issuer / brand (self-described) | xU3O8 |
| Seed hosts | `app.uranium.io`, `help.uranium.io`, `uranium.io` |

### Token / chain (live probe)

No ERC-20 (or equivalent) contract was confirmed via live `eth_call` in this pass for a token identity matching this project. Marketing may describe a token, but without a confirmed address + successful RPC getters, Tokn cannot treat token identity as verified.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

CoinGecko search returned hit(s): Uranium (XU3O8) — still not proof of underlying-asset verification.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Fractional ownership of underlying real-world assets (docs/marketing)

**What was actually confirmed here**

- 10/19 research URLs reachable in this pass.
- **No** independently queryable underlying-asset registry/ownership contract was confirmed.
- **No** independently queryable staking/profit/royalty distribution contract was confirmed.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | Fractional ownership of underlying real-world assets (docs/marketing) | **no** |
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
| `https://uranium.io/en` | HTTP 200 — live (text/html) |
| `https://help.uranium.io/en/articles/10110492-what-is-xu3o8` | HTTP 200 — live (text/html) |
| `https://help.uranium.io/en/articles/10711639-where-is-the-physical-uranium-ore-concentrate-u3o8-stored` | HTTP 200 — live (text/html) |
| `https://app.uranium.io/en/polygon` | HTTP 403: Forbidden |
| `https://uranium.io/` | HTTP 200 — live (text/html) |
| `https://docs.uranium.io/` | URL error: [Errno -2] Name or service not known |
| `https://app.uranium.io/` | HTTP 403: Forbidden |
| `https://blog.uranium.io/` | URL error: [Errno -2] Name or service not known |
| `https://uranium.io/whitepaper` | HTTP 200 — live (text/html) |
| `https://uranium.io/whitepaper.pdf` | HTTP 200 — live (application/pdf) |
| `https://uranium.io/llm/xu3o8-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://xu3o8.gitbook.io/xu3o8-docs/llms.txt` | HTTP 404: Not Found |
| `https://xu3o8.gitbook.io/xu3o8-docs/` | HTTP 404: Not Found |
| `https://xu3o8.gitbook.io/xu3o8-docs.md` | HTTP 404: Not Found |
| `https://help.uranium.io/en/articles/10222880-what-are-the-benefits-of-acquiring-u3o8-via-the-xu3o8-smart-contract` | HTTP 200 — live (text/html) |
| `https://help.uranium.io/en/articles/11604935-token-not-appearing-in-wallet-usdc-xu3o8` | HTTP 200 — live (text/html) |
| `https://uranium.io/en/whitepaper` | HTTP 200 — live (text/html) |
| `https://uranium.io/en/micar-whitepaper` | HTTP 200 — live (text/html) |
| `https://app.uranium.io/tokenize` | HTTP 403: Forbidden |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search returned hit(s): Uranium (XU3O8) — still not proof of underlying-asset verification. |
| Public EVM RPC eth_call | No successful project-matched token probe |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `app.uranium.io`, `help.uranium.io`, `uranium.io`

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

**Main blocker(s):** No independently confirmed token contract via eth_call; No issuer-published ownership/registry contract address for the underlying asset

**To move to the next state:** Publish contract addresses / public APIs for token identity and economic mechanism, then re-run the research agent.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fractional ownership of underlying real-world assets (docs/marketing) | As stated in official marketing/docs | Official website/docs | official website | physical-world | No verification method currently available | self-reported | claims[] ; underlying fields null until contracts exist | No public ownership/registry/distribution surface confirmed |

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
| Official page text | official documentation | `https://uranium.io/en` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://help.uranium.io/en/articles/10110492-what-is-xu3o8` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://help.uranium.io/en/articles/10711639-where-is-the-physical-uranium-ore-concentrate-u3o8-stored` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://uranium.io/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://uranium.io/whitepaper` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://uranium.io/whitepaper.pdf` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
  status: blocked
  researched_at: "2026-10-05T12:29Z"

  token_verification:
    available: false

  underlying_asset_verification:
    available: false

  economic_mechanism_verification:
    available: false

  market_data:
    available: false

  independent_sources:
    available: true
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
    - "No independently confirmed token contract via eth_call"
    - "No issuer-published ownership/registry contract address for the underlying asset"

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

### `https://uranium.io/en`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Invest in uranium / U3O8 / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Buy Own Trade uranium xU3O8 powers your ownership and trading of physical uranium (U3O8) Buy Uranium Powered by Featured in Featured in Power your portfolio with uranium (Value of $100 invested) S&P 500 vs uranium Returns (2020-2025) Spot uranium S&P 500 *since September 2020 until September 2025 (172.5% vs. 9

### `https://help.uranium.io/en/articles/10110492-what-is-xu3o8`

> What is xU3O8? / xU3O8 Help Center Skip to main content Search for articles... All Collections General Questions What is xU3O8? What is xU3O8? December 2, 2024 xU3O8 enables investors to own and trade U3O8 in an investment friendly and transparent manner by administering fractional ownership of physical uranium in the form of a smart contract ledger. Each xU3O8 represents a unit of ownership of U3O8 held by Archax as a custodian for investors. This novel blockchain-based ownership register leverages Tezos blockchain technology and key third parties to provide direct ownership of physical urani

### `https://help.uranium.io/en/articles/10711639-where-is-the-physical-uranium-ore-concentrate-u3o8-stored`

> Where is the physical uranium ore concentrate (U3O8) stored? / xU3O8 Help Center Skip to main content Search for articles... All Collections General Questions Where is the physical uranium ore concentrate (U3O8) stored? Where is the physical uranium ore concentrate (U3O8) stored? March 5, 2025 The physical uranium ore concentrate (U3O8) is securely stored at regulated storage facility, operated by Cameco, one of the three globally recognized uranium conversion and storage providers. The uranium is held in the account of Archax Ltd, acting as trustee. Any additional uranium ore concentrate purc

### `https://uranium.io/`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Invest in uranium / U3O8 / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Buy Own Trade uranium xU3O8 powers your ownership and trading of physical uranium (U3O8) Buy Uranium Powered by Featured in Featured in Power your portfolio with uranium (Value of $100 invested) S&P 500 vs uranium Returns (2020-2025) Spot uranium S&P 500 *since September 2020 until September 2025 (172.5% vs. 9

### `https://uranium.io/whitepaper`

> xU3O8 powers your ownership and trading of physical uranium (U3O8) Whitepaper / Invest in uranium / Powered by Tezos, Archax and Curzon uranium x Uranium.io is evolving into Metals.io! Commodities trading evolved Why invest Learn Borrow Help Buy Uranium Why invest Learn Borrow Help Buy Uranium Learn / Whitepaper Resources Proof of Reserves Whitepaper MiCAR Whitepaper Help Center Learn Tokenize Uranium Redeem Uranium Legal Privacy & Cookie Policy Terms of Service © 2026 English Powered by

### `https://uranium.io/whitepaper.pdf`

> [PDF reachable — 200000 bytes fetched; binary not fully text-extracted by this agent]

### `https://help.uranium.io/en/articles/10222880-what-are-the-benefits-of-acquiring-u3o8-via-the-xu3o8-smart-contract`

> What are the benefits of acquiring U3O8 via the xU3O8 smart contract? / xU3O8 Help Center Skip to main content Search for articles... All Collections General Questions What are the benefits of acquiring U3O8 via the xU3O8 smart contract? What are the benefits of acquiring U3O8 via the xU3O8 smart contract? December 2, 2024 Direct uranium ownership via the blockchain powered market infrastructure has the advantage of representing legal ownership of physically allocated uranium but does not have the limitations of minimum purchase amount, lack of transparency, restricted trading hours, and high

### `https://help.uranium.io/en/articles/11604935-token-not-appearing-in-wallet-usdc-xu3o8`

> Token not appearing in wallet (USDC, xU3O8) / xU3O8 Help Center Skip to main content Search for articles... All Collections Troubleshooting Token not appearing in wallet (USDC, xU3O8) Token not appearing in wallet (USDC, xU3O8) June 19, 2025 Table of contents Third-party wallets do not always detect and display all tokens automatically. If USDC or xU3O8 is missing, you may need to add it manually or use the automatic import option via the Uranium app. Common Causes The token has not yet been recognized by the wallet interface The wallet may be experiencing a sync delay There may be a display i

