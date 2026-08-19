# GLW price & emissions — on-chain investigation

Factual record for the `payout_mechanism` risk component. This is **not** a
misconduct finding about Glow. It documents the structural properties of a
`token-emission-reward` payout: newly minted protocol token whose market
price is an independent variable from physical-asset performance.

Investigation date: 2026-08-18.
Method: direct Ethereum JSON-RPC (`eth_call`, `eth_getLogs`) against public
endpoints. **No aggregator price APIs** (those have already mis-keyed this
token). All prices below come from the Uniswap V2 pair’s own `Sync` logs or
`getReserves()`.

---

## Contracts verified on-chain

| Role | Address | How verified |
| --- | --- | --- |
| GLW token (`GLW-BETA`, 18 decimals) | `0xf4fbc617a5733eaaf9af08e1ab816b103388d8b6` | Given; `symbol`/`decimals` via `eth_call` |
| USDG (6 decimals) | `0xe010ec500720be9ef3f82129e7ed2ee1fb7955f2` | Pair `token0` |
| Uniswap V2 factory | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | Canonical V2 |
| **GLW–USDG pair** | `0x6FA09ffC45F1dDC95c1bc192956717042f142c5d` | `factory.getPair(USDG, GLW)` → this address. `token0`=USDG, `token1`=GLW |
| MinerPoolAndGCA (infra rewards) | `0x6Fa8C7a89b22bf3212392b778905B12f3dBAF5C4` | Matches adapters/FINDINGS.md; dominant mint destination |
| GrantsTreasury | `0x0116da066517f010e59b32274bf18083af34e108` | Observed as large mint destination (not a steady weekly drip) |
| VetoCouncil / foundation-side | `0xa3a32d3c9a5a593bc35d69bacbe2df5ea2c3cf5c` | One large observed mint |

Pool address was **not** taken from a third-party tracker. It was resolved
from the Uniswap V2 factory against the token + USDG addresses above.

Spot reserves at investigation time (`getReserves` on the pair):

- USDG reserve ≈ **306,006.74**
- GLW reserve ≈ **1,327,519.16**
- Implied price ≈ **0.2305 USDG per GLW**

---

## Part 1 — Mint events (Transfer from `0x0`)

Docs / whitepaper / 2025 tokenomics claim **fixed weekly** emissions of:

- 175,000 GLW → Infrastructure (MinerPool)
- 40,000 GLW → Grants
- 15,000 GLW → Foundation
- **Total 230,000 GLW / week**

### What the chain actually shows

Full `eth_getLogs` scan of `Transfer(from=0x0, …)` on the GLW token from
pair-launch vicinity through latest (RPC: Tenderly public / Flashbots; chunked
ranges). Results:

| Destination | Mint events | Total GLW minted (sampled era) | Max single mint |
| --- | --- | --- | --- |
| MinerPoolAndGCA | **7,013** | **≈ 17,223,331** | ≈ 114,946 |
| GrantsTreasury (`0x0116da06…`) | 7 large events | ≈ 1,324,304 | ≈ 304,465 |
| VetoCouncil (`0xa3a32d3c…`) | 1 large event | ≈ 366,441 | ≈ 366,441 |

MinerPool mints are **not** one Transfer of exactly 175,000 per week. They are
many small (and some mid-size) mints whose **weekly sum** clusters near the
documented infrastructure figure.

Weekly aggregation (≈50,400 blocks/week buckets over the mint-active window,
**94 weeks with mints**):

| Metric | Value |
| --- | ---: |
| MinerPool weekly median | **≈ 187,002 GLW** |
| MinerPool weekly mean | **≈ 183,227 GLW** |
| Weeks with MinerPool total in 150k–200k | **71 / 94** |
| Weeks with MinerPool total in 160k–190k | **48 / 94** |
| Weeks with *all-dest* total in 200k–260k (doc’s 230k band) | **16 / 94** |

Example weekly MinerPool totals (GLW):

| Approx week block | MinerPool sum |
| ---: | ---: |
| 21122145 | 171,044 |
| 21172545 | 196,801 |
| 21222945 | 198,636 |
| 23138145 | 191,915 |
| 23238945 | 187,305 |
| 25607745 | 191,600 |
| 25708545 | 189,919 |

Example large individual mints (plain numbers from logs):

| Block | Amount (GLW) | To |
| ---: | ---: | --- |
| 24623867 | 366,440.58 | `0xa3a32d3c…` (VetoCouncil) |
| 21816795 | 304,465.08 | GrantsTreasury |
| 22125863 | 246,732.54 | GrantsTreasury |
| 21451856 | 114,945.93 | MinerPoolAndGCA |
| 21555081 | 107,068.75 | MinerPoolAndGCA |

