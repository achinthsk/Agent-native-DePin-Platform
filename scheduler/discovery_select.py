"""
Candidate selection for discovery: pool → dedupe → physical-RWA gate →
already-investigated filter → diversity ranking → best candidate.

Replaces blind next_index selection as the primary mechanism while still
advancing/updating backlog metadata for compatibility.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from scheduler.candidate_state import (
    host_key,
    is_already_investigated,
    load_pool,
    normalize_name,
    save_pool,
    sync_state_from_filesystem,
    upsert_candidate_record,
)
from scheduler.discovery_catalog import (
    GENERIC_DEPIN_BLOCKLIST,
    GENERIC_DEPIN_MARKERS,
    LIVE_PLATFORM_SLUGS,
    OWNERSHIP_EXPOSURE_MARKERS,
    PHYSICAL_MARKERS,
    PHYSICAL_RWA_CATEGORIES,
    SEED_CATALOG,
)

ADDR_RE = re.compile(r"0x[a-fA-F0-9]{40}")


def domains_from_seeds(seeds: list[str]) -> list[str]:
    out: list[str] = []
    for u in seeds or []:
        h = host_key(u)
        if h and h not in out:
            out.append(h)
    return out


def infer_category(candidate: dict[str, Any]) -> str:
    if candidate.get("category") in PHYSICAL_RWA_CATEGORIES:
        return candidate["category"]
    blob = " ".join(
        [
            candidate.get("display_name") or "",
            candidate.get("slug") or "",
            candidate.get("notes") or "",
            " ".join(candidate.get("seeds") or []),
        ]
    ).lower()
    rules = [
        ("farmland", ("farmland", "plantation", "agro", "agrifi", "acre")),
        ("agriculture", ("agriculture", "agricultural", "crop")),
        ("solar", ("solar",)),
        ("battery", ("battery", "storage infrastructure")),
        ("energy", ("energy", "renewable", "power plant")),
        ("mining", ("mining", "mineral", "royalty", "nsr", "smelter")),
        ("real_estate", ("real estate", "real-estate", "rental", "property", "lofty", "realt")),
        ("data_center", ("data center", "datacenter")),
        ("infrastructure", ("infrastructure financing", "equipment financing")),
    ]
    for cat, keys in rules:
        if any(k in blob for k in keys):
            return cat
    return "other_physical_rwa"


def physical_asset_preclass(candidate: dict[str, Any], blob: str = "") -> str:
    """
    Early physical-asset relevance gate.

    Returns one of:
      physical-rwa | physical-infrastructure-but-not-tokenized-asset |
      generic-depin | pure-crypto | unclear
    """
    slug = (candidate.get("slug") or "").lower()
    name_n = normalize_name(candidate.get("display_name") or "")
    if slug in GENERIC_DEPIN_BLOCKLIST or name_n in {
        normalize_name(x) for x in GENERIC_DEPIN_BLOCKLIST
    }:
        return "generic-depin"

    text = " ".join(
        [
            candidate.get("display_name") or "",
            candidate.get("notes") or "",
            blob,
        ]
    ).lower()

    has_physical = any(m in text for m in PHYSICAL_MARKERS)
    has_exposure = any(m in text for m in OWNERSHIP_EXPOSURE_MARKERS)
    has_depin = any(m in text for m in GENERIC_DEPIN_MARKERS)

    # Explicit catalog skip / live platforms
    if candidate.get("skip") or slug in LIVE_PLATFORM_SLUGS:
        return "physical-rwa"  # known, but selection layer skips investigated/live

    if has_depin and not has_exposure:
        return "generic-depin"
    if has_physical and has_exposure:
        return "physical-rwa"
    if has_physical and not has_exposure:
        # Physical infra mentioned but no ownership/economic claim language yet
        if has_depin:
            return "physical-infrastructure-but-not-tokenized-asset"
        return "unclear"
    if not has_physical and not has_depin:
        # crypto-only marketing
        if any(k in text for k in ("token", "defi", "swap", "meme", "airdrop")):
            return "pure-crypto"
        return "unclear"
    if has_depin:
        return "generic-depin"
    return "unclear"


def refine_physical_class_after_fetch(
    preclass: str, blob: str, candidate: dict[str, Any]
) -> str:
    """Re-evaluate after seed fetch text is available."""
    return physical_asset_preclass(candidate, blob=blob or "")


def identity_keys(candidate: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    slug = candidate.get("slug") or ""
    if slug:
        keys.add(f"slug:{slug}")
    dn = normalize_name(candidate.get("display_name") or "")
    if dn:
        keys.add(f"name:{dn}")
    for a in candidate.get("aliases") or []:
        na = normalize_name(a)
        if na:
            keys.add(f"alias:{na}")
    for d in domains_from_seeds(candidate.get("seeds") or []):
        keys.add(f"domain:{d}")
    for d in candidate.get("domains") or []:
        keys.add(f"domain:{d}")
    for addr in candidate.get("token_addresses") or []:
        if isinstance(addr, str) and ADDR_RE.fullmatch(addr):
            keys.add(f"addr:{addr.lower()}")
        elif isinstance(addr, dict):
            chain = (addr.get("chain") or "").lower()
            a = (addr.get("address") or "").lower()
            if a and ADDR_RE.fullmatch(a):
                keys.add(f"chain_addr:{chain}:{a}" if chain else f"addr:{a}")
    # NOTE: ticker-only keys intentionally omitted — tickers are never identity.
    return keys


def find_duplicate(
    candidate: dict[str, Any],
    state: dict[str, Any],
    pool_items: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return an existing record this candidate duplicates, else None."""
    keys = identity_keys(candidate)
    if not keys:
        return None

    # Against state
    for slug, rec in (state.get("candidates") or {}).items():
        other = {
            "slug": slug,
            "display_name": rec.get("display_name") or slug,
            "aliases": rec.get("aliases") or [],
            "domains": rec.get("domains") or [],
            "seeds": [],
            "token_addresses": rec.get("token_addresses") or [],
        }
        overlap = keys & identity_keys(other)
        if overlap and slug != candidate.get("slug"):
            return {
                "slug": slug,
                "reason": f"identity overlap with state:{slug}",
                "overlap": sorted(overlap),
            }

    # Against other pool items
    for other in pool_items:
        if other.get("slug") == candidate.get("slug"):
            continue
        overlap = keys & identity_keys(other)
        if overlap:
            return {
                "slug": other.get("slug"),
                "reason": f"identity overlap with pool:{other.get('slug')}",
                "overlap": sorted(overlap),
            }
    return None


