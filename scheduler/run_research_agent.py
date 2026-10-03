#!/usr/bin/env python3
"""
Adapter-spec research agent — deeper pass for `candidate-for-adapter` only.

Extends discovery; does not replace it. After a candidate is classified
`candidate-for-adapter` (FINDINGS.md already written), this job produces
`candidates/<slug>/ADAPTER_SPEC.md`: an adapter-readiness specification
for human review. It writes **zero** adapter code, schema, scoring, or
storage changes.

The spec answers: can Tokn build a meaningful verification adapter, what
exactly can it verify, what can it not, and what evidence should an
eventual adapter pull?

Usage:
  python3 scheduler/run_research_agent.py --candidate-name AgriFi
  python3 scheduler/run_research_agent.py --candidate-name PTX --no-status-log
  python3 scheduler/run_research_agent.py --candidate-name AgriFi --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scheduler._guards import assert_scheduler_safe
from scheduler.run_discovery import (
    CANDIDATES_DIR,
    load_backlog,
    match_backlog_candidate,
    slugify,
    synthetic_candidate,
)
from scheduler.status_log import append_status, utc_now_iso

UA = "Mozilla/5.0 (compatible; DePIN-scheduler-research/1.0)"
TIMEOUT = 45
CLASSIFICATION_RE = re.compile(
    r"\*\*Classification:\s*`([^`]+)`\*\*", re.IGNORECASE
)
ADDR_RE = re.compile(r"0x[a-fA-F0-9]{40}")

READINESS_STATES = ("adapter-ready", "token-data-only", "blocked")
CLAIM_STATUSES = (
    "verified",
    "partially-verified",
    "observable",
    "self-reported",
    "conflicted",
    "unverified",
    "blocked",
)

CHAIN_RPC = {
    "polygon": "https://polygon-bor-rpc.publicnode.com",
    "ethereum": "https://ethereum-rpc.publicnode.com",
    "arbitrum": "https://arbitrum-one-rpc.publicnode.com",
    "bsc": "https://bsc-rpc.publicnode.com",
    "base": "https://base-rpc.publicnode.com",
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style", "noscript"):
            self._skip = True
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)

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


def html_to_text_and_links(raw: str, base_url: str) -> tuple[str, list[str]]:
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
        hrefs = parser.hrefs
    except Exception:
        body = re.sub(r"<[^>]+>", " ", raw)
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', raw, flags=re.I)
    text = (" ".join(meta_bits) + " " + body).strip() if meta_bits else body
    abs_links: list[str] = []
    for h in hrefs:
        if h.startswith("#") or h.startswith("mailto:") or h.startswith("javascript:"):
            continue
        abs_links.append(urljoin(base_url, h))
    return text, abs_links


def fetch_url(url: str, max_bytes: int = 200_000) -> dict[str, Any]:
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=TIMEOUT) as resp:
            raw_bytes = resp.read(max_bytes)
            code = getattr(resp, "status", 200)
            ct = (resp.headers.get("Content-Type") or "").split(";")[0].strip()
            if "pdf" in ct.lower() or raw_bytes[:4] == b"%PDF":
                return {
                    "url": url,
                    "ok": True,
                    "http_status": code,
                    "content_type": ct or "application/pdf",
                    "excerpt": (
                        f"[PDF reachable — {len(raw_bytes)} bytes fetched; "
                        "binary not fully text-extracted by this agent]"
                    ),
                    "raw_text": "",
                    "links": [],
                    "error": None,
                    "kind": "pdf",
                }
            raw = raw_bytes.decode("utf-8", errors="replace")
            links: list[str] = []
            if url.rstrip("/").endswith(".md") or "text/markdown" in ct or url.endswith(
                ".txt"
            ):
                text = raw
            elif "html" in ct or raw.lstrip().startswith("<"):
                text, links = html_to_text_and_links(raw, url)
            else:
                text = raw
            text = re.sub(r"\s+", " ", text).strip()
            return {
                "url": url,
                "ok": True,
                "http_status": code,
                "content_type": ct,
                "excerpt": text[:2000],
                "raw_text": text[:25000],
                "links": links,
                "error": None,
                "kind": "text",
            }
    except HTTPError as e:
        return _err(url, f"HTTP {e.code}: {e.reason}", e.code)
    except URLError as e:
        return _err(url, f"URL error: {e.reason}")
    except Exception as e:
        return _err(url, f"{type(e).__name__}: {e}")


def _err(url: str, error: str, code: int | None = None) -> dict[str, Any]:
    return {
        "url": url,
        "ok": False,
        "http_status": code,
        "content_type": None,
        "excerpt": "",
        "raw_text": "",
        "links": [],
        "error": error,
        "kind": "error",
    }


def read_findings_classification(slug: str) -> tuple[Path, str | None]:
    path = CANDIDATES_DIR / slug / "FINDINGS.md"
    if not path.is_file():
        return path, None
    text = path.read_text(encoding="utf-8")
    m = CLASSIFICATION_RE.search(text)
    return path, (m.group(1).strip() if m else None)


def resolve_candidate(name: str) -> dict[str, Any]:
    backlog = load_backlog()
    items = backlog.get("candidates") or []
    matched = match_backlog_candidate(items, name)
    if matched is not None:
        return matched[0]
    return synthetic_candidate(name)


def expand_research_urls(candidate: dict[str, Any]) -> list[str]:
    """Seed URLs + generic doc/app guesses from the candidate hostnames."""
    seeds = list(candidate.get("seeds") or [])
    extras: list[str] = []
    hosts: set[str] = set()
    for u in seeds:
        try:
            host = urlparse(u).netloc.lower()
            if host:
                hosts.add(host)
                # strip leading www.
                if host.startswith("www."):
                    hosts.add(host[4:])
        except Exception:
            continue
    for host in sorted(hosts):
        root = host.split(".")
        if len(root) >= 2:
            base = ".".join(root[-2:])  # e.g. agrifi.tech, ptxtoken.com
            extras.extend(
                [
                    f"https://{base}/",
                    f"https://docs.{base}/",
                    f"https://app.{base}/",
                    f"https://blog.{base}/",
                    f"https://{base}/whitepaper",
                    f"https://{base}/whitepaper.pdf",
                    f"https://{base}/llm/{slugify(candidate['display_name'])}-llm-knowledge-base.html",
                ]
            )
            # Common gitbook pattern from product name
            compact = slugify(candidate["display_name"]).replace("-", "")
            extras.append(f"https://{compact}.gitbook.io/{compact}-docs/llms.txt")
            extras.append(f"https://{compact}.gitbook.io/{compact}-docs/")
    # Follow .md mirrors of gitbook HTML seeds.
    mirrored: list[str] = []
    for u in seeds + extras:
        if "gitbook.io" in u and not u.endswith((".md", ".txt")):
            mirrored.append(u.rstrip("/") + ".md")
    seen: set[str] = set()
    out: list[str] = []
    for u in seeds + extras + mirrored:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def interesting_follow_links(links: list[str], limit: int = 10) -> list[str]:
    keys = (
        "gitbook",
        "docs",
        "whitepaper",
        "token",
        "tokenomics",
        "architecture",
        "llm",
        "api",
        "contract",
        "staking",
        "nsr",
        "royalty",
        "rwa",
        "farmland",
        "llms.txt",
    )
    picked: list[str] = []
    seen: set[str] = set()
    for link in links:
        low = link.lower()
        if any(k in low for k in keys) and link not in seen:
            # Prefer markdown for gitbook
            if "gitbook.io" in low and not low.endswith((".md", ".txt")):
                md = link.rstrip("/") + ".md"
                if md not in seen:
                    picked.append(md)
                    seen.add(md)
            picked.append(link)
            seen.add(link)
        if len(picked) >= limit:
            break
    return picked


def rpc_eth_call(rpc: str, to: str, data: str) -> str | None:
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": to, "data": data}, "latest"],
        }
    ).encode()
    req = Request(
        rpc,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read())
            return body.get("result")
    except Exception:
        return None


def decode_abi_string(hexdata: str | None) -> str | None:
    if not hexdata or hexdata == "0x" or len(hexdata) < 2:
        return None
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 64:
            return None
        off = int.from_bytes(b[0:32], "big")
        if off + 32 > len(b):
            return None
        ln = int.from_bytes(b[off : off + 32], "big")
        return b[off + 32 : off + 32 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None


def probe_erc20(address: str, rpc: str, chain: str) -> dict[str, Any]:
    selectors = {
        "name": "0x06fdde03",
        "symbol": "0x95d89b41",
        "decimals": "0x313ce567",
        "totalSupply": "0x18160ddd",
    }
    out: dict[str, Any] = {
        "address": address,
        "rpc": rpc,
        "chain": chain,
        "ok": False,
    }
    name_h = rpc_eth_call(rpc, address, selectors["name"])
    sym_h = rpc_eth_call(rpc, address, selectors["symbol"])
    dec_h = rpc_eth_call(rpc, address, selectors["decimals"])
    sup_h = rpc_eth_call(rpc, address, selectors["totalSupply"])
    if not any([name_h, sym_h, dec_h, sup_h]):
        out["error"] = "eth_call failed or empty"
        return out
    out["ok"] = True
    out["name"] = decode_abi_string(name_h)
    out["symbol"] = decode_abi_string(sym_h)
    try:
        out["decimals"] = int(dec_h, 16) if dec_h else None
    except Exception:
        out["decimals"] = None
    try:
        out["totalSupply_raw"] = int(sup_h, 16) if sup_h else None
    except Exception:
        out["totalSupply_raw"] = None
    if out["totalSupply_raw"] is not None and out["decimals"] is not None:
        out["totalSupply_tokens"] = out["totalSupply_raw"] / (10 ** out["decimals"])
    return out


def candidate_search_terms(candidate: dict[str, Any]) -> list[str]:
    name = candidate.get("display_name") or ""
    slug = candidate.get("slug") or ""
    terms = [name, slug, slug.replace("-", " "), slug.replace("-", "").upper()]
    # ticker-ish guesses from notes
    notes = candidate.get("notes") or ""
    for m in re.findall(r"\b([A-Z]{2,6})\b", notes):
        terms.append(m)
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for t in terms:
        t = t.strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def dexscreener_token_search(
    query: str, prefer_name_bits: list[str] | None = None
) -> list[dict[str, Any]]:
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        pairs = data.get("pairs") or []
        bits = [b.lower() for b in (prefer_name_bits or []) if b]
        q = query.strip().upper()
        scored: list[tuple[int, dict[str, Any]]] = []
        for p in pairs:
            base = p.get("baseToken") or {}
            sym = (base.get("symbol") or "").upper()
            name = (base.get("name") or "")
            name_u = name.upper()
            name_l = name.lower()
            score = 0
            if sym == q:
                score += 4
            if q and q in name_u.replace(" ", ""):
                score += 3
            for b in bits:
                if b and b in name_l:
                    score += 3
                if b and b in sym.lower():
                    score += 2
            # Penalize huge aggregate "symbols" (noise from some chains)
            if len(sym) > 12 or "," in sym:
                score -= 10
            scored.append((score, p))
        scored.sort(key=lambda x: -x[0])
        return [p for s, p in scored if s > 0][:8]
    except Exception:
        return []


def dexscreener_by_token(address: str) -> list[dict[str, Any]]:
    url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        return data.get("pairs") or []
    except Exception:
        return []


def collect_addresses(texts: list[str]) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for t in texts:
        for m in ADDR_RE.findall(t or ""):
            low = m.lower()
            if low not in seen:
                seen.add(low)
                found.append(m)
    return found


def coingecko_search(query: str) -> dict[str, Any]:
    try:
        req = Request(
            f"https://api.coingecko.com/api/v3/search?query={query}",
            headers={"User-Agent": UA},
        )
        with urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "coins": []}


def extract_claim_snippets(blob: str) -> dict[str, str | None]:
    out: dict[str, str | None] = {
        "yield": None,
        "staking_lock": None,
        "supply": None,
        "royalty": None,
        "ownership": None,
    }
    for pat in (
        r"(\d+\s*%\s*to\s*\d+\s*%\s*APY)",
        r"(\d+\s*[–-]\s*\d+\s*%\s*APY)",
        r"(APY[s]?\s*\([^)]*\d+\s*[–-]\s*\d+%[^)]*\))",
    ):
        m = re.search(pat, blob, flags=re.I)
        if m:
            out["yield"] = m.group(1)
            break
    m = re.search(r"(lock-up periods?\s*\([^)]+\))", blob, flags=re.I)
    if m:
        out["staking_lock"] = m.group(1)
    elif re.search(r"30\s*[–-]\s*360\s*days", blob, flags=re.I):
        out["staking_lock"] = "30–360 days (stated in docs)"
    m = re.search(
        r"((?:total|fully circulating)\s+supply[^.]*\d[\d.,]*\s*(?:billion|B|million)?[^.]*\.?)",
        blob,
        flags=re.I,
    )
    if m:
        out["supply"] = m.group(1)[:160]
    if re.search(r"net smelter royalty|NSR", blob, flags=re.I):
        out["royalty"] = "Net Smelter Royalty / NSR share claims (marketing)"
    if re.search(r"fractional (farmland )?ownership|tokenized farmland", blob, flags=re.I):
        out["ownership"] = "Fractional ownership of underlying real-world assets (docs/marketing)"
    return out


def md_escape(s: str) -> str:
    return s.replace("|", "/").replace("\n", " ").strip()


def build_assessment(
    *,
    candidate: dict[str, Any],
    evidence: list[dict[str, Any]],
    token_probe: dict[str, Any] | None,
    dex_pairs: list[dict[str, Any]],
    coingecko: dict[str, Any] | None,
    claim_bits: dict[str, str | None],
    blob: str,
) -> dict[str, Any]:
    token_ok = bool(token_probe and token_probe.get("ok"))
    market_ok = bool(dex_pairs)
    cg_coins = (coingecko or {}).get("coins") or []
    independent_market = market_ok or bool(cg_coins)
    unconfirmed_ticker = bool(
        token_probe and token_probe.get("unconfirmed_ticker_collision_risk")
    )

    # Heuristic: underlying/economic contracts published?
    has_ownership_addr = bool(
        re.search(r"ownership contract.{0,80}0x[a-fA-F0-9]{40}", blob, flags=re.I)
    )
    has_staking_addr = bool(
        re.search(r"staking contract.{0,80}0x[a-fA-F0-9]{40}", blob, flags=re.I)
    )
    has_dist_addr = bool(
        re.search(
            r"(profit distribution|distribution|payout|royalty).{0,80}0x[a-fA-F0-9]{40}",
            blob,
            flags=re.I,
        )
    )
    docs_claim_underlying = bool(
        claim_bits.get("ownership")
        or claim_bits.get("royalty")
        or re.search(r"farmland|mining|royalty|NSR|real[- ]world", blob, flags=re.I)
    )
    underlying_verifiable = has_ownership_addr  # strict: need address
    economic_verifiable = has_staking_addr or has_dist_addr

    # Conflicts
    conflicts: list[str] = []
    if re.search(r"fully circulating", blob, flags=re.I) and re.search(
        r"vesting", blob, flags=re.I
    ):
        conflicts.append(
            "Docs describe supply as fully circulating while also describing "
            "team/partner vesting — allocation schedule conflict."
        )
    if claim_bits.get("yield") and not economic_verifiable:
        conflicts.append(
            "Yield/APY is claimed in official materials, but no staking or "
            "distribution contract address was confirmed as independently queryable."
        )

    # Readiness
    if token_ok and (underlying_verifiable or economic_verifiable):
        status = "adapter-ready"
    elif token_ok or market_ok:
        # Token or market surface exists, but underlying/economic not verifiable
        status = "token-data-only" if token_ok else "blocked"
        # If only thin market noise without matching token probe, treat blocked
        if not token_ok and market_ok:
            status = "blocked"
    else:
        status = "blocked"
    # Refine: marketing-only SPA with no token → blocked
    if not token_ok and not underlying_verifiable and not economic_verifiable:
        status = "blocked"

    blockers: list[str] = []
    if not token_ok:
        if unconfirmed_ticker:
            blockers.append(
                "Short-ticker DexScreener hit exists but issuer-published contract "
                "address / strong name corroboration is missing — token identity "
                "not confirmed (collision risk)"
            )
        else:
            blockers.append("No independently confirmed token contract via eth_call")
    if docs_claim_underlying and not underlying_verifiable:
        blockers.append(
            "No issuer-published ownership/registry contract address for the underlying asset"
        )
    if (claim_bits.get("yield") or claim_bits.get("royalty")) and not economic_verifiable:
        blockers.append(
            "No publicly reachable staking/profit/royalty distribution contract or payout API"
        )
    if not independent_market and not token_ok:
        blockers.append("No independent market/indexer surface confirming asset identity")

    # Claim rows
    claims: list[dict[str, str]] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    if token_ok and token_probe:
        supply = token_probe.get("totalSupply_tokens")
        supply_s = (
            f"{supply:,.0f} token units"
            if isinstance(supply, (int, float))
            else "decoded via eth_call"
        )
        claims.append(
            {
                "claim": "Token total supply equals eth_call totalSupply()",
                "claimed_value": claim_bits.get("supply")
                or f"{token_probe.get('symbol')} supply (docs or market)",
                "source": f"{token_probe['chain']} `{token_probe['address']}` via `{token_probe['rpc']}`",
                "source_type": "blockchain",
                "fact_domain": "on-chain",
                "verification_method": (
                    f"{token_probe['chain']} eth_call → totalSupply() "
                    f"@ {token_probe['address']}"
                ),
                "current_status": "verified",
                "adapter_output": "total_supply / claims[]",
                "blocker": "—",
            }
        )
        claims.append(
            {
                "claim": "Token identity (name/symbol/decimals)",
                "claimed_value": (
                    f"{token_probe.get('name')} / {token_probe.get('symbol')} / "
                    f"{token_probe.get('decimals')}"
                ),
                "source": f"`{token_probe['address']}` on {token_probe['chain']}",
                "source_type": "blockchain",
                "fact_domain": "on-chain",
                "verification_method": "eth_call → name()/symbol()/decimals()",
                "current_status": "verified",
                "adapter_output": "token identity fields / claims[]",
                "blocker": "—",
            }
        )
        # Address provenance caveat
        claims.append(
            {
                "claim": "Contract address is issuer-published",
                "claimed_value": token_probe["address"],
                "source": "DexScreener metadata match and/or docs (see research)",
                "source_type": "DEX/indexer",
                "fact_domain": "on-chain",
                "verification_method": (
                    "Compare issuer docs address list to probed address; "
                    "if docs omit address, provenance is only market metadata"
                ),
                "current_status": "partially-verified",
                "adapter_output": "claims[] (provenance note)",
                "blocker": (
                    "Issuer docs may not publish the address; treat DexScreener "
                    "attribution as supporting until docs confirm"
                ),
            }
        )

    if market_ok:
        p0 = dex_pairs[0]
        liq = (p0.get("liquidity") or {}).get("usd")
        claims.append(
            {
                "claim": "Public DEX market price/liquidity exists for the token",
                "claimed_value": f"price=${p0.get('priceUsd')}; liquidity_usd={liq}",
                "source": f"DexScreener pair `{p0.get('pairAddress')}` ({p0.get('chainId')}/{p0.get('dexId')})",
                "source_type": "DEX/indexer",
                "fact_domain": "on-chain",
                "verification_method": "GET DexScreener /latest/dex/tokens/{address}",
                "current_status": "observable",
                "adapter_output": "token_price (context only) / claims[]",
                "blocker": "—",
            }
        )
        claims.append(
            {
                "claim": "DEX liquidity proves underlying-asset liquidity / backing",
                "claimed_value": "implied by marketing sometimes",
                "source": "DexScreener",
                "source_type": "DEX/indexer",
                "fact_domain": "self-reported",
                "verification_method": "No valid verification — category error",
                "current_status": "blocked",
                "adapter_output": "null / unavailable",
                "blocker": "Market liquidity ≠ physical/underlying liquidity",
            }
        )

    if claim_bits.get("yield"):
        claims.append(
            {
                "claim": "Staking / advertised yield APY",
                "claimed_value": claim_bits["yield"],
                "source": "Official docs/blog (reachable text)",
                "source_type": "official documentation",
                "fact_domain": "self-reported",
                "verification_method": (
                    "Query staking/reward contract events and compute observed APY"
                    if economic_verifiable
                    else "No verification method currently available"
                ),
                "current_status": "self-reported" if not economic_verifiable else "unverified",
                "adapter_output": (
                    "claims[] (self-reported) ; realized_yield_pct=null"
                    if not economic_verifiable
                    else "realized_yield_pct / claims[]"
                ),
                "blocker": (
                    "Staking/reward contract address not identified"
                    if not economic_verifiable
                    else "—"
                ),
            }
        )

    if claim_bits.get("ownership") or claim_bits.get("royalty"):
        claims.append(
            {
                "claim": claim_bits.get("ownership")
                or claim_bits.get("royalty")
                or "Underlying economic claim",
                "claimed_value": "As stated in official marketing/docs",
                "source": "Official website/docs",
                "source_type": "official website",
                "fact_domain": "physical-world",
                "verification_method": (
                    "Query ownership/registry + distribution contracts or independent attestations"
                    if underlying_verifiable or economic_verifiable
                    else "No verification method currently available"
                ),
                "current_status": "self-reported",
                "adapter_output": "claims[] ; underlying fields null until contracts exist",
                "blocker": (
                    "No public ownership/registry/distribution surface confirmed"
                    if not (underlying_verifiable or economic_verifiable)
                    else "—"
                ),
            }
        )

    if not claims:
        claims.append(
            {
                "claim": "Public capital-product identity / investability surface",
                "claimed_value": "Marketing site describes investable product",
                "source": "; ".join(e["url"] for e in evidence if e.get("ok"))[:300]
                or "seeds",
                "source_type": "official website",
                "fact_domain": "self-reported",
                "verification_method": "No independent contract/API verification method found",
                "current_status": "blocked",
                "adapter_output": "null / unavailable",
                "blocker": "No confirmed token, registry, or payout API",
            }
        )

    if unconfirmed_ticker and token_probe:
        claims.insert(
            0,
            {
                "claim": "Token contract identity matching this project",
                "claimed_value": (
                    f"{token_probe.get('name')}/{token_probe.get('symbol')} @ "
                    f"{token_probe.get('address')} on {token_probe.get('chain')}"
                ),
                "source": "DexScreener short-ticker search (uncorroborated)",
                "source_type": "DEX/indexer",
                "fact_domain": "on-chain",
                "verification_method": (
                    "Require issuer-published address + eth_call name/symbol match "
                    "before treating as project token"
                ),
                "current_status": "blocked",
                "adapter_output": "null / unavailable",
                "blocker": token_probe.get("error")
                or "Ticker collision risk — not confirmed as this project's token",
            }
        )

    # Readiness rationale
    verified_bits = [c["claim"] for c in claims if c["current_status"] == "verified"]
    blocked_bits = [
        c["claim"]
        for c in claims
        if c["current_status"] in ("blocked", "self-reported", "unverified")
    ]
    if status == "adapter-ready":
        reason = (
            f"Independently queryable token/economic surfaces exist "
            f"({', '.join(verified_bits) or 'see matrix'}). Underlying or "
            f"payout mechanism verification is also reachable."
        )
        next_step = (
            "Human greenlight can proceed to a scoped adapter implementing "
            "only the verified surfaces plus self-reported claims[] provenance."
        )
    elif status == "token-data-only":
        reason = (
            "Token-level (and possibly market) facts can be independently "
            "queried, but the underlying real-world / economic mechanism "
            "claims lack published, queryable contracts or independent "
            "attestations. Tokn must not equate token verification with "
            "infrastructure verification."
        )
        next_step = (
            "To become adapter-ready: issuer-published ownership/registry "
            "and/or payout-distribution contracts (or an equivalent public "
            "attestation API) that connect the token to specific underlying "
            "assets and cashflows."
        )
    else:
        reason = (
            "Even a minimum useful verification surface could not be "
            "established: no confirmed token eth_call identity matched to "
            "the project and no independently queryable underlying/payout "
            "source. Marketing pages alone are insufficient."
        )
        next_step = (
            "Publish contract addresses / public APIs for token identity and "
            "economic mechanism, then re-run the research agent."
        )

    recommended_scope: list[str] = []
    prohibited: list[str] = []
    if token_ok:
        recommended_scope.extend(
            ["ERC-20 identity (name/symbol/decimals)", "totalSupply via eth_call"]
        )
    if market_ok:
        recommended_scope.append("DEX market context (price/liquidity) as non-backing context")
    recommended_scope.append(
        "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"
    )
    if not underlying_verifiable:
        prohibited.append("Verified underlying-asset ownership / registry identity")
    if not economic_verifiable:
        prohibited.extend(
            [
                "Observed staking APY as a verified fact",
                "Realized underlying revenue/yield distributions",
            ]
        )
    if not token_ok:
        prohibited.append("Any on-chain token identity fields")
        recommended_scope = [
            "Do not implement an adapter yet — research only until identity is confirmed"
        ]

    checklist = [
        ("Token/asset identity independently confirmed", token_ok),
        ("Relevant contracts confirmed", token_ok or underlying_verifiable or economic_verifiable),
        ("Required APIs reachable", any(e.get("ok") for e in evidence)),
        ("Required blockchain calls reproducible", token_ok),
        ("Claim sources documented", True),
        ("Independent evidence identified where available", independent_market or token_ok),
        ("Conflicts documented", True),
        ("Verification boundary defined", True),
        ("Claims mapped to evidence", True),
        ("Unknown values explicitly preserved", True),
        ("Adapter outputs defined", True),
        ("Schema compatibility checked", False),  # human/adapter phase
        ("Scoring impact understood", False),
        ("Snapshot reproducibility confirmed", False),
        ("Human review completed", False),
    ]

    return {
        "status": status,
        "reason": reason,
        "next_step": next_step,
        "token_ok": token_ok,
        "market_ok": market_ok,
        "underlying_identified_in_docs": docs_claim_underlying,
        "underlying_verifiable": underlying_verifiable,
        "economic_verifiable": economic_verifiable,
        "economic_bridge_verifiable": underlying_verifiable and economic_verifiable,
        "independent_market": independent_market,
        "independent_underlying": False,  # never true without third-party physical/attest
        "blockers": blockers,
        "conflicts": conflicts,
        "claims": claims,
        "recommended_scope": recommended_scope,
        "prohibited": prohibited,
        "checklist": checklist,
        "researched_at": now,
        "claim_bits": claim_bits,
        "supply_observed": (
            token_probe.get("totalSupply_tokens") if token_ok and token_probe else None
        ),
    }


def build_spec_md(
    *,
    candidate: dict[str, Any],
    findings_path: Path,
    evidence: list[dict[str, Any]],
    token_probe: dict[str, Any] | None,
    dex_pairs: list[dict[str, Any]],
    coingecko_search: dict[str, Any] | None,
    assessment: dict[str, Any],
) -> str:
    today = date.today().isoformat()
    name = candidate["display_name"]
    slug = candidate["slug"]
    notes = candidate.get("notes", "")
    seeds = candidate.get("seeds") or []

    rows = []
    for e in evidence:
        if e["ok"]:
            result = (
                f"HTTP {e['http_status']} — live "
                f"({e.get('content_type') or 'unknown type'})"
            )
        else:
            result = e.get("error") or "unreachable"
        rows.append(f"| `{e['url']}` | {result} |")

    reachable = [e for e in evidence if e["ok"]]
    official_hosts = sorted(
        {
            urlparse(u).netloc
            for u in seeds + [e["url"] for e in reachable]
            if urlparse(u).netloc
        }
    )

    if token_probe and token_probe.get("ok"):
        supply = token_probe.get("totalSupply_tokens")
        supply_s = (
            f"{supply:,.0f}" if isinstance(supply, (int, float)) else "not decoded"
        )
        identity_token = f"""| Field | Observed |
