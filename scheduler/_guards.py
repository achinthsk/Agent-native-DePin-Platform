"""Hard exclusions for scheduler entrypoints."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXECUTION_DIR = REPO_ROOT / "execution"


def assert_scheduler_safe() -> None:
    """
    Refuse to run if execution/ code is loaded or if we are being invoked
    as part of an execution/ path. Discovery/refresh must stay structurally
    separated from Step 7 investing code.
    """
    for name, mod in list(sys.modules.items()):
        if name == "execution" or name.startswith("execution."):
            raise RuntimeError(
                "SCHEDULER GUARD: execution/ module is loaded "
                f"({name!r}). Scheduler must not call investing code."
            )
        path = getattr(mod, "__file__", None)
        if path and Path(path).resolve().is_relative_to(EXECUTION_DIR.resolve()):
            raise RuntimeError(
                "SCHEDULER GUARD: module under execution/ is loaded "
                f"({path}). Scheduler must not call investing code."
            )


def assert_not_elmnts(target: str) -> None:
    if "elmnt" in target.lower():
        raise RuntimeError(
            "SCHEDULER GUARD: Elmnts is manual-entry only and must never "
            f"be auto-refreshed (got {target!r})."
        )