def replenish_pool(state: dict[str, Any], min_uninvestigated: int = 5) -> dict[str, Any]:
    """Ensure discovery_pool.json has enough uninvestigated physical-RWA seeds."""
    pool = load_pool()
    items: list[dict[str, Any]] = list(pool.get("candidates") or [])
    by_slug = {c.get("slug"): c for c in items if c.get("slug")}

    # Merge catalog entries (skip sentinels)
    for seed in SEED_CATALOG:
        slug = seed["slug"]
        if seed.get("skip"):
            upsert_candidate_record(
                state,
                slug=slug,
                display_name=seed["display_name"],
                category=seed.get("category"),
                domains=domains_from_seeds(seed.get("seeds") or []),
                aliases=seed.get("aliases") or [],
                status="live" if slug in ("glow-protocol", "realt-platform") else "rejected",
                discovery_source="seed_catalog",
                notes=seed.get("notes"),
            )
            state["candidates"][slug]["skip"] = True
            state["candidates"][slug]["investigated"] = True
            continue
        if slug not in by_slug:
            entry = {
                "slug": slug,
                "display_name": seed["display_name"],
                "category": seed.get("category") or infer_category(seed),
                "seeds": list(seed.get("seeds") or []),
                "notes": seed.get("notes") or "",
                "aliases": list(seed.get("aliases") or []),
                "domains": domains_from_seeds(seed.get("seeds") or []),
                "discovery_source": seed.get("discovery_source") or "seed_catalog",
            }
            items.append(entry)
            by_slug[slug] = entry

    uninvestigated = [
        c
        for c in items
        if not is_already_investigated(c["slug"], state) and not c.get("skip")
    ]
    # If still low, nothing else to invent — catalog is the replenishment source.
    pool["candidates"] = items
    pool["uninvestigated_count"] = len(uninvestigated)
    save_pool(pool)
    return pool


def diversity_score(category: str, recent_categories: list[str]) -> float:
    """Higher is better. Penalize categories seen recently."""
    if not category:
        return 0.0
    recent = recent_categories[-8:]
    repeats = sum(1 for c in recent if c == category)
    # Prefer unseen categories
    if category not in recent:
        return 5.0
    return max(0.0, 4.0 - repeats)


