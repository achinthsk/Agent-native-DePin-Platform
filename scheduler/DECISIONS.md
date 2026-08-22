# Scheduler decisions

**Date:** 2026-08-21  
**Scope:** Automate (1) Glow + RealT snapshot refresh and (2) one-at-a-time
candidate discovery from a maintained backlog. Manual Elmnts entry and
anything under `execution/` are explicitly out of scope.

---

## 1. Where this runs — Render Cron vs GitHub Actions

| Criterion | Render Cron Job | GitHub Actions `schedule` |
| --- | --- | --- |
| Already used here | Web service via `render.yaml` | Not yet for cron |
| Can open a **PR** without extra secret plumbing | Awkward — needs a GitHub PAT in Render env + git push from an ephemeral disk | Native: `contents: write` + `pull-requests: write` on `GITHUB_TOKEN` |
| Fits “never auto-merge; human reviews PR” | Possible, but the job is not git-native | Direct match: commit → branch → `gh pr create` |
| Free-tier fit | Separate Cron Job product; billed/limited independently of free web sleep | Public-repo Actions minutes are free for this workload |
| Outbound HTTP/RPC for adapters | Yes | Yes |
| Failure visibility | Render logs (easy to miss) | Actions run UI + committed `scheduler/status/` in the PR |

### Recommendation: **GitHub Actions**

Reasoning: this scheduler’s primary output is a **PR with real file diffs**
(new `storage/` snapshots or a new `candidates/<slug>/FINDINGS.md`), not an
in-process HTTP side effect. GitHub Actions is the path that makes “open a
PR, never merge” structural rather than bolted on. Render remains the right
host for the public API; it is the wrong host for a git-writing research
cron unless we duplicate GitHub auth on Render for no gain.

Render Cron stays a fallback if Actions scheduling is disabled for the
repo; the Python entrypoints (`run_refresh.py`, `run_discovery.py`) are
platform-agnostic so that swap does not require rewriting adapter logic.

---

## 2. Cadence

These are slow-moving real-world cashflows (weekly solar reward buckets;
weekly rent distributions). Daily pulls burn Cloudflare/RPC budget and
produce near-duplicate snapshots.

| Job | Cadence | Cron (UTC) | Why |
| --- | --- | --- | --- |
| **Asset refresh** (Glow + RealT) | **Weekly** | `0 14 * * 0` (Sunday 14:00) | Glow buckets finalize on a weekly rhythm; RealT rent is weekly. Weekly history is enough to build a real time series without looking like a scrape bot. |
| **Discovery** (one candidate) | **Twice weekly** | `0 14 * * 3,6` (**Wednesday** + **Saturday** 14:00) | Keep the original Wednesday slot; add Saturday as the roughly opposite mid-week point (~3–4 days apart) so runs are evenly spaced rather than clustered. Still one candidate per cycle. Clear of Sunday refresh. |

**On-demand discovery:** GitHub Actions **`workflow_dispatch`** remains the
correct native mechanism for a manual “Run workflow” button with typed
inputs (confirmed against current Actions docs / usage: optional string
inputs default to `""` when blank). Discovery workflow exposes optional
`candidate_name`:

| Manual input | Behavior | Advances `next_index`? |
| --- | --- | --- |
| **Set** | Investigate that named candidate (need not be on backlog) | **No** — ad-hoc checks must not skip the queue |
| **Empty** | Same as scheduled: next backlog item | **Yes** |

Scheduled cron runs always use backlog order and advance the pointer.
Same investigation rigor and PR-only output in every mode. Status log
records `trigger` = `scheduled` \| `manual`, and for manual runs
`manual_mode` = `backlog_order` \| `override`.

Refresh has no on-demand name input (out of scope).

**Not chosen:** daily refresh; once-weekly discovery; adjacent cron days
(Tue/Fri clusters less cleanly than Wed/Sat opposite the week).

---

## 3. Candidate backlog (order)

Compiled from project backlog items already identified for investigation
(not from inventing new names). Aethir is **already** investigated
(`candidates/aethir/FINDINGS.md`) and is **not** re-queued.

**Rule (learned 2026-08-21):** backlog entries must be **named platforms**,
not bare categories. Category probes for “mining royalty tokenization” and
“tokenized farmland” both returned `insufficient-information` because the
queue asked “is there anything in this bucket?” against mismatched /
non-issuer seeds — the same failure mode as queuing “GPU compute DePIN”
instead of “Aethir”. Those two category rows are **closed**; named
replacements follow.

| Order | Slug | What | Status |
| --- | --- | --- | --- |
| 1 | `spacecoin` | Spacecoin | Done — `wrong-model` |
| 2 | `decentralized-space` | Decen Space | Done — `not-yet-investable` |
| 3 | `mining-royalty-tokenization` | *(category probe)* | Closed — `insufficient-information` |
| 4 | `tokenized-farmland` | *(category probe)* | Closed — `insufficient-information` |
| 5 | `ptx` | **PTX** (NSR mining royalty tokens) | Queued — named replacement for mining category |
| 6 | `agrifi` | **AgriFi** (farmland / ag RWA) | Queued — named replacement for farmland category |
| 7 | `agro-digital-token` | **Agro Digital Token** (plantation RWA) | Queued — second named farmland candidate |

Pointer state lives in `scheduler/backlog.json` (`next_index`). Only
**backlog-order** runs (scheduled cron, or manual with empty
`candidate_name`) advance it by one on success. A named on-demand
override never advances the pointer — even if the name happens to match
the next backlog item — so an ad-hoc check cannot silently skip queue
order. Re-runs after the list is exhausted fail loudly and log
`backlog_exhausted`.

Current `next_index` after the category closures: **4** (next scheduled /
empty-manual run = **PTX**).

---

## 4. Hard exclusions (enforced in code)

1. **Never auto-merge** — workflows only open PRs (`gh pr create`); no
   `gh pr merge`.
2. **Never refresh Elmnts** — `run_refresh.py` only invokes Glow + RealT.
3. **Never import or subprocess `execution/`** — `scheduler/_guards.py`
   refuses to start if `execution` is on `sys.modules` or if a caller path
   resolves under `execution/`.
4. **Source failures abort** — adapter `SourceError` / non-zero exit → no
   new “fresh” snapshot claim; status log records `failed`.
5. **Every run appends** `scheduler/status/status_log.jsonl`.
