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
| **Discovery** (one candidate) | **Twice weekly** | `0 14 * * 2,5` (**Tuesday** + **Friday** 14:00) | Still one candidate per cycle (cost throttle), but twice a week clears a short backlog without waiting a full week between items. Tuesday/Friday are ~3 days apart — evenly spaced, not back-to-back — and sit clear of Sunday refresh so Actions failures stay distinguishable. |

**On-demand discovery:** the discovery workflow also has `workflow_dispatch`
with optional input `candidate_name`. When set, that platform is
investigated immediately (need not be on `backlog.json`). When blank,
behavior matches a scheduled run (next backlog item). Same investigation
rigor and PR-only output either way. Refresh has no on-demand name input
(out of scope).

**Not chosen:** daily refresh (unnecessary for rent/solar); once-weekly
discovery (too slow for a four-item backlog); adjacent cron days (clusters
load and review).

---

## 3. Candidate backlog (order)

Compiled from project backlog items already identified for investigation
(not from inventing new names). Aethir is **already** investigated
(`candidates/aethir/FINDINGS.md`) and is **not** re-queued.

| Order | Slug | What | Notes |
| --- | --- | --- | --- |
| 1 | `spacecoin` | Spacecoin | DePIN / satellite connectivity capital question |
| 2 | `decentralized-space` | Decen Space | Space DePIN ground-station marketplace — capital vs operator |
| 3 | `mining-royalty-tokenization` | Mining royalty tokenization (category) | General category probe: is there a live capital-only royalty path with public data? |
| 4 | `tokenized-farmland` | Tokenized farmland (category) | General category probe: live farmland RWA with public economics? |

Pointer state lives in `scheduler/backlog.json` (`next_index`). Each
successful discovery cycle advances it by one. Re-runs after the list is
exhausted no-op loudly and log `backlog_exhausted`.

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
