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
| Seed hosts | `albion.exchange`, `albionlabs.org`, `api.github.com`, `app.co.uk`, `basescan.org`, `blog.github.com`, `docs.basescan.org`, `docs.github.com`, `github.com`, `raw.githubusercontent.com`, `www.albionlabs.org`, `www.facebook.com`, `www.lse.co.uk` |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | base |
| Token contract | `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` |
| `name()` | `Albion Wressle-1 4.5% Royalty Investor Preview` |
| `symbol()` | `ALB-WR1-R2` |
| `decimals()` | `18` |
| `totalSupply()` | 36,000 token units (raw `35999999999999999998000`) |
| RPC used | `https://mainnet.base.org` |
| Address source | https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json |
| Issuer-published address? | YES |
| Identity confidence | `high` |
| Evidence: eth_call | YES |
| Evidence: metadata match | YES |
| Evidence: market corroboration | NO |

**Layer separation:** this table establishes **TOKEN IDENTITY** only. It does
**not** verify physical-asset backing, ownership/registry rights, or payouts.

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

CoinGecko search API returned **zero** coins for query `Albion Labs — tokenized Wressle-1 oil royalty` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- Physical asset cue: `Oil Field`
- Economic right language: Revenue-swap / contractual revenue share (docs/filings)
- Issuer-published payout records / distribution language present

**What was actually confirmed here**

