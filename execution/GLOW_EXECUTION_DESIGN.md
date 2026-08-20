# Glow execution design — investigation only (Step 7, Part A)

**Date:** 2026-08-20  
**Scope:** Answers to five pre-build questions with cited evidence. **No
execution, adapter, or wallet code** is produced in this task. Part B builds
only after human review of this document.

**Standard:** Same as `adapters/FINDINGS.md` / `candidates/*/FINDINGS.md` —
what was checked, what is reachable, what is still unknown. Do not treat
marketing copy as an on-chain interface.

---

## Executive summary (for reviewers)

| Question | Short answer |
| --- | --- |
| 1. What on-chain call finances a farm? | **Real callable path today:** `OffchainFractions.buyFractions(...)` on mainnet `0x80EA8524…F7db`, buying “steps” of a Launchpad fraction whose metadata (creator, `bytes32 id`, step size, payment token) comes from Glow’s **Hub API**. This is **not** `MinerPoolAndGCA` and **not** `GLOW.stake`. It is **new-farm protocol-deposit crowdfunding** (all-or-nothing listing), not “only share rewards on an already-live farm.” |
| 2. Must GLW be acquired first? | **Usually yes** for the GLW leg (payment token on live listing = GLW). Acquire via Uniswap V2 GLW–USDG (and often ETH→USDC→USDG first). Pool is thin (~$301k USDG side at investigation); Glow’s own app defaults to **5%** slippage. Hard `amountOutMin` / size caps required. |
| 3. Testnet? | **Sepolia addresses exist** for OffchainFractions / GLW test tokens in `@glowlabs-org/utils`, but **live Launchpad listings were only confirmed on the production Hub**. Glow’s own frontend tests use **Anvil mainnet forks**. **Recommend Anvil/Hardhat mainnet fork** as the Part B proving ground. |
| 4. Spending limits (non-custodial)? | **Part B: platform soft limits only** (refuse to construct / quote above configured USD or GLW). Honest: bypassable outside the tool. **On-chain hard caps (session keys / AA) = future upgrade**, not implied shipped. |
| 5. Test wallet without platform keys? | **Agent-owned local key** (env / OS keychain, never uploaded) or **wallet-extension / WalletConnect** for interactive tests; fork tests may **impersonate** via Anvil without holding a mainnet key. Platform must never custody. |

---

## Q1 — What does “delegating capital to a Glow farm” require on-chain, right now?

### What official product docs say

Glow V2 Launchpad (product description, not ABI):

- https://glow.org/blog/guide-to-delegating-glow  
- https://glow.org/blog/delegating-with-gctl  
- https://glow.org/blog/the-simple-way-to-fund-solar  

Delegators post **protocol deposits** (GLW, and/or sGCTL / other assets) so a
listed farm can go live. Listings are fractional (“steps”); fill is
**all-or-nothing**; incomplete listings expire (~4 weeks in the guide) with
refunds. Commitment horizon described as **100 weeks**. Rewards: deposit
recovery (+ surplus/forfeit dynamics) and a share of GLW emissions.

That is **crowdfunding a farm’s entry deposit**, not “stake GLW somewhere
generic for emissions.”

### What is *not* the farm-finance call

**Guarded-launch `MinerPoolAndGCA`**  
`0x6Fa8C7a89b22bf3212392b778905B12f3dBAF5C4`  
(source: https://github.com/glowlabs-org/glow-contracts README “Live Guarded
Launch Addresses”; also `adapters/FINDINGS.md`)

Public write surface includes bucket claims / GCA flows — **not** a
“delegate to farm ShortID” function for Launchpad deposits. Prior adapter
work correctly used it for **read** of weekly buckets only.

**`GLOW.stake(uint256 stakeAmount)`** on  
`0xf4fbC617A5733EAAF9af08E1Ab816B103388d8B6`  
(source: `glow-contracts/src/GLOW.sol`)

This manages **GLW token staking / unstake-position accounting on the GLW
contract itself**. It is **not** the Launchpad protocol-deposit purchase.
Do not conflate “stake GLW” with “delegate to a farm.”

### What *is* the farm-finance call (confirmed)