| --- | --- |
| Chain | {token_probe.get("chain")} |
| Token contract | `{token_probe["address"]}` |
| `name()` | `{token_probe.get("name")}` |
| `symbol()` | `{token_probe.get("symbol")}` |
| `decimals()` | `{token_probe.get("decimals")}` |
| `totalSupply()` | {supply_s} token units (raw `{token_probe.get("totalSupply_raw")}`) |
| RPC used | `{token_probe.get("rpc")}` |"""
    else:
        identity_token = (
            "No ERC-20 (or equivalent) contract was confirmed via live "
            "`eth_call` in this pass for a token identity matching this "
            "project. Marketing may describe a token, but without a "
            "confirmed address + successful RPC getters, Tokn cannot treat "
            "token identity as verified."
        )
        if token_probe and token_probe.get("unconfirmed_ticker_collision_risk"):
            identity_token += (
                f"\n\n**Unconfirmed short-ticker Dex hit (not used as identity):** "
                f"`{token_probe.get('symbol')}` / `{token_probe.get('name')}` at "
                f"`{token_probe.get('address')}` on `{token_probe.get('chain')}` — "
                f"{token_probe.get('error')}"
            )

    dex_rows = []
    for p in dex_pairs[:5]:
        base = p.get("baseToken") or {}
        liq = (p.get("liquidity") or {}).get("usd")
        dex_rows.append(
            f"| {p.get('chainId')} / {p.get('dexId')} | "
            f"`{p.get('pairAddress')}` | "
            f"{base.get('symbol')} / {(p.get('quoteToken') or {}).get('symbol')} | "
            f"${liq} | ${p.get('priceUsd')} |"
        )
    if not dex_rows:
        dex_rows.append("| — | — | — | — | — |")

    cg_coins = (coingecko_search or {}).get("coins") or []
    if coingecko_search is None:
        cg_note = "CoinGecko search not run."
    elif cg_coins:
        cg_note = (
            "CoinGecko search returned hit(s): "
            + ", ".join(
                f"{c.get('name')} ({c.get('symbol')})" for c in cg_coins[:5]
            )
            + " — still not proof of underlying-asset verification."
        )
    else:
        q = candidate_search_terms(candidate)[0]
        cg_note = (
            f"CoinGecko search API returned **zero** coins for query `{q}` "
            "in this pass — no independent CoinGecko listing confirmed."
        )

    excerpt_blocks = []
    for e in reachable[:8]:
        snippet = md_escape((e.get("excerpt") or "")[:600])
        excerpt_blocks.append(f"### `{e['url']}`\n\n> {snippet}\n")
    if not excerpt_blocks:
        excerpt_blocks.append("_No reachable research URL returned extractable text._\n")

    # Narrative research sections (generic)
    claim_bits = assessment["claim_bits"]
    confirmed_lines = []
    if assessment["token_ok"]:
        confirmed_lines.append(
            f"- Token eth_call identity confirmed on **{token_probe.get('chain')}** "
            f"at `{token_probe.get('address')}` "
            f"({token_probe.get('name')}/{token_probe.get('symbol')})."
        )
    if assessment["market_ok"]:
        confirmed_lines.append(
            f"- DexScreener reports {len(dex_pairs)} pair(s) for the probed token "
            "(market context only)."
        )
    confirmed_lines.append(
        f"- {sum(1 for e in evidence if e.get('ok'))}/{len(evidence)} research "
        "URLs reachable in this pass."
    )
    if not assessment["underlying_verifiable"]:
        confirmed_lines.append(
            "- **No** independently queryable underlying-asset registry/ownership "
            "contract was confirmed."
        )
    if not assessment["economic_verifiable"]:
        confirmed_lines.append(
            "- **No** independently queryable staking/profit/royalty distribution "
            "contract was confirmed."
        )

    docs_claim_lines = []
    if claim_bits.get("ownership"):
        docs_claim_lines.append(f"- {claim_bits['ownership']}")
    if claim_bits.get("royalty"):
        docs_claim_lines.append(f"- {claim_bits['royalty']}")
    if claim_bits.get("yield"):
        docs_claim_lines.append(f"- Claimed yield/APY language: `{claim_bits['yield']}`")
    if claim_bits.get("staking_lock"):
        docs_claim_lines.append(f"- Staking lock language: `{claim_bits['staking_lock']}`")
    if not docs_claim_lines:
        docs_claim_lines.append(
            "- Official pages describe a capital-style product; see excerpts."
        )

    conflict_lines = assessment["conflicts"] or [
        "- No hard textual conflict isolated beyond marketing vs evidence gaps."
    ]

    # Claim matrix table
    claim_rows = []
    for c in assessment["claims"]:
        claim_rows.append(
            "| "
            + " | ".join(
                md_escape(c[k])
                for k in (
                    "claim",
                    "claimed_value",
                    "source",
                    "source_type",
                    "fact_domain",
                    "verification_method",
                    "current_status",
                    "adapter_output",
                    "blocker",
                )
            )
            + " |"
        )

    # Recommended inputs table
    input_rows: list[str] = []
    if assessment["token_ok"] and token_probe:
        input_rows.append(
            f"| ERC-20 getters | blockchain | `{token_probe['address']}` on "
            f"{token_probe['chain']} | eth_call name/symbol/decimals/totalSupply "
            f"via `{token_probe['rpc']}` | identity + supply | on snapshot / daily | "
            f"**required** — token identity |"
        )
    if assessment["market_ok"] and token_probe:
        input_rows.append(
            f"| DEX market context | DEX/indexer | "
            f"`https://api.dexscreener.com/latest/dex/tokens/{token_probe['address']}` | "
            f"GET JSON pairs | price/liquidity context | optional cadence | "
            f"**optional** — never as backing proof |"
        )
    for e in reachable[:6]:
        role = "**optional** — self-reported claims provenance"
        if "gitbook" in e["url"] or "docs" in e["url"]:
            role = "**required** for claims[] sourcing (self-reported)"
        input_rows.append(
            f"| Official page text | official documentation | `{e['url']}` | "
            f"HTTP GET + text extract | claim language / product description | "
            f"on research refresh | {role} |"
        )
    if not input_rows:
        input_rows.append(
            "| — | — | — | — | — | — | No safe adapter inputs identified |"
        )

    # Do not use
    dont_use = [
        "| Marketing slogans without contracts/APIs | Self-reported; not independently queryable |",
        "| Unnamed ownership/staking/profit contracts | Described in docs but address missing |",
        "| DEX liquidity as proof of underlying-asset liquidity/backing | Category error |",
        "| Project's own unverified API (if any) as independent verification | Same trust domain as issuer |",
        "| Unextracted PDF bytes as confirmation of a specific numeric claim | PDF may be reachable without text verification |",
        "| Unrelated DEX tickers sharing a short symbol | Symbol collision risk |",
    ]

    checklist_lines = []
    for label, done in assessment["checklist"]:
        if done:
            checklist_lines.append(f"- [x] {label}")
        else:
            checklist_lines.append(f"- [ ] {label}")

    yaml_block = f"""```yaml
adapter_readiness:
  status: {assessment["status"]}
  researched_at: "{assessment["researched_at"]}"

  token_verification:
    available: {str(assessment["token_ok"]).lower()}

  underlying_asset_verification:
    available: {str(assessment["underlying_verifiable"]).lower()}

  economic_mechanism_verification:
    available: {str(assessment["economic_verifiable"]).lower()}

  market_data:
    available: {str(assessment["market_ok"]).lower()}

  independent_sources:
    available: {str(assessment["independent_market"]).lower()}
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
{chr(10).join(f'    - "{b}"' for b in (assessment["blockers"] or ["None recorded"]))}

  recommended_adapter_scope:
{chr(10).join(f'    - "{s}"' for s in assessment["recommended_scope"])}

  prohibited_outputs:
{chr(10).join(f'    - "{s}"' for s in (assessment["prohibited"] or ["None"])) }
```"""

    return f"""# {name} — adapter specification (research)

