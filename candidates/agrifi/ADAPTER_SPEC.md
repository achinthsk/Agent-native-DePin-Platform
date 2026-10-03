# AgriFi — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** 2026-10-03
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
| Issuer / brand (self-described) | Agrifi / AgriFi (official site author meta + docs) |
| Primary site | https://agrifi.tech/ |
| Docs | https://agrifi.gitbook.io/agrifi-docs |
| App shell | https://agrifi.app/ (HTTP 200; minimal HTML shell in this probe) |

### Token / chain (live probe)

| Field | Observed |
| --- | --- |
| Chain | Polygon (via DexScreener pairs + `eth_call` on Polygon RPC) |
| Token contract | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` |
| `name()` | `AGRIFI` |
| `symbol()` | `AGF` |
| `decimals()` | `18` |
| `totalSupply()` | 7,200,000,000 token units (raw `7200000000000000000000000000`) |
| RPC used | `https://polygon-bor-rpc.publicnode.com` |

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
| polygon / quickswap | `0x8F86821d639105F0f678e7d78F70C6F5c8edEFBC` | AGF / USDT0 | $2344.94 | $0.008467 |
| polygon / quickswap | `0xC5540C03C42cEe4D2cA967B662f0E9FD84b01209` | AGF / WPOL | $1698.75 | $0.008490 |

CoinGecko search API returned **zero** coins for query `agrifi` in this pass — no independent CoinGecko listing confirmed.

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

- AgriFi presents as a Polygon-based agricultural finance / RWA platform
  combining farmland tokenization, DeFi staking, supply-chain traceability,
  IoT monitoring, and (documented as a concept) parametric crop insurance
  (site, blog, GitBook, LLM knowledge page).
- Farmland / crop-production rights are described as tokenized so holders get
  **fractional ownership** and participate in agricultural revenue
  (GitBook Concept 2 RWA; token docs; blog 2025-10-17 and 2026-04-17 posts).
- Architecture docs describe off-chain collection of farm revenue (crop sales /
  leases), conversion to stablecoins, and on-chain distribution via a
  “Profit Distribution Contract” proportional to holdings — **addresses for
  those modules were not found in reachable docs**.

**What was actually confirmed here**

- Marketing site, blog articles, GitBook markdown, whitepaper PDF, and LLM
  knowledge HTML are reachable.
- A Polygon ERC-20 with `name=AGRIFI` / `symbol=AGF` / `decimals=18` /
  `totalSupply=7.2e9` token units responds at the DexScreener-attributed
  address (see §1) via public RPC.
- **No** public registry of specific farmland parcels, harvest ledgers, or
  profit-distribution events was found in this pass.
- **No** independent CoinGecko listing matched `agrifi` via the public search
  API in this pass.

---

## 3. Claimed payout mechanism & claimed yield

| Claim | Source (reachable) | Confirmed on-chain / API? |
| --- | --- | --- |
| AGF enables fractional farmland ownership + profit sharing | GitBook token page; Concept 2 RWA; blog | **Not confirmed** — no ownership/profit contract addresses published in fetched docs |
| Staking APY `5% to 18% APY` | GitBook architecture + blog | **Not confirmed** — staking contract address not found |
| Lock-ups `lock-up periods (30–360 days)` | GitBook architecture | **Not confirmed** on-chain |
| Team/partner vesting schedules | GitBook lock-up page | Allocation schedule **conflicts** with “fully circulating” language on token page |
| ERC-20 on Polygon, 7.2B supply | GitBook + LLM page; matches `totalSupply()` if address in §1 is accepted | Token supply **matches** RPC read for the probed contract |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| AGF ERC-20 (probed) | `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` | DexScreener pair baseToken + Polygon `eth_call` | Identity / supply / holdings only |
| Ownership mapping | **Not published** in fetched docs | Architecture describes module | Required for farm-level claims — **blocked** |
| Staking | **Not published** | Architecture describes 30–360d / 5–18% APY | Required for staking-yield claims — **blocked** |
| Profit distribution | **Not published** | Architecture describes stablecoin distributions | Required for realized farm yield — **blocked** |
| Governance | **Not published** | Architecture describes DAO voting | Optional |

