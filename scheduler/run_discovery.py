#!/usr/bin/env python3
"""
One-candidate discovery cycle for the scheduler.

Pulls the next entry from scheduler/backlog.json, runs the candidates/
investigation process (seed fetch + FINDINGS.md + README index row),
advances the backlog pointer, and appends a status record.

Never touches execution/. Never refreshes Elmnts. Does not auto-merge —
the GitHub Actions workflow opens a PR for human review.

Usage:
  python3 scheduler/run_discovery.py
  python3 scheduler/run_discovery.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scheduler._guards import assert_scheduler_safe
from scheduler.status_log import append_status, utc_now_iso

BACKLOG_PATH = Path(__file__).resolve().parent / "backlog.json"
CANDIDATES_DIR = REPO_ROOT / "candidates"
README_PATH = CANDIDATES_DIR / "README.md"
UA = "Mozilla/5.0 (compatible; DePIN-scheduler-discovery/1.0)"
TIMEOUT = 45

# candidates/README.md classifications — do not invent others.
VALID_CLASSIFICATIONS = {
    "candidate-for-adapter",
    "not-yet-investable",
    "wrong-model",
    "insufficient-information",
}

OPERATOR_MARKERS = (
    "run a node",
    "run the node",
    "operate a node",
    "node operator",
    "hardware requirements",
    "stake and run",
    "contribute hardware",
    "host a",
    "miner setup",
    "validator client",
    "download the client",
    "gpu host",
    "provide compute",
)

CAPITAL_MARKERS = (
    "buy a license",
    "purchase a license",
    "capital only",
    "passive income",
    "rental yield",
    "royalty",
    "tokenized",
    "own a share",
    "fractional ownership",
    "no hardware",
    "without operating",
)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if not self._skip:
            t = data.strip()
            if t:
                self._chunks.append(t)

    def text(self) -> str:
        return " ".join(self._chunks)


def load_backlog() -> dict[str, Any]:
    return json.loads(BACKLOG_PATH.read_text(encoding="utf-8"))


def save_backlog(data: dict[str, Any]) -> None:
    BACKLOG_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def html_to_text(raw: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(raw)
        return parser.text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", raw)


def fetch_url(url: str) -> dict[str, Any]:
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=TIMEOUT) as resp:
            raw_bytes = resp.read()
            code = getattr(resp, "status", 200)
            ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
            raw = raw_bytes.decode("utf-8", errors="replace")
            text = html_to_text(raw) if "html" in ct or raw.lstrip().startswith("<") else raw
            text = re.sub(r"\s+", " ", text).strip()
            return {
                "url": url,
                "ok": True,
                "http_status": code,
                "content_type": ct,
                "excerpt": text[:1500],
                "error": None,
            }
    except HTTPError as e:
        return {
            "url": url,
            "ok": False,
            "http_status": e.code,
            "content_type": None,
            "excerpt": "",
            "error": f"HTTP {e.code}: {e.reason}",
        }
    except URLError as e:
        return {
            "url": url,
            "ok": False,
            "http_status": None,
            "content_type": None,
            "excerpt": "",
            "error": f"URL error: {e.reason}",
        }
    except Exception as e:
        return {
            "url": url,
            "ok": False,
            "http_status": None,
            "content_type": None,
            "excerpt": "",
            "error": f"{type(e).__name__}: {e}",
        }


def classify(blob: str, reachable_count: int) -> tuple[str, str]:
    """
    Provisional classification from reachable seed text.
    Defaults to insufficient-information when evidence is thin —
    never invents candidate-for-adapter without clear capital-only language.
    """
    if reachable_count == 0:
        return (
            "insufficient-information",
            "None of the seed URLs returned usable content during this "
            "scheduled cycle. Retry with better primary sources before "
            "any stronger disposition.",
        )

    lower = blob.lower()
    has_operator = any(m in lower for m in OPERATOR_MARKERS)
    has_capital = any(m in lower for m in CAPITAL_MARKERS)

    if has_operator and not has_capital:
        return (
            "wrong-model",
            "Reachable seeds emphasize node/hardware operation (or "
            "equivalent active work) without a clear capital-only path "
            "matching Glow / Elmnts / RealT. Provisional — human should "
            "confirm before treating as final.",
        )
    if has_capital and not has_operator:
        return (
            "candidate-for-adapter",
            "Reachable seeds describe a capital / ownership / royalty-style "
            "path without clear operator-hardware requirements. This is a "
            "**first-pass** signal only — a human must greenlight any "
            "adapter work separately. No adapter is created by this cycle.",
        )
    if "coming soon" in lower or "waitlist" in lower or "not launched" in lower:
        return (
            "not-yet-investable",
            "Seeds look project-shaped but signal pre-launch / waitlist "
            "state rather than a live participation path with public data.",
        )
    return (
        "insufficient-information",
        "Seeds were reachable but did not clearly establish either a "
        "capital-only path or a hard wrong-model operator requirement. "
        "Manual follow-up is required (docs deep-dive, contracts, payout "
        "shape) before a stronger classification.",
    )


def investigate(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = [fetch_url(u) for u in (candidate.get("seeds") or [])]
    reachable = [e for e in evidence if e["ok"]]
    blob = " ".join(e["excerpt"] for e in reachable)
    classification, why = classify(blob, len(reachable))
    assert classification in VALID_CLASSIFICATIONS

    today = date.today().isoformat()
    slug = candidate["slug"]
    name = candidate["display_name"]
    notes = candidate.get("notes", "")

    rows = []
    for e in evidence:
        if e["ok"]:
            result = f"HTTP {e['http_status']} — live ({e['content_type'] or 'unknown type'})"
        else:
            result = e["error"] or "unreachable"
        rows.append(f"| `{e['url']}` | {result} |")

    excerpt_blocks = []
    for e in reachable:
        snippet = e["excerpt"][:500].replace("|", "/")
        excerpt_blocks.append(f"### `{e['url']}`\n\n> {snippet}\n")

    if not excerpt_blocks:
        excerpt_blocks.append("_No reachable seed returned extractable text._\n")

    findings = f"""# {name} — candidate investigation

