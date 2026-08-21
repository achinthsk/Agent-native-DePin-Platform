# Tokenized farmland (category) — candidate investigation

**Classification: `insufficient-information`**

**Date investigated:** 2026-08-21  
**Investigator note:** On-demand discovery simulating
`workflow_dispatch` with `candidate_name="Tokenized farmland"`
(`python3 scheduler/run_discovery.py --trigger manual --candidate-name
"Tokenized farmland"`). Research log only. No adapter, schema, scoring,
storage, or API changes accompany this document beyond this FINDINGS
file and the candidates index row. Elmnts was not touched. `execution/`
was not invoked. **Named override — backlog `next_index` was not
advanced.**

This is a **category probe**, not a single-issuer ticket: are there live
**tokenized / publicly readable** farmland RWAs with a capital-only path
and adapter-grade public data (Glow / RealT bar)? Seeds cover major
farmland investment brands plus one crypto lending surface that appeared
in the backlog list.

---

## What was checked

| Source | URL | Result |
| --- | --- | --- |
| Farmland LP | https://www.farmlandlp.com/ | HTTP 200 — organic/regenerative farmland fund manager; 19,000+ acres; “Investor Portal / INVEST NOW” |
| Farmland LP invest | https://www.farmlandlp.com/invest | HTTP 200 — individual-investor funnel for the fund |
| AcreTrader | https://acretrader.com/ | HTTP 200 — site reachable; response body was compressed/binary to this client (SPA) — no usable extracted text |
| FarmTogether | https://www.farmtogether.com/ | HTTP 200 — “Invest in US Farmland”; $217M+ AUM marketing claim |
| FarmTogether how-it-works | https://www.farmtogether.com/how-it-works | HTTP 200 — product matrix: crowdfunded offerings, fund, TICs, SMAs; **accreditation required** on most rows; target IRR/cash-yield ranges shown as marketing targets |
| FarmTogether FAQ | https://www.farmtogether.com/faq | HTTP 200 — “accredited and institutional investors”; digital investment experience; **not** described as a public on-chain token |
| HarvestFlow | https://harvestflow.io/ | HTTP 200 — crypto lending marketing (JP); not farmland title |
| HarvestFlow docs | https://docs.harvestflow.io/ | HTTP 200 — Polygon DAI / lending guide (GitBook); **not** farmland RWA docs |

### What’s actually reachable right now

| Surface | Reachable? | Notes |
| --- | --- | --- |
| Traditional farmland investment sites | Yes | Farmland LP, FarmTogether live |
| Public on-chain farmland token + rent/yield API | **Not found** among seeds | No contract addresses, no RealT-style rent tracker |
| Keyless adapter-grade cashflow feed | **Not found** | FarmTogether is capital-only but accredited / private-market |
| HarvestFlow as farmland tokenization | **No** | Lending product on Polygon, wrong asset class for this probe |

---

## Mechanism vs this platform’s capital-provision bar

This platform’s bar: passive capital with **publicly readable** economics
(adapter can pull facts without partner keys), à la Glow / RealT.

- **FarmTogether / Farmland LP:** Capital-only farmland exposure exists,
  but as **accredited private-market** products (crowdfund / fund / TIC).
  That is closer to Elmnts-style gated fundraising than to a permissionless
  public snapshot source. No public weekly rent series or on-chain property
  token was found on the pages fetched.
- **AcreTrader:** Reachable host; content not extractable here — cannot
  claim a tokenized public path from this pull.
- **HarvestFlow:** Live crypto lending docs (Polygon) — **not** tokenized
  farmland.

No seed produced a Glow/RealT-shaped “token + public payout history”
surface for farmland.

---

## Classification

**`insufficient-information`**

Category probe did **not** identify a specific live tokenized-farmland
asset with adapter-grade public data. Traditional capital-only farmland
platforms are real but gated; crypto seed (HarvestFlow) is the wrong
model/asset class. Stronger dispositions (`candidate-for-adapter` or
`not-yet-investable` for a named issuer) need a concrete tokenized
product with reachable contracts / APIs.

---

## Can the four scores be computed?

**No.** No concrete `storage/`-ready asset instance emerged from this
cycle.

---

## Explicit unknowns / next checks

1. Whether AcreTrader (or peers) expose any on-chain / public API after
   authenticated docs review.
2. Named tokenized farmland issuers beyond these seeds (if any launch with
   public economics).
3. Whether any FarmTogether offering ever maps to a RealT-like public
   rent file — not evidenced on FAQ / how-it-works pages today.

---

## Scheduler notes

- Trigger: **`manual`** / **`override`** (`candidate_name` set).
- Backlog `next_index` **unchanged** (was 2 / mining-royalty next).
- Same four classifications and PR-only review rule as scheduled runs.