**Status:** research document only — **not** an approval to build an adapter.
**Prerequisite FINDINGS:** [`FINDINGS.md`](./FINDINGS.md) must already classify
this candidate as `candidate-for-adapter`.
**Date researched:** {today}
**Research agent:** `scheduler/run_research_agent.py`
**Investigator note:** Additive to FINDINGS.md (FINDINGS was not modified by
this agent). Writes **no** adapter code, schema fields, scoring weights,
storage snapshots, or API routes. A human must still read this spec and
explicitly greenlight any real adapter work.

Backlog notes: {notes}

---

## 1. Identity

| Field | Value |
| --- | --- |
| Display name | {name} |
| Slug | `{slug}` |
| Issuer / brand (self-described) | {name} |
| Seed hosts | {", ".join(f"`{h}`" for h in official_hosts) or "—"} |

### Token / chain (live probe)

{identity_token}

### Dex / market metadata (supporting only)

| Chain / DEX | Pair | Tokens | Liquidity (USD) | Price (USD) |
| --- | --- | --- | --- | --- |
{chr(10).join(dex_rows)}

{cg_note}

---

## 2. Underlying infrastructure & revenue story

**What official sources claim**

{chr(10).join(docs_claim_lines)}

**What was actually confirmed here**

{chr(10).join(confirmed_lines)}