**Contract (Ethereum mainnet):**  
`OffchainFractions` = `0x80EA852448c2807BeAe321deC7c603990209F7db`  

- Published in `@glowlabs-org/utils` `src/constants/addresses.ts` (`getAddresses(1)`).  
- Verified this investigation: `eth_getCode` → **10,927 bytes** (real
  contract, via Tenderly public mainnet RPC).

**Function (from published ABI
`@glowlabs-org/utils` `src/lib/abis/offchainFractions.ts`):**

```text
buyFractions(
  address creator,
  bytes32 id,
  uint256 stepsToBuy,
  uint256 minStepsToBuy,
  address refundTo,
  address creditTo,
  bool useCounterfactualAddressForRefund
)
```

**Typical prerequisite:** ERC-20 `approve(OffchainFractions, amount)` on the
fraction’s payment token (for GLW listings: GLW).

**Parameter meanings (from SDK `BuyFractionsParams` + frontend
`usePatchedOffchainFractions` in `glowlabs-org/glow-smart-route-nextJS`):**

| Param | Role |
| --- | --- |
| `creator` | Fraction creator / owner on-chain (Hub listings use Glow hub manager wallet) |
| `id` | `bytes32` fraction id |
| `stepsToBuy` | Number of fractional steps to purchase |
| `minStepsToBuy` | Minimum acceptable fill (partial-fill / race protection) |
| `refundTo` | Refund recipient if listing fails / expires |
| `creditTo` | Address credited for the purchase |
| `useCounterfactualAddressForRefund` | Refund-via-counterfactual-holder flag |

**Discovery is off-chain; settlement is on-chain.** Live listing source
confirmed this investigation:

- Hub: `https://gca-crm-backend-production-1f2a.up.railway.app`  
  (default in Glow frontend `lib/server/headline-stats.ts`)
- `GET /applications/sponsor-listings-applications` → HTTP 200, live auction
  applications with `activeFraction`
- Example live fraction (2026-08-20 pull):

| Field | Value |
| --- | --- |
| Application id | `5b4d8b87-3a23-45c9-856c-949324e63559` |
| `activeFraction.id` | `0x51ab76b04053b16422787348785f051b636f7b0e066ffc9bcf4bab5b2116c53d` |
| `activeFraction.owner` (→ `creator`) | `0x2b57e1bf5071c6579f2145b367eec34f8729aa9c` (= `FOUNDATION_HUB_MANAGER_WALLET` in utils addresses) |
| `token` | GLW `0xf4fbC617…d8B6` |
| `isCommittedOnChain` | `true` |
| `totalSteps` / `splitsSold` / remaining | 106 / 13 / 93 |
| `step` (wei GLW per step) | `1740639358686088571708` (~1740.64 GLW) |
| Create tx | `0x098fed11269d192fed49588b222e7a4cba409126bce1d3a7f1136552a0b1246b` |
| Expiration | `2026-09-15T12:58:56.306Z` |

Also: `GET /fractions/total-actively-delegated` →
`totalGlwDelegatedWei` ≈ **5.26e24** wei (~5.26M GLW), `totalWallets` 190 —
protocol has material delegated inventory, not a paper feature.

Control API host `https://api-prod-34ce.up.railway.app` responds
`Glow Control API` (HTTP 200) and some farm routes work (e.g.
`/farms/1/weekly-rewards`), but **`/farms/sponsored` returned 404** here.
**Launchpad purchase discovery for Part B should treat Hub listings as the
confirmed source**; Control API is not fully mapped in this investigation.

### Which flow is real? (direct answer)

| Flow | Real today? |
| --- | --- |
| A. New financer posts fractional protocol deposit toward a **Launchpad-listed farm** via **`buyFractions`** | **Yes** — on-chain function + live Hub listing with `isCommittedOnChain: true` |
| B. Purely off-chain application to Glow with no user tx | **No** as the settlement path — Hub/app orchestrate, but money moves via approve + `buyFractions` |
| C. Only `GLOW.stake` / MinerPool reward-share on already-built farms | **Different product** — do not use as the “delegate to farm” design |

