# Mining royalty tokenization (category) — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-08-21  
**Investigator note:** Backlog-order discovery simulating
`workflow_dispatch` with **empty** `candidate_name`
(`python3 scheduler/run_discovery.py --trigger manual`). Research log
only. No adapter, schema, scoring, storage, or API changes accompany this
document beyond this FINDINGS file and the candidates index row. Elmnts
was not touched. `execution/` was not invoked. **Backlog pointer
advanced** (`2 → 3`).

Category probe: is there a live **capital-only mining royalty** path with
public adapter-grade data? Seeds on `scheduler/backlog.json` were fetched
live; none resolved to a mining-royalty product.

---

## What was checked

| Source | URL | Result |
| --- | --- | --- |
| Vultisig | https://www.vultisig.com/ | HTTP 200 — **MPC wallet** (seedless multi-chain vault). Not mining royalties. |
| mineralized.io | https://mineralized.io/ | DNS NXDOMAIN — unreachable |
| www.mineralized.io | https://www.mineralized.io/ | DNS NXDOMAIN — unreachable |
| Tangible | https://www.tangible.store/ | HTTP 200 — RWA tokenization (USTB treasuries, real-estate “BASKETS” TNFTs). Not mining royalties. |
| Goldfinch | https://goldfinch.finance/ | HTTP 200 — private credit onchain; banner: **“Goldfinch Prime is shutting down. No new deposits will be taken.”** Not mining royalties. |

### What’s actually reachable right now

| Surface | Reachable? | Notes |
| --- | --- | --- |
| Live mining-royalty tokenization product in seeds | **No** | Seeds miss the category |
| Public royalty cashflow API / on-chain royalty NFT with open data | **Not found** | — |
| Adjacent RWA (Tangible) | Yes | Wrong asset class for this probe |
| Adjacent credit (Goldfinch) | Yes but shutting down Prime | Wrong asset class |

---

## Mechanism vs this platform’s capital-provision bar

No seed described a capital-only claim on mine / mineral royalty cashflows
with public readable economics. Tangible’s real-estate baskets and
Goldfinch’s private credit are capital-ish but **out of category**.
Vultisig is wallet infrastructure (wrong-model family for yield).

---

## Classification

**`insufficient-information`**

Cannot promote a mining-royalty adapter target from these seeds. Replace
seeds with actual royalty/mineral platforms (if any are live and public)
before a stronger disposition.

---

## Can the four scores be computed?

**No.**

---

## Explicit unknowns / next checks

1. Identify real mining-royalty tokenization issuers (names + URLs) and
   re-queue them as concrete candidates.
2. Confirm whether any Tangible product ever covers mineral royalties
   (not evidenced on homepage text fetched today).

---

## Scheduler notes

- Trigger: **`manual`** / **`backlog_order`** (empty `candidate_name`).
- `next_index` advanced `2 → 3` (next scheduled/empty run = tokenized-farmland,
  already investigated via named override — human may skip or re-check).