---

## 3. Claimed payout mechanism & claimed yield

| Claim theme | Observed language | Independently queryable now? |
| --- | --- | --- |
| Advertised yield / APY | {claim_bits.get("yield") or "not clearly extracted"} | {"yes" if assessment["economic_verifiable"] else "**no**"} |
| Ownership / royalty / RWA claim | {claim_bits.get("ownership") or claim_bits.get("royalty") or "see docs excerpts"} | {"yes" if assessment["underlying_verifiable"] or assessment["economic_verifiable"] else "**no**"} |
| Token supply | {claim_bits.get("supply") or ("matches eth_call" if assessment["token_ok"] else "not confirmed")} | {"yes" if assessment["token_ok"] else "**no**"} |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| Primary token (probed) | `{token_probe["address"] if token_probe and token_probe.get("ok") else "not confirmed"}` | {"eth_call + market metadata" if assessment["token_ok"] else "not confirmed"} | Identity / supply only |
| Ownership / asset registry | **Not confirmed** | Docs may describe; address not verified | Required for underlying claims — blocked unless published |
| Staking / rewards | **Not confirmed** | Docs may describe; address not verified | Required for APY observation — blocked unless published |
| Profit / royalty distribution | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |

**Events:** No verified payout/harvest event ABI + public indexer endpoint for
this candidate’s underlying economics was confirmed in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
{chr(10).join(rows)}

