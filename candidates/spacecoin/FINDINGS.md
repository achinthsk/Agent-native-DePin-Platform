# Spacecoin — candidate investigation

**Classification: `wrong-model`**

**Date investigated:** 2026-08-21  
**Investigator note:** Scheduler discovery cycle #1
(`scheduler/run_discovery.py` + follow-on docs deep-dive using the
`candidates/README.md` checklist). Research log only. No adapter,
schema, scoring, storage, or API changes accompany this document beyond
this FINDINGS file, the candidates index row, and backlog pointer
advance. Elmnts was not touched. `execution/` was not invoked.

Spacecoin is a live DePIN project (LEO satellites + Creditcoin + $SPACE)
with real docs, a live SpaceRouter Proxy product, published contracts,
and a staking dApp. The **participation paths that pay you** require
**running a Provider / Home Node** (contribute residential bandwidth +
keep a node online) in addition to staking. That is an active-operator
model — Helium / Render / Aethir-Checker style — **not** this platform’s
passive capital-provision bar (Glow / Elmnts / RealT).

---

## What was checked

### Official surface

| Source | URL | Result |
| --- | --- | --- |
| Marketing site | https://www.spacecoin.org/ | HTTP 200 — live SPA (“DePIN Powered By Satellites”, Launch List, Whitepaper CTA) |
| Docs home / index | https://docs.spacecoin.org/llms.txt | HTTP 200 — structured GitBook map |
| Welcome | https://docs.spacecoin.org/readme.md | Fetched — audience includes “node operators” |
| What is Spacecoin | https://docs.spacecoin.org/start-here/what-is-spacecoin.md | Fetched — DePIN; 4 satellites in orbit; Creditcoin; $SPACE |
| Token overview | https://docs.spacecoin.org/usdspace-token/token-overview-and-utility.md | Fetched — ERC-20 on Creditcoin; utilities include staking for operators |
| Tokenomics | https://docs.spacecoin.org/usdspace-token/tokenomics.md | Fetched — fixed 21B supply allocation tables |
| Staking guide | https://docs.spacecoin.org/usdspace-token/staking.md | Fetched — **explicit:** staking alone does not qualify for SpaceRouter rewards |
| SpaceRouter overview | https://docs.spacecoin.org/spacerouter-proxy/overview.md | Fetched — consumers pay; **providers run a home app** |
| Provider guide | https://docs.spacecoin.org/spacerouter-proxy/proxy-provider-guide.md | Fetched — install app, Start, earn SPACE for served traffic |
| Provider prerequisites | https://docs.spacecoin.org/spacerouter-proxy/proxy-provider-guide/prerequisites.md | Fetched — always-on connection, port 9090, min 1 SPACE stake |
| Service user guide | https://docs.spacecoin.org/spacerouter-proxy/service-user-guide.md | Fetched — consumer path pays for proxy usage (spend, not earn) |
| Reference / contracts | https://docs.spacecoin.org/spacerouter-proxy/reference.md | Fetched — SPACE / StakingV2 / escrow addresses + Creditcoin RPC |
| Staking dApp | https://penguinbase.com/dapp/spacestaking | HTTP 200 — live SPA (“Stake SPACE Tokens to Run Nodes…”) |
| Proxy gateway | https://gateway.spacerouter.org/ | HTTP **402 Payment Required** (endpoint live; unpaid probe) |
| Seed `spacecoin.com` | https://spacecoin.com/ | SSL EOF — unreachable from this environment |
| Seed `docs.spacecoin.com` | https://docs.spacecoin.com/ | SSL EOF — unreachable (canonical docs are `docs.spacecoin.org`) |
| Seed `spacecoin.io` | https://spacecoin.io/ | DNS failure |
| GitHub org `spacecoin` | https://github.com/spacecoin | HTTP 404 |
| Provider releases | https://github.com/space-labs/space-router-node/releases/latest | Linked from official docs (operator software) |

### On-chain (Creditcoin mainnet)

From docs reference: SPACE `0x7ab7C6A935Ab2D1437398790C9C0660af62A80b9`,
RPC `https://mainnet3.creditcoin.network`, chain id `102030`.