**Still unknown (must not invent):** exact post-`RoundFilled` / closer
pipeline that moves collected GLW into the long-lived protocol-deposit /
deposit-recovery accounting. Part B can settle `buyFractions` without
fully documenting that downstream bookkeeping, but claiming “deposit
recovery starts immediately on buy” needs a follow-up eth_call / event
trace before promising UX copy.

**sGCTL path:** Glow docs + frontend describe a separate Monday sGCTL window
with EIP-712 stake/delegate messaging (`delegateSgctlEIP712Types` in
deposit orchestrator). Payment token sentinel
`SGCTL_OFFCHAIN_TOKEN_ADDRESS = 0xSGCTL000…` in utils shows sGCTL is **not**
a normal mainnet ERC-20 buy. Part B should **start with the GLW leg**
(`buyFractions` + ERC-20 GLW), and treat sGCTL as a later phase.

---

## Q2 — If GLW must be acquired first: requirements and slippage risk

### Acquisition path Glow’s own app uses

From `glow-smart-route-nextJS` deposit / swap hooks (and utils addresses):

1. Optional: ETH → USDC (Uniswap V3 router addresses appear in
   `useSwapETHToUSDC` for some flows).  
2. USDC → USDG (Glow USDG redemption / wrap path).  
3. USDG → GLW on **Uniswap V2** via router  
   `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`  
   pair factory-confirmed GLW–USDG:  
   `0x6FA09ffC45F1dDC95c1bc192956717042f142c5d`  
   (also `scoring/GLW_PRICE_EMISSIONS_FINDINGS.md`).  
4. `GLW.approve(OffchainFractions, …)` then `buyFractions`.

If the agent **already holds GLW**, step 3 can be skipped.

### Measured pool depth (this investigation, Tenderly public RPC)

| Metric | Value |
| --- | ---: |
| USDG reserve | ≈ **301,028.91** |
| GLW reserve | ≈ **1,349,630.80** |
| Spot (USDG/GLW) | ≈ **0.2230** |
| GLW `totalSupply` | ≈ **48.47M** |
| FDV at spot | ≈ **$10.8M** (not circ; circ not independently verified here) |

Prior research cited ~$5.46M market cap and ~−94% peak→trough price path
(`scoring/GLW_PRICE_EMISSIONS_FINDINGS.md`). **Price risk and thin book are
confirmed structural facts**, regardless of which mcap definition is used.

**Constant-product impact (approx., 0.3% fee, buying GLW with USDG):**

| USDG spent | ≈ GLW received | ≈ premium vs spot |
| ---: | ---: | ---: |
| 50 | 223 | 0.32% |
| 250 | 1,117 | 0.38% |
| 1,000 | 4,455 | 0.63% |
| 2,000 | 8,881 | 0.97% |

One Launchpad **step** on the live listing is ~**1,741 GLW** ≈ **$388** at
spot — a single step is already a non-trivial clip relative to a ~$300k
USDG book. Multi-step buys compound impact and MEV risk.

### Slippage / price-limit protection required on the **acquisition** step

Glow frontend defaults (`lib/swap-slippage.ts`):

- `DEFAULT_SLIPPAGE_TOLERANCE = "5"` (**5%**)  
- `DEFAULT_SLIPPAGE_BPS = 500n`  
- Helpers compute Uniswap V2 `amountOutMin` from quoted out × slippage.

**Part B must:**

1. Quote via reserves / router `getAmountsOut` immediately before send.  
2. Set hard **`amountOutMin`** (and deadline) on
   `swapExactTokensForTokens` (or ETH variants).  
3. Cap notional per tx and per day (see Q4) — thin pool ⇒ size limit is a
   safety control, not just UX.  
4. Revert / abort if spot moved beyond configured band between quote and
   simulation.  
5. Never treat aggregator prices as authority (prior GLW tracker failures).

**Risks to state plainly to agents:** acquisition can fail or fill poorly
even when `buyFractions` would succeed; GLW can move sharply after fill
while deposit is locked for the listing/100-week horizon.

---

## Q3 — Testnet vs “test before real money”

### What exists