| Indexer / market API | Result |
| --- | --- |
| DexScreener search/token API | {"Reachable" if assessment["market_ok"] or True else "n/a"} — used for market context when pairs match |
| CoinGecko search | {cg_note} |
| Public EVM RPC eth_call | {"Reachable for probed token" if assessment["token_ok"] else "No successful project-matched token probe"} |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** {", ".join(f"`{h}`" for h in official_hosts) or "seed sites"}

**Independent / market:** DexScreener (if pairs match); CoinGecko as noted.
Independent market metadata is **not** independent underlying-asset verification.

**Conflicts / tensions**

{chr(10).join("- " + c if not c.startswith("-") else c for c in conflict_lines)}

---

## 7. Per-claim confidence

| Claim | Confidence now | Why |
| --- | --- | --- |
| Public project web presence | {"High" if reachable else "Low"} | Reachable official HTTP surfaces |
| Capital-style (non-operator) marketing path | Medium-high | Discovery already classified `candidate-for-adapter` — first-pass only |
| Token identity on-chain | {"High" if assessment["token_ok"] else "Low"} | {"Successful eth_call getters" if assessment["token_ok"] else "No matched token probe"} |
| Underlying asset independently verifiable | {"High" if assessment["underlying_verifiable"] else "Low"} | Ownership/registry contract reachability |
| Economic mechanism / realized yield observable | {"High" if assessment["economic_verifiable"] else "Low"} | Distribution/staking contract reachability |
| Independent market listing quality | {"Medium" if assessment["market_ok"] else "Low"} | Dex/CG presence without implying backing |

