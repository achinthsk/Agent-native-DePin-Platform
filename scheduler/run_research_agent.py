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

# Ordered RPC fallbacks per chain. Prefer archive-capable / full nodes for
# eth_getTransactionByHash (publicnode often returns null for historical txs).
CHAIN_RPC: dict[str, list[str]] = {
    "polygon": [
        "https://polygon-bor-rpc.publicnode.com",
        "https://polygon-rpc.com",
    ],
    "ethereum": [
        "https://ethereum-rpc.publicnode.com",
        "https://cloudflare-eth.com",
    ],
    "arbitrum": [
        "https://arbitrum-one-rpc.publicnode.com",
        "https://arb1.arbitrum.io/rpc",
    ],
    "bsc": [
        "https://bsc-rpc.publicnode.com",
        "https://bsc-dataseed.binance.org",
    ],
    "base": [
        "https://mainnet.base.org",
        "https://base-rpc.publicnode.com",
    ],
}

# Hosts treated as independent (non-issuer) when classifying evidence quality.
INDEPENDENT_HOST_SUFFIXES = (
    "lse.co.uk",
    "londonstockexchange.com",
    "investegate.co.uk",
    "sec.gov",
    "companieshouse.gov.uk",
    "sedarplus.ca",
    "sedar.com",
    "edgar.sec.gov",
    "northseatransitionauthority.co.uk",
    "nstauthority.co.uk",
    "gov.uk",
)

ECONOMIC_REPO_NAME_KEYS = (
    "reward",
    "payout",
    "claim",
    "distribution",
    "dividend",
    "vault",
    "royalty",
    "yield",
)


def rpcs_for(chain: str) -> list[str]:
    return list(CHAIN_RPC.get(chain) or [])


def primary_rpc(chain: str) -> str | None:
    rpcs = rpcs_for(chain)
    return rpcs[0] if rpcs else None


def host_of(url: str) -> str:
    try:
        h = urlparse(url).netloc.lower()
    except Exception:
        return ""
    return h[4:] if h.startswith("www.") else h


def is_independent_host(host: str) -> bool:
    h = (host or "").lower()
    if h.startswith("www."):
        h = h[4:]
    return any(h == s or h.endswith("." + s) for s in INDEPENDENT_HOST_SUFFIXES)


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
            is_json = (
                "json" in (ct or "").lower()
                or url.endswith(".json")
                or "api.github.com" in url
                or raw.lstrip().startswith(("{", "["))
            )
            if url.rstrip("/").endswith(".md") or "text/markdown" in ct or url.endswith(
                ".txt"
            ):
                text = raw
            elif is_json:
                # Preserve JSON structure for payout metadata / GitHub trees.
                text = raw
            elif "html" in ct or raw.lstrip().startswith("<"):
                text, links = html_to_text_and_links(raw, url)
                text = re.sub(r"\s+", " ", text).strip()
            else:
                text = re.sub(r"\s+", " ", raw).strip()
            # Keep larger window for structured economic surfaces.
            raw_limit = 120_000 if is_json else 25_000
            return {
                "url": url,
                "ok": True,
                "http_status": code,
                "content_type": ct,
                "excerpt": re.sub(r"\s+", " ", text).strip()[:2000],
                "raw_text": text[:raw_limit],
                "links": links,
                "error": None,
                "kind": "json" if is_json else "text",
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


def github_orgs_from_urls(urls: list[str]) -> list[str]:
    """Extract GitHub org/user logins from github / raw.githubusercontent URLs."""
    orgs: list[str] = []
    seen: set[str] = set()
    for u in urls:
        try:
            p = urlparse(u)
            host = p.netloc.lower()
            parts = [x for x in p.path.split("/") if x]
        except Exception:
            continue
        org: str | None = None
        if host == "github.com" and parts:
            org = parts[0]
        elif host == "raw.githubusercontent.com" and parts:
            org = parts[0]
        if not org:
            continue
        low = org.lower()
        if low in {"settings", "orgs", "marketplace", "topics", "features"}:
            continue
        if low not in seen:
            seen.add(low)
            orgs.append(org)
    return orgs


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
    # GitHub org surfaces → discover payout/rewards/registry repos generically.
    for org in github_orgs_from_urls(seeds):
        extras.extend(
            [
                f"https://github.com/{org}",
                f"https://api.github.com/orgs/{org}/repos?per_page=50",
                f"https://api.github.com/users/{org}/repos?per_page=50",
            ]
        )
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
        "reward",
        "payout",
        "distribution",
        "revenue",
        "vault",
        "safe",
        "filing",
        "rns",
        "registry",
        "metadata",
        "claims",
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


def rpc_json(rpc: str, method: str, params: list[Any]) -> Any | None:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode()
    req = Request(
        rpc,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": UA,
        },
    )
    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read())
            if body.get("error"):
                return None
            return body.get("result")
    except Exception:
        return None


def rpc_eth_call(rpc: str, to: str, data: str) -> str | None:
    return rpc_json(rpc, "eth_call", [{"to": to, "data": data}, "latest"])


def rpc_eth_call_any(
    chain: str, to: str, data: str
) -> tuple[str | None, str | None]:
    for rpc in rpcs_for(chain):
        result = rpc_eth_call(rpc, to, data)
        if result and result != "0x":
            return result, rpc
    return None, None


def rpc_get_transaction(chain: str, tx_hash: str) -> dict[str, Any] | None:
    for rpc in rpcs_for(chain):
        result = rpc_json(rpc, "eth_getTransactionByHash", [tx_hash])
        if isinstance(result, dict) and result.get("hash"):
            result = dict(result)
            result["_rpc"] = rpc
            return result
    return None


def rpc_get_receipt(chain: str, tx_hash: str) -> dict[str, Any] | None:
    for rpc in rpcs_for(chain):
        result = rpc_json(rpc, "eth_getTransactionReceipt", [tx_hash])
        if isinstance(result, dict) and result.get("transactionHash"):
            result = dict(result)
            result["_rpc"] = rpc
            return result
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


def probe_erc20(
    address: str, rpc: str | None, chain: str
) -> dict[str, Any]:
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
    rpc_list = [rpc] if rpc else []
    for alt in rpcs_for(chain):
        if alt not in rpc_list:
            rpc_list.append(alt)
    name_h = sym_h = dec_h = sup_h = None
    used_rpc: str | None = None
    for candidate_rpc in rpc_list:
        if not candidate_rpc:
            continue
        name_h = rpc_eth_call(candidate_rpc, address, selectors["name"])
        sym_h = rpc_eth_call(candidate_rpc, address, selectors["symbol"])
        dec_h = rpc_eth_call(candidate_rpc, address, selectors["decimals"])
        sup_h = rpc_eth_call(candidate_rpc, address, selectors["totalSupply"])
        if any([name_h, sym_h, dec_h, sup_h]):
            used_rpc = candidate_rpc
            break
    if not used_rpc:
        out["error"] = "eth_call failed or empty"
        return out
    out["rpc"] = used_rpc
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


# chainId / explorer / keyword → internal CHAIN_RPC key
_CHAIN_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bchainid\s*[:=]?\s*8453\b", re.I), "base"),
    (re.compile(r"\bbasescan\.org\b", re.I), "base"),
    (re.compile(r"\bon\s+base\b", re.I), "base"),
    (re.compile(r"\bbase\s+network\b", re.I), "base"),
    (re.compile(r"\bchainid\s*[:=]?\s*137\b", re.I), "polygon"),
    (re.compile(r"\bpolygonscan\.org\b", re.I), "polygon"),
    (re.compile(r"\bpolygon\b", re.I), "polygon"),
    (re.compile(r"\bchainid\s*[:=]?\s*56\b", re.I), "bsc"),
    (re.compile(r"\bbscscan\.org\b", re.I), "bsc"),
    (re.compile(r"\b(bsc|bnb|binance)\b", re.I), "bsc"),
    (re.compile(r"\bchainid\s*[:=]?\s*42161\b", re.I), "arbitrum"),
    (re.compile(r"\barbiscan\.org\b", re.I), "arbitrum"),
    (re.compile(r"\barbitrum\b", re.I), "arbitrum"),
    (re.compile(r"\betherscan\.org\b", re.I), "ethereum"),
    (re.compile(r"\bchainid\s*[:=]?\s*1\b", re.I), "ethereum"),
    (re.compile(r"\bethereum\b", re.I), "ethereum"),
]


def infer_chains_for_address(address: str, blob: str) -> list[str]:
    """
    Infer likely EVM chain(s) for an address from nearby / global research text.
    Prefer local context windows around the address (explorer links, chainId).
    """
    ordered: list[str] = []
    low = (address or "").lower()
    # Prefer windows around each occurrence of the address.
    for m in re.finditer(re.escape(address), blob or "", flags=re.I):
        start = max(0, m.start() - 240)
        end = min(len(blob), m.end() + 240)
        window = blob[start:end]
        for pat, chain in _CHAIN_HINTS:
            if pat.search(window) and chain not in ordered and chain in CHAIN_RPC:
                ordered.append(chain)
    # Global blob fallback
    if not ordered:
        for pat, chain in _CHAIN_HINTS:
            if pat.search(blob or "") and chain not in ordered and chain in CHAIN_RPC:
                ordered.append(chain)
    # Always allow a multi-chain probe fallback if hints miss (wrong-chain
    # eth_call was the Albion failure mode: Base addr probed as Ethereum).
    for chain in ("ethereum", "base", "polygon", "arbitrum", "bsc"):
        if chain in CHAIN_RPC and chain not in ordered:
            ordered.append(chain)
    # Keep address key unused warning quiet
    _ = low
    return ordered


