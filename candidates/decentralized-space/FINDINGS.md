# Decen Space — candidate investigation

**Classification: `not-yet-investable`**

**Date investigated:** 2026-08-21  
**Investigator note:** On-demand discovery via
`python3 scheduler/run_discovery.py --candidate-name "Decen Space"`
(same process as a scheduled cycle). Research log only. No adapter,
schema, scoring, storage, or API changes accompany this document beyond
this FINDINGS file, the candidates index row, and backlog pointer
advance. Elmnts was not touched. `execution/` was not invoked.

Decen Space (also styled DecenSpace) is a real early-stage DePIN startup
building a **marketplace / orchestration layer for satellite ground
stations** (unified API over independently operated antennas). Official
site and third-party accelerator / ESA BIC coverage are reachable. What
is **not** reachable today is a live, public participation path with
keyless economics — no public docs portal, no public booking/rewards
API, no published token contract or claim surface for this investigation
to score against. The *intended* supply-side model (monetize ground
station hardware via token incentives) is operator/hardware-sided and
would likely be **`wrong-model`** for this platform **if/when** it goes
live that way; until a live path exists, the honest call is
**`not-yet-investable`**.

---

## What was checked

### Official / primary

| Source | URL | Result |
| --- | --- | --- |
| Marketing site | https://decenspace.com/ | HTTP 200 — live. Meta description: “ground station marketplace for satellite operators. One unified API to a global network of independently operated antennas for TT&C, payload downlink, and mission operations.” |
| `www.decenspace.com` | https://www.decenspace.com/ | SSL hostname mismatch — not used |
| Docs host | https://docs.decenspace.com/ | DNS NXDOMAIN |
| App host | https://app.decenspace.com/ | DNS NXDOMAIN |
| Site paths `/docs`, `/api`, `/api/v1`, `/pricing`, `/providers`, `/operators`, `/waitlist` | under https://decenspace.com | **HTTP 404** |
| GitHub org | https://github.com/DecenSpace | HTTP 200 — org exists |
| GitHub repos (API) | https://api.github.com/orgs/DecenSpace/repos | Only public repo: `DecenSpace.github.io` (“Website for Decen Space”) — **no** protocol / contracts / SDK repo published |
| X / Twitter | https://x.com/decenspace | HTTP 200 — account exists |

### Stale backlog seeds (corrected this cycle)

Initial `scheduler/backlog.json` seeds pointed at `*.decentralized.space`,
which **do not resolve**. Those failures are recorded below; investigation
continued against the real brand domain `decenspace.com`.

| Source | Result |
| --- | --- |
| `https://www.decentralized.space/` | DNS failure |
| `https://decentralized.space/` | DNS failure |
| `https://docs.decentralized.space/` | DNS failure |

### Secondary (named coverage — not primary product docs)

| Source | URL | Result |
| --- | --- | --- |
| Outlier Ventures DePIN Base Camp 2 | https://outlierventures.io/article/meet-the-next-wave-of-depin-pioneers-announcing-the-startups-in-base-camp-2/ | HTTP 200 — cohort write-up (2025-04-17): decentralized ground station network; “hardware owners to monetize their assets through our token-based incentive system” |
| Aviaspace Bremen / ESA BIC NG | https://www.aviaspace-bremen.de/en/2025/11/04/decen-space-the-future-of-satellite-ground-operations/ | HTTP 200 — 2025-11-04 profile: joining ESA BIC Northern Germany; mission-control orchestration; DLT coordination; year-1 plan = onboard small group of European ground stations |
| BulgarianDegen / Solana interview | https://bulgariandegen.substack.com/p/the-new-faces-of-solana-ep-2-decenspace | HTTP 200 — 2025-09-18 interview: “first decentralized ground station network on Solana”; Colosseum DePIN track; CEO Tristan Hundley |

### On-chain / public economics

| Check | Result |
| --- | --- |
| Published token contract / explorer link on official site | **Not found** in fetched HTML / meta |
| Public rewards / staking / booking API | **Not found** (`/api` 404; docs host missing) |
| Keyless farm/rent-style cashflow feed | **Not found** |

---

## What’s actually reachable right now

| Surface | Reachable? | Notes |
| --- | --- | --- |
| Marketing site + meta description | Yes | Product framing clear |
| Public technical docs | No | `docs.decenspace.com` missing |
| Public API for capacity / payouts | No | 404 / missing |
| Open-source protocol / contracts | No | GitHub = website only |
| Accelerator / ESA press | Yes | Confirms existence + early roadmap |
| Capital-only “finance a ground station / share lease revenue” product | **Not found** | Supply side described as hardware owners / ground stations |

---

## Mechanism vs this platform’s capital-provision bar

This platform’s bar (Glow / Elmnts / RealT): **passive capital** finances
or owns a claim on an underlying asset’s cashflow without operating
infrastructure.

Decen Space’s documented / press-described sides:

1. **Demand (satellite operators)** — book / schedule ground-station
   access via a unified API. That is a **customer spend** surface, not a
   yield opportunity for this platform.
2. **Supply (ground station providers)** — Outlier Ventures: “allowing
   **hardware owners** to monetize their assets through our **token-based
   incentive system**.” Substack: “reward and incentivize the ground
   stations who are doing it well.” That is an **operate / contribute
   antenna** model — wrong-model family **when live**.
3. **Live investable path today** — not evidenced. Aviaspace: year-1
   onboarding of a small European station set; no public economics feed.

No Glow-style financed deposit or RealT-style rent claim on a
third-party-operated asset was found.

---

## Classification

**`not-yet-investable`**

Legitimate early DePIN (site + accelerator/ESA coverage), but **nothing
is actually live** for public participation with adapter-grade data.
Intended supply-side incentives look **hardware/operator** (would be
`wrong-model` if that becomes the live earn path with no capital-only
alternative). Revisit when docs, contracts, and a keyless public data
surface exist.

---

## Can the four scores be computed?

**No.** No live asset instance, no public payout series, no adapter
target. Discovery does not invent scores.

---

## Explicit unknowns / next checks

1. Whether a capital-only capacity NFT / stake-without-antenna product
   ever ships (not claimed on the official site today).
2. Solana program IDs / token mint once published.
3. Public provider earnings API or on-chain receipt schema.
4. Whether ESA BIC / year-1 pilots expose any permissionless read path.

---

## Scheduler notes

- Trigger: **on-demand** `--candidate-name "Decen Space"` (matched backlog
  slug `decentralized-space` / display name Decentralized Space via fuzzy
  match).
- Because this was the backlog `next_index` item, pointer advanced
  `1 → 2`.
- Same rigor and PR-only review rule as scheduled discovery — nothing
  auto-merges.
- Backlog seeds should be updated to `https://decenspace.com/` (done in
  this cycle’s `scheduler/backlog.json`).