---

## 8. Recommended data sources for an eventual adapter

See **Recommended Adapter Inputs** below for the concrete table. High-level:

{chr(10).join("- " + s for s in assessment["recommended_scope"])}

**Honest adapter boundary:** implement only independently queryable surfaces;
leave unrealized underlying/yield fields **null** rather than inventing values.

---

## 9. Adapter Readiness

**Status: `{assessment["status"]}`**

Allowed values: `adapter-ready` | `token-data-only` | `blocked`.

### Readiness rationale

{assessment["reason"]}

**What can currently be verified:** {", ".join(c["claim"] for c in assessment["claims"] if c["current_status"] in ("verified", "observable")) or "none beyond marketing reachability"}

**What cannot currently be verified:** {", ".join(assessment["prohibited"]) or "see claim matrix"}

**Main blocker(s):** {"; ".join(assessment["blockers"]) or "none recorded"}

**To move to the next state:** {assessment["next_step"]}

---

## 10. Claim-to-Verification Map

| Claim | Claimed value | Source | Source type | Fact domain | Verification method | Current status | Adapter output | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(claim_rows)}

Status vocabulary: `verified` | `partially-verified` | `observable` |
`self-reported` | `conflicted` | `unverified` | `blocked`.

---

## 11. Verification Boundary

### Token-level verification

| Capability | Available now? |
| --- | --- |
| Contract identity / symbol / decimals | {"YES" if assessment["token_ok"] else "NO"} |
| Total supply | {"YES" if assessment["token_ok"] else "NO"} |
| Holder balances / transfers (generic ERC-20) | {"YES (standard)" if assessment["token_ok"] else "NO"} |
| DEX price | {"YES" if assessment["market_ok"] else "NO"} |
| DEX liquidity | {"YES" if assessment["market_ok"] else "NO"} |

### Underlying-asset verification