def significant_identity_tokens(candidate: dict[str, Any]) -> list[str]:
    """Brand/product tokens used to match on-chain name/symbol to a candidate."""
    raw_bits = [
        candidate.get("display_name") or "",
        candidate.get("slug") or "",
        candidate.get("notes") or "",
    ]
    # Explicit symbol-like tokens from notes / display (ALB-WR1-R1 etc.)
    text = " ".join(raw_bits)
    tokens: list[str] = []
    for m in re.findall(r"\b([A-Za-z][A-Za-z0-9-]{2,})\b", text):
        t = m.lower().strip("-")
        if t in {
            "the",
            "and",
            "for",
            "with",
            "from",
            "token",
            "tokens",
            "tokenized",
            "labs",
            "network",
            "protocol",
            "individual",
            "property",
            "oil",
            "gas",
            "on",
        }:
            continue
        if len(t) >= 4:
            tokens.append(re.sub(r"[^a-z0-9]", "", t))
    # Slug hyphen parts
    for part in (candidate.get("slug") or "").split("-"):
        p = re.sub(r"[^a-z0-9]", "", part.lower())
        if len(p) >= 4:
            tokens.append(p)
    # Preserve order, unique
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def token_metadata_matches_candidate(
    candidate: dict[str, Any], name: str | None, symbol: str | None
) -> bool:
    """
    True when live ERC-20 name/symbol aligns with the candidate identity.
    Requires meaningful brand overlap — not ticker-alone for short names.
    """
    bn = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    bs = re.sub(r"[^a-z0-9]", "", (symbol or "").lower())
    if not bn and not bs:
        return False
    sigs = significant_identity_tokens(candidate)
    if not sigs:
        compact = re.sub(
            r"[^a-z0-9]", "", (candidate.get("display_name") or "").lower()
        )
        return bool(compact and (compact[:5] in bn or compact in bn))
    # Need at least one strong brand token in on-chain name, or exact symbol
    # equality to a multi-char published symbol-like token from notes/name.
    name_hits = [t for t in sigs if len(t) >= 4 and t in bn]
    sym_hits = [t for t in sigs if t == bs and len(t) >= 4]
    if name_hits:
        return True
    if sym_hits:
        return True
    # Hyphenated symbols like ALB-WR1-R1 → albwr1r1 compact
    for t in sigs:
        if len(t) >= 6 and (t in bs or bs in t):
            return True
    return False


def classify_issuer_source(url: str, official_hosts: set[str]) -> bool:
    """Whether a URL counts as issuer-controlled for address publication."""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    if host.startswith("www."):
        host = host[4:]
    if host in official_hosts:
        return True
    # Common issuer publication surfaces
    if host in {"raw.githubusercontent.com", "github.com"}:
        return True
    if host.endswith(".gitbook.io"):
        return True
    return False


