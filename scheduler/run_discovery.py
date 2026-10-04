#!/usr/bin/env python3
"""
One-candidate discovery cycle for the scheduler.

Default: select the best *new* physical-RWA candidate from the replenishable
pool + backlog, skipping anything already investigated (FINDINGS.md / durable
candidate state). Override: --candidate-name investigates that platform
immediately unless it was already researched.

Never touches execution/. Never refreshes Elmnts. Never auto-merges.

Usage:
  python3 scheduler/run_discovery.py --trigger scheduled
  python3 scheduler/run_discovery.py --trigger manual
  python3 scheduler/run_discovery.py --trigger manual --candidate-name "Lofty"
  python3 scheduler/run_discovery.py --dry-run
  python3 scheduler/run_discovery.py --candidate-name AgriFi --skip-research
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
from scheduler.candidate_state import (
    mark_investigated,
    save_state,
    sync_state_from_filesystem,
)
from scheduler.discovery_select import (
    domains_from_seeds,
    ensure_backlog_contains,
    infer_category,
    physical_asset_preclass,
    refine_physical_class_after_fetch,
    select_next_candidate,
)
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

    Primary path uses physical-RWA pool ranking and skips anything that
    already has FINDINGS.md / durable candidate state (fixes AgriFi loops
    when next_index is stale because discovery PRs were never merged).
    """
    cand, _state, meta = select_next_candidate(
        backlog,
        candidate_name=candidate_name,
        match_fn=match_backlog_candidate,
        synthetic_fn=synthetic_candidate,
    )
    advance = bool(meta.get("advance_backlog"))
    return cand, advance, meta


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


def classify(
    blob: str,
    reachable_count: int,
    *,
    physical_class: str,
) -> tuple[str, str]:
    """
    Provisional classification from reachable seed text + physical-asset gate.
    Defaults to insufficient-information when evidence is thin —
    never invents candidate-for-adapter without clear capital-only language.
    Never promotes generic DePIN / pure-crypto to candidate-for-adapter.
    """
    if physical_class == "generic-depin":
        return (
            "wrong-model",
            "Physical-asset gate: classified `generic-depin`. The project "
            "appears to be a network/utility token where holding the token "
            "does not represent ownership or economic exposure to a specific "
            "physical asset pool (Helium/Render/Filecoin-style). Rejected "
            "before adapter research.",
        )
    if physical_class == "pure-crypto":
        return (
            "wrong-model",
            "Physical-asset gate: classified `pure-crypto`. No meaningful "
            "relationship to an identifiable physical real-world asset was "
            "found. Rejected before adapter research.",
        )
    if physical_class == "physical-infrastructure-but-not-tokenized-asset":
        return (
            "wrong-model",
            "Physical-asset gate: physical infrastructure is mentioned, but "
            "reachable evidence does not show the token representing "
            "ownership, revenue rights, or financing exposure to that asset. "
            "Treated as non-tokenized-asset infrastructure for Tokn's thesis.",
        )

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
    if has_capital and not has_operator and physical_class in (
        "physical-rwa",
        "unclear",
    ):
        if physical_class == "unclear":
            return (
                "insufficient-information",
                "Capital-style language appeared, but the physical-asset "
                "relationship is still `unclear` after the relevance gate. "
                "Limited follow-up needed before candidate-for-adapter.",
            )
        return (
            "candidate-for-adapter",
            "Reachable seeds describe a capital / ownership / royalty-style "
            "path tied to a physical-RWA thesis without clear "
            "operator-hardware requirements. This is a **first-pass** signal "
            "only — a human must greenlight any adapter work separately. "
            "No adapter is created by this cycle.",
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
        "capital-only physical-RWA path or a hard wrong-model operator "
        "requirement. Manual follow-up is required (docs deep-dive, "
        "contracts, payout shape) before a stronger classification.",
    )


