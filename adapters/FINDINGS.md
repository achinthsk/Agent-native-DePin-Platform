# Investigation results — written before adapters were treated as final.
# Date of investigation: 2026-08-11.
# Honesty over convenience: if a source was unreachable, that is stated.

## Part A — Glow

### What was checked

1. Official SDK `@glowlabs-org/utils` (npm) documents a **Control API** at
   `https://control-api.glowlabs.org` with farm routers
   (`/farms/sponsored`, `/farms/{id}/weekly-rewards`, reward splits, etc.).
2. DNS lookup for `control-api.glowlabs.org` returned **NXDOMAIN**. The
   hostname does not resolve from this environment right now. The Control API
   is therefore **not a currently reachable data source**, regardless of what
   the SDK README says.
3. Glow's public marketing site `https://glow.org` is up, but has **no public
   farm listing or farm-detail pages** that return structured farm economics
   (sitemap has blog/whitepaper/audits only; `/farms` and `/api/farms` 404).
4. The open-source **glow-subgraph** indexes GCC retirement / governance
   events, **not farm-level reward attribution**, and no working public
   GraphQL endpoint was found that returns farm economics without an API key.
5. **GCA (Glow Certification Agent) backend** at
   `http://95.217.194.59:35015` (listed in `@glowlabs-org/utils` as
   `GCA_URLS`) is publicly reachable with **no login / API key**:
   - `GET /api/v1/equipment` → 227 farms with ShortID, lat/lon, Capacity
     (milliwatts), Debt/ProtocolFee (cents), Initialization/Expiration
     (5-minute timeslots).
   - `GET /api/v1/all-device-stats?timeslot_offset=N` → per-device power
     outputs / impact rates for a week of timeslots.
6. **On-chain Ethereum contracts** (Guarded Launch addresses from
   `glowlabs-org/glow-contracts`) are queryable via public RPC `eth_call`:
   - `MinerPoolAndGCA` `0x6Fa8C7a89b22bf3212392b778905B12f3dBAF5C4`
     - `GENESIS_TIMESTAMP()` → `1700352000` (2023-11-19T00:00:00Z)
     - `currentBucket()` → weekly reward bucket index (observed 142)
     - `isBucketFinalized(bucketId)`, `bucketGlobalState(bucketId)`,
       `bucket(bucketId)` with GCA merkle roots for weekly reports
   - `GLW` `0xf4fbC617A5733EAAF9af08E1Ab816B103388d8B6` (symbol `GLW-BETA`)
   - `RewardsKernel` `0xd6d3139d40a32F8bA71D576c1A743529AB4786BB`
     (`$nextPostNonce()` observed)

### What is actually programmatically reachable right now

| Data | Reachable? | Mechanism |
| --- | --- | --- |
| Farm registry (id, lat/lon, capacity, init timeslot) | Yes | GCA HTTP API `/api/v1/equipment` |
| Farm production telemetry (power / impact rates) | Yes | GCA HTTP API `/api/v1/all-device-stats` |
| Weekly protocol reward buckets / merkle roots | Yes | On-chain `eth_call` to MinerPoolAndGCA |
| Farm-level GLW emissions **to that farm's delegators** | **No** | Merkle leaves are `(payoutWallet, glwWeight, grcWeight)` — no public farm-id→leaf mapping without Control API; Control API DNS is NXDOMAIN |
| Advertised / marketed yield % per farm | **No** | Not on GCA API or readable on-chain getters |
| Control API farm weekly rewards / reward splits | **No** | `control-api.glowlabs.org` does not resolve |

### Choice for the Glow adapter (and why)

**Hybrid: GCA public HTTP API for farm identity + direct on-chain `eth_call`
to MinerPoolAndGCA for protocol reward-bucket state.**

Why not Control API alone: it does not resolve.
Why not subgraph alone: it does not expose farm-level economics.
Why not raw chain alone: farm ShortIDs, locations, and capacities are **not**
stored as named farm entities on MinerPoolAndGCA; they live on the GCA
server. On-chain reports attribute weights to **payout wallets**, not farm
ShortIDs.

### Hard honesty constraint for yield

`realized_yield_pct` must come from observed on-chain reward emissions to
that farm's **delegators**. That attribution is **not** publicly recoverable
from the sources above today. The adapter therefore sets
`realized_yield_pct: null` and fills `yield_calculation_basis` with the real
reason — it does **not** invent a percentage from marketing pages or from
protocol-wide bucket totals.

`verification_tier` is set to `cryptographic-onchain-proof` only for what is
actually on-chain: weekly GCA report merkle roots and reward-bucket state at
MinerPoolAndGCA. Physical production numbers still originate from GCA reports;
this adapter does not independently re-verify satellite imagery.

---

## Part B — Elmnts

### What was checked

1. `https://elmnts.io` — parked **"Coming Soon"** page. No product UI, no API.
2. `https://app.elmnts.io` and `https://docs.elmnts.io` — resolve, but return
   unrelated spam / SEO parking content (not Elmnts product pages). They are
   **not** a usable investor portal or developer docs site from this network.
3. Common API hostnames (`api.elmnts.io`, `invest.elmnts.io`,
   `portal.elmnts.io`, `api.app.elmnts.io`) — do not resolve or do not serve
   Elmnts data.
4. GitHub: no public `elmnts` org/repos returning production/payout APIs
   (search for "elmnts solana" returned 0 relevant public API repos).
5. Press coverage (Decrypt, DL News, Cointelegraph-style reports from the
   Solana beta launch) describes a **permissioned** platform for **accredited
   investors** under Reg D 506(c), with email/password signup and investor
   verification. That is login-gated product access — **not** a public data
   API.
6. No unauthenticated endpoint was found that returns real production,
   payout, or fund NAV/distribution data for Elmnts assets.

### Plain answers to the required questions

- **Is there any publicly accessible endpoint returning real production,
  payout, or fund data — with no login required?**
  **No.** Not at the time of this investigation.
- **If data exists only behind an investor login:** Press materials describe
  accredited-investor onboarding. This investigation did **not** attempt to
  create accounts, bypass auth, or scrape behind a login.
- **If nothing is programmatically accessible:** Correct — nothing usable was
  found.

### Which Elmnts deliverable was built, and why

Built **`adapters/elmnts_manual_entry.py`** (not an automated live adapter).

Reason: there is no public programmatic source to adapt. A fake
`elmnts_adapter.py` that pretended to pull live data would violate the
non-negotiable "never fabricate" rule. The manual-entry tool prompts for
(or accepts a JSON file of) fields taken from public marketing materials,
labels them `verification_tier: self-reported-unverified` and
`retrieval_method: manual-entry`, validates against the schema, and stores a
timestamped snapshot the same way as an automated pull.

---

## IXS (time-permitting note)

Not built in this pass. Same rule would apply: investigate public reachability
first; only write an automated adapter if a real public source exists.