def extract_issuer_published_addresses(
    evidence: list[dict[str, Any]], candidate: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Collect contract addresses published in issuer-controlled reachable sources,
    with per-address chain hints from local context.
    """
    seeds = candidate.get("seeds") or []
    official_hosts: set[str] = set()
    for u in seeds:
        try:
            h = urlparse(u).netloc.lower()
            if h.startswith("www."):
                h = h[4:]
            if h:
                official_hosts.add(h)
        except Exception:
            pass
    # Also treat primary display-name host guesses lightly via seed hosts only.

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for e in evidence:
        if not e.get("ok"):
            continue
        url = e.get("url") or ""
        text = e.get("raw_text") or e.get("excerpt") or ""
        issuer = classify_issuer_source(url, official_hosts)
        # Explorer pages can corroborate but are not issuer publication.
        for m in ADDR_RE.finditer(text):
            addr = m.group(0)
            low = addr.lower()
            if low in seen:
                continue
            start = max(0, m.start() - 240)
            end = min(len(text), m.end() + 240)
            window = text[start:end]
            chains = infer_chains_for_address(addr, window + "\n" + text[:2000])
            out.append(
                {
                    "address": addr,
                    "source_url": url,
                    "issuer_published": issuer,
                    "chains": chains,
                    "context": re.sub(r"\s+", " ", window)[:220],
                }
            )
            seen.add(low)
    # Prefer issuer-published first
    out.sort(key=lambda r: (not r["issuer_published"], r["address"].lower()))
    return out


def resolve_token_identity(
    *,
    candidate: dict[str, Any],
    evidence: list[dict[str, Any]],
    blob: str,
    dex_hits: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Establish TOKEN IDENTITY via an explicit evidence chain:

      issuer-published address (preferred)
        → chain established
        → live eth_call
        → name/symbol/decimals/totalSupply match candidate identity
        → optional market/indexer corroboration

    Token identity ≠ asset backing ≠ economic/payout verification.
    """
    published = extract_issuer_published_addresses(evidence, candidate)
    # Also consider addresses in aggregate blob (may include followed pages)
    for a in collect_addresses([blob])[:12]:
        if not any(p["address"].lower() == a.lower() for p in published):
            published.append(
                {
                    "address": a,
                    "source_url": "(aggregate research text)",
                    "issuer_published": False,
                    "chains": infer_chains_for_address(a, blob),
                    "context": "",
                }
            )

    attempts: list[dict[str, Any]] = []
    for pub in published[:16]:
        addr = pub["address"]
        for chain in pub["chains"][:5]:
            rpc = primary_rpc(chain)
            if not rpc:
                continue
            probe = probe_erc20(addr, rpc, chain)
            attempt = {
                "address": addr,
                "chain": chain,
                "rpc": probe.get("rpc") or rpc,
                "issuer_published": pub["issuer_published"],
                "source_url": pub["source_url"],
                "eth_call_ok": bool(probe.get("ok")),
                "name": probe.get("name"),
                "symbol": probe.get("symbol"),
            }
            if not probe.get("ok"):
                attempt["error"] = probe.get("error") or "eth_call failed"
                attempts.append(attempt)
                continue
            matched = token_metadata_matches_candidate(
                candidate, probe.get("name"), probe.get("symbol")
            )
            attempt["metadata_match"] = matched
            attempts.append(attempt)
            if not matched:
                continue
            # Success — token IDENTITY established
            probe["ok"] = True
            probe["issuer_published"] = pub["issuer_published"]
            probe["address_source_url"] = pub["source_url"]
            probe["identity_evidence"] = {
                "issuer_published_address": bool(pub["issuer_published"]),
                "chain_established": True,
                "eth_call_verified": True,
                "metadata_match": True,
                "market_corroboration": False,  # filled by caller if dex pairs exist
            }
            # Confidence: issuer+rpc+match = high; rpc+match without issuer = medium
            probe["identity_confidence"] = (
                "high" if pub["issuer_published"] else "medium"
            )
            probe["identity_attempts"] = attempts
            return probe

    # DexScreener fallback (not sufficient alone for short tickers)
    name_l = (candidate.get("display_name") or "").lower()
    compact_name = re.sub(r"[^a-z0-9]", "", name_l)
    short_ticker = len(compact_name) <= 4
    for p in dex_hits:
        base = p.get("baseToken") or {}
        bname = base.get("name") or ""
        bsym = base.get("symbol") or ""
        addr = base.get("address")
        chain = (p.get("chainId") or "ethereum").lower()
        if not addr or not token_metadata_matches_candidate(candidate, bname, bsym):
            continue
        if short_ticker and not any(
            x["address"].lower() == addr.lower() and x.get("issuer_published")
            for x in published
        ):
            # Keep as collision-risk note only
            return {
                "ok": False,
                "unconfirmed_ticker_collision_risk": True,
                "address": addr,
                "chain": chain,
                "name": bname,
                "symbol": bsym,
                "error": (
                    "Short-ticker DexScreener hit without issuer-published "
                    "contract address corroboration — not treated as confirmed "
                    "token identity"
                ),
                "identity_attempts": attempts,
            }
        rpc = primary_rpc(chain) or primary_rpc("ethereum")
        probe = probe_erc20(addr, rpc, chain)
        if probe.get("ok") and token_metadata_matches_candidate(
            candidate, probe.get("name"), probe.get("symbol")
        ):
            probe["issuer_published"] = False
            probe["identity_confidence"] = "medium"
            probe["identity_evidence"] = {
                "issuer_published_address": False,
                "chain_established": True,
                "eth_call_verified": True,
                "metadata_match": True,
                "market_corroboration": True,
            }
            probe["identity_attempts"] = attempts
            return probe

    return {
        "ok": False,
        "error": "No issuer-published + eth_call-verified token identity established",
        "identity_attempts": attempts[:12],
    }


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
        "economic_right": None,
        "physical_asset": None,
        "payout": None,
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
    if re.search(r"revenue\s+swap\s+agreement", blob, flags=re.I):
        out["economic_right"] = "Revenue-swap / contractual revenue share (docs/filings)"
    elif re.search(
        r"(\d+(?:\.\d+)?\s*%\s+of\s+gross\s+revenues?)", blob, flags=re.I
    ):
        m = re.search(
            r"(\d+(?:\.\d+)?\s*%\s+of\s+gross\s+revenues?[^.]*\.?)", blob, flags=re.I
        )
        out["economic_right"] = (m.group(1) if m else "Gross-revenue royalty")[:180]
        out["royalty"] = out["royalty"] or out["economic_right"]
    elif re.search(r"royalty\s+interest|gross[- ]revenue\s+royalty", blob, flags=re.I):
        out["economic_right"] = "Royalty interest / gross-revenue royalty (docs/filings)"
        out["royalty"] = out["royalty"] or out["economic_right"]
    m = re.search(
        r"\b([A-Z][a-zA-Z]+(?:-[0-9]+)?)\b(?:\s+(?:well|field|mine|farm|property))?",
        blob,
    )
    # Prefer explicit well/field cues when present.
    m2 = re.search(
        r"\b([A-Za-z][A-Za-z0-9-]+)\s+(?:well|field|mine|farmland|property)\b",
        blob,
        flags=re.I,
    )
    if m2:
        out["physical_asset"] = m2.group(0)[:120]
    if re.search(r"payoutData|txHash|distribution\s+to\s+investors", blob, flags=re.I):
        out["payout"] = "Issuer-published payout records / distribution language present"
    return out


def physical_asset_cues(candidate: dict[str, Any]) -> list[str]:
    """Concrete physical-asset name cues from notes/aliases/display name."""
    bits: list[str] = []
    for a in candidate.get("aliases") or []:
        if a and len(str(a)) >= 4:
            bits.append(str(a))
    notes = candidate.get("notes") or ""
    bits.extend(re.findall(r"\b([A-Z][a-zA-Z]+-[0-9]+)\b", notes))
    bits.extend(re.findall(r"\b(PEDL\d+)\b", notes, flags=re.I))
    for part in re.split(r"[\s,/]+", candidate.get("display_name") or ""):
        if re.search(r"[A-Za-z]+-\d+", part):
            bits.append(part)
    # Category-ish cues are too weak alone; keep named assets only.
    seen: set[str] = set()
    out: list[str] = []
    for b in bits:
        low = b.lower().strip()
        if low in {"albion", "labs", "token", "oil", "gas", "rwa"}:
            continue
        if low and low not in seen and len(low) >= 4:
            seen.add(low)
            out.append(b)
    return out


def discover_github_economic_urls(
    evidence: list[dict[str, Any]], *, limit: int = 24
) -> list[str]:
    """
    From GitHub org/user repo listings already fetched, pick economic-surface
    repos and expand to raw constants/metadata/readme URLs.
    Generic: rewards/payout/claims/vault/royalty-named repos.
    """
    urls: list[str] = []
    seen: set[str] = set()

    def add(u: str) -> None:
        if u and u not in seen:
            seen.add(u)
            urls.append(u)

    repo_full_names: list[str] = []
    for e in evidence:
        if not e.get("ok"):
            continue
        url = e.get("url") or ""
        text = e.get("raw_text") or ""
        if "api.github.com" in url and "/repos" in url and text.lstrip().startswith("["):
            try:
                repos = json.loads(text)
            except Exception:
                repos = []
            if isinstance(repos, list):
                for repo in repos:
                    if not isinstance(repo, dict):
                        continue
                    name = (repo.get("name") or "").lower()
                    full = repo.get("full_name") or ""
                    if any(k in name for k in ECONOMIC_REPO_NAME_KEYS) and full:
                        repo_full_names.append(full)
        # Also catch github.com/org/repo links in HTML
        for m in re.finditer(
            r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", text
        ):
            org, repo = m.group(1), m.group(2)
            if repo.lower() in {"issues", "pulls", "actions", "projects"}:
                continue
            if any(k in repo.lower() for k in ECONOMIC_REPO_NAME_KEYS):
                repo_full_names.append(f"{org}/{repo}")

    # De-dupe repos
    repo_seen: set[str] = set()
    unique_repos: list[str] = []
    for full in repo_full_names:
        low = full.lower()
        if low not in repo_seen:
            repo_seen.add(low)
            unique_repos.append(full)

    for full in unique_repos[:6]:
        org, repo = full.split("/", 1)
        add(f"https://github.com/{org}/{repo}")
        add(f"https://raw.githubusercontent.com/{org}/{repo}/main/readme.md")
        add(f"https://raw.githubusercontent.com/{org}/{repo}/main/README.md")
        add(f"https://raw.githubusercontent.com/{org}/{repo}/main/src/constants.ts")
        add(
            f"https://api.github.com/repos/{org}/{repo}/git/trees/main?recursive=1"
        )

    # From tree listings already in evidence (or just-added will be fetched later),
    # callers re-invoke after fetch; also parse any tree JSON present now.
    for e in evidence:
        if not e.get("ok"):
            continue
        url = e.get("url") or ""
        text = e.get("raw_text") or ""
        if "git/trees/" not in url or "recursive=1" not in url:
            continue
        try:
            tree = json.loads(text)
        except Exception:
            continue
        paths = [
            t.get("path")
            for t in (tree.get("tree") or [])
            if isinstance(t, dict) and t.get("path")
        ]
        # Prefer constants + recent metadata.json under output/
        meta_paths = [
            p
            for p in paths
            if str(p).endswith("metadata.json") and "/output/" in str(p)
        ]
        meta_paths.sort(reverse=True)
        const_paths = [
            p
            for p in paths
            if str(p).endswith(("constants.ts", "constants.js", "config.ts"))
        ]
        m = re.search(
            r"api\.github\.com/repos/([^/]+)/([^/]+)/git/trees/", url
        )
        if not m:
            continue
        org, repo = m.group(1), m.group(2)
        for p in const_paths[:4]:
            add(f"https://raw.githubusercontent.com/{org}/{repo}/main/{p}")
        for p in meta_paths[:8]:
            add(f"https://raw.githubusercontent.com/{org}/{repo}/main/{p}")

    return urls[:limit]


def _walk_json_for_payouts(
    obj: Any, *, source_url: str, found: list[dict[str, Any]], depth: int = 0
) -> None:
    if depth > 8 or len(found) >= 80:
        return
    if isinstance(obj, dict):
        # Direct payoutData array
        if isinstance(obj.get("payoutData"), list):
            token = (
                obj.get("contractAddress")
                or obj.get("tokenAddress")
                or obj.get("address")
            )
            symbol = obj.get("symbol")
            asset_id = obj.get("assetId") or obj.get("assetName")
            asset_block = obj.get("asset") if isinstance(obj.get("asset"), dict) else {}
            for row in obj["payoutData"]:
                if not isinstance(row, dict):
                    continue
                payout = row.get("tokenPayout") if isinstance(row.get("tokenPayout"), dict) else row
                if not isinstance(payout, dict):
                    continue
                tx = payout.get("txHash") or payout.get("transactionHash")
                if not tx or not str(tx).startswith("0x"):
                    continue
                found.append(
                    {
                        "tx_hash": str(tx),
                        "month": row.get("month") or payout.get("month"),
                        "date": payout.get("date"),
                        "total_payout": payout.get("totalPayout"),
                        "payout_per_token": payout.get("payoutPerToken"),
                        "order_hash": payout.get("orderHash"),
                        "token_address": token,
                        "symbol": symbol,
                        "asset_id": asset_id
                        or (asset_block.get("assetName") if asset_block else None),
                        "asset_name": asset_block.get("assetName") if asset_block else None,
                        "source_url": source_url,
                        "note": payout.get("note"),
                    }
                )
        for v in obj.values():
            _walk_json_for_payouts(v, source_url=source_url, found=found, depth=depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            _walk_json_for_payouts(v, source_url=source_url, found=found, depth=depth + 1)


def extract_payout_records(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for e in evidence:
        if not e.get("ok"):
            continue
        text = e.get("raw_text") or ""
        url = e.get("url") or ""
        if "txHash" not in text and "payoutData" not in text:
            continue
        # Try whole-document JSON first
        parsed = None
        try:
            parsed = json.loads(text)
        except Exception:
            # Embedded JSON object containing payoutData
            m = re.search(r"\{[^{}]*\"payoutData\"[\s\S]*\}", text)
            if m:
                try:
                    parsed = json.loads(m.group(0))
                except Exception:
                    parsed = None
        if parsed is not None:
            _walk_json_for_payouts(parsed, source_url=url, found=found)
            continue
        # Fallback: regex for txHash fields near payout language
        for m in re.finditer(
            r'"txHash"\s*:\s*"(0x[a-fA-F0-9]{64})"', text
        ):
            found.append(
                {
                    "tx_hash": m.group(1),
                    "source_url": url,
                    "token_address": None,
                    "symbol": None,
                    "asset_id": None,
                }
            )
    # De-dupe by tx hash
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in found:
        h = (row.get("tx_hash") or "").lower()
        if h and h not in seen:
            seen.add(h)
            out.append(row)
    return out


def extract_distribution_addresses(
    evidence: list[dict[str, Any]], blob: str
) -> list[dict[str, Any]]:
    """Issuer-published Safe/vault/treasury/orderbook addresses near economic keywords."""
    patterns = (
        r"(?:R\d_)?SAFE(?:_ADDRESS)?\s*=\s*[\"']?(0x[a-fA-F0-9]{40})",
        r"(?:VAULT|TREASURY|DISTRIBUTION|PAYOUT|REWARDS?)(?:_ADDRESS|_SAFE)?\s*=\s*[\"']?(0x[a-fA-F0-9]{40})",
        r"(?:safe|vault|treasury|distribution|payout)\s*(?:address)?[^0x]{0,40}(0x[a-fA-F0-9]{40})",
        r"USDC(?:_BASE)?\s*=\s*[\"']?(0x[a-fA-F0-9]{40})",
        r"ORDERBOOK(?:_ADDRESS|_V6_ADDRESS)?\s*=\s*[\"']?(0x[a-fA-F0-9]{40})",
        r"METABOARD(?:_ADDRESS)?\s*=\s*[\"']?(0x[a-fA-F0-9]{40})",
    )
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    texts: list[tuple[str, str]] = [(blob, "(aggregate)")]
    for e in evidence:
        if e.get("ok"):
            texts.append((e.get("raw_text") or "", e.get("url") or ""))
    for text, src in texts:
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.I):
                addr = m.group(1)
                low = addr.lower()
                if low in seen:
                    continue
                seen.add(low)
                window = text[max(0, m.start() - 80) : m.end() + 80]
                role = "distribution_related"
                wl = window.lower()
                if "safe" in wl:
                    role = "safe"
                elif "vault" in wl:
                    role = "vault"
                elif "usdc" in wl:
                    role = "payout_currency"
                elif "orderbook" in wl:
                    role = "orderbook"
                elif "metaboard" in wl:
                    role = "metaboard"
                out.append(
                    {
                        "address": addr,
                        "role": role,
                        "source_url": src,
                        "context": re.sub(r"\s+", " ", window)[:200],
                    }
                )
    return out[:24]


def verify_payout_transactions(
    records: list[dict[str, Any]], *, chain: str
) -> dict[str, Any]:
    """Verify a sample of issuer-published payout txHashes on-chain."""
    verified: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    sample = records[:6]
    for row in sample:
        txh = row.get("tx_hash")
        if not txh:
            continue
        tx = rpc_get_transaction(chain, txh)
        if not tx:
            failed.append({"tx_hash": txh, "error": "transaction not found on chain"})
            continue
        receipt = rpc_get_receipt(chain, txh)
        status_ok = True
        if receipt is not None:
            status_ok = str(receipt.get("status") or "").lower() in ("0x1", "1")
        verified.append(
            {
                "tx_hash": txh,
                "to": tx.get("to"),
                "from": tx.get("from"),
                "block_number": tx.get("blockNumber"),
                "status_ok": status_ok,
                "log_count": len((receipt or {}).get("logs") or []),
                "rpc": tx.get("_rpc"),
                "source_url": row.get("source_url"),
                "month": row.get("month"),
                "total_payout": row.get("total_payout"),
            }
        )
    return {
        "sampled": len(sample),
        "verified_count": len(verified),
        "failed_count": len(failed),
        "verified": verified,
        "failed": failed,
        "chain": chain,
    }


RIGHT_TYPE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"revenue\s+swap\s+agreement", re.I), "revenue_swap"),
    (re.compile(r"net\s+smelter\s+royalty|\bNSR\b", re.I), "net_smelter_royalty"),
    (
        re.compile(r"\d+(?:\.\d+)?\s*%\s+of\s+gross\s+revenues?", re.I),
        "gross_revenue_royalty",
    ),
    (re.compile(r"royalty\s+interest", re.I), "royalty_interest"),
    (re.compile(r"contractual\s+revenue\s+share|revenue\s+share", re.I), "revenue_share"),
    (re.compile(r"fractional\s+(?:farmland\s+)?ownership", re.I), "fractional_ownership"),
    (re.compile(r"vault\s+share", re.I), "vault_share"),
    (re.compile(r"\bdebt\b|\bbond\b", re.I), "debt_like"),
]


