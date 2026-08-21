#!/usr/bin/env python3
"""
One-candidate discovery cycle for the scheduler.

Default: next entry from scheduler/backlog.json.
Override: --candidate-name investigates that platform immediately
(need not already be on the backlog). Same investigation process either
way — seed fetch + FINDINGS.md + README index; PR-only, no auto-merge.

Never touches execution/. Never refreshes Elmnts.

Usage:
  python3 scheduler/run_discovery.py
  python3 scheduler/run_discovery.py --candidate-name "Decen Space"
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


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "candidate"


def _tokens_fuzzy_match(a: str, b: str) -> bool:
    """True when hyphen tokens align by prefix (decen-space ~ decentralized-space)."""
    ta, tb = a.split("-"), b.split("-")
    if not ta or not tb:
        return False
    if len(ta) != len(tb):
        if len(ta) == 1:
            return any(
                t.startswith(ta[0]) or ta[0].startswith(t)
                for t in tb
                if len(ta[0]) >= 4
            )
        return False
    return all(
        x.startswith(y) or y.startswith(x)
        for x, y in zip(tb, ta)
        if len(x) >= 3 and len(y) >= 3
    )


def match_backlog_candidate(
    items: list[dict[str, Any]], name: str
) -> tuple[dict[str, Any], int] | None:
    """Return (candidate, index) if name resolves to a backlog entry."""
    raw = name.strip()
    slug = slugify(raw)
    lower = raw.lower()
    for i, c in enumerate(items):
        if c.get("slug") == slug:
            return c, i
        if (c.get("display_name") or "").lower() == lower:
            return c, i
        if _tokens_fuzzy_match(slug, c.get("slug") or ""):
            return c, i
        dn_slug = slugify(c.get("display_name") or "")
        if dn_slug and _tokens_fuzzy_match(slug, dn_slug):
            return c, i
    return None


def synthetic_candidate(name: str) -> dict[str, Any]:
    """Ad-hoc candidate when name is not on backlog.json — same investigate() path."""
    slug = slugify(name)
    compact = slug.replace("-", "")
    seeds = [
        f"https://www.{compact}.com/",
        f"https://{compact}.com/",
        f"https://www.{compact}.org/",
        f"https://{compact}.org/",
        f"https://docs.{compact}.com/",
        f"https://docs.{compact}.org/",
    ]
    if "-" in slug:
        seeds.extend(
            [
                f"https://www.{slug}.com/",
                f"https://{slug}.org/",
                f"https://docs.{slug}.org/",
            ]
        )
    return {
        "slug": slug,
        "display_name": name.strip(),
        "seeds": seeds,
        "notes": (
            f"On-demand discovery override for {name.strip()!r} "
            "(not required to be on scheduler/backlog.json)."
        ),
        "on_demand": True,
    }


def resolve_candidate(
    backlog: dict[str, Any], candidate_name: str | None
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """
    Resolve who to investigate.

    Returns (candidate, advance_backlog, meta).
    - No override: next backlog item; advance on success.
    - Override matching backlog at next_index: that item; advance on success.
    - Override matching other backlog item: that item; do not advance.
    - Override not on backlog: synthetic candidate; do not advance.
    """
    items = backlog.get("candidates") or []
    idx = int(backlog.get("next_index", 0))
    meta: dict[str, Any] = {
        "override": bool(candidate_name and candidate_name.strip()),
        "next_index": idx,
        "backlog_len": len(items),
    }

    if not candidate_name or not candidate_name.strip():
        if not items:
            raise RuntimeError("backlog is empty — nothing to investigate")
        if idx >= len(items):
            raise RuntimeError(
                f"backlog exhausted (next_index={idx}, len={len(items)}). "
                "Add candidates or reset next_index manually."
            )
        cand = items[idx]
        meta["source"] = "backlog_next"
        return cand, True, meta

    matched = match_backlog_candidate(items, candidate_name)
    if matched is not None:
        cand, found_idx = matched
        advance = found_idx == idx
        meta["source"] = "backlog_match"
        meta["matched_index"] = found_idx
        meta["advance_backlog"] = advance
        return cand, advance, meta

    cand = synthetic_candidate(candidate_name)
    meta["source"] = "synthetic_on_demand"
    meta["advance_backlog"] = False
    return cand, False, meta


def html_to_text(raw: str) -> str:
    # Prefer meta description / og:description for JS-heavy marketing SPAs.
    meta_bits: list[str] = []
    for pat in (
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
    ):
        m = re.search(pat, raw, flags=re.I)
        if m:
            meta_bits.append(m.group(1).strip())
    parser = _TextExtractor()
    try:
        parser.feed(raw)
        body = parser.text()
    except Exception:
        body = re.sub(r"<[^>]+>", " ", raw)
    if meta_bits:
        return " ".join(meta_bits) + " " + body
    return body


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

Seed URLs were fetched live in this cycle
({("on-demand override" if candidate.get("on_demand") else "backlog / matched seeds")}).

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
        "--candidate-name",
        default=None,
        help=(
            "Optional on-demand platform name. Investigates that candidate "
            "immediately (need not be on backlog.json). Blank/omitted = "
            "next backlog item."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Investigate but do not write FINDINGS / advance backlog",
    )
    args = parser.parse_args()

    assert_scheduler_safe()
    started = utc_now_iso()
    details: dict[str, Any] = {
        "dry_run": args.dry_run,
        "candidate_name_input": args.candidate_name,
    }

    try:
        backlog = load_backlog()
        candidate, advance, meta = resolve_candidate(backlog, args.candidate_name)
        details.update(meta)
        slug = candidate["slug"]
        details["candidate"] = slug
        details["display_name"] = candidate.get("display_name")
        details["advance_backlog"] = advance

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

        if advance:
            idx = int(backlog.get("next_index", 0))
            backlog["next_index"] = idx + 1
            save_backlog(backlog)
            details["next_index_after"] = idx + 1
            print(f"Advanced backlog next_index -> {idx + 1}")
        else:
            details["next_index_after"] = backlog.get("next_index")
            print("Backlog pointer unchanged (on-demand / non-next match)")

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