Direct `eth_call` via `https://mainnet3.creditcoin.network` (2026-08-21):

| Call | Result |
| --- | --- |
| `name()` | `Spacecoin` |
| `symbol()` | `SPACE` |
| `totalSupply()` | **21000000000** (21B, matches docs) |

Also documented:

| Contract | Address |
| --- | --- |
| SPACE token | `0x7ab7C6A935Ab2D1437398790C9C0660af62A80b9` |
| StakingV2 | `0x5d07fEd750F77C2DB8e7D1c031c05E3A5d2bc9fA` |
| TokenPaymentEscrow | `0xC130F5D76f0b4Ce8FE2ceA0D2C2b8f53A39a5cd0` |

---

## What’s actually reachable right now

| Surface | Reachable? | Notes |
| --- | --- | --- |
| Marketing site | Yes | Launch-list / satellite narrative |
| Official docs (GitBook `.md`) | Yes | Primary evidence for classification |
| Staking dApp | Yes (SPA) | Title/copy ties staking to running nodes |
| SpaceRouter gateway | Yes (402 without payment) | Live consumer gateway |
| Keyless farm/rent-style public economics API | **No** | Earn path is Provider receipts + claim, not a Glow/RealT-style public cashflow feed |
| Capital-only “finance a satellite / share rent” product | **Not found** | Open constellation language targets **satellite operators** contributing hardware |

---

## Mechanism vs this platform’s capital-provision bar

This platform’s bar (Glow / Elmnts / RealT): **passive capital** finances
or owns a claim on an underlying asset’s cashflow / emissions without the
participant operating infrastructure.

Spacecoin’s **documented earn paths**:

1. **SpaceRouter Proxy Provider** — install a desktop/CLI Provider app,
   keep an always-on residential connection, open port 9090 (or tunnel),
   stake ≥ 1 SPACE, serve proxy traffic, claim SPACE receipts on-chain.
   Official docs: “From zero to earning SPACE in roughly 10 minutes —
   once your stake is in place.”
2. **Staking** — docs state explicitly: *“To earn SpaceRouter rewards,
   you need both staking and node operation”* and *“Staking alone does
   not qualify.”* Step 4 is “Run a Node”; “Your node must remain online
   to earn rewards.”
3. **Consumer / developer path** — deposit SPACE in escrow and **pay**
   for proxy bandwidth. That is a spend surface, not a yield opportunity
   for this platform.
4. **Satellite / open constellation** — “anyone meeting protocol
   standards can contribute their own satellites.” That is hardware
   contribution by satellite operators, not a capital-only share of an
   already-financed farm/property.

Payout shape for Providers is **protocol-token (SPACE) rewards for
bandwidth / node work**, settled via on-chain receipts — not a direct
claim on external satellite lease revenue analogous to RealT rent or a
Glow-style financed-farm deposit.

---

## Classification

**`wrong-model`**

Same family as Helium / Render / Aethir Checker: stake + **operate a
client/node** (or contribute physical capacity) to earn emissions /
receipts. No documented passive capital-provision product matching Glow /
Elmnts / RealT was found in official docs on 2026-08-21.

---

## Can the four scores be computed?

**No.** Wrong-model for this platform’s adapter lane. Even if scores were
desired for research curiosity, there is no capital-only asset instance
with a public rent/emission attribution path to map into `storage/`.

---

## Explicit unknowns / next checks (if a human reopens this)

1. Whether any future “finance a satellite” / capacity-NFT product
   launches with public economics — not present in current docs.
2. Whether staking APR shown on penguinbase is separable from node
   operation for a non-Provider wallet (docs currently say no for
   SpaceRouter rewards).
3. Satellite-operator reward mechanics beyond tokenomics tables (10%
   “Satellite Node Rewards”) — still operator-side.

None of these unknowns weaken the current `wrong-model` call for the
**live** Provider + staking-to-run-node path.

---

## Scheduler notes

- First backlog item (`spacecoin`); `scheduler/backlog.json` `next_index`
  advanced `0 → 1`.
- Output intended for human PR review — nothing auto-merges.