def investigate(
    candidate: dict[str, Any],
    *,
    selection_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = [fetch_url(u) for u in (candidate.get("seeds") or [])]
    reachable = [e for e in evidence if e["ok"]]
    blob = " ".join(e["excerpt"] for e in reachable)

    pre = (selection_meta or {}).get("physical_class_pre") or physical_asset_preclass(
        candidate
    )
    physical_class = refine_physical_class_after_fetch(pre, blob, candidate)
    classification, why = classify(
        blob, len(reachable), physical_class=physical_class
    )
    assert classification in VALID_CLASSIFICATIONS

    today = date.today().isoformat()
    slug = candidate["slug"]
    name = candidate["display_name"]
    notes = candidate.get("notes", "")
    category = candidate.get("category") or infer_category(candidate)
    official = (candidate.get("seeds") or [None])[0] or "—"
    discovery_source = (
        (selection_meta or {}).get("source")
        or candidate.get("discovery_source")
        or "unknown"
    )
    previously = bool((selection_meta or {}).get("previously_investigated"))
    duplicate = (selection_meta or {}).get("duplicate")

    # Physical-asset narrative (honest; no fabrication)
    if physical_class == "physical-rwa":
        physical_asset = (
            "Official/seed language indicates a physical real-world asset "
            "or identifiable asset pool (see excerpts)."
        )
        why_physical = (
            "Physical + ownership/economic-exposure markers present in "
            "notes/seeds/reachable text."
        )
        why_not_depin = (
            "Not classified as generic DePIN: evidence points to asset "
            "claim / financing exposure rather than network-work utility alone."
        )
    elif physical_class == "generic-depin":
        physical_asset = "No Tokn-qualifying tokenized physical-asset claim identified."
        why_physical = "Failed physical-RWA gate."
        why_not_depin = "N/A — this *is* classified as generic DePIN / operator network."
    else:
        physical_asset = "Not independently confirmed in this pass."
        why_physical = f"Physical-asset gate result: `{physical_class}`."
        why_not_depin = (
            "Gate did not assign generic-depin; still not sufficient for "
            "unqualified physical-RWA promotion without more evidence."
        )

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

## Discovery summary

| Field | Value |
| --- | --- |
| Candidate | {name} (`{slug}`) |
| Category | `{category}` |
| Official website | `{official}` |
| Token / asset identity | Not fabricated in discovery — see seeds/excerpts; ticker alone is never identity |
| Physical asset | {physical_asset} |
| Why it qualifies as physical RWA | {why_physical} |
| Why it is NOT generic DePIN | {why_not_depin} |
| Previously investigated? | {"yes" if previously else "no"} |
| Duplicate detected? | {duplicate if duplicate else "no"} |
| Discovery source | `{discovery_source}` |
| Physical-asset gate | `{physical_class}` |
| Classification | `{classification}` |

---

## What was checked

Seed URLs were fetched live in this cycle
({("on-demand override" if candidate.get("on_demand") else "ranked physical-RWA pool / backlog")}).

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
- Already-investigated slugs (existing FINDINGS.md / candidate state) are
  skipped on future discovery runs even if `next_index` is stale.
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
        "category": category,
        "physical_class": physical_class,
        "discovery_source": discovery_source,
        "domains": domains_from_seeds(candidate.get("seeds") or []),
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
            "immediately (need not be on backlog.json) and does NOT advance "
            "the backlog pointer. Blank/omitted = next backlog item."
        ),
    )
    parser.add_argument(
        "--trigger",
        choices=("scheduled", "manual"),
        default="manual",
        help=(
            "How this run was invoked. GitHub Actions sets scheduled for "
            "cron and manual for workflow_dispatch. Default manual for "
            "local CLI runs."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Investigate but do not write FINDINGS / advance backlog",
    )
    parser.add_argument(
        "--skip-research",
        action="store_true",
        help=(
            "Do not auto-run the adapter-spec research agent when "
            "classification is candidate-for-adapter."
        ),
    )
    args = parser.parse_args()

    assert_scheduler_safe()
    started = utc_now_iso()
    details: dict[str, Any] = {
        "dry_run": args.dry_run,
        "candidate_name_input": args.candidate_name,
        "trigger": args.trigger,
    }

    try:
        backlog = load_backlog()
        # Sync durable state first so AgriFi / others with FINDINGS are known
        # before selection — even when next_index is stale.
        sync_state_from_filesystem()
        candidate, advance, meta = resolve_candidate(backlog, args.candidate_name)
        details.update(
            {
                k: v
                for k, v in meta.items()
                if k != "rejected_during_selection"  # keep status log smaller
            }
        )
        details["rejected_count"] = len(meta.get("rejected_during_selection") or [])
        # For scheduled runs, manual_mode is not applicable.
        if args.trigger == "scheduled":
            details["manual_mode"] = None
        elif "manual_mode" not in details:
            details["manual_mode"] = (
                "override" if details.get("override") else "backlog_order"
            )

        slug = candidate["slug"]
        details["candidate"] = slug
        details["display_name"] = candidate.get("display_name")
        details["advance_backlog"] = advance
        details["category"] = candidate.get("category") or infer_category(candidate)
        details["physical_class_pre"] = meta.get("physical_class_pre")

        # Hard refuse re-writing an existing FINDINGS.md as a "new discovery".
        existing_findings = CANDIDATES_DIR / slug / "FINDINGS.md"
        if existing_findings.is_file() and not args.dry_run:
            raise RuntimeError(
                f"Refusing to rediscover '{slug}': {existing_findings} already "
                "exists. Selection should have skipped this candidate."
            )

        result = investigate(candidate, selection_meta=meta)
        details["classification"] = result["classification"]
        details["physical_class"] = result["physical_class"]
        details["category"] = result["category"]
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
            print("DRY RUN — backlog/state not advanced", file=sys.stderr)
            return 0

        out_dir = CANDIDATES_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_path = out_dir / "FINDINGS.md"
        findings_path.write_text(result["findings_md"], encoding="utf-8")
        update_readme_index(
            slug, result["display_name"], result["classification"], result["date"]
        )

        # Persist candidate onto backlog if it came from the pool.
        ensure_backlog_contains(backlog, candidate)

        # Durable state — survives unmerged pointer advances / fresh checkouts.
        state = sync_state_from_filesystem()
        mark_investigated(
            state,
            slug=slug,
            display_name=result["display_name"],
            findings_classification=result["classification"],
            category=result["category"],
            physical_class=result["physical_class"],
            discovery_source=result.get("discovery_source"),
            domains=result.get("domains"),
        )
        save_state(state)

        if advance:
            # Compatibility: keep next_index in sync by moving it to the first
            # backlog row that is still uninvestigated (not blind +1 on a
            # stale AgriFi slot).
            items = backlog.get("candidates") or []
            new_idx = len(items)
            for i, c in enumerate(items):
                cslug = c.get("slug") or ""
                if c.get("status") == "closed-category-probe":
                    continue
                if not (CANDIDATES_DIR / cslug / "FINDINGS.md").is_file():
                    new_idx = i
                    break
            backlog["next_index"] = new_idx
            save_backlog(backlog)
            details["next_index_after"] = new_idx
            print(f"Advanced backlog next_index -> {new_idx} (first uninvestigated)")
        else:
            details["next_index_after"] = backlog.get("next_index")
            save_backlog(backlog)  # may have gained pool candidate
            print(
                "Backlog pointer unchanged "
                f"(named override; next_index stays {backlog.get('next_index')})"
            )

        details["findings_path"] = str(findings_path.relative_to(REPO_ROOT))

        # Deeper research pass — only for candidate-for-adapter; additive
        # ADAPTER_SPEC.md; never auto-approves adapter work.
        # Physical gate must also be physical-rwa (not generic-depin).
        if (
            result["classification"] == "candidate-for-adapter"
            and result["physical_class"] == "physical-rwa"
            and not args.skip_research
        ):
            from scheduler.run_research_agent import research_candidate, write_spec

            research = research_candidate(candidate, require_findings=True)
            spec_path = write_spec(research)
            details["adapter_spec_path"] = str(spec_path.relative_to(REPO_ROOT))
            details["research_reachable_count"] = sum(
                1 for e in research["evidence"] if e["ok"]
            )
            # Refresh state with readiness if present — never auto-promote
            # beyond what the research agent wrote.
            state = sync_state_from_filesystem()
            save_state(state)
            print(f"Wrote {spec_path} (research agent; human review still required)")
        elif result["classification"] == "candidate-for-adapter":
            details["adapter_spec_path"] = None
            details["research_skipped"] = True
            print("Research agent skipped (--skip-research or non-physical-rwa gate)")

        append_status(
            job="discovery",
            status="success",
            started_at=started,
            finished_at=utc_now_iso(),
            details=details,
        )
        print(f"Wrote {findings_path}")
        print(f"Classification: {result['classification']}")
        print(f"Physical-asset gate: {result['physical_class']}")
        print(f"Category: {result['category']}")
        print(
            f"trigger={args.trigger} manual_mode={details.get('manual_mode')} "
            f"advance_backlog={advance} selection={meta.get('selection_mode')}"
        )
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
