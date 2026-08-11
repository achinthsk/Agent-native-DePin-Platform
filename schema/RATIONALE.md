# Rationale: Normalized Asset Schema (v1.0.0)

This document explains *why* each field in `asset-v1.schema.json` exists,
and specifically what mistake or blind spot it is designed to prevent when
an AI agent (not a human) is using this data to compare fractional-ownership
positions across structurally different platforms.

The schema stores **facts, not scores**. It intentionally contains no
risk score, yield score, or composite rating field. That kind of judgment
is computed downstream by a separate scoring service that reads validated
instances of this schema — mixing the two would make the raw facts
unauditable, since you could no longer tell whether a number came from the
source platform or from someone's opinion about it.

---

## Why normalization matters here specifically

Glow, Elmnts, and IXS are not three flavors of the same thing. Glow pays
delegators in protocol-token emissions tied to a shared revenue pool, not a
direct cut of any one farm's electricity sales. Elmnts pays token holders a
direct share of metered oil/gas production revenue, restricted to accredited
investors under a Reg D 506(c) offering. IXS wraps conventional regulated
fund and credit instruments under a different jurisdiction's licensing
regime entirely. An agent that treats "18% yield" from Glow and "11% yield"
from Elmnts as directly comparable numbers has already made a category
error before any real analysis begins. This schema exists to make that
category error structurally impossible: it forces every asset, regardless
of source, into the same set of fields, so that differences in *mechanism*
are visible as differences in *field values*, not silently absorbed into a
single headline percentage.

## Top-level identity

- **`schema_version`** — Pins every instance to the schema shape it was
  produced against. Without this, a future schema revision (e.g. splitting
  `payout_frequency` into finer categories) would silently break parsing of
  older instances with no way to detect why.
- **`asset_id`** — Identifies one specific asset (one farm, one fund
  tranche), never the platform in general. Track record, age, and payout
  history are properties of a specific asset, not of "Glow" as a brand —
  collapsing the two would let a mature platform's reputation launder a
  brand-new, unproven asset.
- **`source_platform`** / **`asset_class`** — Kept as two separate fields on
  purpose. `source_platform` is *where the data came from*; `asset_class` is
  *what kind of real-world thing it is*. This lets an agent compare two
  oil-and-gas royalty positions to each other even if they came from two
  different platforms, instead of comparisons being artificially scoped to
  a single source.
- **`name`** / **`description_text`** — Identification only. Nothing
  categorical is allowed to live here; if a fact is a judgment call, it
  belongs in one of the closed-enum fields below, not smuggled into a
  human-readable label.
- **`source_url`** — Auditability. Every fact in this schema should be
  traceable back to where it was pulled from.
- **`data_pulled_at`** — Required, never optional. Tokenized DePIN and
  fractional-ownership data changes fast. An instance without a visible
  freshness timestamp cannot be trusted to still be accurate no matter how
  complete its other fields are, and an agent has no way to know how stale
  it is without this field.
- **`retrieval_method`** — On-chain-direct data, API data, and manually
  entered data carry different baseline trust levels *before* any scoring
  is applied. Making this a visible fact (rather than an invisible
  implementation detail of the scraper) lets the trust difference survive
  into downstream analysis.

## Payout mechanism

This is the single most important section in the schema. The three fields
here — `payout_mechanism_type`, `payout_currency`, `payout_frequency` — are
what prevent the Glow-vs-Elmnts category error described above.
`payout_mechanism_type` distinguishes a direct revenue share from a
token-emission reward from fixed interest from pure price appreciation:
these are not different *amounts* of the same thing, they are different
*kinds* of claim, with different risk profiles. `payout_currency` captures
a risk that's easy to lose track of once you're only looking at a
percentage: a reward paid in a native protocol token carries market-price
risk on top of whatever the "yield" number says, in a way a stablecoin or
fiat payout does not. `payout_frequency` is included because cadence
affects both compounding and practical liquidity, and needs to be
comparable without parsing free-text payout schedules.

## Yield

