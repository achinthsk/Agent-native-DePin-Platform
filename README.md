# Agent-Native DePIN/RWA Platform

**Could an AI agent actually tell a real investment apart from a good-looking website?**

That's the question this started from. Tokenized real-world assets — solar
farms, rental properties, oil and gas royalties, GPU compute, satellites —
are a real and growing category. Every one of them publishes numbers. Almost
none of those numbers are independently checkable. An agent (or a person)
comparing "18% yield" from one platform against "11%" from another has
usually already made a category error before any real analysis begins,
because those two numbers rarely mean the same thing underneath.

This is a scoring and verification layer built specifically for agents to
query — not a dashboard for humans to eyeball, though one of those exists
too, sitting on top of the same live data.

## Try it right now

```bash
curl https://agent-native-depin-platform.onrender.com/v1/assets
```

That's real, live data — not a demo, not mocked. Every asset in the response
carries four independent scores (yield, risk, liquidity, data confidence),
and every score ships with the raw fields that produced it. Nothing is ever
blended into one ranking number.

- **API root:** `https://agent-native-depin-platform.onrender.com`
- **Interactive docs:** `/docs`
- **MCP endpoint** (for agent frameworks): `/mcp/` — trailing slash required
- **Methodology, pulled live, not paraphrased:** `/v1/methodology`

## What it's actually found

This is the part worth reading before anything else, because it's the
actual evidence this is doing real work, not just organizing marketing
copy.

- **Glow's GLW token is down roughly 94% from its January 2025 peak** —
  pulled directly from real on-chain Uniswap reserves, not a price
  aggregator (one aggregator checked along the way was pricing the wrong
  contract entirely and showing internally inconsistent numbers). This
  finding fed directly back into the scoring methodology — the platform now
  has an explicit, evidence-based risk component for token-emission-based
  payout mechanisms, separate from a flat category penalty.
- **Aethir and Spacecoin were both investigated and rejected** — not
  because they aren't real, but because their reward models require
  actively operating hardware (a "checker node," a provider node), which is
  a structurally different economic relationship than the passive
  capital-provision model this platform is built around. Getting this
  distinction right, specific to the actual mechanism rather than a
  surface-level "is this DePIN" check, is most of the point.
- **RealT's own claimed token-to-deed structure has a documented,
  independently-reported discrepancy** — a journalism investigation found
  recorded deeds for a Detroit property portfolio that didn't match what
  the tokenization claimed. This is exactly the category of thing an agent
  trusting a platform's own marketing would never catch.

None of this was invented to make a good README. It's what came out of
actually investigating each source before writing any adapter code.

## How it's built

```
schema/     → one normalized shape for any tokenized asset, regardless of
              source-specific mechanics (payout type, verification tier,
              liquidity, regulatory wrapper, concentration)
adapters/   → source-specific pullers (Glow, RealT — live; Elmnts —
              manual-entry only, since no public data source exists)
scoring/    → four independent scores, weights external and versioned,
              methodology written before the code that implements it
api/        → MCP + REST, read-only, no advice language anywhere in output
execution/  → non-custodial Glow investing, proven on a mainnet fork —
              not live with real funds yet, deliberately
scheduler/  → automated weekly refresh + biweekly discovery of new
              candidates, running on its own via GitHub Actions
candidates/ → the discovery process's research log — investigations that
              didn't pass are kept, not deleted, because a rejection with
              real evidence is worth as much as an approval
web/        → the human-facing dashboard, reading the same live API
```

## The rules this doesn't break

These weren't decided in the abstract — most were learned the hard way,
from real bugs and real near-misses along the way.

- **Never fabricate.** A missing fact is `null` plus a stated reason, never
  a guessed number standing in for what isn't known.
- **No fused scores.** Yield, risk, liquidity, and data confidence stay
  separate, always. An agent optimizing for safety and one optimizing for
  yield need different information, not one number that's already made the
  tradeoff for them.
- **Every score ships with its inputs.** Nothing is ever presented as a
  bare number with no way to check why.
- **Nothing gets listed for pay.** No asset — current or future — can pay
  for inclusion or favorable treatment. This is a deliberate structural
  choice, made specifically because the issuer-pays model is widely
  identified as the core conflict of interest behind the credit rating
  agencies' role in the 2008 financial crisis. A scoring platform that
  takes money from what it scores has recreated that problem, regardless
  of how good the methodology looks on paper.
- **No investment-advice language**, anywhere in the API's output —
  actively scanned for, not just assumed clean.
- **Nothing auto-merges.** The discovery process investigates and proposes;
  a human still reviews every classification before anything changes.

## Where it actually is right now

Three fully investigated, live-scored assets. One non-custodial execution
path, proven correct on a forked mainnet, deliberately not yet turned on
with real funds. A discovery process that's rejected more candidates than
it's approved so far — which says more about the current state of tokenized
DePIN than it does about the platform.

This is early. The methodology has already been revised twice based on
real evidence turning up mid-build, and it'll likely be revised again. If
you find something wrong with it — the scoring, the schema, a source that
should be investigated differently — that's genuinely the most useful thing
you could tell me.
