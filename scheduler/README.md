# Scheduler — refresh + discovery (no auto-merge)

Automates two previously manual workflows:

1. **Refresh** — re-pull Glow + RealT into new timestamped `storage/` snapshots
2. **Discovery** — investigate **one** backlog candidate per cycle into
   `candidates/<slug>/FINDINGS.md`

Elmnts stays manual. Nothing under `execution/` is imported or invoked.
Nothing is auto-merged — GitHub Actions opens a PR for a human.

See [`DECISIONS.md`](./DECISIONS.md) for platform choice, cadence, and backlog
order.

## Entry points

```bash
python3 scheduler/run_refresh.py
python3 scheduler/run_refresh.py --break-gca   # deliberate loud Glow failure
python3 scheduler/run_discovery.py
python3 scheduler/run_discovery.py --dry-run
```

## Status log

Every run appends one JSON line to `scheduler/status/status_log.jsonl`
(`success` or `failure`). This is the durable “did the cron still work?”
record for a future dashboard.

## Workflows

| File | Cron (UTC) | Job |
| --- | --- | --- |
| `.github/workflows/scheduler-refresh.yml` | Sunday 14:00 | Glow + RealT refresh → PR |
| `.github/workflows/scheduler-discovery.yml` | Wednesday 14:00 | One backlog candidate → PR |

Both support `workflow_dispatch`. Both create PRs only — never merge.
