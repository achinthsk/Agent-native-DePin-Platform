# Aethir — candidate investigation

**Classification: `wrong-model`**

**Date investigated:** 2026-08-19  
**Investigator note:** Research log only. No adapter, schema, scoring, storage,
or API changes accompany this document.

Aethir is a live GPU-cloud / DePIN network with real docs, a live owner portal,
and an on-chain Checker License NFT. The participation paths that were checked
(Cloud Host, Checker Node — including NaaS delegation, and ATH token staking)
do **not** match this platform’s passive capital-provision bar (Glow / Elmnts /
RealT). Checker “buy a license” still depends on an operated Checker Client
(self, VPS, or NaaS) earning **protocol-token emissions for validation work**,
not a capital claim on financed GPU capacity or external rental revenue.

---

## What was checked

### Official surface

| Source | URL | Result |
| --- | --- | --- |
| Marketing site | https://aethir.com/ | HTTP 200 — live |
| Docs home | https://docs.aethir.com/ | HTTP 200 — live |
| Docs index (`llms.txt`) | https://docs.aethir.com/llms.txt | HTTP 200 — structured doc map |
| Checker Owner Portal | https://app.aethir.com/ | HTTP 200 — live SPA |
| Checker License NFT docs | https://docs.aethir.com/checker-guide/what-is-the-checker-node/what-is-the-checker-node-license-nft.md | Fetched |
| License owner ↔ operator | https://docs.aethir.com/checker-guide/how-to-run-checker-nodes/what-is-a-checker-node-client/the-relationship-between-checker-license-owner-and-checker-node-operator.md | Fetched |
| Checker hardware requirements | https://docs.aethir.com/checker-guide/how-to-run-checker-nodes/what-is-a-checker-node-client/what-is-the-hardware-requirements-for-running-checker-node-client.md | Fetched |
| VPS / NaaS | https://docs.aethir.com/checker-guide/how-to-manage-checker-nodes/delegate-and-undelegate/virtual-private-servers-vps-and-node-as-a-service-naas-provider.md | Fetched |
| How checkers work / rewards | https://docs.aethir.com/checker-guide/what-is-the-checker-node/how-do-checker-nodes-work.md | Fetched |
| Purchase / secondary markets | https://docs.aethir.com/checker-guide/how-to-purchase-checker-nodes | HTTP 200 |
| License rewards API docs | https://docs.aethir.com/checker-guide/how-to-manage-checker-nodes/api-for-querying-license-rewards.md | Fetched — **premium partners only** |
| Container staking / rewards | https://docs.aethir.com/aethir-network/the-container/staking-and-rewards | HTTP 200 |
| ATH staking key info | https://docs.aethir.com/aethir-staking/staking-key-information.md | Fetched |
| Cloud host operational requirements | https://docs.aethir.com/aethir-cloud/aethir-cloud-host/operational-requirements-for-cloud-hosts | Summarized via docs search / page content |
| OpenSea collection (secondary) | https://opensea.io/collection/aethir-checker-license | HTTP 200 |
| Ecosystem “key information” page | https://ecosystem.aethir.com/aethir-checker-nodes-key-information | **HTTP 404** as of 2026-08-19 |

### On-chain (Arbitrum One)

Official purchase docs cite authenticity check on Arbiscan for:

`0xc227e25544edd261a9066932c71a25f4504972f1`

Direct `eth_call` via `https://arbitrum-one-rpc.publicnode.com` (2026-08-19):

| Call | Result |
| --- | --- |
| `name()` | `Aethir Checker License` |
| `symbol()` | `ATHCL` |
| `totalSupply()` | **91759** |

So the Checker License NFT collection is real, live, and non-trivial in size.
(Arbiscan HTML itself returned HTTP 403 from this environment; contract state
was read from RPC, not from the explorer UI.)

### Rewards API probe

Docs: `POST https://app.aethir.com/console-api/v2/client/query-daily-reward`  
Requires partner-issued `x-ak` / `x-op-token` (premium partners).

Unauthenticated POST with `{"licenseIds":[1]}` returned HTTP 200 body:

```json
{"code":135500,"msg":"The system is busy. Please try again later","data":""}
```

`https://app.aethir.com/console-api/v2/` without credentials → HTTP 401.  
**No public, keyless bulk rewards API** was found for adapter-style pulls.

`https://stake.aethir.com/` TLS handshake timed out from this environment —
staking may still exist (docs describe Ethereum-mainnet ATH staking), but the
stake UI was **not** confirmed reachable here.

---

## What’s actually reachable right now

| Surface | Reachable? | Notes |
| --- | --- | --- |
| Official docs | Yes | Primary evidence source |
| Checker Owner Portal (`app.aethir.com`) | Yes (UI) | Wallet/KYC flows not exercised beyond HTTP 200 |
| Checker License NFT (Arbitrum) | Yes | `name`/`symbol`/`totalSupply=91759` via RPC |
| OpenSea secondary market listing | Yes (page) | Supporting transferability context only |
| License daily-rewards API | Partner-gated | Docs say premium partners; unauthenticated probe not usable |
| Ecosystem “key information” URL | No (404) | Do not rely on that page |
| Stake UI (`stake.aethir.com`) | Not confirmed | Handshake timeout here |
| Public farm-/asset-level yield API analogous to Glow GCA | **Not found** | — |