**Classification: `{classification}`**

**Date investigated:** {today}
**Investigator note:** Scheduler discovery cycle (`scheduler/run_discovery.py`).
Research log only. No adapter, schema, scoring, storage, or API changes
accompany this document beyond this FINDINGS file and the candidates index
row. Elmnts was not touched. `execution/` was not invoked.

Backlog notes: {notes}

---

## What was checked

Seed URLs from `scheduler/backlog.json` were fetched live in this cycle.

| Source | Result |
| --- | --- |
{chr(10).join(rows)}

## Reachable text excerpts (truncated)

{chr(10).join(excerpt_blocks)}

## Classification rationale

**`{classification}`**

{why}

## Can the four scores be computed?

**No.** Discovery does not invent scores. An adapter + real `storage/`
snapshot would be required first, and only after a human greenlights
adapter work for a `candidate-for-adapter` disposition.

## What would need to change for this to become scoreable

1. Human review of this FINDINGS.md.
2. If promoted: a dedicated adapter under `adapters/` (SourceError
   discipline; no fabrication).
3. At least one real snapshot under `storage/<asset-id>/`.
4. Confirmation that payout / claim mechanics fit this project's
   capital-provision bar — or keep `wrong-model` / `not-yet-investable`
   / `insufficient-information` as the honest outcome.

## Scheduler notes

- One candidate per cycle (this file).
- Output is intended to land as a PR for human merge — nothing auto-merges.
"""
    return {
        "slug": slug,
        "display_name": name,
        "classification": classification,
        "findings_md": findings,
        "evidence": evidence,
        "reachable_count": len(reachable),
        "date": today,
    }


def update_readme_index(slug: str, name: str, classification: str, day: str) -> None:
    text = README_PATH.read_text(encoding="utf-8")
    if f"`{slug}/FINDINGS.md`" in text or f"./{slug}/FINDINGS.md" in text:
        return
    row = (
        f"| {name} | `{classification}` | {day} | "
        f"[`{slug}/FINDINGS.md`](./{slug}/FINDINGS.md) |"
    )
    # Insert after the header separator line of the index table.
    marker = "| --- | --- | --- | --- |"
    alt = "|---------|---------|-------------|"
    if marker in text:
        text = text.replace(marker, marker + "\n" + row, 1)
    elif alt in text:
        text = text.replace(alt, alt + "\n" + row, 1)
    else:
        # Fallback: append under ## Index
        if "## Index" not in text:
            raise RuntimeError("candidates/README.md missing ## Index section")
        text = text.rstrip() + "\n" + row + "\n"
    README_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Investigate but do not write FINDINGS / advance backlog",
    )
    args = parser.parse_args()

    assert_scheduler_safe()
    started = utc_now_iso()
    details: dict[str, Any] = {"dry_run": args.dry_run}

    try:
        backlog = load_backlog()
        items = backlog.get("candidates") or []
        idx = int(backlog.get("next_index", 0))
        details["next_index_before"] = idx
        details["backlog_len"] = len(items)

        if not items:
            raise RuntimeError("backlog is empty — nothing to investigate")
        if idx >= len(items):
            raise RuntimeError(
                f"backlog exhausted (next_index={idx}, len={len(items)}). "
                "Add candidates or reset next_index manually."
            )

        candidate = items[idx]
        slug = candidate["slug"]
        details["candidate"] = slug
        details["display_name"] = candidate.get("display_name")

        result = investigate(candidate)
        details["classification"] = result["classification"]
        details["reachable_count"] = result["reachable_count"]
        details["evidence"] = [
            {
                "url": e["url"],
                "ok": e["ok"],
                "http_status": e.get("http_status"),
                "error": e.get("error"),
            }
            for e in result["evidence"]
        ]

        if args.dry_run:
            print(result["findings_md"])
            append_status(
                job="discovery",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                details={**details, "note": "dry-run; no files written"},
            )
            print("DRY RUN — backlog not advanced", file=sys.stderr)
            return 0

        out_dir = CANDIDATES_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_path = out_dir / "FINDINGS.md"
        findings_path.write_text(result["findings_md"], encoding="utf-8")
        update_readme_index(
            slug, result["display_name"], result["classification"], result["date"]
        )

        backlog["next_index"] = idx + 1
        save_backlog(backlog)
        details["next_index_after"] = idx + 1
        details["findings_path"] = str(findings_path.relative_to(REPO_ROOT))

        append_status(
            job="discovery",
            status="success",
            started_at=started,
            finished_at=utc_now_iso(),
            details=details,
        )
        print(f"Wrote {findings_path}")
        print(f"Classification: {result['classification']}")
        print(f"Advanced backlog next_index -> {idx + 1}")
        return 0

    except Exception as e:
        append_status(
            job="discovery",
            status="failure",
            started_at=started,
            finished_at=utc_now_iso(),
            error=f"{type(e).__name__}: {e}",
            details=details,
        )
        print(f"DISCOVERY FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