`advertised_yield_pct` and `realized_yield_pct` are two separate required
fields, and the schema will not validate an instance that merges them into
one number. A platform's marketing figure and its actual observed payout
performance answer different questions, and an agent that only sees one
merged "yield" has no way to know which one it's looking at — or whether
the two even agree. `realized_yield_pct` is explicitly nullable (not
omittable) so "this asset is too new to have a track record" is
distinguishable from "this asset returned zero" or "this platform didn't
report a figure." `yield_calculation_basis` and `yield_last_computed_at`
are conditionally required whenever either percentage is present, because a
bare percentage without its method and its age is not independently
verifiable or comparable to a percentage another platform computed a
different way.

## Verification

`verification_tier` is the schema's fraud/trust-risk proxy. Data that is
self-reported by the asset issuer, with no independent check, is a
fundamentally different quality of fact than data backed by an independent
audit, a cryptographic on-chain proof, or independent remote-sensing
verification (e.g. Glow's satellite/AI imagery of physical solar output).
Making this a required, closed-enum field means self-reported data can
never be silently displayed with the same apparent authority as verified
data — an agent reading this field always knows which kind of claim it's
looking at.

## Maturity / track record

`protocol_age_months` and `asset_age_months` are deliberately kept as two
separate fields. "The protocol is 2.5 years old" and "this specific asset
has existed for 7 months" are different facts, and an agent relying only on
protocol age could be misled into treating a brand-new, unproven asset as
carrying the maturity of the platform it happens to sit on.
`completed_payout_cycles` goes a step further: it's the field that actually
answers "has this asset delivered a payout, not just existed." A platform
can be old and reputable while a specific asset on it has paid out zero
times — this field makes that visible instead of letting platform-level
maturity imply asset-level performance.

## Liquidity

`exit_type` captures the contractual/structural exit mechanism.
`lockup_period_weeks` is conditionally required whenever `exit_type` is
`fixed-lockup`, so a locked asset can never omit how long the holder is
actually locked in. `estimated_time_to_exit_days` exists because
contractual tradeability and practical liquidity are not the same thing —
a token that is technically tradeable on an open market can still sit in a
thin order book for days before it can be sold at a fair price. Keeping
this separate from `exit_type` lets an agent see both the contractual
promise and the practical reality.

## Regulatory

`regulatory_wrapper` and `accreditation_required` are both required because
they jointly determine who is legally permitted to hold a given position —
getting this wrong isn't just an analysis error, it's a compliance one.
`restricted_jurisdictions` and `permitted_jurisdictions` are both allowed to
be empty arrays, but the schema's field descriptions are explicit that
*both empty simultaneously must be read as "jurisdictional eligibility is
unknown," never as "unrestricted worldwide."* An absence of a stated
restriction is not evidence that none exists, and a downstream consumer
that treats an empty array as "no restrictions" is making an unjustified
inference the source data never actually supported.

## Concentration / counterparty

`exposure_type` (`single-asset` vs. `pooled-diversified`) is a required,
closed-enum field precisely because concentration risk is one of the
easiest things to bury in prose. `underlying_reference` forces a concrete
referent — a specific farm ID, well ID, or "network-wide pool" — so a
`single-asset` claim is checkable against something specific rather than a
vague description. `operator_name` is nullable rather than omittable, so an
unnamed or unknown operator is a visible gap in the data rather than a
field that was simply never asked about.

## Explicit-missing-data convention

Throughout the schema, when a required fact is not published by a source
platform, the instance must still carry the field — set to a documented
sentinel rather than left out:

- Closed-enum judgment-call fields (`payout_mechanism_type`,
  `payout_currency`, `payout_frequency`, `exit_type`, `regulatory_wrapper`,
  `exposure_type`) include an `"unverifiable"` enum value for exactly this
  case.
- Numeric fields that can be legitimately unpublished
  (`protocol_age_months`, `asset_age_months`, `completed_payout_cycles`,
  `lockup_period_weeks` when relevant, `estimated_time_to_exit_days`) are
  typed as nullable, and the schema conditionally *requires* a paired
  `*_unknown_reason` string whenever the value is null — so a missing
  number always comes with a stated reason, never a silent gap.

This convention exists so that "we don't know" and "the value is absent
from this JSON document" can never be confused with each other by a
downstream consumer, human or agent.