- Token eth_call identity confirmed on **base** at `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` (Albion Wressle-1 4.5% Royalty Investor Preview/ALB-WR1-R2).
- 46/84 research URLs reachable in this pass.
- Physical asset layer: `verified` (`wressle-1`); economic right: `verified` (`revenue_swap`); revenue: `partially-verified`; payout: `verified` (6 on-chain tx samples; 22 metadata records).

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | not clearly extracted | yes |
| Ownership / royalty / RWA claim | see docs excerpts | yes |
| Token supply | matches eth_call | yes |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` | eth_call + market metadata | Identity / supply only |
| safe | `0xa51fd23d6e2442805130eac0712f590691e91517` | issuer-published constants/docs | Payout plumbing context |
| safe | `0x1c56fc57bbc18879d8059562a371722b682ca984` | issuer-published constants/docs | Payout plumbing context |
| safe | `0x4e5bd3cf829010280f76754b49921d4e1448b8cf` | issuer-published constants/docs | Payout plumbing context |
| payout_currency | `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913` | issuer-published constants/docs | Payout plumbing context |
| orderbook | `0xb05D73E6BCc26AEB5b67Ff68C6E9C6151073e3cE` | issuer-published constants/docs | Payout plumbing context |
| orderbook | `0x59401c9302e79eb8ac6aea659b8b3ae475715e86` | issuer-published constants/docs | Payout plumbing context |

**Payout observability:** Verified — issuer payout metadata + on-chain txHash sample(s)

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
| `https://github.com/albionlabs` | HTTP 200 — live (text/html) |
| `https://api.github.com/orgs/albionlabs/repos?per_page=50` | HTTP 200 — live (application/json) |
| `https://api.github.com/users/albionlabs/repos?per_page=50` | HTTP 200 — live (application/json) |
| `https://albionlabstokenizedwressle1oilroyalty.gitbook.io/albionlabstokenizedwressle1oilroyalty-docs.md` | HTTP 404: Not Found |
| `https://www.lse.co.uk/rns/` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/rns/ftse-100.html` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/rns/ftse-250.html` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/rns/aim.html` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/rns/sector.html` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/rns-alerts.html` | HTTP 200 — live (text/html) |
| `https://www.lse.co.uk/news-and-rns/` | HTTP 200 — live (text/html) |
| `https://www.facebook.com/sharer/sharer.php?u=https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html` | HTTP 200 — live (text/html) |
| `https://docs.basescan.org/llms.txt` | HTTP 200 — live (text/html) |
| `https://etherscan.io/api/pricing` | HTTP 403: Forbidden |
| `https://docs.basescan.org/set-up-your-api-key` | HTTP 200 — live (text/html) |
| `https://github.com/albionlabs/albion.rewards` | HTTP 200 — live (text/html) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/readme.md` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/README.md` | HTTP 404: Not Found |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/src/constants.ts` | HTTP 200 — live (text/plain) |
| `https://api.github.com/repos/albionlabs/albion.rewards/git/trees/main?recursive=1` | HTTP 200 — live (application/json) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-05-01_to_2026-05-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-05-01_to_2026-05-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-04-01_to_2026-04-30/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-04-01_to_2026-04-30/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-03-01_to_2026-03-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | HTTP 200 — live (text/plain) |
| `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-03-01_to_2026-03-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | HTTP 200 — live (text/plain) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | Reachable — used for market context when pairs match |
| CoinGecko search | CoinGecko search API returned **zero** coins for query `Albion Labs — tokenized Wressle-1 oil royalty` in this pass — no independent CoinGecko listing confirmed. |
| Public EVM RPC eth_call | Reachable for probed token |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** `albion.exchange`, `albionlabs.org`, `api.github.com`, `app.co.uk`, `basescan.org`, `blog.github.com`, `docs.basescan.org`, `docs.github.com`, `github.com`, `raw.githubusercontent.com`, `www.albionlabs.org`, `www.facebook.com`, `www.lse.co.uk`

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
| Underlying asset independently verifiable | High | Independent filings/registries naming the asset |
| Economic right established | High | Right-type evidence (filings/docs) |
| Economic mechanism / realized yield observable | High | Payout metadata + on-chain tx verification |
| Independent market listing quality | Low | Dex/CG presence without implying backing |

---

## 8. Recommended data sources for an eventual adapter

See **Recommended Adapter Inputs** below for the concrete table. High-level:

- ERC-20 identity (name/symbol/decimals)
- totalSupply via eth_call
- Historical payout metadata + on-chain txHash verification for distributions
- Published Safe/vault/orderbook addresses as payout plumbing context
- claims[] rows for documented self-reported yield/ownership claims with explicit tiers
- Record physical-asset identity + independent filing URLs as claims[] provenance

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `adapter-ready`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

Evidence graph supports a useful adapter: TOKEN IDENTITY verified; PHYSICAL ASSET verified (wressle-1); ECONOMIC RIGHT verified (revenue_swap); PAYOUT MECHANISM verified with 6 on-chain sample tx(s) and machine-queryable payout metadata. Verified surfaces: Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), TOKEN IDENTITY: contract address is issuer-published + eth_call-verified, PHYSICAL ASSET: underlying physical asset identity, ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues, PAYOUT MECHANISM: machine-queryable investor distributions.

**What can currently be verified:** Token total supply equals eth_call totalSupply(), Token identity (name/symbol/decimals), TOKEN IDENTITY: contract address is issuer-published + eth_call-verified, PHYSICAL ASSET: underlying physical asset identity, ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues, PAYOUT MECHANISM: machine-queryable investor distributions

**What cannot currently be verified:** Continuously verified production/revenue figures as facts

**Main blocker(s):** none recorded

**To move to the next state:** Human greenlight can proceed to a scoped adapter implementing only the verified token + payout surfaces, with physical/economic right evidence recorded as claims[] provenance — not fabricated fields.

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Token total supply equals eth_call totalSupply() | ALB-WR1-R2 supply (docs or market) | base `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` via `https://mainnet.base.org` | blockchain | on-chain | base eth_call → totalSupply() @ 0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7 | verified | total_supply / claims[] | — |
| Token identity (name/symbol/decimals) | Albion Wressle-1 4.5% Royalty Investor Preview / ALB-WR1-R2 / 18 | `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` on base | blockchain | on-chain | eth_call → name()/symbol()/decimals() | verified | token identity fields / claims[] | — |
| TOKEN IDENTITY: contract address is issuer-published + eth_call-verified | Albion Wressle-1 4.5% Royalty Investor Preview / ALB-WR1-R2 @ 0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7 (base); confidence=high | https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json | official documentation | on-chain | Issuer-controlled source publishes address → infer chain → eth_call name()/symbol()/decimals()/totalSupply() → match candidate identity | verified | token identity fields / claims[] | — |
| PHYSICAL ASSET: underlying physical asset identity | wressle-1 | https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html | regulatory/independent filing | physical-world | Independent filings/registries naming the asset + economic context; NOT implied by ERC-20 identity | verified | underlying_asset | — |
| ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues | revenue_swap | https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html | regulatory/independent filing | physical-world | Independent filing and/or issuer legal/technical docs describing right type (royalty, revenue-swap, ownership, etc.) | verified | claims[] / economic_right | — |
| PAYOUT MECHANISM: machine-queryable investor distributions | 22 payout records; 6 on-chain verified; currency=USDC; frequency=monthly | https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json | blockchain | on-chain | Issuer-published payout metadata → eth_getTransaction(ByHash/Receipt) on the token's chain; or distribution contract events / public API | verified | distribution_history / realized_yield_pct | — |
| REVENUE MECHANISM: how the physical asset generates revenue | described | https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html | official documentation | physical-world | Operator/regulatory production disclosures or continuously queryable revenue APIs | partially-verified | claims[] (context) | Revenue generation described in filings/docs but no continuously machine-queryable production/revenue API confirmed |

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
| DEX price | NO |
| DEX liquidity | NO |

