# RealX — individual property — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Curated pipeline test: RealX named/individual property FRAX tokens (India)

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | RealX — individual property |
| Slug | `realx-individual-property` |
| Issuer / brand (self-described) | RealX — individual property |
| Seed hosts | `realx.in`, `wassup.realx.in`, `www.deloitte.com` |

### Token / chain (live probe)

No ERC-20 (or equivalent) contract was confirmed via live `eth_call` in this pass for a token identity matching this project. Marketing may describe a token, but without a confirmed address + successful RPC getters, Tokn cannot treat token identity as verified.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

CoinGecko search API returned **zero** coins for query `RealX — individual property` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Fractional ownership of underlying real-world assets (docs/marketing)

**What was actually confirmed here**

- 8/18 research URLs reachable in this pass.
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
| `https://realx.in/` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/real-estate-tokenization-india-guide/` | HTTP 200 — live (text/html) |
| `https://docs.realx.in/` | URL error: [Errno -2] Name or service not known |
| `https://app.realx.in/` | URL error: [Errno -2] Name or service not known |
| `https://blog.realx.in/` | URL error: [Errno 101] Network is unreachable |
| `https://realx.in/whitepaper` | HTTP 404: Not Found |
| `https://realx.in/whitepaper.pdf` | HTTP 404: Not Found |
| `https://realx.in/llm/realx-individual-property-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://realxindividualproperty.gitbook.io/realxindividualproperty-docs/llms.txt` | HTTP 404: Not Found |
| `https://realxindividualproperty.gitbook.io/realxindividualproperty-docs/` | HTTP 404: Not Found |
| `https://realxindividualproperty.gitbook.io/realxindividualproperty-docs.md` | HTTP 404: Not Found |
| `https://wassup.realx.in/asset-tokenization-india-fintech-revolution/` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/nandan-nilekanis-vision-indias-roadmap-for-real-estate-tokenization/` | HTTP 200 — live (text/html) |
| `https://www.weforum.org/stories/2025/01/cryptocurrency-regulations-era-experts-digital-finance/#:~:text=How%20is%20the%20World%20Economic,tokenization%20to%20improve%20financial%20systems.` | HTTP 403: Forbidden |
| `https://www.deloitte.com/us/en/insights/industry/financial-services/financial-services-industry-predictions/2025/tokenized-real-estate.html` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/real-estate-tokenization-india-guide/#comments` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/real-estate-tokenization-india-guide/#comment-10` | HTTP 200 — live (text/html) |
| `https://wassup.realx.in/real-estate-tokenization-india-guide/#comment-21` | HTTP 200 — live (text/html) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search API returned **zero** coins for query `RealX — individual property` in this pass — no independent CoinGecko listing confirmed. |
| Public EVM RPC eth_call | No successful project-matched token probe |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `realx.in`, `wassup.realx.in`, `www.deloitte.com`

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
| Official page text | official documentation | `https://realx.in/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://wassup.realx.in/real-estate-tokenization-india-guide/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://wassup.realx.in/asset-tokenization-india-fintech-revolution/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://wassup.realx.in/nandan-nilekanis-vision-indias-roadmap-for-real-estate-tokenization/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://www.deloitte.com/us/en/insights/industry/financial-services/financial-services-industry-predictions/2025/tokenized-real-estate.html` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://wassup.realx.in/real-estate-tokenization-india-guide/#comments` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
  researched_at: "2026-10-05T12:30Z"

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

### `https://realx.in/`

> RealX Marketplace - we are obsessed with bringing quality investment opportunities to everyone. We have broken the access barrier and brought this down, so everyone can digitally invest in quality Real Estate RealX Marketplace - we are obsessed with bringing quality investment opportunities to everyone. We have broken the access barrier and brought this down, so everyone can digitally invest in quality Real Estate RealX

### `https://wassup.realx.in/real-estate-tokenization-india-guide/`

> Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Real Estate Tokenization In India: Investor’s Complete Guide Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey December 6, 2025 April 23, 2026 Real Estate Tokenization Explained: A New Era of Fractional Ownership in India 2026 Introduction: Why Indian Investors Are Struggling t

### `https://wassup.realx.in/asset-tokenization-india-fintech-revolution/`

> Discover how asset tokenization is transforming real estate, gold and wealth ownership in India through blockchain, fintech innovation and regulated digital assets. Discover how asset tokenization is transforming real estate, gold and wealth ownership in India through blockchain, fintech innovation and regulated digital assets. Asset Tokenization In India: Fintech’s Ownership Revolution Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey November 24, 2025 April 23, 2026 The Next Fintech Giant Leap: How Asset Tokenization Will Redefi

### `https://wassup.realx.in/nandan-nilekanis-vision-indias-roadmap-for-real-estate-tokenization/`

> In the late 19th century, when railroads first spread across America, skeptics wondered if anyone would willingly travel faster than a horse could gallop. But In the late 19th century, when railroads first spread across America, skeptics wondered if anyone would willingly travel faster than a horse could gallop. But Nandan Nilekani’s Vision: India's Roadmap For Real Estate Tokenization - Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Arpit Gosain April 7, 2025 April 23, 2026 Nandan Nilekani’s Vision: India’s Roadmap for Real Estate Tokenization

### `https://www.deloitte.com/us/en/insights/industry/financial-services/financial-services-industry-predictions/2025/tokenized-real-estate.html`

> The global market for tokenized real estate is expected to expand dramatically by 2035. Here&#39;s how a few players are making waves. The global market for commercial real estate tokenization is expected to expand dramatically by 2035. Here’s how a few players are making waves. Tokenized real estate / Deloitte Insights Skip to main content Deloitte Insights and our research centers deliver proprietary research designed to help organizations turn their aspirations into action. DELOITTE INSIGHTS Home Spotlight Digital Media Trends FSI Predictions Human Capital Trends Tech Trends TMT Predictions

### `https://wassup.realx.in/real-estate-tokenization-india-guide/#comments`

> Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Real Estate Tokenization In India: Investor’s Complete Guide Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey December 6, 2025 April 23, 2026 Real Estate Tokenization Explained: A New Era of Fractional Ownership in India 2026 Introduction: Why Indian Investors Are Struggling t

### `https://wassup.realx.in/real-estate-tokenization-india-guide/#comment-10`

> Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Real Estate Tokenization In India: Investor’s Complete Guide Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey December 6, 2025 April 23, 2026 Real Estate Tokenization Explained: A New Era of Fractional Ownership in India 2026 Introduction: Why Indian Investors Are Struggling t

### `https://wassup.realx.in/real-estate-tokenization-india-guide/#comment-21`

> Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Learn how real estate tokenization in India works, and discover how platforms like RealX enable secure property token ownership. Real Estate Tokenization In India: Investor’s Complete Guide Skip to content Menu Home FAQs Explore RealX How It works Why RealX About Us Login / Signup by: Saurabh Kumar Dey December 6, 2025 April 23, 2026 Real Estate Tokenization Explained: A New Era of Fractional Ownership in India 2026 Introduction: Why Indian Investors Are Struggling t

