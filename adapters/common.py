"""
Shared helpers for adapters: schema validation (reusing schema/validate.py
logic) and timestamped snapshot storage.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "asset-v1.schema.json"
STORAGE_ROOT = REPO_ROOT / "storage"

_validator: Draft202012Validator | None = None


def get_validator() -> Draft202012Validator:
    """Load and cache the Draft 2020-12 validator used by schema/validate.py."""
    global _validator
    if _validator is None:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        # Same construction as schema/validate.py — do not reimplement rules.
        _validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return _validator


def describe_error(err) -> str:
    path = "/".join(str(p) for p in err.path) or "(root)"
    return f"{path}: {err.message}"


def validate_instance(instance: dict[str, Any]) -> list[str]:
    """Return a list of human-readable validation errors (empty if valid)."""
    validator = get_validator()
    errors = sorted(validator.iter_errors(instance), key=str)
    return [describe_error(e) for e in errors]


def require_valid(instance: dict[str, Any], context: str) -> None:
    """
    Validate against asset-v1.schema.json. On failure: log errors and raise
    SystemExit(1). Never persist an invalid instance.
    """
    errors = validate_instance(instance)
    if not errors:
        print(f"[VALIDATE] PASS — {context} is schema-valid (0 errors).")
        return
    print(f"[VALIDATE] FAIL — {context} has {len(errors)} schema error(s):", file=sys.stderr)
    for e in errors:
        print(f"        - {e}", file=sys.stderr)
    raise SystemExit(1)


def storage_path_for(asset_id: str, data_pulled_at: str) -> Path:
    """
    File naming: storage/{asset_id}/{data_pulled_at}.json
    Colons in the ISO timestamp are replaced with '-' so the filename is
    portable across filesystems; the timestamp *inside* the JSON remains
    unmodified ISO 8601.
    """
    safe_ts = data_pulled_at.replace(":", "-")
    return STORAGE_ROOT / asset_id / f"{safe_ts}.json"


def write_snapshot(instance: dict[str, Any]) -> Path:
    """
    Validate then write a new timestamped snapshot. Never overwrites: if the
    target path already exists, abort with a non-zero exit.
    """
    asset_id = instance["asset_id"]
    data_pulled_at = instance["data_pulled_at"]
    require_valid(instance, f"{asset_id} @ {data_pulled_at}")

    path = storage_path_for(asset_id, data_pulled_at)
    if path.exists():
        print(
            f"[STORAGE] REFUSING TO OVERWRITE existing snapshot: {path}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(instance, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"[STORAGE] Wrote new snapshot: {path}")
    return path