def classify_economic_right(blob: str) -> dict[str, Any]:
    hits: list[str] = []
    for pat, label in RIGHT_TYPE_PATTERNS:
        if pat.search(blob or ""):
            hits.append(label)
    # Preserve order unique
    seen: set[str] = set()
    ordered = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return {
        "right_types": ordered,
        "primary": ordered[0] if ordered else None,
    }


def layer_status(
    *,
    verified: bool,
    partial: bool,
    blocker: str | None = None,
) -> dict[str, Any]:
    if verified:
        status = "verified"
    elif partial:
        status = "partially-verified"
    else:
        status = "unverified"
    return {"status": status, "blocker": blocker if status != "verified" else None}


def build_evidence_graph(
    *,
    candidate: dict[str, Any],
    evidence: list[dict[str, Any]],
    token_probe: dict[str, Any] | None,
    blob: str,
    claim_bits: dict[str, str | None],
    payout_records: list[dict[str, Any]],
    payout_verification: dict[str, Any],
    distribution_addrs: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Layered TOKEN → ASSET → RIGHT → REVENUE → PAYOUT evidence graph.
    Each layer has independent status/evidence/confidence.
    """
    token_ok = bool(token_probe and token_probe.get("ok"))
    id_ev = (token_probe or {}).get("identity_evidence") or {}
    cues = [c.lower() for c in physical_asset_cues(candidate)]

    independent_ev = [
        e
        for e in evidence
        if e.get("ok") and is_independent_host(host_of(e.get("url") or ""))
    ]
    issuer_ev = [
        e
        for e in evidence
        if e.get("ok") and not is_independent_host(host_of(e.get("url") or ""))
    ]

    # --- physical asset ---
    phys_evidence: list[dict[str, Any]] = []
    independent_asset_hit = False
    issuer_asset_hit = False
    named_asset: str | None = None
    for e in independent_ev:
        text = (e.get("raw_text") or "").lower()
        hit_cues = [c for c in cues if c in text]
        if hit_cues and re.search(
            r"royalty|revenue\s+swap|gross\s+revenues?|well|field|licence|license",
            text,
            flags=re.I,
        ):
            independent_asset_hit = True
            named_asset = named_asset or hit_cues[0]
            phys_evidence.append(
                {
                    "source": e["url"],
                    "tier": "highest",
                    "kind": "independent_filing",
                    "proves": (
                        f"Independent source names physical asset cue(s) "
                        f"{hit_cues} in economic/royalty context"
                    ),
                    "reachable": True,
                    "independently_verifiable": True,
                }
            )
    for e in issuer_ev:
        text = (e.get("raw_text") or "").lower()
        hit_cues = [c for c in cues if c in text]
        # Also accept asset names from payout metadata
        if hit_cues or re.search(
            r"wressle|pedl\d+|onshore\s+conventional\s+oil", text, flags=re.I
        ):
            if hit_cues or "assetname" in text.replace(" ", "").lower() or "asset" in text:
                issuer_asset_hit = True
                named_asset = named_asset or (hit_cues[0] if hit_cues else claim_bits.get("physical_asset"))
                if any(
                    x in (e.get("url") or "")
                    for x in ("metadata.json", "whitepaper", "tokenlist")
                ) or hit_cues:
                    phys_evidence.append(
                        {
                            "source": e["url"],
                            "tier": "medium" if "metadata.json" in (e.get("url") or "") else "medium",
                            "kind": "issuer_documentation",
                            "proves": "Issuer materials name a specific physical asset",
                            "reachable": True,
                            "independently_verifiable": False,
                        }
                    )
                    break
    # Payout metadata asset blocks
    for row in payout_records:
        if row.get("asset_name") or row.get("asset_id"):
            issuer_asset_hit = True
            named_asset = named_asset or row.get("asset_name") or row.get("asset_id")
            phys_evidence.append(
                {
                    "source": row.get("source_url"),
                    "tier": "medium",
                    "kind": "issuer_payout_metadata",
                    "proves": (
                        f"Payout metadata binds token to asset "
                        f"{row.get('asset_id') or row.get('asset_name')}"
                    ),
                    "reachable": True,
                    "independently_verifiable": False,
                }
            )
            break

    if independent_asset_hit:
        phys_layer = {
            **layer_status(verified=True, partial=False),
            "confidence": "high",
            "named_asset": named_asset,
            "evidence": phys_evidence[:8],
        }
    elif issuer_asset_hit and named_asset:
        phys_layer = {
            **layer_status(
                verified=False,
                partial=True,
                blocker=(
                    "Physical asset named only in issuer materials — "
                    "no independent filing/registry corroboration"
                ),
            ),
            "confidence": "medium",
            "named_asset": named_asset,
            "evidence": phys_evidence[:8],
        }
    else:
        phys_layer = {
            **layer_status(
                verified=False,
                partial=False,
                blocker="No specific physical asset identity established from research sources",
            ),
            "confidence": "none",
            "named_asset": None,
            "evidence": phys_evidence[:8],
        }

    # --- economic / legal right ---
    right_info = classify_economic_right(blob)
    right_evidence: list[dict[str, Any]] = []
    independent_right = False
    issuer_right = False
    brand_bits = [
        b.lower()
        for b in (
            list((candidate.get("display_name") or "").split()[:3])
            + list(candidate.get("aliases") or [])[:6]
            + cues
        )
        if b and len(str(b)) >= 4
    ]
    for e in independent_ev:
        text = e.get("raw_text") or ""
        text_l = text.lower()
        ri = classify_economic_right(text)
        if not ri["primary"]:
            continue
        has_asset_cue = bool(cues) and any(c in text_l for c in cues)
        has_brand = any(b in text_l for b in brand_bits)
        if not (has_asset_cue or has_brand):
            continue
        independent_right = True
        right_evidence.append(
            {
                "source": e["url"],
                "tier": "highest",
                "kind": "independent_filing",
                "proves": (
                    f"Independent source links project/asset to right type "
                    f"`{ri['primary']}`"
                ),
                "reachable": True,
                "independently_verifiable": True,
                "right_type": ri["primary"],
            }
        )
    if right_info["primary"]:
        issuer_right = True
        right_evidence.append(
            {
                "source": "issuer research corpus",
                "tier": "medium",
                "kind": "issuer_documentation",
                "proves": f"Issuer/docs language indicates `{right_info['primary']}`",
                "reachable": True,
                "independently_verifiable": False,
                "right_type": right_info["primary"],
            }
        )
    # Token name itself often encodes royalty
    if token_ok and token_probe:
        nm = f"{token_probe.get('name') or ''} {token_probe.get('symbol') or ''}"
        if re.search(r"royalty|NSR|revenue", nm, flags=re.I):
            issuer_right = True
            right_evidence.append(
                {
                    "source": f"on-chain token metadata @ {token_probe.get('address')}",
                    "tier": "highest",
                    "kind": "blockchain_token_metadata",
                    "proves": "Token name/symbol encodes economic-right claim (not legal proof alone)",
                    "reachable": True,
                    "independently_verifiable": True,
                    "right_type": right_info["primary"] or "royalty_interest",
                }
            )

    if independent_right and right_info["primary"]:
        right_layer = {
            **layer_status(verified=True, partial=False),
            "confidence": "high",
            "right_type": right_info["primary"],
            "right_types_seen": right_info["right_types"],
            "evidence": right_evidence[:8],
        }
    elif issuer_right and right_info["primary"]:
        right_layer = {
            **layer_status(
                verified=False,
                partial=True,
                blocker=(
                    "Economic/legal right described in issuer materials only — "
                    "independent legal corroboration missing"
                ),
            ),
            "confidence": "medium",
            "right_type": right_info["primary"],
            "right_types_seen": right_info["right_types"],
            "evidence": right_evidence[:8],
        }
    else:
        right_layer = {
            **layer_status(
                verified=False,
                partial=False,
                blocker="No concrete economic/legal right type established",
            ),
            "confidence": "none",
            "right_type": None,
            "right_types_seen": [],
            "evidence": right_evidence[:8],
        }

    # --- revenue mechanism ---
    rev_evidence: list[dict[str, Any]] = []
    revenue_described = bool(
        re.search(
            r"production|producing|gross\s+revenues?|oil\s+field|harvest|lease\s+income|mining\s+revenue",
            blob,
            flags=re.I,
        )
    )
    revenue_queryable = False  # continuous public production API — rare
    if revenue_described:
        for e in independent_ev + issuer_ev:
            text = e.get("raw_text") or ""
            if re.search(
                r"gross\s+revenues?|producing|production|oil\s+field|harvest",
                text,
                flags=re.I,
            ):
                rev_evidence.append(
                    {
                        "source": e["url"],
                        "tier": (
                            "highest"
                            if is_independent_host(host_of(e["url"]))
                            else "medium"
                        ),
                        "kind": (
                            "independent_filing"
                            if is_independent_host(host_of(e["url"]))
                            else "issuer_documentation"
                        ),
                        "proves": "Source describes how the underlying asset generates revenue",
                        "reachable": True,
                        "independently_verifiable": is_independent_host(host_of(e["url"])),
                        "machine_queryable": False,
                    }
                )
                if len(rev_evidence) >= 4:
                    break
    if independent_ev and revenue_described:
        rev_layer = {
            **layer_status(
                verified=False,
                partial=True,
                blocker=(
                    "Revenue generation described in filings/docs but no continuously "
                    "machine-queryable production/revenue API confirmed"
                ),
            ),
            "confidence": "medium",
            "machine_queryable": revenue_queryable,
            "evidence": rev_evidence[:6],
        }
    elif revenue_described:
        rev_layer = {
            **layer_status(
                verified=False,
                partial=True,
                blocker="Revenue mechanism described only by issuer; not independently queryable",
            ),
            "confidence": "low",
            "machine_queryable": False,
            "evidence": rev_evidence[:6],
        }
    else:
        rev_layer = {
            **layer_status(
                verified=False,
                partial=False,
                blocker="No revenue-generation mechanism identified",
            ),
            "confidence": "none",
            "machine_queryable": False,
            "evidence": [],
        }

    # --- payout mechanism ---
    pay_evidence: list[dict[str, Any]] = []
    verified_n = int(payout_verification.get("verified_count") or 0)
    for row in (payout_verification.get("verified") or [])[:6]:
        pay_evidence.append(
            {
                "source": row.get("source_url"),
                "tier": "highest",
                "kind": "blockchain_transaction",
                "proves": (
                    f"Issuer-published payout txHash {row.get('tx_hash')} "
                    f"found on {payout_verification.get('chain')} "
                    f"(to={row.get('to')}, status_ok={row.get('status_ok')})"
                ),
                "reachable": True,
                "independently_verifiable": True,
                "machine_queryable": True,
                "tx_hash": row.get("tx_hash"),
            }
        )
    for e in evidence:
        url = e.get("url") or ""
        if e.get("ok") and "metadata.json" in url and "payoutData" in (e.get("raw_text") or ""):
            pay_evidence.append(
                {
                    "source": url,
                    "tier": "medium",
                    "kind": "issuer_payout_metadata",
                    "proves": "Public issuer payout metadata JSON with historical payoutData",
                    "reachable": True,
                    "independently_verifiable": False,
                    "machine_queryable": True,
                }
            )
            break
    for d in distribution_addrs[:6]:
        pay_evidence.append(
            {
                "source": d.get("source_url"),
                "tier": "medium",
                "kind": "issuer_contract_address",
                "proves": f"Published {d.get('role')} address {d.get('address')}",
                "reachable": True,
                "independently_verifiable": False,
                "machine_queryable": True,
                "address": d.get("address"),
                "role": d.get("role"),
            }
        )

    if verified_n > 0 and payout_records:
        pay_layer = {
            **layer_status(verified=True, partial=False),
            "confidence": "high",
            "machine_queryable": True,
            "payout_record_count": len(payout_records),
            "onchain_verified_sample": verified_n,
            "currency_hint": (
                "USDC"
                if any(d.get("role") == "payout_currency" for d in distribution_addrs)
                or re.search(r"\bUSDC\b", blob)
                else None
            ),
            "frequency_hint": (
                "monthly"
                if re.search(r"monthly\s+payment|per\s+month|month\":", blob, flags=re.I)
                else None
            ),
            "evidence": pay_evidence[:10],
        }
    elif payout_records or distribution_addrs:
        pay_layer = {
            **layer_status(
                verified=False,
                partial=True,
                blocker=(
                    "Payout addresses/metadata published but historical payout "
                    "transactions not independently confirmed on-chain"
                ),
            ),
            "confidence": "medium",
            "machine_queryable": bool(payout_records or distribution_addrs),
            "payout_record_count": len(payout_records),
            "onchain_verified_sample": verified_n,
            "currency_hint": None,
            "frequency_hint": None,
            "evidence": pay_evidence[:10],
        }
    else:
        # Legacy regex surfaces
        has_dist_addr = bool(
            re.search(
                r"(profit distribution|distribution|payout|royalty).{0,80}0x[a-fA-F0-9]{40}",
                blob,
                flags=re.I,
            )
        )
        has_staking_addr = bool(
            re.search(r"staking contract.{0,80}0x[a-fA-F0-9]{40}", blob, flags=re.I)
        )
        if has_dist_addr or has_staking_addr:
            pay_layer = {
                **layer_status(
                    verified=False,
                    partial=True,
                    blocker="Distribution/staking address pattern found but payout history not verified",
                ),
                "confidence": "low",
                "machine_queryable": True,
                "payout_record_count": 0,
                "onchain_verified_sample": 0,
                "currency_hint": None,
                "frequency_hint": None,
                "evidence": pay_evidence[:10],
            }
        else:
            pay_layer = {
                **layer_status(
                    verified=False,
                    partial=False,
                    blocker=(
                        "No publicly reachable payout metadata, distribution "
                        "contract, or verified payout transactions"
                    ),
                ),
                "confidence": "none",
                "machine_queryable": False,
                "payout_record_count": 0,
                "onchain_verified_sample": 0,
                "currency_hint": None,
                "frequency_hint": None,
                "evidence": [],
            }

    # --- token identity layer (from prior resolver) ---
    if token_ok:
        token_layer = {
            "status": "verified",
            "confidence": (token_probe or {}).get("identity_confidence") or "medium",
            "blocker": None,
            "evidence": [
                {
                    "source": (token_probe or {}).get("address_source_url")
                    or "token probe",
                    "tier": "highest",
                    "kind": "blockchain_eth_call",
                    "proves": (
                        f"eth_call identity for {(token_probe or {}).get('symbol')} @ "
                        f"{(token_probe or {}).get('address')} on "
                        f"{(token_probe or {}).get('chain')}"
                    ),
                    "reachable": True,
                    "independently_verifiable": True,
                    "machine_queryable": True,
                }
            ],
            "identity_evidence": id_ev,
        }
    else:
        token_layer = {
            "status": "unverified",
            "confidence": "none",
            "blocker": (token_probe or {}).get("error")
            or "Token identity not established",
            "evidence": [],
            "identity_evidence": id_ev,
        }

    machine_sources: list[dict[str, Any]] = []
    if token_ok and token_probe:
        machine_sources.append(
            {
                "source": f"{token_probe.get('chain')}:{token_probe.get('address')}",
                "what_it_proves": "ERC-20 token identity and supply",
                "reachable": True,
                "independently_verifiable": True,
                "kind": "eth_call",
            }
        )
    for row in (payout_verification.get("verified") or [])[:4]:
        machine_sources.append(
            {
                "source": row.get("tx_hash"),
                "what_it_proves": "Historical investor payout transaction",
                "reachable": True,
                "independently_verifiable": True,
                "kind": "eth_getTransaction",
            }
        )
    for e in evidence:
        url = e.get("url") or ""
        if e.get("ok") and "metadata.json" in url and "payoutData" in (e.get("raw_text") or ""):
            machine_sources.append(
                {
                    "source": url,
                    "what_it_proves": "Structured payout history (issuer-published JSON)",
                    "reachable": True,
                    "independently_verifiable": False,
                    "kind": "http_json",
                }
            )
    for e in independent_ev[:3]:
        machine_sources.append(
            {
                "source": e["url"],
                "what_it_proves": "Independent filing/announcement text (not continuous API)",
                "reachable": True,
                "independently_verifiable": True,
                "kind": "http_text",
            }
        )

    return {
        "token_identity": token_layer,
        "physical_asset": phys_layer,
        "economic_right": right_layer,
        "revenue_mechanism": rev_layer,
        "payout_mechanism": pay_layer,
        "machine_queryable_sources": machine_sources[:16],
    }


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
    evidence_graph: dict[str, Any] | None = None,
    payout_records: list[dict[str, Any]] | None = None,
    payout_verification: dict[str, Any] | None = None,
    distribution_addrs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    token_ok = bool(token_probe and token_probe.get("ok"))
    market_ok = bool(dex_pairs)
    cg_coins = (coingecko or {}).get("coins") or []
    independent_market = market_ok or bool(cg_coins)
    unconfirmed_ticker = bool(
        token_probe and token_probe.get("unconfirmed_ticker_collision_risk")
    )
    identity_evidence = (
        (token_probe or {}).get("identity_evidence")
        if token_probe
        else None
    ) or {
        "issuer_published_address": False,
        "chain_established": False,
        "eth_call_verified": False,
        "metadata_match": False,
        "market_corroboration": False,
    }
    identity_confidence = (
        (token_probe or {}).get("identity_confidence") if token_ok else "none"
    )

    payout_records = payout_records or []
    payout_verification = payout_verification or {}
    distribution_addrs = distribution_addrs or []
    graph = evidence_graph or build_evidence_graph(
        candidate=candidate,
        evidence=evidence,
        token_probe=token_probe,
        blob=blob,
        claim_bits=claim_bits,
        payout_records=payout_records,
        payout_verification=payout_verification,
        distribution_addrs=distribution_addrs,
    )

    phys = graph.get("physical_asset") or {}
    right = graph.get("economic_right") or {}
    revenue = graph.get("revenue_mechanism") or {}
    payout = graph.get("payout_mechanism") or {}

    docs_claim_underlying = bool(
        claim_bits.get("ownership")
        or claim_bits.get("royalty")
        or claim_bits.get("economic_right")
        or claim_bits.get("physical_asset")
        or re.search(r"farmland|mining|royalty|NSR|real[- ]world", blob, flags=re.I)
    )
    # Back-compat flags used by ADAPTER_SPEC sections:
    # underlying_verifiable ≈ physical asset independently established
    # economic_verifiable ≈ machine-queryable payout/economic surface
    underlying_verifiable = phys.get("status") == "verified"
    economic_verifiable = payout.get("status") == "verified"
    economic_bridge_verifiable = (
        phys.get("status") in ("verified", "partially-verified")
        and right.get("status") in ("verified", "partially-verified")
        and payout.get("status") == "verified"
    )

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

    # Readiness — require the investment chain, not merely a token + marketing.
    # adapter-ready only when an adapter could continuously retrieve meaningful
    # asset/investment data without fabrication:
    #   token identity + physical asset (independent) + economic right + queryable payout
    fundamental_ready = (
        token_ok
        and phys.get("status") == "verified"
        and right.get("status") in ("verified", "partially-verified")
        and payout.get("status") == "verified"
        and bool(payout.get("machine_queryable"))
    )
    if fundamental_ready:
        status = "adapter-ready"
    elif token_ok:
        status = "token-data-only"
    elif market_ok:
        status = "blocked"
    else:
        status = "blocked"
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
    if phys.get("status") != "verified":
        blockers.append(
            phys.get("blocker")
            or "Physical asset identity not independently verified"
        )
    if right.get("status") not in ("verified", "partially-verified"):
        blockers.append(
            right.get("blocker")
            or "Economic/legal right linking token to asset revenues not established"
        )
    if payout.get("status") != "verified":
        blockers.append(
            payout.get("blocker")
            or "No machine-queryable payout/distribution surface with on-chain confirmation"
        )
    if revenue.get("status") == "unverified" and docs_claim_underlying:
        # Optional layer — recorded but not always a hard blocker when payout exists
        pass
    if not independent_market and not token_ok:
        blockers.append("No independent market/indexer surface confirming asset identity")
    # De-dupe blockers
    blockers = list(dict.fromkeys(b for b in blockers if b))

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
        # Address provenance — separate from asset/backing verification
        issuer_pub = bool(token_probe.get("issuer_published"))
        claims.append(
            {
                "claim": "TOKEN IDENTITY: contract address is issuer-published + eth_call-verified",
                "claimed_value": (
                    f"{token_probe.get('name')} / {token_probe.get('symbol')} @ "
                    f"{token_probe['address']} ({token_probe.get('chain')}); "
                    f"confidence={identity_confidence}"
                ),
                "source": token_probe.get("address_source_url")
                or "DexScreener / research text",
                "source_type": (
                    "official documentation" if issuer_pub else "DEX/indexer"
                ),
                "fact_domain": "on-chain",
                "verification_method": (
                    "Issuer-controlled source publishes address → infer chain → "
                    "eth_call name()/symbol()/decimals()/totalSupply() → match "
                    "candidate identity"
                    + ("; DexScreener corroboration" if market_ok else "")
                ),
                "current_status": "verified" if issuer_pub else "partially-verified",
                "adapter_output": "token identity fields / claims[]",
                "blocker": (
                    "—"
                    if issuer_pub
                    else (
                        "Address provenance is market/indexer-attributed rather "
                        "than issuer-published; token identity still eth_call-matched"
                    )
                ),
            }
        )
        # Explicit layered claims — keep TOKEN / ASSET / RIGHT / PAYOUT separate
        phys_src = ((phys.get("evidence") or [{}])[0] or {}).get("source") or "n/a"
        claims.append(
            {
                "claim": "PHYSICAL ASSET: underlying physical asset identity",
                "claimed_value": phys.get("named_asset")
                or claim_bits.get("physical_asset")
                or "not established by token identity alone",
                "source": str(phys_src),
                "source_type": (
                    "regulatory/independent filing"
                    if phys.get("status") == "verified"
                    else "official documentation"
                ),
                "fact_domain": "physical-world",
                "verification_method": (
                    "Independent filings/registries naming the asset + economic context; "
                    "NOT implied by ERC-20 identity"
                ),
                "current_status": (
                    "verified"
                    if phys.get("status") == "verified"
                    else (
                        "partially-verified"
                        if phys.get("status") == "partially-verified"
                        else "blocked"
                    )
                ),
                "adapter_output": (
                    "underlying_asset"
                    if phys.get("status") in ("verified", "partially-verified")
                    else "null / unavailable"
                ),
                "blocker": phys.get("blocker") or "—",
            }
        )
        right_src = ((right.get("evidence") or [{}])[0] or {}).get("source") or "n/a"
        claims.append(
            {
                "claim": "ECONOMIC/LEGAL RIGHT: token holder right over asset/revenues",
                "claimed_value": right.get("right_type")
                or claim_bits.get("economic_right")
                or claim_bits.get("royalty")
                or "not established by token identity alone",
                "source": str(right_src),
                "source_type": (
                    "regulatory/independent filing"
                    if right.get("status") == "verified"
                    else "official documentation"
                ),
                "fact_domain": "physical-world",
                "verification_method": (
                    "Independent filing and/or issuer legal/technical docs describing "
                    "right type (royalty, revenue-swap, ownership, etc.)"
                ),
                "current_status": (
                    "verified"
                    if right.get("status") == "verified"
                    else (
                        "partially-verified"
                        if right.get("status") == "partially-verified"
                        else "blocked"
                    )
                ),
                "adapter_output": (
                    "claims[] / economic_right"
                    if right.get("status") in ("verified", "partially-verified")
                    else "null / unavailable"
                ),
                "blocker": right.get("blocker") or "—",
            }
        )
        pay_src = ((payout.get("evidence") or [{}])[0] or {}).get("source") or "n/a"
        claims.append(
            {
                "claim": "PAYOUT MECHANISM: machine-queryable investor distributions",
                "claimed_value": (
                    f"{payout.get('payout_record_count') or 0} payout records; "
                    f"{payout.get('onchain_verified_sample') or 0} on-chain verified; "
                    f"currency={payout.get('currency_hint') or 'unknown'}; "
                    f"frequency={payout.get('frequency_hint') or 'unknown'}"
                ),
                "source": str(pay_src),
                "source_type": (
                    "blockchain" if economic_verifiable else "official documentation"
                ),
                "fact_domain": "on-chain" if economic_verifiable else "physical-world",
                "verification_method": (
                    "Issuer-published payout metadata → eth_getTransaction(ByHash/Receipt) "
                    "on the token's chain; or distribution contract events / public API"
                ),
                "current_status": (
                    "verified"
                    if payout.get("status") == "verified"
                    else (
                        "partially-verified"
                        if payout.get("status") == "partially-verified"
                        else "blocked"
                    )
                ),
                "adapter_output": (
                    "distribution_history / realized_yield_pct"
                    if economic_verifiable
                    else "null / unavailable"
                ),
                "blocker": payout.get("blocker") or "—",
            }
        )
        claims.append(
            {
                "claim": "REVENUE MECHANISM: how the physical asset generates revenue",
                "claimed_value": (
                    "described"
                    if revenue.get("status") in ("verified", "partially-verified")
                    else "not established"
                ),
                "source": str(
                    ((revenue.get("evidence") or [{}])[0] or {}).get("source") or "n/a"
                ),
                "source_type": "official documentation",
                "fact_domain": "physical-world",
                "verification_method": (
                    "Operator/regulatory production disclosures or continuously "
                    "queryable revenue APIs"
                ),
                "current_status": (
                    "verified"
                    if revenue.get("status") == "verified"
                    else (
                        "partially-verified"
                        if revenue.get("status") == "partially-verified"
                        else "unverified"
                    )
                ),
                "adapter_output": (
                    "claims[] (context)"
                    if revenue.get("status") in ("verified", "partially-verified")
                    else "null / unavailable"
                ),
                "blocker": revenue.get("blocker") or "—",
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
    if status == "adapter-ready":
        reason = (
            "Evidence graph supports a useful adapter: TOKEN IDENTITY verified; "
            f"PHYSICAL ASSET verified ({phys.get('named_asset') or 'named'}); "
            f"ECONOMIC RIGHT {right.get('status')} ({right.get('right_type')}); "
            f"PAYOUT MECHANISM verified with "
            f"{payout.get('onchain_verified_sample') or 0} on-chain sample "
            f"tx(s) and machine-queryable payout metadata. "
            f"Verified surfaces: {', '.join(verified_bits) or 'see matrix'}."
        )
        next_step = (
            "Human greenlight can proceed to a scoped adapter implementing "
            "only the verified token + payout surfaces, with physical/economic "
            "right evidence recorded as claims[] provenance — not fabricated fields."
        )
    elif status == "token-data-only":
        missing = []
        if phys.get("status") != "verified":
            missing.append(f"physical_asset={phys.get('status')}")
        if right.get("status") not in ("verified", "partially-verified"):
            missing.append(f"economic_right={right.get('status')}")
        if payout.get("status") != "verified":
            missing.append(f"payout_mechanism={payout.get('status')}")
        reason = (
            "TOKEN IDENTITY can be established"
            + (
                f" (confidence={identity_confidence}; issuer-published="
                f"{identity_evidence.get('issuer_published_address')}; "
                f"eth_call={identity_evidence.get('eth_call_verified')})"
                if token_ok
                else ""
            )
            + ", but the TOKEN→ASSET→RIGHT→PAYOUT chain is incomplete "
            f"({', '.join(missing) or 'see evidence graph'}). Tokn must not "
            "equate token identity with physical-asset ownership or realized yield."
        )
        next_step = (
            "To become adapter-ready: independently corroborate the physical asset, "
            "establish the economic/legal right type, and publish a machine-queryable "
            "payout surface (distribution txs/events/API) that an adapter can poll. "
            "Token identity alone is insufficient."
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
    if economic_verifiable:
        recommended_scope.append(
            "Historical payout metadata + on-chain txHash verification for distributions"
        )
        if distribution_addrs:
            recommended_scope.append(
                "Published Safe/vault/orderbook addresses as payout plumbing context"
            )
    recommended_scope.append(
        "claims[] rows for documented self-reported yield/ownership claims with explicit tiers"
    )
    if phys.get("status") in ("verified", "partially-verified"):
        recommended_scope.append(
            "Record physical-asset identity + independent filing URLs as claims[] provenance"
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
    if revenue.get("status") != "verified":
        prohibited.append("Continuously verified production/revenue figures as facts")
    if not token_ok:
        prohibited.append("Any on-chain token identity fields")
        recommended_scope = [
            "Do not implement an adapter yet — research only until identity is confirmed"
        ]

    independent_underlying = phys.get("status") == "verified"
    checklist = [
        ("Token/asset identity independently confirmed", token_ok),
        (
            "Relevant contracts confirmed",
            token_ok or underlying_verifiable or economic_verifiable,
        ),
        ("Required APIs reachable", any(e.get("ok") for e in evidence)),
        ("Required blockchain calls reproducible", token_ok or economic_verifiable),
        ("Claim sources documented", True),
        (
            "Independent evidence identified where available",
            independent_market or token_ok or independent_underlying,
        ),
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
        "economic_bridge_verifiable": economic_bridge_verifiable,
        "independent_market": independent_market,
        "independent_underlying": independent_underlying,
        "identity_evidence": identity_evidence,
        "identity_confidence": identity_confidence,
        "evidence_graph": graph,
        "payout_records_count": len(payout_records),
        "payout_verified_count": int(payout_verification.get("verified_count") or 0),
        "distribution_addresses": distribution_addrs,
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
        id_ev = token_probe.get("identity_evidence") or {}
        identity_token = f"""| Field | Observed |
| --- | --- |
| Chain | {token_probe.get("chain")} |
| Token contract | `{token_probe["address"]}` |
| `name()` | `{token_probe.get("name")}` |
| `symbol()` | `{token_probe.get("symbol")}` |
| `decimals()` | `{token_probe.get("decimals")}` |
| `totalSupply()` | {supply_s} token units (raw `{token_probe.get("totalSupply_raw")}`) |
| RPC used | `{token_probe.get("rpc")}` |
| Address source | {token_probe.get("address_source_url") or "—"} |
| Issuer-published address? | {"YES" if token_probe.get("issuer_published") else "NO"} |
| Identity confidence | `{token_probe.get("identity_confidence") or "n/a"}` |
| Evidence: eth_call | {"YES" if id_ev.get("eth_call_verified") else "NO"} |
| Evidence: metadata match | {"YES" if id_ev.get("metadata_match") else "NO"} |
| Evidence: market corroboration | {"YES" if id_ev.get("market_corroboration") else "NO"} |

**Layer separation:** this table establishes **TOKEN IDENTITY** only. It does
**not** verify physical-asset backing, ownership/registry rights, or payouts."""
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
    eg = assessment.get("evidence_graph") or {}
    phys = eg.get("physical_asset") or {}
    right = eg.get("economic_right") or {}
    revenue = eg.get("revenue_mechanism") or {}
    payout = eg.get("payout_mechanism") or {}
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
    confirmed_lines.append(
        f"- Physical asset layer: `{phys.get('status')}`"
        + (f" (`{phys.get('named_asset')}`)" if phys.get("named_asset") else "")
        + f"; economic right: `{right.get('status')}`"
        + (f" (`{right.get('right_type')}`)" if right.get("right_type") else "")
        + f"; revenue: `{revenue.get('status')}`"
        + f"; payout: `{payout.get('status')}`"
        + (
            f" ({payout.get('onchain_verified_sample') or 0} on-chain tx samples; "
            f"{assessment.get('payout_records_count') or 0} metadata records)"
            if payout
            else ""
        )
        + "."
    )
    if not assessment["underlying_verifiable"]:
        confirmed_lines.append(
            "- **No** independently corroborated physical-asset identity "
            "(filings/registries) was confirmed."
        )
    if not assessment["economic_verifiable"]:
        confirmed_lines.append(
            "- **No** machine-queryable payout/distribution surface with "
            "on-chain confirmation was established."
        )

    docs_claim_lines = []
    if claim_bits.get("physical_asset"):
        docs_claim_lines.append(f"- Physical asset cue: `{claim_bits['physical_asset']}`")
    if claim_bits.get("economic_right"):
        docs_claim_lines.append(f"- Economic right language: {claim_bits['economic_right']}")
    if claim_bits.get("ownership"):
        docs_claim_lines.append(f"- {claim_bits['ownership']}")
    if claim_bits.get("royalty"):
        docs_claim_lines.append(f"- {claim_bits['royalty']}")
    if claim_bits.get("payout"):
        docs_claim_lines.append(f"- {claim_bits['payout']}")
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
    for e in reachable:
        url = e.get("url") or ""
        if "metadata.json" in url and "payoutData" in (e.get("raw_text") or ""):
            input_rows.append(
                f"| Payout metadata JSON | issuer HTTP | `{url}` | "
                f"GET JSON payoutData[] | historical distributions + txHashes | "
                f"monthly / on snapshot | **required** — payout verification |"
            )
        if url.rstrip("/").endswith("constants.ts") or "/constants.ts" in url:
            input_rows.append(
                f"| Distribution plumbing constants | issuer source | `{url}` | "
                f"HTTP GET + parse Safe/USDC/orderbook addresses | payout route context | "
                f"on research refresh | **optional** — payout plumbing |"
            )
    for d in (assessment.get("distribution_addresses") or [])[:4]:
        input_rows.append(
            f"| {d.get('role') or 'distribution'} address | blockchain | "
            f"`{d.get('address')}` | eth_call / eth_getTransaction* | "
            f"payout plumbing state | on snapshot | **optional** — payout context |"
        )
    for e in reachable[:6]:
        role = "**optional** — self-reported claims provenance"
        if "gitbook" in e["url"] or "docs" in e["url"]:
            role = "**required** for claims[] sourcing (self-reported)"
        if is_independent_host(host_of(e["url"])):
            role = "**required** — independent physical/economic corroboration"
        input_rows.append(
            f"| {'Independent filing' if is_independent_host(host_of(e['url'])) else 'Official page text'} | "
            f"{'regulatory/independent' if is_independent_host(host_of(e['url'])) else 'official documentation'} | "
            f"`{e['url']}` | "
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

    id_ev = assessment.get("identity_evidence") or {}

    def _yaml_evidence(layer: dict[str, Any], indent: str = "      ") -> str:
        lines: list[str] = []
        for ev in (layer.get("evidence") or [])[:5]:
            proves = str(ev.get("proves") or "").replace('"', "'")
            src = str(ev.get("source") or "").replace('"', "'")
            lines.append(f'{indent}- source: "{src}"')
            lines.append(f'{indent}  tier: {ev.get("tier") or "n/a"}')
            lines.append(f'{indent}  proves: "{proves}"')
            lines.append(
                f'{indent}  reachable: {str(bool(ev.get("reachable"))).lower()}'
            )
            lines.append(
                f'{indent}  independently_verifiable: '
                f'{str(bool(ev.get("independently_verifiable"))).lower()}'
            )
        return "\n".join(lines) if lines else f"{indent}[]"

    mq_lines = []
    for mq in (eg.get("machine_queryable_sources") or [])[:10]:
        mq_lines.append(
            f'    - source: "{str(mq.get("source") or "").replace(chr(34), chr(39))}"'
        )
        mq_lines.append(
            f'      what_it_proves: "{str(mq.get("what_it_proves") or "").replace(chr(34), chr(39))}"'
        )
        mq_lines.append(f'      reachable: {str(bool(mq.get("reachable"))).lower()}')
        mq_lines.append(
            f'      independently_verifiable: '
            f'{str(bool(mq.get("independently_verifiable"))).lower()}'
        )
    yaml_block = f"""```yaml
adapter_readiness:
  status: {assessment["status"]}
  researched_at: "{assessment["researched_at"]}"

  # Layered evidence graph — do not collapse into one confidence value.
  token_identity:
    status: {((eg.get("token_identity") or {}).get("status") or ("verified" if assessment["token_ok"] else "unverified"))}
    confidence: {assessment.get("identity_confidence") or "none"}
    issuer_published_address: {str(bool(id_ev.get("issuer_published_address"))).lower()}
    chain_established: {str(bool(id_ev.get("chain_established"))).lower()}
    eth_call_verified: {str(bool(id_ev.get("eth_call_verified"))).lower()}
    metadata_match: {str(bool(id_ev.get("metadata_match"))).lower()}
    market_corroboration: {str(bool(id_ev.get("market_corroboration"))).lower()}
    note: "Token identity ≠ asset backing ≠ economic/payout verification"

  physical_asset:
    status: {phys.get("status") or "unverified"}
    confidence: {phys.get("confidence") or "none"}
    named_asset: "{phys.get("named_asset") or ""}"
    blocker: "{(phys.get("blocker") or "")}"
    evidence:
{_yaml_evidence(phys)}

  economic_right:
    status: {right.get("status") or "unverified"}
    confidence: {right.get("confidence") or "none"}
    right_type: "{right.get("right_type") or ""}"
    blocker: "{(right.get("blocker") or "")}"
    evidence:
{_yaml_evidence(right)}

  revenue_mechanism:
    status: {revenue.get("status") or "unverified"}
    confidence: {revenue.get("confidence") or "none"}
    machine_queryable: {str(bool(revenue.get("machine_queryable"))).lower()}
    blocker: "{(revenue.get("blocker") or "")}"
    evidence:
{_yaml_evidence(revenue)}

  payout_mechanism:
    status: {payout.get("status") or "unverified"}
    confidence: {payout.get("confidence") or "none"}
    machine_queryable: {str(bool(payout.get("machine_queryable"))).lower()}
    payout_record_count: {payout.get("payout_record_count") or 0}
    onchain_verified_sample: {payout.get("onchain_verified_sample") or 0}
    currency_hint: "{payout.get("currency_hint") or ""}"
    frequency_hint: "{payout.get("frequency_hint") or ""}"
    blocker: "{(payout.get("blocker") or "")}"
    evidence:
{_yaml_evidence(payout)}

  machine_queryable_sources:
{chr(10).join(mq_lines) if mq_lines else "    []"}

  # Back-compat summary flags
  token_verification:
    available: {str(assessment["token_ok"]).lower()}
  underlying_asset_verification:
    available: {str(assessment["underlying_verifiable"]).lower()}
  economic_mechanism_verification:
    available: {str(assessment["economic_verifiable"]).lower()}
  market_data:
    available: {str(assessment["market_ok"]).lower()}
  independent_sources:
    available: {str(bool(assessment.get("independent_underlying") or assessment["independent_market"])).lower()}
    note: "Independent market/indexer data ≠ independent underlying-asset verification"

  critical_blockers:
{chr(10).join(f'    - "{b}"' for b in (assessment["blockers"] or ["None recorded"]))}

  recommended_adapter_scope:
{chr(10).join(f'    - "{s}"' for s in assessment["recommended_scope"])}

  prohibited_outputs:
{chr(10).join(f'    - "{s}"' for s in (assessment["prohibited"] or ["None"]))}
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
{chr(10).join(
    f"| {d.get('role') or 'distribution'} | `{d.get('address')}` | issuer-published constants/docs | Payout plumbing context |"
    for d in (assessment.get("distribution_addresses") or [])[:8]
) or "| Distribution / Safe / vault | **Not confirmed** | Docs may describe; address not verified | Required for realized yield — blocked unless published |"}

**Payout observability:** {"Verified — issuer payout metadata + on-chain txHash sample(s)" if assessment["economic_verifiable"] else "No verified payout/harvest event ABI + confirmed historical txs for this candidate’s underlying economics in this research pass."}

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
| Underlying asset independently verifiable | {"High" if assessment["underlying_verifiable"] else "Low"} | Independent filings/registries naming the asset |
| Economic right established | {"High" if right.get("status") == "verified" else ("Medium" if right.get("status") == "partially-verified" else "Low")} | Right-type evidence (filings/docs) |
| Economic mechanism / realized yield observable | {"High" if assessment["economic_verifiable"] else "Low"} | Payout metadata + on-chain tx verification |
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

### Evidence graph (layered)

| Layer | Status | Confidence | Notes |
| --- | --- | --- | --- |
| token_identity | {(eg.get("token_identity") or {}).get("status") or "unverified"} | {assessment.get("identity_confidence") or "none"} | eth_call + issuer address provenance |
| physical_asset | {phys.get("status") or "unverified"} | {phys.get("confidence") or "none"} | {phys.get("named_asset") or phys.get("blocker") or "—"} |
| economic_right | {right.get("status") or "unverified"} | {right.get("confidence") or "none"} | {right.get("right_type") or right.get("blocker") or "—"} |
| revenue_mechanism | {revenue.get("status") or "unverified"} | {revenue.get("confidence") or "none"} | {revenue.get("blocker") or ("machine_queryable=" + str(bool(revenue.get("machine_queryable"))).lower())} |
| payout_mechanism | {payout.get("status") or "unverified"} | {payout.get("confidence") or "none"} | records={payout.get("payout_record_count") or 0}; onchain_sample={payout.get("onchain_verified_sample") or 0}; currency={payout.get("currency_hint") or "n/a"} |

**Reminder:** Independent market/indexer sources ≠ independent underlying-asset
verification. Every link in TOKEN→ASSET→RIGHT→REVENUE→PAYOUT needs its own evidence.

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
                        "reward",
                        "payout",
                    )
                ):
                    follow.append(m)
    for u in follow[:12]:
        if u not in seen_urls:
            seen_urls.add(u)
            evidence.append(fetch_url(u))

    # Pass 1: discover economic GitHub surfaces (rewards/payout/claims repos).
    for u in discover_github_economic_urls(evidence, limit=20):
        if u not in seen_urls:
            seen_urls.add(u)
            evidence.append(fetch_url(u))
    # Pass 2: tree JSON now available → expand constants/metadata.json URLs.
    for u in discover_github_economic_urls(evidence, limit=28):
        if u not in seen_urls:
            seen_urls.add(u)
            evidence.append(fetch_url(u, max_bytes=400_000))

    texts = [e.get("raw_text") or "" for e in evidence if e.get("ok")]
    blob = " ".join(texts)

    # Dex search terms (supporting corroboration only — not primary identity).
    notes_l = (candidate.get("notes") or "").lower()
    product_bits = [
        b
        for b in (
            candidate.get("display_name") or "",
            candidate.get("slug") or "",
            *re.findall(
                r"\b(agri|farm|farmland|mining|royalty|nsr|rwa|tokenized|wressle|oil)\b",
                notes_l,
                flags=re.I,
            ),
        )
        if b
    ]
    dex_hits: list[dict[str, Any]] = []
    for term in candidate_search_terms(candidate):
        # Prefer shorter search terms (full display names with punctuation
        # are poor Dex queries).
        if len(term) > 48:
            continue
        dex_hits.extend(dexscreener_token_search(term, prefer_name_bits=product_bits))
        if dex_hits:
            break

    # TOKEN IDENTITY evidence chain (issuer addr → chain → eth_call → match).
    # Does NOT imply asset backing or payout verification.
    token_probe = resolve_token_identity(
        candidate=candidate,
        evidence=evidence,
        blob=blob,
        dex_hits=dex_hits,
    )
    token_addr = (
        token_probe.get("address")
        if token_probe and token_probe.get("ok")
        else None
    )

    dex_pairs = dexscreener_by_token(token_addr) if token_addr else []
    if token_probe and token_probe.get("ok"):
        ev = token_probe.setdefault(
            "identity_evidence",
            {
                "issuer_published_address": bool(token_probe.get("issuer_published")),
                "chain_established": True,
                "eth_call_verified": True,
                "metadata_match": True,
                "market_corroboration": False,
            },
        )
        ev["market_corroboration"] = bool(dex_pairs)
        if dex_pairs and token_probe.get("identity_confidence") == "medium":
            # Market corroboration can raise medium→high when eth_call matched.
            if ev.get("eth_call_verified") and ev.get("metadata_match"):
                token_probe["identity_confidence"] = "high"

    cg = coingecko_search(candidate_search_terms(candidate)[0])
    claim_bits = extract_claim_snippets(blob)

    # ASSET / ECONOMIC / PAYOUT evidence (generic — not Albion-specific).
    payout_records = extract_payout_records(evidence)
    # Prefer records matching the probed token when available.
    if token_addr and payout_records:
        matched = [
            r
            for r in payout_records
            if (r.get("token_address") or "").lower() == token_addr.lower()
        ]
        if matched:
            payout_records = matched + [
                r
                for r in payout_records
                if (r.get("token_address") or "").lower() != token_addr.lower()
            ]
    chain_for_payout = (
        (token_probe or {}).get("chain")
        if token_probe and token_probe.get("ok")
        else "ethereum"
    )
    payout_verification = verify_payout_transactions(
        payout_records, chain=chain_for_payout or "ethereum"
    )
    distribution_addrs = extract_distribution_addresses(evidence, blob)
    evidence_graph = build_evidence_graph(
        candidate=candidate,
        evidence=evidence,
        token_probe=token_probe,
        blob=blob,
        claim_bits=claim_bits,
        payout_records=payout_records,
        payout_verification=payout_verification,
        distribution_addrs=distribution_addrs,
    )

    assessment = build_assessment(
        candidate=candidate,
        evidence=evidence,
        token_probe=token_probe,  # may be ok:false with collision-risk note
        dex_pairs=dex_pairs,
        coingecko=cg,
        claim_bits=claim_bits,
        blob=blob,
        evidence_graph=evidence_graph,
        payout_records=payout_records,
        payout_verification=payout_verification,
        distribution_addrs=distribution_addrs,
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
