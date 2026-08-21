#!/usr/bin/env python3
"""
Scheduled Glow + RealT snapshot refresh.

Reuses adapters/glow_adapter.py and adapters/realt_adapter.py via subprocess
(same CLIs as a manual run). Never touches Elmnts. Never imports execution/.

Usage:
  python3 scheduler/run_refresh.py
  python3 scheduler/run_refresh.py --glow-farm-id 1 --realt-address 0xFe17...
  python3 scheduler/run_refresh.py --break-gca   # Part C: deliberate loud fail
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scheduler._guards import assert_not_elmnts, assert_scheduler_safe  # noqa: E402
from scheduler.status_log import append_status, utc_now_iso  # noqa: E402

DEFAULT_REALT = "0xFe17C3C0B6F38cF3bD8bA872bEE7a18Ab16b43fB"
DEFAULT_GLOW_FARM = "1"


def _run_adapter(label: str, argv: list[str]) -> dict:
    assert_not_elmnts(label)
    assert_not_elmnts(" ".join(argv))
    print(f"[REFRESH] starting {label}: {' '.join(argv)}")
    proc = subprocess.run(
        argv,
        cwd=str(REPO_ROOT),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    return {
        "label": label,
        "argv": argv,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Refresh Glow + RealT snapshots (scheduler)")
    p.add_argument("--glow-farm-id", default=DEFAULT_GLOW_FARM)
    p.add_argument("--realt-address", default=DEFAULT_REALT)
    p.add_argument(
        "--break-gca",
        action="store_true",
        help="Point Glow GCA base at an unreachable URL to prove loud failure",
    )
    p.add_argument(
        "--skip-realt",
        action="store_true",
        help="Only run Glow (used with --break-gca proofs)",
    )
    return p.parse_args()


def main() -> int:
    assert_scheduler_safe()
    args = parse_args()
    started = utc_now_iso()
    results: list[dict] = []
    details: dict = {
        "glow_farm_id": args.glow_farm_id,
        "realt_address": None if (args.skip_realt or args.break_gca) else args.realt_address,
        "deliberate_break": bool(args.break_gca),
        "note": (
            "No auto-merge. Elmnts not touched. execution/ not called. "
            "Human must review any resulting PR."
        ),
    }

    glow_cmd = [
        sys.executable,
        str(REPO_ROOT / "adapters" / "glow_adapter.py"),
        "--farm-id",
        str(args.glow_farm_id),
    ]
    if args.break_gca:
        glow_cmd.extend(["--gca-base", "http://127.0.0.1:1"])
        print("[REFRESH] DELIBERATE FAIL MODE: GCA base → http://127.0.0.1:1")

    results.append(_run_adapter("glow", glow_cmd))

    if not args.skip_realt and not args.break_gca:
        realt_cmd = [
            sys.executable,
            str(REPO_ROOT / "adapters" / "realt_adapter.py"),
            "--address",
            args.realt_address,
        ]
        results.append(_run_adapter("realt", realt_cmd))
    elif args.break_gca:
        print("[REFRESH] skipping RealT during deliberate Glow-failure proof")

    details["results"] = [
        {
            "label": r["label"],
            "ok": r["ok"],
            "returncode": r["returncode"],
            "stderr_tail": r["stderr_tail"][-500:],
        }
        for r in results
    ]

    all_ok = all(r["ok"] for r in results)
    if all_ok:
        append_status(
            job="refresh",
            status="success",
            started_at=started,
            finished_at=utc_now_iso(),
            details=details,
        )
        print("[DONE] refresh cycle succeeded")
        return 0

    failed = [r["label"] for r in results if not r["ok"]]
    err = f"adapter(s) failed: {', '.join(failed)}"
    append_status(
        job="refresh",
        status="failure",
        started_at=started,
        finished_at=utc_now_iso(),
        error=err,
        details=details,
    )
    print(f"[FATAL] refresh cycle failed — {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
