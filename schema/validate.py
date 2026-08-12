#!/usr/bin/env python3
"""
Validates example instances in examples/ and every snapshot under ../storage/
against asset-v1.schema.json using Draft 2020-12 semantics.

Usage:
    python3 validate.py
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

BASE = Path(__file__).resolve().parent
REPO_ROOT = BASE.parent
SCHEMA_PATH = BASE / "asset-v1.schema.json"
EXAMPLES_DIR = BASE / "examples"
STORAGE_DIR = REPO_ROOT / "storage"

# Instances that must validate cleanly against the schema.
SHOULD_PASS = ["glow-example.json", "elmnts-example.json"]

# Instances that are deliberately malformed and must be rejected.
SHOULD_FAIL = ["invalid-example.json"]


def load(path: Path):
    with open(path, "r") as f:
        return json.load(f)


def describe_error(err) -> str:
    path = "/".join(str(p) for p in err.path) or "(root)"
    return f"{path}: {err.message}"


def validate_one(validator: Draft202012Validator, path: Path) -> list:
    instance = load(path)
    return sorted(validator.iter_errors(instance), key=str)


def main() -> int:
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    all_ok = True

    print("=" * 70)
    print("Validating instances that SHOULD PASS")
    print("=" * 70)
    for fname in SHOULD_PASS:
        path = EXAMPLES_DIR / fname
        errors = validate_one(validator, path)
        if not errors:
            print(f"[PASS] {fname} — validated with 0 errors, as expected.")
        else:
            all_ok = False
            print(f"[FAIL] {fname} — expected 0 errors, got {len(errors)}:")
            for e in errors:
                print(f"        - {describe_error(e)}")

    print()
    print("=" * 70)
    print("Validating instances that SHOULD BE REJECTED")
    print("=" * 70)
    for fname in SHOULD_FAIL:
        path = EXAMPLES_DIR / fname
        errors = validate_one(validator, path)
        if errors:
            print(f"[PASS] {fname} — correctly rejected with {len(errors)} error(s):")
            for e in errors:
                print(f"        - {describe_error(e)}")
        else:
            all_ok = False
            print(f"[FAIL] {fname} — expected rejection, but it validated with 0 errors.")

    print()
    print("=" * 70)
    print("Validating live snapshots under storage/")
    print("=" * 70)
    if not STORAGE_DIR.exists():
        print("[WARN] storage/ does not exist yet — nothing to validate.")
    else:
        snapshots = sorted(STORAGE_DIR.glob("*/*.json"))
        if not snapshots:
            print("[WARN] storage/ has no snapshots yet.")
        for path in snapshots:
            rel = path.relative_to(REPO_ROOT)
            errors = validate_one(validator, path)
            if not errors:
                print(f"[PASS] {rel} — validated with 0 errors.")
            else:
                all_ok = False
                print(f"[FAIL] {rel} — {len(errors)} error(s):")
                for e in errors:
                    print(f"        - {describe_error(e)}")

    print()
    print("=" * 70)
    if all_ok:
        print("RESULT: ALL CHECKS PASSED")
    else:
        print("RESULT: ONE OR MORE CHECKS FAILED")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