| Environment | Evidence | Usable for Part B? |
| --- | --- | --- |
| **Ethereum mainnet** | Live OffchainFractions, GLW, pair, Hub listings | Production only |
| **Sepolia** | Distinct addresses in `@glowlabs-org/utils` `sepoliaAddresses`, including `OFFCHAIN_FRACTIONS: 0x5Ad30F90…a05D2`, test GLW/USDG | Contracts exist in the address book; **no Sepolia Launchpad listings confirmed** in this investigation (Sepolia RPC probes from this environment were 403) |
| **Goerli** | Historical forks in `glow-contracts` tests | **Dead network** — do not plan on it |
| **Anvil / Hardhat mainnet fork** | Glow frontend ships
  `__tests__/mainnet-fork-high-slippage-buys.test.ts` (Anvil,
  `PINNED_FORK_BLOCK`, real GLW/USDG/router addresses, opt-in
  `RUN_MAINNET_FORK_TESTS=1`) | **Yes — recommended** |

### Recommendation

**Primary:** local **Anvil (or Hardhat) fork of Ethereum mainnet**, pinned
block, impersonation / funded test EOA, against real
`OffchainFractions` + Uniswap V2 pair bytecode and (when forking a block
with an open listing) real fraction state — **or** createFraction on the
fork for a synthetic listing if live listings are awkward to pin.

**Secondary / optional:** Sepolia only if Glow confirms public test
listings + Hub endpoints for that chain. Do not assume Sepolia mirrors
production Launchpad inventory.

**Not sufficient alone:** unit tests against mocked ABIs without a fork —
they will not catch allowance, slippage, or `InsufficientSharesAvailable`
races.

---

## Q4 — Spending limits under non-custodial architecture

The platform **never holds funds**, so it cannot stop a user who bypasses
the tool and builds their own calldata.

### Option A — Platform soft limits (recommended for Part B)

**Mechanism:** tool refuses to **quote, simulate, or construct** a swap /
`buyFractions` above configured ceilings (per-tx USD, per-tx GLW steps,
daily aggregate per agent id).

| Pros | Cons |
| --- | --- |
| Implementable immediately | Bypassable outside the platform |
| Matches non-custodial stance | Not a cryptographic guarantee |
| Aligns with thin GLW liquidity | Needs clear UX: “limit is tool policy, not chain law” |

### Option B — On-chain hard enforcement (session keys / AA / allowances)

Patterns in the abstract: ERC-4337 session keys, spending-limited smart
accounts, Permit2 allowances scoped to router + OffchainFractions, EIP-7702
delegations.

**Glow-specific feasibility (honest):**

- Glow’s own app **detects and often blocks** smart-account / EIP-7702
  paths for some flows (`detectSmartAccount.ts`, deposit preflight
  `handleSmartAccountCheck`). Building Part B **assuming AA session keys
  work against Glow’s contracts/UX** is unsafe without a dedicated spike.
- `buyFractions` pulls ERC-20 via allowance to **OffchainFractions only** —
  a user can still set unlimited allowance; Permit2/session scoping would
  be **extra infrastructure we own**, not something Glow provides today.
- Unlimited `approve(OffchainFractions, type(uint256).max)` is the common
  wallet pattern and **defeats** “allowance as spend cap” unless Part B
  always uses exact allowances and users never widen them elsewhere.

### Recommendation

| Stage | Policy |
| --- | --- |
| **Part B (now)** | Soft limits + exact (or tightly buffered) ERC-20 allowances + mandatory swap `amountOutMin` + simulate-before-send. Document bypassability in agent-facing copy. |
| **Future upgrade (explicit)** | Optional smart-account / session-key spend envelopes — **only after** a Spike proves compatibility with Glow `buyFractions` and Hub flows. **Do not imply this exists** in Part B. |

---

## Q5 — Test agent wallet without the platform holding a key

Goal: prove non-custodial design, not “custody for convenience in staging.”