---

## Mechanism analysis (the question that matters)

### 1) Cloud Host / Container provider — contribute GPU hardware

Official cloud-host requirements: bare-metal x86 servers, Ubuntu 20.04/22.04,
enterprise GPUs, HostAgent, public IP/SSH, then stake ATH to activate. Rewards
are tied to providing compute (PoC / PoD / service fees).

**This is classic contribute-your-own-hardware.** Same family as Render /
Filecoin operator models for this platform’s purposes → **`wrong-model`**.

### 2) Checker Node — license NFT + operated client (focus of this investigation)

Official license doc (verbatim substance):

> The Checker Node License, which is an ERC721 NFT, **allows you to earn
> rewards by running a Checker Node Client**. You can choose to run your
> Checker Node Client on your own machine, through a VPS or NaaS, or
> delegate to another user's machine.

Hardware for the **Checker Client** (not a GPU rack, but still operated
infrastructure):

- 64MB RAM, 1× x86 CPU @ 2.1GHz, 10GB disk, 10Mbps — per license, scales
  linearly; uptime / correct task results required; bans for repeated wrong
  calculations.

Owner ↔ operator flow (official):

1. Owner purchases license NFT  
2. Operator creates burner wallet in Checker Client GUI/CLI  
3. Owner delegates via Checker Owner Portal  
4. Operator accepts in Client  
5. **Owner earns rewards** (viewable in portal)

**NaaS path:** official docs say you can delegate the NFT to a NaaS partner
(Animoca, Easeflow, Luganodes, Infstones, Nodeops, DepinX, SuperNoderz listed)
and “earn rewards automatically” while they run the client. That means the
**license buyer need not run the software themselves** — but **someone must
still operate a Checker Client** continuously. Capital buys a **right to an
operated network-checking role**, not a financed share of GPU rental cash
flows.

**Payout shape (official reward math):**

- Base rewards: daily; share of a pool equal to **10% of total platform
  tokens** over four years; proportional to tasks completed by the license vs
  network total.
- Bonus rewards: quarterly; **5% of total platform tokens** over four years;
  requires **>95% uptime** (from fifth quarter post-TGE); proportional to base
  rewards share.

That is **protocol-token emission for performing / keeping checker work
online** — not `direct-revenue-share` on GPU cloud revenue, and not Glow-style
financing of a physical productive asset’s protocol deposit.

**Comparison to this platform’s bar**

| | Glow / RealT / Elmnts | Aethir Checker |
| --- | --- | --- |
| Participant action | Provide capital; do not operate network nodes | Buy license; **a Checker Client must run** (self / VPS / NaaS) |
| Economic claim | Financed asset / property / mineral rights economics | Share of ATH emission pool for validation tasks |
| Closest analogy | Passive RWA / DePIN financing | Helium-style **node license + operator** (even if operator is outsourced) |

NaaS makes Checker **more passive for the buyer**, but it does **not** convert
the model into capital provision against a financed real asset. It remains an
active network-operator role with outsourced ops — **`wrong-model`**.

### 3) ATH token staking — capital lock, different product

Docs describe Ethereum-mainnet ATH staking with weekly epochs, variable
rewards, lock periods from one week to four years, reward power =
staked amount × epochs in lock. That is **generic protocol-token staking**,
not financing GPU inventory or a RealT-like claim on external cash flow. It
is capital-only in a narrow sense, but it is **not** a DePIN/RWA yield
opportunity of the kind this platform indexes. It does not rescue Checker or
Cloud Host into `candidate-for-adapter`.

---

## Classification rationale (summary)

**`wrong-model`** because:

1. **Cloud Host** explicitly requires contributing and operating GPU
   hardware.  
2. **Checker Node** — the capital-looking tier — still requires an operated
   Checker Client; official docs tie earning to running that client; NaaS only
   outsources operation. Rewards are ATH emissions for check-task / uptime
   work, not a direct claim on GPU rental revenue.  
3. No Glow/RealT-like “finance the asset, don’t operate the network” path was
   found for Checker or Cloud Host.

This is **not** `not-yet-investable`: licenses, portal, and NFT supply are
live.  
This is **not** `candidate-for-adapter`: reachable data exists, but the
**economic model** fails the passive capital-provision test.  
This is **not** `insufficient-information` on the Checker hardware-vs-capital
question: official docs answer it directly.

---

## Explicit unknowns / what would be checked next (if revisited)

These do **not** change the classification above, but should be noted:

- Exact NaaS fee splits and whether any NaaS product markets a “revenue share
  of GPU rentals” (no such claim found in official Checker docs; would need
  partner terms).
- Whether any separate Aethir product finances third-party GPU CapEx with
  investor claims on rental income (not found in the docs paths checked).
- Stake UI reachability (`stake.aethir.com` timed out here).
- Partner rewards API field-level schema under real credentials (gated).

---

## Decision for this research log

| Field | Value |
| --- | --- |
| Classification | **`wrong-model`** |
| Adapter recommended? | **No** |
| Live platform impact | **None** — `candidates/` only |
