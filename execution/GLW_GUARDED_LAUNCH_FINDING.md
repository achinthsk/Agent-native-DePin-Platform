# GLW transfer restrictions — guarded launch finding

**Date:** 2026-08-20  
**Verdict:** This is a **real, on-chain characteristic** of the deployed GLW
token (`GlowGuardedLaunch` at `0xf4fbC617…d8B6`, symbol `GLW-BETA`). It is
**not** merely an Anvil impersonation artifact. It **does** qualify as a
material correction to any prior assumption that Glow assets are fully
permissionless for arbitrary smart-contract composability. It does **not**
block a normal non-custodial EOA from `buyFractions` on mainnet.

## What the token actually does

Verified source pattern (Etherscan / `GlowGuardedLaunch`):

```solidity
error ErrIsContract();
mapping(address => bool) public allowlistedContracts;

function _update(address from, address to, uint256 value) internal override {
    if (permanentlyFreezeTransfers) revert ErrPermanentlyFrozen();
    if (!_isZeroAddress(from)) {
        _revertIfNotAllowlistedContract(from);
        _revertIfNotAllowlistedContract(to);
    }
    super._update(from, to, value);
}

function _revertIfNotAllowlistedContract(address _address) internal view {
    if (_isContract(_address)) {          // extcodesize > 0
        if (!allowlistedContracts[_address]) revert ErrIsContract();
    }
}
```

Selector `0x7d3bdde5` = `ErrIsContract()` (cast 4byte).

Glow’s own guarded-launch docs describe this intent: block non-Glow smart
contracts from interacting with Glow assets during guarded launch
(https://glow.org/blog/glow-guarded-launch).

## Live eth_call / storage evidence (mainnet state)

| Check | Result |
| --- | --- |
| `allowlistedContracts(OffchainFractions)` | **`false`** |
| `allowlistedContracts(GLW–USDG Uniswap V2 pair)` | **`true`** |
| `allowlistedContracts(MinerPoolAndGCA)` | **`true`** |
| EOA → EOA `transfer` | **succeeds** |
| EOA → `OffchainFractions` `transfer` | **`ErrIsContract`** |
| EOA → Anvil default `#0` (`0xf39F…`) | **`ErrIsContract`** — that address has mainnet code `0xef0100…` (EIP-7702 delegation), so it is a “contract” under `extcodesize` |

## How real Launchpad buys still work

Nine recent `FractionSold` txs for live listing `0x51ab…` all moved GLW:

`buyer EOA → 0x19379e7bf3afd791eae99220bb1b434e58d550bb`

That destination has **`extcodesize == 0`** (counterfactual holder / unpaid
CREATE2 address). Under guarded launch it is treated like an EOA, so the
allowlist does not apply. `OffchainFractions` itself never holds the GLW
(`balanceOf(OF) == 0` after buys). Live fraction metadata:

- `useCounterfactualAddress == true`
- payment is **not** routed as GLW → OffchainFractions

Fork reproduction (Anvil, real GLW token, fresh keypairs with empty code,
`createFraction(..., useCounterfactualAddress=true)`):

- `buyFractions` **succeeds**
- GLW lands on CFH address with `code_len=0`
- `balanceOf(OffchainFractions) == 0`

## What our Part B demo failure actually was

The earlier phrase “mainnet GLW allowlists transfers” was **directionally
right about guarded launch** but **imprecise about the demo failure mode**:

1. **Real restriction:** arbitrary contracts cannot send/receive GLW unless
   allowlisted. That is permanent for the guarded-launch deployment (until
   Glow’s documented full relaunch).
2. **Demo footgun (not “EOAs can’t buy”):** we pointed payment at Anvil
   account `#0` / non-CFH paths. `#0` has EIP-7702 code on current mainnet,
   so it fails `ErrIsContract`. Production listings use
   `useCounterfactualAddress=true` (or another extcodesize-0 sink).
3. **MockERC20 workaround** was unnecessary for proving EOA buys; it only
   bypassed the guarded-launch check. Prefer demonstrating with real GLW +
   CFH/`useCounterfactualAddress=true` + clean EOAs.

## Implications for “permissionless”

| Actor | Can hold/transfer GLW? | Can `buyFractions`? |
| --- | --- | --- |
| Normal EOA wallet | Yes (EOA↔EOA) | Yes, via Glow’s CFH payment path |
| Arbitrary unallowlisted contract (vault, AA wallet with code, random DeFi router) | **No** (`ErrIsContract`) | **No** if it must custody/receive GLW |
| Allowlisted Glow contracts (Uni V2 GLW–USDG pair, MinerPool, etc.) | Yes | N/A / protocol-specific |

So: Glow Launchpad is **permissionless for EOA agents** in the sense Part B
needs. It is **not** permissionless for general smart-contract composability
while guarded launch remains active. Treat that as a standing platform
constraint, not a fork quirk.

## Artifacts

- This note
- `artifacts/glw_guarded_launch_evidence.json` (when regenerated)
- Live buy tx examples (GLW → CFH): e.g. `ba8b2549…`, `9604dadf…` (see investigation logs)
