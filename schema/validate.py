#!/usr/bin/env python3
"""
Validates the example instances in examples/ against asset-v1.schema.json
using Draft 2020-12 semantics, and prints a clear PASS/FAIL report.

Usage:
    python3 validate.py
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

BASE = Path(__file__).resolve().parent
SCHEMA_PATH = BASE / "asset-v1.schema.json"
EXAMPLES_DIR = BASE / "examples"

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


def main() -> int:
    schema = load(SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    all_ok = True

    print("=" * 70)
    print("Validating instances that SHOULD PASS")
    print("=" * 70)
    for fname in SHOULD_PASS:
        instance = load(EXAMPLES_DIR / fname)
        errors = sorted(validator.iter_errors(instance), key=str)
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
        instance = load(EXAMPLES_DIR / fname)
        errors = sorted(validator.iter_errors(instance), key=str)
        if errors:
            print(f"[PASS] {fname} — correctly rejected with {len(errors)} error(s):")
            for e in errors:
                print(f"        - {describe_error(e)}")
        else:
            all_ok = False
            print(f"[FAIL] {fname} — expected rejection, but it validated with 0 errors.")

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