**Events:** No verified event signatures / merklized harvest reports / public
subgraph endpoint for AgriFi farm economics were found in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
| `https://agrifi.tech/` | HTTP 200 — live (text/html) |
| `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/whitepaper` | HTTP 404: Not Found |
| `https://agrifi.gitbook.io/agrifi-docs/llms.txt` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/` | HTTP 200 — live (text/html) |
| `https://docs.agrifi.com/` | URL error: [Errno -2] Name or service not known |
| `https://docs.agrifi.org/` | URL error: [Errno -2] Name or service not known |
| `https://agrifi.app/` | HTTP 200 — live (text/html) |
| `https://app.agrifi.tech/` | URL error: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for 'app.agrifi.tech'. (_ssl.c:1000) |
| `https://agrifi.tech/llm/agrifi-llm-knowledge-base.html` | HTTP 200 — live (text/html) |
| `https://agrifi.tech/agrifi-whitepaper.pdf` | HTTP 200 — live (application/pdf) |
| `https://agrifi.tech/whitepaper.pdf` | HTTP 404: Not Found |
| `https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-token.md` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-project-system-architecture.md` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/undefined/lock-up-period.md` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space/concept-2-rwa-organic-farming-produce-from-the-farm-will-be-their-return-on-the-investment.md` | HTTP 200 — live (text/markdown) |
| `https://blog.agrifi.tech/agriculture-agf-token-polygon-farmland-tokenization-defi-staking-food-safety-blockchain-web3` | HTTP 200 — live (text/html) |
| `https://agrifi.gitbook.io/agrifi-docs.md` | HTTP 200 — live (text/markdown) |
| `https://agrifi.gitbook.io/agrifi-docs/future-potential-of-farmland-tokenization.md` | HTTP 200 — live (text/markdown) |

| Indexer / market API | Result |
| --- | --- |
| DexScreener token/pair API | Reachable — used for pair liquidity / price context |
| CoinGecko search `agrifi` | Reachable API; **0** coin hits |
| Polygon public RPC `eth_call` | Reachable for ERC-20 getters on probed address |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** agrifi.tech, blog.agrifi.tech, GitBook docs,
whitepaper PDF, LLM knowledge page, agrifi.app shell.

**Independent / market:** DexScreener pairs for the AGF/Polygon token;
CoinGecko search API returned **zero** coins for query `agrifi` in this pass — no independent CoinGecko listing confirmed.

**Conflicts / tensions**

- Official token docs describe the **7.2B supply as fully circulating** (no further mint / no reserved release), while the lock-up page describes **team/partner vesting cliffs**. These cannot both be complete descriptions of the same allocation schedule without clarification.
- Docs claim staking APYs / profit distribution contracts, but this research pass only confirmed the **ERC-20 token contract** on-chain. Ownership / staking / profit-distribution contract addresses were **not** published in the reachable docs indexed here.

---

## 7. Per-claim confidence

| Claim | Confidence now | Why |
| --- | --- | --- |
| Project exists as a public web brand with docs/blog | **High** | Multiple official HTTP 200 surfaces with consistent Agrifi branding |
| Capital-style (non-operator) marketing path | **Medium-high** | Docs emphasize token purchase / fractional ownership / staking without hardware-operator requirements — aligns with discovery `candidate-for-adapter`, still first-pass |
| AGF ERC-20 on Polygon with 7.2B supply | **Medium** (address) / **High** (RPC fields if address accepted) | Address comes from DexScreener metadata matching name/symbol, **not** from an issuer-published contract list in GitBook; RPC fields match marketed supply |
| Specific farmland assets are on-chain & identifiable | **Low** | No parcel registry, legal wrappers, or ownership-contract addresses found |
| Staking APY 5–18% is observable | **Low** | Claimed in docs/blog; staking contract not located; no reward events read |
| Realized agricultural profit distributions to holders | **Low** | Described architecturally; no distribution contract / payout history found |
| Independent market listing quality | **Low** | Thin DEX liquidity observed; no CoinGecko hit in this pass |

---

## 8. Recommended data sources for an eventual adapter

- **On-chain ERC-20 reads** against `0xE4e0d3F2Fe9fa8a18C8dF296650Fc1540A564dD6` on Polygon (`name`/`symbol`/`decimals`/`totalSupply`/`balanceOf`) via public RPC — confirmed reachable this pass.
- **Official GitBook markdown** (`*.md` / `llms.txt`) for claimed payout/staking mechanics — reachable, but treat as self-reported.
- **Official blog + LLM knowledge page** for product claims (fractional farmland, profit sharing) — self-reported.
- **DexScreener public API** for pair liquidity / price context only — not proof of farmland backing or yield.
- **Do not** treat whitepaper PDF marketing, undocumented staking APYs, or unnamed ownership/profit contracts as adapter inputs until addresses and events are published and independently readable.