### Underlying-asset verification

| Capability | Available now? |
| --- | --- |
| Physical / real-world asset identity | YES |
| Asset ownership / registry | NO |
| Economic/legal right type established | YES |
| Infrastructure operation / production | NO |
| Revenue generation / leases / harvests | YES |
| Actual distributions to holders | YES |

### Bridge summary

```text
Token exists (independently queryable): YES
Underlying asset identified in docs: YES
Underlying asset independently verifiable: YES
Economic connection between token and asset verifiable: YES
```

### Evidence graph (layered)

| Layer | Status | Confidence | Notes |
| --- | --- | --- | --- |
| token_identity | verified | high | eth_call + issuer address provenance |
| physical_asset | verified | high | wressle-1 |
| economic_right | verified | high | revenue_swap |
| revenue_mechanism | partially-verified | medium | Revenue generation described in filings/docs but no continuously machine-queryable production/revenue API confirmed |
| payout_mechanism | verified | high | records=22; onchain_sample=6; currency=USDC |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
| ERC-20 getters | blockchain | `0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7` on base | eth_call name/symbol/decimals/totalSupply via `https://mainnet.base.org` | identity + supply | on snapshot / daily | **required** — token identity |
| Distribution plumbing constants | issuer source | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/src/constants.ts` | HTTP GET + parse Safe/USDC/orderbook addresses | payout route context | on research refresh | **optional** — payout plumbing |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-05-01_to_2026-05-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-05-01_to_2026-05-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-04-01_to_2026-04-30/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-04-01_to_2026-04-30/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-03-01_to_2026-03-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| Payout metadata JSON | issuer HTTP | `https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-03-01_to_2026-03-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json` | GET JSON payoutData[] | historical distributions + txHashes | monthly / on snapshot | **required** — payout verification |
| safe address | blockchain | `0xa51fd23d6e2442805130eac0712f590691e91517` | eth_call / eth_getTransaction* | payout plumbing state | on snapshot | **optional** — payout context |
| safe address | blockchain | `0x1c56fc57bbc18879d8059562a371722b682ca984` | eth_call / eth_getTransaction* | payout plumbing state | on snapshot | **optional** — payout context |
| safe address | blockchain | `0x4e5bd3cf829010280f76754b49921d4e1448b8cf` | eth_call / eth_getTransaction* | payout plumbing state | on snapshot | **optional** — payout context |
| payout_currency address | blockchain | `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913` | eth_call / eth_getTransaction* | payout plumbing state | on snapshot | **optional** — payout context |
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

- ERC-20 identity (name/symbol/decimals)
- totalSupply via eth_call
- Historical payout metadata + on-chain txHash verification for distributions
- Published Safe/vault/orderbook addresses as payout plumbing context
- claims[] rows for documented self-reported yield/ownership claims with explicit tiers
- Record physical-asset identity + independent filing URLs as claims[] provenance

### What the future adapter MUST NOT implement

- Continuously verified production/revenue figures as facts

### What requires human review

- Whether the project token (if any) should be treated as the representation
  of specific underlying assets vs a generic ecosystem/utility token.
- Whether DexScreener-attributed contract addresses are acceptable before
  issuer-published address lists exist.
- Whether to greenlight any adapter at `adapter-ready` readiness.

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
  status: adapter-ready
  researched_at: "2026-10-05T15:47Z"

  # Layered evidence graph — do not collapse into one confidence value.
  token_identity:
    status: verified
    confidence: high
    issuer_published_address: true
    chain_established: true
    eth_call_verified: true
    metadata_match: true
    market_corroboration: false
    note: "Token identity ≠ asset backing ≠ economic/payout verification"

  physical_asset:
    status: verified
    confidence: high
    named_asset: "wressle-1"
    blocker: ""
    evidence:
      - source: "https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html"
        tier: highest
        proves: "Independent source names physical asset cue(s) ['wressle-1'] in economic/royalty context"
        reachable: true
        independently_verifiable: true
      - source: "https://raw.githubusercontent.com/albionlabs/tokenlist/main/albion.tokenlist.json"
        tier: medium
        proves: "Issuer materials name a specific physical asset"
        reachable: true
        independently_verifiable: false
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: medium
        proves: "Payout metadata binds token to asset WRESSLE-1-ROYALTY-4.5"
        reachable: true
        independently_verifiable: false

  economic_right:
    status: verified
    confidence: high
    right_type: "revenue_swap"
    blocker: ""
    evidence:
      - source: "https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html"
        tier: highest
        proves: "Independent source links project/asset to right type `revenue_swap`"
        reachable: true
        independently_verifiable: true
      - source: "issuer research corpus"
        tier: medium
        proves: "Issuer/docs language indicates `revenue_swap`"
        reachable: true
        independently_verifiable: false
      - source: "on-chain token metadata @ 0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7"
        tier: highest
        proves: "Token name/symbol encodes economic-right claim (not legal proof alone)"
        reachable: true
        independently_verifiable: true

  revenue_mechanism:
    status: partially-verified
    confidence: medium
    machine_queryable: false
    blocker: "Revenue generation described in filings/docs but no continuously machine-queryable production/revenue API confirmed"
    evidence:
      - source: "https://www.lse.co.uk/rns/potential-funding-structure-with-albion-labs-pdno648eeh859t5.html"
        tier: highest
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: true
      - source: "https://www.lse.co.uk/rns/"
        tier: highest
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: true
      - source: "https://www.lse.co.uk/rns/ftse-100.html"
        tier: highest
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: true
      - source: "https://www.lse.co.uk/rns/ftse-250.html"
        tier: highest
        proves: "Source describes how the underlying asset generates revenue"
        reachable: true
        independently_verifiable: true

  payout_mechanism:
    status: verified
    confidence: high
    machine_queryable: true
    payout_record_count: 22
    onchain_verified_sample: 6
    currency_hint: "USDC"
    frequency_hint: "monthly"
    blocker: ""
    evidence:
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: highest
        proves: "Issuer-published payout txHash 0x3c382c0dd282d46060f0cef888ab73588ed2e01a7bfa3827ea8e6d61c173ad05 found on base (to=0x1c56fc57bbc18879d8059562a371722b682ca984, status_ok=True)"
        reachable: true
        independently_verifiable: true
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: highest
        proves: "Issuer-published payout txHash 0xd5f9223af2492269e9482be0549805740a73b33259f44b2439d89321975a6f29 found on base (to=0x4e5bd3cf829010280f76754b49921d4e1448b8cf, status_ok=True)"
        reachable: true
        independently_verifiable: true
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: highest
        proves: "Issuer-published payout txHash 0xd6f953e54edf172049457aa81eea951cf06ac55a936fac2da7e9abbaeb5a60cb found on base (to=0x4e5bd3cf829010280f76754b49921d4e1448b8cf, status_ok=True)"
        reachable: true
        independently_verifiable: true
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: highest
        proves: "Issuer-published payout txHash 0x99378ed12fca004b169fb4d5ffe29726460b16b028fba20517f7718abe6fc044 found on base (to=0x1c56fc57bbc18879d8059562a371722b682ca984, status_ok=True)"
        reachable: true
        independently_verifiable: true
      - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
        tier: highest
        proves: "Issuer-published payout txHash 0xaf3abeb9d512112a3da3dd2747982146b940ae0204fa37b3dd92503705603c57 found on base (to=0x1c56fc57bbc18879d8059562a371722b682ca984, status_ok=True)"
        reachable: true
        independently_verifiable: true

  machine_queryable_sources:
    - source: "base:0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7"
      what_it_proves: "ERC-20 token identity and supply"
      reachable: true
      independently_verifiable: true
    - source: "0x3c382c0dd282d46060f0cef888ab73588ed2e01a7bfa3827ea8e6d61c173ad05"
      what_it_proves: "Historical investor payout transaction"
      reachable: true
      independently_verifiable: true
    - source: "0xd5f9223af2492269e9482be0549805740a73b33259f44b2439d89321975a6f29"
      what_it_proves: "Historical investor payout transaction"
      reachable: true
      independently_verifiable: true
    - source: "0xd6f953e54edf172049457aa81eea951cf06ac55a936fac2da7e9abbaeb5a60cb"
      what_it_proves: "Historical investor payout transaction"
      reachable: true
      independently_verifiable: true
    - source: "0x99378ed12fca004b169fb4d5ffe29726460b16b028fba20517f7718abe6fc044"
      what_it_proves: "Historical investor payout transaction"
      reachable: true
      independently_verifiable: true
    - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json"
      what_it_proves: "Structured payout history (issuer-published JSON)"
      reachable: true
      independently_verifiable: false
    - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-07-01_to_2026-07-31/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
      what_it_proves: "Structured payout history (issuer-published JSON)"
      reachable: true
      independently_verifiable: false
    - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json"
      what_it_proves: "Structured payout history (issuer-published JSON)"
      reachable: true
      independently_verifiable: false
    - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-06-01_to_2026-06-30/0x1d57246fd0ba134d7cc78ddf3ed829379d95f4b7/metadata.json"
      what_it_proves: "Structured payout history (issuer-published JSON)"
      reachable: true
      independently_verifiable: false
    - source: "https://raw.githubusercontent.com/albionlabs/albion.rewards/main/output/2026-05-01_to_2026-05-31/0xf836a500910453a397084ade41321ee20a5aade1/metadata.json"
      what_it_proves: "Structured payout history (issuer-published JSON)"
      reachable: true
      independently_verifiable: false

  # Back-compat summary flags
  token_verification:
    available: true
  underlying_asset_verification:
    available: true
  economic_mechanism_verification:
    available: true
  market_data:
    available: false
  independent_sources:
    available: true
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
    - "None recorded"

  recommended_adapter_scope:
    - "ERC-20 identity (name/symbol/decimals)"
    - "totalSupply via eth_call"
    - "Historical payout metadata + on-chain txHash verification for distributions"
    - "Published Safe/vault/orderbook addresses as payout plumbing context"
    - "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"
    - "Record physical-asset identity + independent filing URLs as claims[] provenance"

  prohibited_outputs:
    - "Continuously verified production/revenue figures as facts"
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

> Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Potential Funding Structure with Albion Labs / Regulatory News Home Home About Us Advertise With Us Investor Relations What's New Share Prices Share Prices Financial Diary Commodities UK Industry Sectors Aquis Stock Exchange Share Prices Euronext Share Prices US Share Prices UK Indices FTSE 100 FTSE 250 FTSE All-Share FTSE Small Cap FTSE 350 FTSE AIM All-Share Share Risers Tech Minerals (MNTL) +25.00% Macau Property (MPO) +24.07% Tullow Oil (TLW) +23.97% Georgina Energy

### `https://albion.exchange`

> 