def rank_candidate(
    candidate: dict[str, Any],
    state: dict[str, Any],
    physical_class: str,
) -> float:
    score = 0.0
    if physical_class == "physical-rwa":
        score += 10.0
    elif physical_class == "unclear":
        score += 3.0
    elif physical_class == "physical-infrastructure-but-not-tokenized-asset":
        score += 1.0
    else:
        return -100.0  # generic-depin / pure-crypto — do not select for deep discovery

    cat = infer_category(candidate)
    score += diversity_score(cat, list(state.get("recent_categories") or []))

    # Prefer named issuers with real seeds
    seeds = candidate.get("seeds") or []
    score += min(3.0, 0.5 * len(seeds))
    if candidate.get("discovery_source") == "seed_catalog":
        score += 0.5
    return score


def collect_selection_universe(
    backlog: dict[str, Any], pool: dict[str, Any]
) -> list[dict[str, Any]]:
    """Merge backlog + pool; prefer richer records; named platforms only."""
    by_slug: dict[str, dict[str, Any]] = {}
    for c in backlog.get("candidates") or []:
        slug = c.get("slug")
        if not slug:
            continue
        # Skip closed category probes
        if c.get("status") == "closed-category-probe":
            continue
        entry = dict(c)
        entry["category"] = infer_category(entry)
        entry["domains"] = domains_from_seeds(entry.get("seeds") or [])
        entry["discovery_source"] = entry.get("discovery_source") or "backlog"
        by_slug[slug] = entry
    for c in pool.get("candidates") or []:
        slug = c.get("slug")
        if not slug or c.get("skip"):
            continue
        if slug in by_slug:
            # Merge seeds/aliases
            cur = by_slug[slug]
            seeds = list(dict.fromkeys((cur.get("seeds") or []) + (c.get("seeds") or [])))
            cur["seeds"] = seeds
            cur["aliases"] = sorted(
                set(cur.get("aliases") or []) | set(c.get("aliases") or [])
            )
            cur["category"] = c.get("category") or cur.get("category")
            cur["domains"] = domains_from_seeds(seeds)
            if c.get("notes") and not cur.get("notes"):
                cur["notes"] = c["notes"]
            cur["discovery_source"] = cur.get("discovery_source") or c.get(
                "discovery_source"
            )
        else:
            entry = dict(c)
            entry["category"] = infer_category(entry)
            entry["domains"] = domains_from_seeds(entry.get("seeds") or [])
            by_slug[slug] = entry
    return list(by_slug.values())