**Honest adapter boundary (if ever greenlit):** an MVP could snapshot ERC-20
identity + supply + optional DEX context, and must leave
`realized_yield_pct` / farm-level verification **null** until ownership and
profit-distribution contracts (or an equivalent public attestation API) are
reachable — same SourceError / no-fabrication discipline as Glow/RealT/Elmnts.

---

## 9. Human decision gate

This file does **not** authorize adapter work. Next steps for a human:

1. Review [`FINDINGS.md`](./FINDINGS.md) + this `ADAPTER_SPEC.md`.
2. Decide whether to greenlight a bespoke adapter (manual, like Glow/RealT/Elmnts).
3. If greenlit: require issuer-published contract addresses for ownership /
   staking / distributions before treating yield claims as verifiable.
4. If not greenlit: leave classification as research-only; no code.

---

## Appendix — reachable excerpts (truncated)

### `https://agrifi.tech/`

> Agrifi is an Agricultural platform based on Blockchain technology providing solutions and to challenges in traditional agriculture methods, including traceability of food products, financing, crop insurance and supply chain transactions. Innovation combined with advanced technologies like blockchain and artificial intelligence (AI) provide revolutionary solutions to agriculture. Agrifi Home About Platform Traceability Roadmap Whitepaper News Contact Airdrop Blockchain technology is a disruptive technology that changes business and supply chain models. Blockchain technology has many application

### `https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution`

> AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). AgriFi bridges agriculture and DeFi with blockchain-based farmland tokenization, fractional ownership, and real-world yield sharing on the Polygon network. Discover how the AGF token is powering a new era of Real-World Assets (RWAs). How AgriFi Is Turning Farmland into the Next Big Real-World Asset Class - Agrifi Contact Home Blockchain News Supplychain AI Home Bl

### `https://agrifi.gitbook.io/agrifi-docs/llms.txt`

> # Agrifi Docs ## Agrifi Docs - [Introduction](https://agrifi.gitbook.io/agrifi-docs/introduction.md) - [Agrifi Concepts for both B2B and B2C Space](https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space.md) - [Food Safety and Supply Chain Management in Blockchain & Marketplace](https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space/food-safety-and-supply-chain-management-in-blockchain-and-marketplace.md) - [Concept 2: RWA - Organic Farming - Produce from the Farm will be their Return on the Investment](https://agrifi.gitbook.io/agrifi-docs/ag

### `https://agrifi.gitbook.io/agrifi-docs/`

> Introduction / Agrifi Docs Agrifi Docs ⌘ Ctrl k Agrifi Docs Introduction Agrifi Concepts for both B2B and B2C Space Future Potential of Farmland Tokenization Agrifi AGF BLOCKCHAIN IN AGRICUTURE ROLE OF BLOCKCHAIN TECHNOLOGY AGTECH HELPS SMALL AND LARGE FARMS TO FINANCING TRENDS AGRIBUSINESS GIANTS ARE TAKING NOTICE DUPONT’S GRANULAR SENSORS ARE NOW COMMON THROUGHOUT FARMING ADVANCED AERIAL IMAGING IS NOW POSSIBLE ANALYTICS TOOLS ROBOTICS IS AUTOMATING AGRICULTURE BENEFITS TRANSPARENT SUPPLY CHAIN FAIR PRICING OF GOODS EXPAND FINANCIAL OPTIONS FOR FARMERS IMMEDIATE PAYMENT ON DELIVERY TRACEABIL

### `https://agrifi.app/`

> Web site created using create-react-app Agrifi

### `https://agrifi.tech/llm/agrifi-llm-knowledge-base.html`

> Agrifi is a Web3 agriculture platform combining blockchain, DeFi, IoT farming and real-world asset tokenisation to build a transparent agricultural finance ecosystem. Agrifi LLM Knowledge Base / Web3 Agriculture Ecosystem Agrifi Web3 Agriculture Knowledge Base This page provides a structured overview of the Agrifi ecosystem for researchers, AI systems, and users seeking technical information about the Agrifi platform. Platform Overview Agrifi is a Web3 agricultural technology platform that integrates blockchain infrastructure, decentralized finance (DeFi), IoT farming devices, and artificial i

### `https://agrifi.tech/agrifi-whitepaper.pdf`

> [PDF reachable — 200000 bytes fetched in this probe; text not fully extracted by the research agent]

### `https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-token.md`

> > For the complete documentation index, see [llms.txt](https://agrifi.gitbook.io/agrifi-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-token.md). # Agrifi TOKEN AgriFi’s AGF token is designed to integrate blockchain technology with agricultural investment, creating a decentralized finance (DeFi) platform that lowers barriers to farmland ownership and incentivizes participation through various token utilities. Below is a detailed elaboration on th