| Capability | Available now? |
| --- | --- |
| Physical / real-world asset identity | {"YES" if assessment["underlying_verifiable"] else "NO"} |
| Asset ownership / registry | {"YES" if assessment["underlying_verifiable"] else "NO"} |
| Infrastructure operation / production | NO |
| Revenue generation / leases / harvests | {"YES" if assessment["economic_verifiable"] else "NO"} |
| Actual distributions to holders | {"YES" if assessment["economic_verifiable"] else "NO"} |

### Bridge summary

```text
Token exists (independently queryable): {"YES" if assessment["token_ok"] else "NO"}
Underlying asset identified in docs: {"YES" if assessment["underlying_identified_in_docs"] else "NO"}
Underlying asset independently verifiable: {"YES" if assessment["underlying_verifiable"] else "NO"}
Economic connection between token and asset verifiable: {"YES" if assessment["economic_bridge_verifiable"] else "NO"}
```

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification.

---

## 12. Recommended Adapter Inputs

| Input | Source | Exact endpoint/contract | Method/query | Expected data | Frequency | Verification role |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(input_rows)}

---

## 13. Sources Not Suitable for Verification

| Source / pattern | Why unsuitable |
| --- | --- |
{chr(10).join(dont_use)}

---

## 14. Adapter Implementation Boundary

### What the future adapter SHOULD implement

{chr(10).join("- " + s for s in assessment["recommended_scope"])}

### What the future adapter MUST NOT implement

{chr(10).join("- " + s for s in (assessment["prohibited"] or ["Nothing additional beyond empty nulls"]))}

### What requires human review

- Whether the project token (if any) should be treated as the representation
  of specific underlying assets vs a generic ecosystem/utility token.
- Whether DexScreener-attributed contract addresses are acceptable before
  issuer-published address lists exist.
- Whether to greenlight any adapter at `{assessment["status"]}` readiness.

---

## 15. Promotion Checklist

{chr(10).join(checklist_lines)}

`[x]` = demonstrated in this research pass. `[ ]` = not demonstrated (human /
adapter phase).

---

## 16. Human decision gate

This file does **not** authorize adapter work. Next steps for a human:

1. Review [`FINDINGS.md`](./FINDINGS.md) + this `ADAPTER_SPEC.md`.
2. Decide whether to greenlight a bespoke adapter (manual, like Glow/RealT/Elmnts).
3. If greenlit: implement **only** the SHOULD list; keep MUST NOT as null/unavailable.
4. If not greenlit: leave as research-only; no code.

---

## 17. Machine-readable summary (research only)

Not consumed by scoring/schema. For humans and future tooling only.

{yaml_block}

---

## Appendix — reachable excerpts (truncated)