def select_next_candidate(
    backlog: dict[str, Any],
    *,
    candidate_name: str | None = None,
    match_fn=None,
    synthetic_fn=None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """
    Select the next discovery candidate.

    Returns (candidate, state, meta).

    - Named override still allowed (manual), but if already investigated,
      raises unless explicitly forcing via override of a new synthetic name.
    - Default path ignores stale next_index for already-investigated rows and
      picks the best uninvestigated physical-RWA-ranked candidate.
    """
    state = sync_state_from_filesystem()
    pool = replenish_pool(state, min_uninvestigated=5)
    meta: dict[str, Any] = {
        "selection_mode": None,
        "next_index_before": int(backlog.get("next_index", 0)),
        "backlog_len": len(backlog.get("candidates") or []),
        "pool_len": len(pool.get("candidates") or []),
        "rejected_during_selection": [],
    }

    # Manual named override
    if candidate_name and candidate_name.strip():
        meta["override"] = True
        matched = match_fn(backlog.get("candidates") or [], candidate_name) if match_fn else None
        if matched is not None:
            cand, found_idx = matched
            cand = dict(cand)
            cand["category"] = infer_category(cand)
            cand["domains"] = domains_from_seeds(cand.get("seeds") or [])
            meta["source"] = "backlog_match"
            meta["matched_index"] = found_idx
            meta["manual_mode"] = "override"
            meta["advance_backlog"] = False
        else:
            # Try pool
            slug_guess = re.sub(r"[^a-z0-9]+", "-", candidate_name.strip().lower()).strip(
                "-"
            ) or "candidate"
            pool_hit = next(
                (
                    c
                    for c in (pool.get("candidates") or [])
                    if c.get("slug") == slug_guess
                    or (c.get("display_name") or "").lower()
                    == candidate_name.strip().lower()
                ),
                None,
            )
            if pool_hit:
                cand = dict(pool_hit)
                meta["source"] = "pool_match"
            else:
                cand = synthetic_fn(candidate_name) if synthetic_fn else {
                    "slug": slug_guess,
                    "display_name": candidate_name.strip(),
                    "seeds": [],
                    "notes": "synthetic",
                    "on_demand": True,
                }
                meta["source"] = "synthetic_on_demand"
            cand["category"] = infer_category(cand)
            cand["domains"] = domains_from_seeds(cand.get("seeds") or [])
            meta["manual_mode"] = "override"
            meta["advance_backlog"] = False

        if is_already_investigated(cand["slug"], state):
            raise RuntimeError(
                f"Candidate '{cand['slug']}' was already investigated "
                f"(FINDINGS.md or state={((state.get('candidates') or {}).get(cand['slug']) or {}).get('state')}). "
                "Discovery will not re-select it as a new candidate. "
                "Use the research agent if you need to refresh ADAPTER_SPEC.md."
            )
        pre = physical_asset_preclass(cand)
        meta["physical_class_pre"] = pre
        meta["selection_mode"] = "manual_override"
        meta["previously_investigated"] = False
        meta["duplicate"] = find_duplicate(cand, state, pool.get("candidates") or [])
        return cand, state, meta

    # Automatic selection
    meta["override"] = False
    meta["manual_mode"] = "backlog_order"
    meta["advance_backlog"] = True
    universe = collect_selection_universe(backlog, pool)

    ranked: list[tuple[float, dict[str, Any], str]] = []
    for cand in universe:
        slug = cand["slug"]
        if is_already_investigated(slug, state):
            meta["rejected_during_selection"].append(
                {"slug": slug, "reason": "already_investigated"}
            )
            continue
        if slug in LIVE_PLATFORM_SLUGS or cand.get("skip"):
            meta["rejected_during_selection"].append(
                {"slug": slug, "reason": "live_or_skip"}
            )
            continue
        dup = find_duplicate(cand, state, universe)
        if dup and is_already_investigated(dup["slug"], state):
            meta["rejected_during_selection"].append(
                {
                    "slug": slug,
                    "reason": "duplicate_of_investigated",
                    "duplicate_of": dup["slug"],
                    "overlap": dup.get("overlap"),
                }
            )
            continue
        pre = physical_asset_preclass(cand)
        score = rank_candidate(cand, state, pre)
        if score < 0:
            meta["rejected_during_selection"].append(
                {"slug": slug, "reason": f"physical_gate:{pre}"}
            )
            continue
        ranked.append((score, cand, pre))

    if not ranked:
        raise RuntimeError(
            "No eligible physical-RWA discovery candidates remain. "
            "Replenish scheduler/discovery_pool.json / discovery_catalog.py "
            "with new named platforms."
        )

    ranked.sort(key=lambda t: (-t[0], t[1]["slug"]))
    score, cand, pre = ranked[0]
    meta["source"] = "ranked_pool"
    meta["selection_mode"] = "physical_rwa_ranked"
    meta["selection_score"] = score
    meta["physical_class_pre"] = pre
    meta["category"] = infer_category(cand)
    meta["previously_investigated"] = False
    meta["duplicate"] = None
    meta["ranked_top"] = [
        {
            "slug": c["slug"],
            "score": s,
            "physical_class": p,
            "category": infer_category(c),
        }
        for s, c, p in ranked[:5]
    ]
    # Ensure state knows this candidate exists as undiscovered until written
    upsert_candidate_record(
        state,
        slug=cand["slug"],
        display_name=cand.get("display_name") or cand["slug"],
        category=infer_category(cand),
        domains=domains_from_seeds(cand.get("seeds") or []),
        aliases=cand.get("aliases") or [],
        status="undiscovered",
        physical_class=pre,
        discovery_source=cand.get("discovery_source"),
        notes=cand.get("notes"),
    )
    return cand, state, meta


def ensure_backlog_contains(backlog: dict[str, Any], candidate: dict[str, Any]) -> None:
    """Add newly selected pool candidates onto backlog for auditability."""
    items = backlog.setdefault("candidates", [])
    if any(c.get("slug") == candidate["slug"] for c in items):
        return
    items.append(
        {
            "slug": candidate["slug"],
            "display_name": candidate.get("display_name"),
            "seeds": candidate.get("seeds") or [],
            "notes": candidate.get("notes") or "",
            "category": infer_category(candidate),
            "discovery_source": candidate.get("discovery_source") or "pool",
        }
    )
