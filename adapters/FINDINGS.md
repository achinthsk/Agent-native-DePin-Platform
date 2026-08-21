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

### Later addition (2026-08-20) — transfer-side caveat, not a data-read correction

The Step 2 findings above remain accurate for their scope: Glow’s **public
data / read access** (GCA HTTP, on-chain `eth_call`) is genuinely reachable
without permission. That conclusion about **data verifiability is unchanged**.

A later Step 7 investigation found that the **GLW token contract itself**
(`GlowGuardedLaunch` / `GLW-BETA`) blocks transfers to arbitrary
unallowlisted smart contracts while guarded launch is active. So a blanket
“permissionless” label for Glow as a whole is incomplete once token custody
and contract composability are in scope. Full write-up:
[`execution/GLW_GUARDED_LAUNCH_FINDING.md`](../execution/GLW_GUARDED_LAUNCH_FINDING.md).
This is an **addition**, not a rewrite of the read-path findings above.

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

## Part C — RealT (investigation date: 2026-08-12)

### What was checked

1. **Official RealT site / FAQ / PPM**
   - `https://realt.co` (marketing site) is reachable; property economics are
     not exposed as a structured public API there.
   - FAQ confirms weekly rental income in USDC (Ethereum, claim) or USDC/xDAI
     (Gnosis, airdropped to the registered income wallet). KYC/AML is required
     to **purchase / hold / transfer** tokens; it is **not** required merely to
     read public community property metadata or the public rent tracker.
   - Private Placement Memoranda (e.g. Series #1 Marlowe, Series #3 Fullerton)
     state U.S. offerings are conducted under **Rule 506(c) of Regulation D**
     (accredited investors) and offshore sales under **Regulation S**. This
     adapter therefore uses `regulatory_wrapper: reg-d-506c` for the U.S.
     Reg D path — confirmed from RealT's own PPM language, not copied from
     Elmnts by habit. Schema has no separate Reg S enum; Reg S eligibility for
     non-U.S. persons is noted in description text / jurisdictions fields.

2. **Community property API**
   - Documented host `https://api.realt.community/v1/token` — TLS handshake
     **reset** from this environment (unreachable here).
   - Working host: **`https://api.realtoken.community/v1/token`** — public GET,
     no login. Returns ~829 tokens with `fullName`, `tokenPrice`,
     `ethereumContract` / `gnosisContract` / `xDaiContract`, `productType`
     (including `real_estate_rental`), etc. Cloudflare sometimes returns
     **403** under automated traffic; retries / cooldown may be required.
   - Per-token detail routes exist but are also subject to the same 403
     behavior; the list payload alone is enough for identity + token price.

3. **The Graph subgraphs** (`realtoken-thegraph/realtoken-xdai`,
   `realtoken-eth`) — hosted service redirects fail / gateway requires an API
   key. **Not used** for this adapter (no Graph key assumed).

4. **On-chain (Gnosis)** — public RPC `eth_call` works. Example for
   `0xFe17C3C0B6F38cF3bD8bA872bEE7a18Ab16b43fB` (15777 Ardmore):
   `name()`, `symbol()`, `totalSupply()` succeed. Rent on Gnosis is
   **airdropped** as USDC/xDAI to many holder wallets from RealT distribution
   flows — there is **no** practical public mapping from a raw Transfer log
   back to "this payment was for property X" without RealT's per-token rent
   schedule. So: platform-level payments are on-chain; **property-level
   attribution is not independently recoverable from chain alone** (same class
   of problem as Glow farm→delegator attribution, but for a different reason).

5. **Public weekly rent history (property-level)**
   - Community **RealToken rent tracker**
     `https://ehpst.duckdns.org/realt_rent_tracker/` (no login) exposes, for a
     token address, a Chart.js series of **weekly annualized yield %** from
     **2021-02-28 through 2026-02-01**, stated to be based on **"publicly
     available weekly RealT master rent files"**.
   - For Ardmore, the tracker also prints the average weekly rent per token
     implied by that series and the token price. This is the first source in
     this project that yields a real multi-year, property-specific payment
     history suitable for a non-null `realized_yield_pct`.

### What is actually reachable right now

| Data | Reachable? | Mechanism |
| --- | --- | --- |
| Property / token list, token price, contract addresses | Yes (with CF flakiness) | `GET https://api.realtoken.community/v1/token` |
| On-chain token metadata (name/symbol/supply) | Yes | Gnosis `eth_call` |
| Property-level weekly rent / annualized yield history | Yes | Public rent tracker (master rent files) |
| Independent eth_getLogs attribution of USDC/xDAI airdrops → one property | **No** | Airdrops are not property-tagged on-chain in a way this adapter can decode without the master rent schedule |
| Official Control-style RealT private portfolio APIs | Not used | Would require investor login/KYC — out of scope |

### Schema fit

- Needs new `asset_class`: **`real-estate-rental`** (schema bumped to **1.1.0**).
- Needs new `source_platform`: **`realt`**.
- `payout_mechanism_type`: **`direct-revenue-share`** (net rental income in
  stablecoins) — matches FAQ/PPM, not a token-emission reward.
- `regulatory_wrapper`: **`reg-d-506c`** per PPM Rule 506(c) language for U.S.
  purchasers; `accreditation_required: true`.

### Choice for the RealT adapter (and why)

**Primary:** community API for property identity + token price, plus the
public rent tracker’s weekly annualized-yield series (from RealT master rent
files) to compute `realized_yield_pct`.
**Enrichment:** Gnosis `eth_call` to confirm the token contract.
**Not used:** The Graph (needs key / broken hosted URL); `api.realt.community`
(TLS reset here); any KYC-gated RealT portfolio endpoint.

### Realized yield method (explicit)

For a property with weekly annualized yield observations
`y_1 … y_n` (percent) and API `tokenPrice` `P`:

1. Treat each `y_t` as the annualized rent rate for that week implied by the
   master rent file (`weekly_rent_t = (y_t/100) * P / 52`).
2. `realized_yield_pct = mean(y_1 … y_n)` over the full observed window
   (including zero-rent weeks). Equivalent to
   `(sum weekly_rent_t / P) / (n/52) * 100`.
3. `completed_payout_cycles = count of weeks with y_t > 0`.
4. **Do not** copy RealT marketing “expected APY” into `realized_yield_pct`.
   `advertised_yield_pct` stays `null` unless a marketed figure is actually
   present on the public payload used (the slim public list has no APY field).

### Verification tier choice

`verification_tier: self-reported-unverified` for the **rent-amount / yield**
facts: property-level weekly amounts come from RealT’s published master rent
files (via the public tracker), not from independently decoded on-chain
Transfer logs for that property. Token contracts and supplies are on-chain
(stronger evidence than Elmnts for existence), but that does not upgrade the
rent-attribution tier under this schema’s definitions. Notes field records
both facts.

