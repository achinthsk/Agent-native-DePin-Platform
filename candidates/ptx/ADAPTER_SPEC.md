# PTX — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-05
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: Named mining-royalty issuer (Net Smelter Royalty tokenization) — replaces bare category mining-royalty-tokenization

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | PTX |
| Slug | `ptx` |
| Issuer / brand (self-described) | PTX |
| Seed hosts | `ptxtoken.com` |

### Token / chain (live probe)

No ERC-20 (or equivalent) contract was confirmed via live `eth_call` in this pass for a token identity matching this project. Marketing may describe a token, but without a confirmed address + successful RPC getters, Tokn cannot treat token identity as verified.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

CoinGecko search returned hit(s): DEEPTICS (DPTX), ASMPT xStock (ASMPTX), Camden Property Trust xStock (CPTX), Sunny Optical Technology Group xStock (SUOPTX) — still not proof of underlying-asset verification.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Net Smelter Royalty / NSR share claims (marketing)

**What was actually confirmed here**

- 4/12 research URLs reachable in this pass.
- Physical asset layer: `unverified`; economic right: `partially-verified` (`net_smelter_royalty`); revenue: `partially-verified`; payout: `unverified` (0 on-chain tx samples; 0 metadata records).
- **No** independently corroborated physical-asset identity (filings/registries) was confirmed.
- **No** machine-queryable payout/distribution surface with on-chain confirmation was established.

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | **no** |
| Ownership / royalty / RWA claim | Net Smelter Royalty / NSR share claims (marketing) | **no** |
| Token supply | not confirmed | **no** |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `not confirmed` | not confirmed | Identity / supply only |
| Distribution / Safe / vault | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Payout observability:** No verified payout/harvest event ABI + confirmed historical txs for this candidate’s underlying economics in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://ptxtoken.com/` | HTTP 200 — live (text/html) |
| `https://ptxtoken.com/#how-it-works` | HTTP 200 — live (text/html) |
| `https://ptxtoken.com/#nsr` | HTTP 200 — live (text/html) |
| `https://docs.ptxtoken.com/` | URL error: [Errno -2] Name or service not known |
| `https://app.ptxtoken.com/` | URL error: [Errno -2] Name or service not known |
| `https://blog.ptxtoken.com/` | URL error: [Errno -2] Name or service not known |
| `https://ptxtoken.com/whitepaper` | HTTP 200 — live (text/html) |
| `https://ptxtoken.com/whitepaper.pdf` | HTTP 404: Not Found |
| `https://ptxtoken.com/llm/ptx-llm-knowledge-base.html` | HTTP 404: Not Found |
| `https://ptx.gitbook.io/ptx-docs/llms.txt` | HTTP 404: Not Found |
| `https://ptx.gitbook.io/ptx-docs/` | HTTP 404: Not Found |
| `https://ptx.gitbook.io/ptx-docs.md` | HTTP 404: Not Found |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search returned hit(s): DEEPTICS (DPTX), ASMPT xStock (ASMPTX), Camden Property Trust xStock (CPTX), Sunny Optical Technology Group xStock (SUOPTX) — still not proof of underlying-asset verification. |
| Public EVM RPC eth_call | No successful project-matched token probe |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `ptxtoken.com`

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
| Underlying asset independently verifiable | Low | Independent filings/registries naming the asset |
| Economic right established | Medium | Right-type evidence (filings/docs) |
| Economic mechanism / realized yield observable | Low | Payout metadata + on-chain tx verification |
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

**What cannot currently be verified:** Verified underlying-asset ownership / registry identity, Observed staking APY as a verified fact, Realized underlying revenue/yield distributions, Continuously verified production/revenue figures as facts, Any on-chain token identity fields

**Main blocker(s):** No independently confirmed token contract via eth_call; No specific physical asset identity established from research sources; No publicly reachable payout metadata, distribution contract, or verified payout transactions

**To move to the next state:** Publish contract addresses / public APIs for token identity and economic mechanism, then re-run the research agent.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Net Smelter Royalty / NSR share claims (marketing) | As stated in official marketing/docs | Official website/docs | official website | physical-world | No verification method currently available | self-reported | claims[] ; underlying fields null until contracts exist | No public ownership/registry/distribution surface confirmed |

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

### Evidence graph (layered)

| Layer | Status | Confidence | Notes |
| --- | --- | --- | --- |
| token_identity | unverified | none | eth_call + issuer address provenance |
| physical_asset | unverified | none | No specific physical asset identity established from research sources |
| economic_right | partially-verified | medium | net_smelter_royalty |
| revenue_mechanism | partially-verified | low | Revenue mechanism described only by issuer; not independently queryable |
| payout_mechanism | unverified | none | records=0; onchain_sample=0; currency=n/a |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| Official page text | official documentation | `https://ptxtoken.com/` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://ptxtoken.com/#how-it-works` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://ptxtoken.com/#nsr` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |
| Official page text | official documentation | `https://ptxtoken.com/whitepaper` | HTTP GET + text extract | claim language / product description | on research refresh | **optional** — self-reported claims provenance |

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
- Continuously verified production/revenue figures as facts
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
  researched_at: "2026-10-05T15:46Z"

  # Layered evidence graph — do not collapse into one confidence value.
  token_identity:
    status: unverified
    confidence: none
    issuer_published_address: false
    chain_established: false
    eth_call_verified: false
    metadata_match: false
    market_corroboration: false
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
    right_type: "net_smelter_royalty"
    blocker: "Economic/legal right described in issuer materials only — independent legal corroboration missing"
    evidence:
      - source: "issuer research corpus"
        tier: medium
        proves: "Issuer/docs language indicates `net_smelter_royalty`"
        reachable: true
        independently_verifiable: false

  revenue_mechanism:
    status: partially-verified
    confidence: low
    machine_queryable: false
    blocker: "Revenue mechanism described only by issuer; not independently queryable"
    evidence:
      - source: "https://ptxtoken.com/"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://ptxtoken.com/#how-it-works"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://ptxtoken.com/#nsr"
        tier: medium
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: false
      - source: "https://ptxtoken.com/whitepaper"
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
    []

  # Back-compat summary flags
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
    - "No specific physical asset identity established from research sources"
    - "No publicly reachable payout metadata, distribution contract, or verified payout transactions"

  recommended_adapter_scope:
    - "Do not implement an adapter yet — research only until identity is confirmed"

  prohibited_outputs:
    - "Verified underlying-asset ownership / registry identity"
    - "Observed staking APY as a verified fact"
    - "Realized underlying revenue/yield distributions"
    - "Continuously verified production/revenue figures as facts"
    - "Any on-chain token identity fields"
```

---

## Appendix — reachable excerpts (truncated)

### `https://ptxtoken.com/`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

### `https://ptxtoken.com/#how-it-works`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

### `https://ptxtoken.com/#nsr`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

### `https://ptxtoken.com/whitepaper`

> PTX Tokens represent shares in Net Smelter Royalty agreements from diversified mining operations. Earn from mining production with blockchain transparency, 24/7 liquidity, and verified NSR portfolio. Invest in tokenized mining royalties. Earn from 47+ NSR agreements across producing mines with complete blockchain transparency. PTX Mining Royalty Tokens / Invest in Net Smelter Royalty Revenue