| Pattern | Platform holds key? | Use |
| --- | --- | --- |
| **A. Agent-local EOA** — key only in agent env / OS secret store; platform receives **unsigned or user-signed intent**, never the key | No | Integration tests that hit fork or (carefully) tiny mainnet |
| **B. Browser extension / WalletConnect / Privy user wallet** — human or agent UI triggers signatures | No | Interactive dry-runs |
| **C. Anvil `impersonateAccount` / `deal`** on a fork | No mainnet key at all | Default CI / Part B automated tests |
| **D. Platform-hosted hot wallet “just for tests”** | **Yes — forbidden** | Do not build |

**Part B rule:** test harnesses use **A or C**; production path uses **B**
(or A for autonomous agents that keep keys off-platform). Logging must
never persist raw private keys. CI secrets for fork RPC URLs are fine;
CI secrets that are **spending keys for mainnet** are not.

---

## Recommended concrete architecture for Part B

Build a **non-custodial Glow Launchpad GLW-leg executor** with this shape:

```text
[Agent / operator]
    │  intent: farm listing id, max USD, max steps, slippage bps
    ▼
[Platform execution service — no keys]
    │  1. GET Hub /applications/sponsor-listings-applications (or by id)
    │  2. Read activeFraction { owner, id, token, step, remainingSteps, expiration }
    │  3. Enforce soft limits (reject if over policy)
    │  4. If GLW balance < required: build Uniswap V2 swap tx skeleton
    │       with amountOutMin from fresh quote × slippage bps (default ≤ Glow’s 5%,
    │       configurable tighter)
    │  5. Build GLW.approve(OffchainFractions, exact-or-buffer)
    │  6. Build OffchainFractions.buyFractions(creator=owner, id, stepsToBuy,
    │       minStepsToBuy, refundTo, creditTo, false)
    │  7. eth_call / simulate bundle; return unsigned txs or WalletConnect payload
    ▼
[Agent wallet signs & broadcasts]  ← key never on platform
```

**Out of Part B scope (flag, don’t silently skip):**

- sGCTL EIP-712 delegation leg  
- Claiming that deposit-recovery accounting is fully understood post-fill  
- On-chain hard spend limits / AA session keys  
- Relying on Control API `/farms/sponsored` until paths are re-verified  

**Success criteria for Part B demo (suggested):**

1. On Anvil mainnet fork: simulate approve + `buyFractions` against a pinned
   open fraction (or fork-created fraction) with soft limit enforced.  
2. Show swap path with `amountOutMin` reverting when slippage exceeded.  
3. Show platform rejection when intent exceeds configured cap.  
4. Prove no private key material in platform logs/env for the “service”
   role.

---

## Explicit unknowns / next checks before or during Part B

1. **Post-fill deposit pipeline** — event trace from `FractionSold` /
   `RoundFilled` to protocol-deposit recovery wallets (needs dedicated
   explorer/RPC work).  
2. **Sepolia Launchpad inventory** — whether Hub has a test base URL with
   listings.  
3. **Control API vs Hub** — which endpoints are canonical for production
   agents long-term (`api-prod-34ce…` vs `gca-crm-backend-production…`).  
4. **Exact allowance buffer policy** Glow uses in production buys
   (`approvalBufferAtomic` defaults in frontend).  
5. **Circ circulating supply** for mcap messaging (FDV ≠ circ).

---

## Sources checklist (primary)

| Source | Role |
| --- | --- |
| https://glow.org/blog/guide-to-delegating-glow | Product mechanics |
| https://glow.org/blog/delegating-with-gctl | sGCTL / schedule |
| https://github.com/glowlabs-org/glow-contracts | MinerPool / GLOW.stake |
| `@glowlabs-org/utils` addresses + `OFFCHAIN_FRACTIONS_ABI` | Canonical buy API |
| `glowlabs-org/glow-smart-route-nextJS` deposit / fractions hooks | How app actually calls it |
| Hub `…railway.app/applications/sponsor-listings-applications` | Live listing + on-chain ids |
| Hub `…/fractions/total-actively-delegated` | Scale of delegation |
| Uniswap V2 pair `0x6FA09ffC…2c5d` reserves | Liquidity / slippage |
| `scoring/GLW_PRICE_EMISSIONS_FINDINGS.md` | Historical price path |
| Frontend Anvil fork tests | Official “test without mainnet funds” pattern |

---

*End of Part A. No code beyond this document was written for execution.*