### Verdict on the “fixed weekly emissions” claim

- **Infrastructure (≈175k/week): confirmed at the weekly-aggregate level.**
  On-chain weekly MinerPool mint totals sit near 175k for most active weeks
  (median ≈187k). The delivery shape is many mints per week, not a single
  175,000 Transfer — but the *rate* matches the documented fixed schedule.
- **Grants / Foundation (40k + 15k every week): not confirmed as a steady
  weekly drip.** Observed Grants/Foundation-side mints are **lumpy,
  multi-week batches** (100k–300k+), so calendar weeks rarely total near the
  neat 230k documentation band (only 16/94 weeks in 200k–260k).
- Overall: the chain **supports ongoing, roughly fixed infrastructure
  emission** and **does not contradict** disciplined operation. It also shows
  the picture is messier than “exactly 230,000 every week in three clean
  transfers.”

None of this is evidence of wrongdoing. Fixed or lumpy, these are still
**newly minted protocol tokens**, which is the structural category risk.

---

## Part 2 — Uniswap V2 price history (pair Sync logs)

Source: `Sync(uint112,uint112)` logs on pair
`0x6FA09ffC45F1dDC95c1bc192956717042f142c5d`, sampled roughly weekly from the
earliest Sync through 2026-08-15, plus latest `getReserves`.

Earliest Sync: block **18,809,519** (2023-12-18T01:10:47Z) — matches launch
window. Initial Sync reserves implied ≈ **0.36 USDG/GLW**; within the same
day the weekly sample sits at ≈ **1.47**.

### Selected price points (USDG per GLW)

| Date | Block | USDG reserve | GLW reserve | Price |
| --- | ---: | ---: | ---: | ---: |
| 2023-12-18 | 18809619 | 21,922.04 | 14,919.42 | **1.469** |
| 2024-05-21 | 19918006 | 50,554.99 | 18,673.78 | **2.707** |
| 2024-12-18 | 21429645 | 67,256.85 | 18,091.52 | **3.718** |
| 2025-01-08 | 21579589 | 69,418.71 | 17,554.45 | **3.954** (sample peak) |
| 2025-06-12 | 22688904 | 12,859.15 | 19,320.55 | **0.666** |
| 2025-12-19 | 24047302 | 87,471.43 | 363,976.90 | **0.240** |
| 2026-08-15 | 25763439 | 302,520.08 | 1,312,241.11 | **0.231** |
| latest spot | — | 306,006.74 | 1,327,519.16 | **0.2305** |

### Trend (plain)

- Launch-era weekly sample ≈ **1.47**; peak weekly sample ≈ **3.95** (Jan 2025).
- Latest Sync sample / spot ≈ **0.23**.
- **Peak → latest: about −94%.**
- Emissions to MinerPool continued through this drawdown at roughly the same
  weekly infrastructure rate.

That is the structural point for scoring: a financer paid in GLW can see the
underlying farm perform as designed while the USD value of the reward token
falls sharply. Price path and mint schedule are independent variables.

---

## Part 3 — Implications for risk severity (not accusations)

1. `token-emission-reward` introduces **market-price risk on the payout asset
   itself**, separate from physical production / revenue.
2. On-chain evidence shows Glow’s infrastructure mint rate is **real and
   ongoing at a roughly fixed weekly aggregate**, so this is not a
   theoretical footnote — newly minted supply keeps arriving while price can
   (and did) move by an order of magnitude.
3. Severity chosen for the scoring component is therefore **material but not
   catastrophic**: worse than `direct-revenue-share` / `fixed-interest` (which
   omit this component entirely), comparable in harshness to other structural
   weak signals already in the risk table (e.g. mid/low enum mappings), not a
   Glow-only penalty.

See `scoring/METHODOLOGY.md` § risk → payout mechanism + emission-token
peak decline, `scoring/weights.yaml`, and the machine-readable price
registry `scoring/token_emission_price_history.yaml`.

---

## Part 4 — Explicit reconciliation gap (mint destinations ≠ supply)

The mint scan totals above (MinerPool ≈17.2M + Grants ≈1.3M + VetoCouncil
≈0.37M ≈ **18.9M** GLW in the scanned window) are a **partial destination
ledger**. They are **not** reconciled against ERC-20 `totalSupply()` or a
full circulating-supply series. Other mint recipients, burns, or
pre-window emissions may exist outside those three addresses.

Peak-decline risk scoring uses **Uniswap V2 pool price path only** and
does **not** assume mint destinations sum to supply. Do not treat the
mint tables as a closed supply identity.