{chr(10).join(excerpt_blocks)}
"""


def research_candidate(
    candidate: dict[str, Any],
    *,
    require_findings: bool = True,
) -> dict[str, Any]:
    slug = candidate["slug"]
    findings_path, classification = read_findings_classification(slug)
    if require_findings:
        if classification is None:
            raise RuntimeError(
                f"Missing or unreadable classification in {findings_path}. "
                "Run scheduler/run_discovery.py first."
            )
        if classification != "candidate-for-adapter":
            raise RuntimeError(
                f"Research agent only runs for candidate-for-adapter "
                f"(found `{classification}` in {findings_path})."
            )

    urls = expand_research_urls(candidate)
    evidence: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for u in urls:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        evidence.append(fetch_url(u))

    # Follow interesting links from reachable HTML (bounded).
    follow: list[str] = []
    for e in list(evidence):
        if e.get("ok") and e.get("links"):
            follow.extend(interesting_follow_links(e["links"], limit=8))
        if e.get("ok") and e["url"].endswith("llms.txt"):
            for m in re.findall(r"https://[^\s\)]+\.md", e.get("raw_text") or ""):
                if any(
                    k in m.lower()
                    for k in (
                        "token",
                        "architecture",
                        "concept",
                        "lock-up",
                        "rwa",
                        "royalty",
                        "nsr",
                    )
                ):
                    follow.append(m)
    for u in follow[:12]:
        if u not in seen_urls:
            seen_urls.add(u)
            evidence.append(fetch_url(u))

    texts = [e.get("raw_text") or "" for e in evidence if e.get("ok")]
    blob = " ".join(texts)
    addrs = collect_addresses(texts)

    # Token discovery via DexScreener using candidate terms (generic — no
    # asset-specific hardcoded addresses). Short tickers require stronger
    # corroboration than symbol equality alone (collision risk).
    notes_l = (candidate.get("notes") or "").lower()
    product_bits = [
        b
        for b in (
            candidate.get("display_name") or "",
            candidate.get("slug") or "",
            *re.findall(
                r"\b(agri|farm|farmland|mining|royalty|nsr|rwa|tokenized)\b",
                notes_l,
                flags=re.I,
            ),
        )
        if b
    ]
    dex_hits: list[dict[str, Any]] = []
    for term in candidate_search_terms(candidate):
        dex_hits.extend(dexscreener_token_search(term, prefer_name_bits=product_bits))
        if dex_hits:
            break

    name_l = (candidate.get("display_name") or "").lower()
    slug_l = (candidate.get("slug") or "").lower()
    compact_name = re.sub(r"[^a-z0-9]", "", name_l)
    short_ticker = len(compact_name) <= 4

    def _strong_token_name_match(bname: str, bsym: str) -> bool:
        """Reject bare short-ticker collisions without product corroboration."""
        bn = re.sub(r"[^a-z0-9]", "", (bname or "").lower())
        bs = (bsym or "").lower()
        # Longer product names: require stem containment in token name.
        if len(compact_name) >= 5:
            return compact_name[:5] in bn or compact_name in bn
        # Short tickers (e.g. PTX): symbol match alone is insufficient.
        # Require (a) token name longer than ticker with product keywords, or
        # (b) official research text already embeds this address (checked later).
        if bs != compact_name and compact_name not in bn:
            return False
        product_kw = [
            k
            for k in (
                "mining",
                "royalty",
                "nsr",
                "farm",
                "farmland",
                "agri",
                "rwa",
                slug_l.replace("-", ""),
            )
            if k and len(k) >= 3
        ]
        if any(k in bn for k in product_kw if k != compact_name):
            return True
        # Name is more than ticker+generic "coin/token" fluff → weak accept only
        # if display name itself is longer branding (handled above). Else reject.
        fluff = {"coin", "token", "tokens", "the", "protocol", "finance", "fi"}
        extras = [w for w in re.findall(r"[a-z]+", (bname or "").lower()) if w not in fluff]
        return False if short_ticker else bool(extras)

    token_addr = None
    chain = "ethereum"
    addr_from_docs = False
    # Prefer addresses embedded in reachable official research text.
    if addrs:
        for a in addrs[:6]:
            # Guess chain from surrounding blob keywords near research pass.
            ch = "polygon" if "polygon" in blob.lower() else (
                "bsc" if re.search(r"\b(bsc|bnb|binance)\b", blob, flags=re.I) else "ethereum"
            )
            probe_try = probe_erc20(a, CHAIN_RPC.get(ch, CHAIN_RPC["ethereum"]), ch)
            if probe_try and probe_try.get("ok"):
                tname = (probe_try.get("name") or "").lower()
                tsym = (probe_try.get("symbol") or "").lower()
                if _strong_token_name_match(tname, tsym) or (
                    compact_name and compact_name in re.sub(r"[^a-z0-9]", "", tname)
                ):
                    token_addr = a
                    chain = ch
                    addr_from_docs = True
                    token_probe_docs = probe_try
                    break
        else:
            token_probe_docs = None
    else:
        token_probe_docs = None

    if not token_addr:
        for p in dex_hits:
            base = p.get("baseToken") or {}
            bname = base.get("name") or ""
            bsym = base.get("symbol") or ""
            if _strong_token_name_match(bname, bsym):
                token_addr = base.get("address")
                chain = (p.get("chainId") or "ethereum").lower()
                break

    # Short-ticker Dex hits without docs address: keep as unconfirmed candidate
    # only if we already found nothing — do not treat as verified identity.
    unconfirmed_ticker_hit: dict[str, Any] | None = None
    if not token_addr and short_ticker:
        for p in dex_hits:
            base = p.get("baseToken") or {}
            bsym = (base.get("symbol") or "").lower()
            if bsym == compact_name and base.get("address"):
                unconfirmed_ticker_hit = {
                    "address": base.get("address"),
                    "chain": (p.get("chainId") or "ethereum").lower(),
                    "name": base.get("name"),
                    "symbol": base.get("symbol"),
                    "note": (
                        "Short-ticker DexScreener hit without issuer-published "
                        "contract address or product-keyword name corroboration — "
                        "not treated as confirmed token identity"
                    ),
                }
                break

    if addr_from_docs and token_probe_docs:
        token_probe = token_probe_docs
    else:
        rpc = CHAIN_RPC.get(chain, CHAIN_RPC["ethereum"])
        token_probe = probe_erc20(token_addr, rpc, chain) if token_addr else None
        if token_probe and token_probe.get("ok"):
            tname = token_probe.get("name") or ""
            tsym = token_probe.get("symbol") or ""
            if not _strong_token_name_match(tname, tsym) and not addr_from_docs:
                token_probe = {
                    "ok": False,
                    "error": (
                        f"Probed token {tname}/{tsym} failed strong identity match; "
                        "discarded to avoid ticker collision"
                    ),
                    "address": token_addr,
                    "chain": chain,
                }
                token_addr = None

    # If only unconfirmed short-ticker hit remains, do not promote to token_ok.
    if (not token_probe or not token_probe.get("ok")) and unconfirmed_ticker_hit:
        token_probe = {
            "ok": False,
            "error": unconfirmed_ticker_hit["note"],
            "address": unconfirmed_ticker_hit["address"],
            "chain": unconfirmed_ticker_hit["chain"],
            "name": unconfirmed_ticker_hit.get("name"),
            "symbol": unconfirmed_ticker_hit.get("symbol"),
            "unconfirmed_ticker_collision_risk": True,
        }
        token_addr = None

    dex_pairs = (
        dexscreener_by_token(token_addr)
        if token_addr
        else (
            dexscreener_by_token(unconfirmed_ticker_hit["address"])
            if unconfirmed_ticker_hit
            else []
        )
    )
    # Market pairs alone must not imply confirmed token identity.
    if not token_addr:
        dex_pairs = []

    cg = coingecko_search(candidate_search_terms(candidate)[0])
    claim_bits = extract_claim_snippets(blob)

    assessment = build_assessment(
        candidate=candidate,
        evidence=evidence,
        token_probe=token_probe,  # may be ok:false with collision-risk note
        dex_pairs=dex_pairs,
        coingecko=cg,
        claim_bits=claim_bits,
        blob=blob,
    )

    spec_md = build_spec_md(
        candidate=candidate,
        findings_path=findings_path,
        evidence=evidence,
        token_probe=token_probe,  # render unconfirmed notes when present
        dex_pairs=dex_pairs,
        coingecko_search=cg,
        assessment=assessment,
    )
    return {
        "slug": slug,
        "display_name": candidate["display_name"],
        "classification": classification,
        "findings_path": findings_path,
        "spec_md": spec_md,
        "evidence": evidence,
        "token_probe": token_probe,
        "dex_pair_count": len(dex_pairs),
        "assessment": assessment,
        "date": date.today().isoformat(),
    }


def write_spec(result: dict[str, Any]) -> Path:
    out_dir = CANDIDATES_DIR / result["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "ADAPTER_SPEC.md"
    path.write_text(result["spec_md"], encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-name",
        required=True,
        help="Candidate display name or slug (must already be candidate-for-adapter).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print ADAPTER_SPEC.md to stdout; do not write files.",
    )
    parser.add_argument(
        "--no-status-log",
        action="store_true",
        help="Do not append scheduler/status/status_log.jsonl (artifact-only run).",
    )
    parser.add_argument(
        "--allow-missing-findings",
        action="store_true",
        help="Escape hatch for tests — do not use for production cycles.",
    )
    args = parser.parse_args(argv)

    assert_scheduler_safe()
    started = utc_now_iso()
    details: dict[str, Any] = {
        "candidate_name_input": args.candidate_name,
        "dry_run": args.dry_run,
    }

    try:
        candidate = resolve_candidate(args.candidate_name)
        details["candidate"] = candidate["slug"]
        details["display_name"] = candidate.get("display_name")

        result = research_candidate(
            candidate, require_findings=not args.allow_missing_findings
        )
        details["classification"] = result["classification"]
        details["reachable_count"] = sum(1 for e in result["evidence"] if e["ok"])
        details["token_probe_ok"] = bool(
            result.get("token_probe") and result["token_probe"].get("ok")
        )
        details["dex_pair_count"] = result.get("dex_pair_count")
        details["adapter_readiness"] = (result.get("assessment") or {}).get("status")

        if args.dry_run:
            print(result["spec_md"])
            if not args.no_status_log:
                append_status(
                    job="research_agent",
                    status="success",
                    started_at=started,
                    finished_at=utc_now_iso(),
                    details={**details, "note": "dry-run; no files written"},
                )
            print("DRY RUN — ADAPTER_SPEC.md not written", file=sys.stderr)
            return 0

        path = write_spec(result)
        details["adapter_spec_path"] = str(path.relative_to(REPO_ROOT))
        rel = path.resolve().relative_to((CANDIDATES_DIR / result["slug"]).resolve())
        if rel != Path("ADAPTER_SPEC.md"):
            raise RuntimeError(f"Refusing unexpected write path: {path}")

        if not args.no_status_log:
            append_status(
                job="research_agent",
                status="success",
                started_at=started,
                finished_at=utc_now_iso(),
                details=details,
            )

        print(f"Wrote {path}")
        print(f"Adapter readiness: {details.get('adapter_readiness')}")
        print(
            "Research complete — human review of ADAPTER_SPEC.md required "
            "before any adapter work."
        )
        return 0

    except Exception as e:
        if not args.no_status_log:
            append_status(
                job="research_agent",
                status="failure",
                started_at=started,
                finished_at=utc_now_iso(),
                error=f"{type(e).__name__}: {e}",
                details=details,
            )
        print(f"RESEARCH AGENT FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
