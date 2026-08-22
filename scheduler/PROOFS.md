# Scheduler Part C proofs (2026-08-21)

Live runs on branch `cursor/scheduler-refresh-discovery-c7dd`. Nothing
auto-merged. Elmnts mtime unchanged throughout
(`storage/elmnts-…/2026-08-11T11-04-46Z.json` mtime `1787162992`).

---

## 1. Real refresh cycle

```bash
python3 scheduler/run_refresh.py
```

**Before**

| Asset | Snapshots |
| --- | --- |
| Glow farm 1 | `2026-08-11T11-04-09Z.json` |
| RealT Ardmore | `2026-08-12T12-01-43Z.json`, `2026-08-13T04-04-52Z.json` |

**After (new files written)**

| Asset | New snapshot |
| --- | --- |
| Glow | `storage/glow-farm-1/2026-08-21T09-17-09Z.json` |
| RealT | `storage/realt-0xfe17c3c0b6f38cf3bd8ba872bee7a18ab16b43fb/2026-08-21T09-17-11Z.json` |

Adapter highlights (live):

- Glow: GCA `229` farms; Ethereum RPC block `25802554`; schema validate PASS
- RealT: community API `829` tokens; rent tracker `258` weeks;
  `realized_yield_pct=9.225`; schema validate PASS

Status log: `job=refresh` `status=success` `started_at=2026-08-21T09:17:08Z`

---

## 2. Real discovery cycle (first backlog item = Spacecoin)

```bash
python3 scheduler/run_discovery.py
```

- Candidate: **Spacecoin** (`next_index` `0 → 1`)
- Wrote `candidates/spacecoin/FINDINGS.md`
- Final classification after docs deep-dive (same cycle): **`wrong-model`**
  — SpaceRouter Provider requires running a home node + stake; official
  staking docs: “Staking alone does not qualify.”
- Index row added in `candidates/README.md`

Status log: `job=discovery` `status=success` `started_at=2026-08-21T09:17:21Z`
(automated seed pass logged `insufficient-information`; FINDINGS then
completed against official docs to the Aethir evidence bar → `wrong-model`)

---

## 3. Status log entries produced

See `scheduler/status/status_log.jsonl` (append-only). Proof-relevant lines:

1. Refresh **success** (Glow + RealT)
2. Discovery **success** (spacecoin)
3. Deliberate break **failure** (below)

(An earlier refresh attempt also logged **failure** when `python-dotenv`
was missing — loud, no snapshots written — then deps were installed and
the success run above was executed.)

---

## 4. Deliberate loud failure

```bash
python3 scheduler/run_refresh.py --break-gca
```

- Points Glow `--gca-base` at `http://127.0.0.1:1`
- Adapter: `[FATAL] Source unreachable — aborting with no writes`
- Scheduler exit code **1**
- **No new Glow snapshot** (still only `2026-08-11…` and `2026-08-21T09-17-09Z`)
- Status: `job=refresh` `status=failure` `deliberate_break=true`
  `error=adapter(s) failed: glow`

---

## Guards checked

- Elmnts storage untouched
- No imports / subprocess of `execution/`
- Workflows open PRs only (`gh pr create`) — no `gh pr merge`

---

## 5. Twice-weekly schedule + on-demand `candidate_name` (follow-up)

### Cron (Wed + Sat) in `.github/workflows/scheduler-discovery.yml`

```yaml
schedule:
  # Wednesday + Saturday 14:00 UTC — see scheduler/DECISIONS.md
  - cron: "0 14 * * 3,6"
workflow_dispatch:
  inputs:
    candidate_name:
      required: false
      default: ""
      type: string
```

`workflow_dispatch` remains the native GitHub Actions “Run workflow”
mechanism (optional string inputs default to `""` when blank).

### Pointer rules

| Run | Advances `next_index`? |
| --- | --- |
| Named override (`--candidate-name` set) | **No** |
| Empty / scheduled backlog-order | **Yes** |

### Proof A — manual override (not next in backlog)

Before: `next_index=2` (next = mining-royalty).  
Override target = **Tokenized farmland** (backlog index 3).

```bash
python3 scheduler/run_discovery.py --trigger manual --candidate-name "Tokenized farmland"
```

- Wrote `candidates/tokenized-farmland/FINDINGS.md` → **`insufficient-information`**
- Status: `trigger=manual`, `manual_mode=override`, `advance_backlog=false`
- After: `next_index=2` (**unchanged**)

### Proof B — manual empty input (backlog-order)

```bash
python3 scheduler/run_discovery.py --trigger manual
```

- Pulled **mining-royalty-tokenization** (the real next item)
- Wrote `candidates/mining-royalty-tokenization/FINDINGS.md` → **`insufficient-information`**
- Status: `trigger=manual`, `manual_mode=backlog_order`, `advance_backlog=true`
- After: `next_index=3`

### Status log labels

Both runs append JSONL with `details.trigger` and `details.manual_mode`
for a future dashboard.
