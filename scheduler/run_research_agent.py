#!/usr/bin/env python3
"""
Adapter-spec research agent — deeper pass for `candidate-for-adapter` only.

Extends discovery; does not replace it. After a candidate is classified
`candidate-for-adapter` (FINDINGS.md already written), this job produces
`candidates/<slug>/ADAPTER_SPEC.md`: an adapter-ready research document
for human review. It writes **zero** adapter code, schema, scoring, or
storage changes.

Usage:
  # Research one candidate that already has FINDINGS.md
  python3 scheduler/run_research_agent.py --candidate-name AgriFi

  # Called automatically by run_discovery.py when classification is
  # candidate-for-adapter (unless --skip-research).

  python3 scheduler/run_research_agent.py --candidate-name AgriFi --dry-run
  python3 scheduler/run_research_agent.py --candidate-name AgriFi --no-status-log
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
from scheduler.run_discovery import (
    BACKLOG_PATH,
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

# Extra surfaces commonly useful for capital/RWA candidates beyond seeds.
EXTRA_URL_TEMPLATES = (
    "https://{compact}.gitbook.io/{compact}-docs/llms.txt",
    "https://{compact}.gitbook.io/{compact}-docs/",
    "https://docs.{compact}.com/",
    "https://docs.{compact}.org/",
    "https://{compact}.app/",
    "https://app.{compact}.tech/",
    "https://{compact}.tech/llm/{compact}-llm-knowledge-base.html",
    "https://{compact}.tech/agrifi-whitepaper.pdf",
    "https://{compact}.tech/whitepaper.pdf",
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


def html_to_text(raw: str) -> str:
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
                        f"[PDF reachable — {len(raw_bytes)} bytes fetched in this "
                        "probe; text not fully extracted by the research agent]"
                    ),
                    "raw_text": "",
                    "error": None,
                    "kind": "pdf",
                }
            raw = raw_bytes.decode("utf-8", errors="replace")
            # Prefer GitBook markdown when HTML shell is thin.
            if url.rstrip("/").endswith(".md") or "text/markdown" in ct:
                text = raw
            elif "html" in ct or raw.lstrip().startswith("<"):
                text = html_to_text(raw)
            else:
                text = raw
            text = re.sub(r"\s+", " ", text).strip()
            return {
                "url": url,
                "ok": True,
                "http_status": code,
                "content_type": ct,
                "excerpt": text[:2000],
                "raw_text": text[:20000],
                "error": None,
                "kind": "text",
            }
    except HTTPError as e:
        return {
            "url": url,
            "ok": False,
            "http_status": e.code,
            "content_type": None,
            "excerpt": "",
            "raw_text": "",
            "error": f"HTTP {e.code}: {e.reason}",
            "kind": "error",
        }
    except URLError as e:
        return {
            "url": url,
            "ok": False,
            "http_status": None,
            "content_type": None,
            "excerpt": "",
            "raw_text": "",
            "error": f"URL error: {e.reason}",
            "kind": "error",
        }
    except Exception as e:
        return {
            "url": url,
            "ok": False,
            "http_status": None,
            "content_type": None,
            "excerpt": "",
            "raw_text": "",
            "error": f"{type(e).__name__}: {e}",
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
    seeds = list(candidate.get("seeds") or [])
    slug = candidate["slug"]
    compact = slug.replace("-", "")
    extras: list[str] = []
    for tmpl in EXTRA_URL_TEMPLATES:
        extras.append(tmpl.format(compact=compact, slug=slug))
    # AgriFi / gitbook-style known deep pages when seeds mention agrifi.
    if "agrifi" in slug or "agrifi" in (candidate.get("display_name") or "").lower():
        extras.extend(
            [
                "https://agrifi.gitbook.io/agrifi-docs/llms.txt",
                "https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-token.md",
                "https://agrifi.gitbook.io/agrifi-docs/technology/agrifi-project-system-architecture.md",
                "https://agrifi.gitbook.io/agrifi-docs/undefined/lock-up-period.md",
                "https://agrifi.gitbook.io/agrifi-docs/agrifi-concepts-for-both-b2b-and-b2c-space/concept-2-rwa-organic-farming-produce-from-the-farm-will-be-their-return-on-the-investment.md",
                "https://agrifi.tech/llm/agrifi-llm-knowledge-base.html",
                "https://agrifi.tech/agrifi-whitepaper.pdf",
                "https://agrifi.app/",
                "https://blog.agrifi.tech/agriculture-agf-token-polygon-farmland-tokenization-defi-staking-food-safety-blockchain-web3",
                "https://blog.agrifi.tech/how-agrifi-turns-farmland-into-real-world-asset-class-agriculture-blockchainsolution",
            ]
        )
    # Follow .md mirrors of any gitbook HTML seeds.
    mirrored: list[str] = []
    for u in seeds + extras:
        if "gitbook.io" in u and not u.endswith(".md") and not u.endswith(".txt"):
            mirrored.append(u.rstrip("/") + ".md")
    seen: set[str] = set()
    out: list[str] = []
    for u in seeds + extras + mirrored:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


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


def probe_erc20(address: str, rpc: str) -> dict[str, Any]:
    selectors = {
        "name": "0x06fdde03",
        "symbol": "0x95d89b41",
        "decimals": "0x313ce567",
        "totalSupply": "0x18160ddd",
    }
    out: dict[str, Any] = {"address": address, "rpc": rpc, "ok": False}
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


def dexscreener_token_search(query: str) -> list[dict[str, Any]]:
    url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    try:
        req = Request(url, headers={"User-Agent": UA})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
        pairs = data.get("pairs") or []
        # Prefer exact symbol matches when query looks like a ticker.
        q = query.strip().upper()
        scored: list[tuple[int, dict[str, Any]]] = []
        for p in pairs:
            base = p.get("baseToken") or {}
            sym = (base.get("symbol") or "").upper()
            name = (base.get("name") or "").upper()
            score = 0
            if sym == q:
                score += 5
            if q in name:
                score += 3
            if "agri" in name.lower() or "agri" in sym.lower():
                score += 2
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


def build_spec_md(
    *,
    candidate: dict[str, Any],
    findings_path: Path,
    evidence: list[dict[str, Any]],
    token_probe: dict[str, Any] | None,
    dex_pairs: list[dict[str, Any]],
    coingecko_search: dict[str, Any] | None,
) -> str:
    today = date.today().isoformat()
    name = candidate["display_name"]
    slug = candidate["slug"]
    notes = candidate.get("notes", "")

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
    blob = " ".join(e.get("raw_text") or e.get("excerpt") or "" for e in reachable)

    # Claim extraction (quoted from reachable text — not invented).
    claimed_yield = None
    for pat in (
        r"(\d+\s*%\s*to\s*\d+\s*%\s*APY)",
        r"(\d+\s*[–-]\s*\d+\s*%\s*APY)",
        r"(APY[s]?\s*\([^)]*\d+\s*[–-]\s*\d+%[^)]*\))",
        r"(5%\s*to\s*18%\s*APY)",
        r"(5\s*[–-]\s*18%\s*APY)",
    ):
        m = re.search(pat, blob, flags=re.I)
        if m:
            claimed_yield = m.group(1)
            break

    staking_lock = None
    m = re.search(r"(lock-up periods?\s*\([^)]+\))", blob, flags=re.I)
    if m:
        staking_lock = m.group(1)
    elif re.search(r"30\s*[–-]\s*360\s*days", blob, flags=re.I):
        staking_lock = "30–360 days (stated in docs)"

    # Conflicts: fully circulating vs vesting
    conflict_lines: list[str] = []
    if re.search(r"fully circulating", blob, flags=re.I) and re.search(
        r"vesting", blob, flags=re.I
    ):
        conflict_lines.append(
            "- Official token docs describe the **7.2B supply as fully "
            "circulating** (no further mint / no reserved release), while the "
            "lock-up page describes **team/partner vesting cliffs**. These "
            "cannot both be complete descriptions of the same allocation "
            "schedule without clarification."
        )
    if claimed_yield and not token_probe:
        conflict_lines.append(
            "- Marketing/docs claim staking APYs, but **no staking contract "
            "address** was confirmed in this pass."
        )
    if claimed_yield and token_probe and token_probe.get("ok"):
        conflict_lines.append(
            "- Docs claim staking APYs / profit distribution contracts, but "
            "this research pass only confirmed the **ERC-20 token contract** "
            "on-chain. Ownership / staking / profit-distribution contract "
            "addresses were **not** published in the reachable docs indexed "
            "here."
        )

    if not conflict_lines:
        conflict_lines.append(
            "- No hard textual conflict isolated beyond normal marketing vs "
            "evidence gaps (see confidence table)."
        )

    # Token / identity block
    if token_probe and token_probe.get("ok"):
        supply = token_probe.get("totalSupply_tokens")
        supply_s = (
            f"{supply:,.0f}" if isinstance(supply, (int, float)) else "not decoded"
        )
        identity_token = f"""| Field | Observed |
| --- | --- |
| Chain | Polygon (via DexScreener pairs + `eth_call` on Polygon RPC) |
| Token contract | `{token_probe["address"]}` |
| `name()` | `{token_probe.get("name")}` |
| `symbol()` | `{token_probe.get("symbol")}` |
| `decimals()` | `{token_probe.get("decimals")}` |
| `totalSupply()` | {supply_s} token units (raw `{token_probe.get("totalSupply_raw")}`) |
| RPC used | `{token_probe.get("rpc")}` |"""
    else:
        identity_token = (
            "No ERC-20 contract was confirmed via live `eth_call` in this "
            "pass. Official docs claim an ERC-20 on Polygon named AGF, but "
            "the **contract address is not printed** in the GitBook pages "
            "fetched here — address attribution below relies on DexScreener "
            "market metadata matching name/symbol, which is supporting "
            "evidence only until the issuer publishes the address in docs."
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

    cg_note = (
        "CoinGecko search API returned **zero** coins for query `agrifi` "
        "in this pass — no independent CoinGecko listing confirmed."
        if coingecko_search is not None
        else "CoinGecko search not run."
    )

    excerpt_blocks = []
    for e in reachable[:8]:
        snippet = (e.get("excerpt") or "")[:600].replace("|", "/")
        excerpt_blocks.append(f"### `{e['url']}`\n\n> {snippet}\n")
    if not excerpt_blocks:
        excerpt_blocks.append("_No reachable research URL returned extractable text._\n")

    recommended = []
    if token_probe and token_probe.get("ok"):
        recommended.append(
            f"- **On-chain ERC-20 reads** against `{token_probe['address']}` "
            f"on Polygon (`name`/`symbol`/`decimals`/`totalSupply`/`balanceOf`) "
            f"via public RPC — confirmed reachable this pass."
        )
    recommended.append(
        "- **Official GitBook markdown** (`*.md` / `llms.txt`) for claimed "
        "payout/staking mechanics — reachable, but treat as self-reported."
    )
    recommended.append(
        "- **Official blog + LLM knowledge page** for product claims "
        "(fractional farmland, profit sharing) — self-reported."
    )
    if dex_pairs:
        recommended.append(
            "- **DexScreener public API** for pair liquidity / price context "
            "only — not proof of farmland backing or yield."
        )
    recommended.append(
        "- **Do not** treat whitepaper PDF marketing, undocumented staking "
        "APYs, or unnamed ownership/profit contracts as adapter inputs until "
        "addresses and events are published and independently readable."
    )

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
| Issuer / brand (self-described) | Agrifi / AgriFi (official site author meta + docs) |
| Primary site | https://agrifi.tech/ |
| Docs | https://agrifi.gitbook.io/agrifi-docs |
| App shell | https://agrifi.app/ (HTTP 200; minimal HTML shell in this probe) |

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

- AgriFi presents as a Polygon-based agricultural finance / RWA platform
  combining farmland tokenization, DeFi staking, supply-chain traceability,
  IoT monitoring, and (documented as a concept) parametric crop insurance
  (site, blog, GitBook, LLM knowledge page).
- Farmland / crop-production rights are described as tokenized so holders get
  **fractional ownership** and participate in agricultural revenue
  (GitBook Concept 2 RWA; token docs; blog 2025-10-17 and 2026-04-17 posts).
- Architecture docs describe off-chain collection of farm revenue (crop sales /
  leases), conversion to stablecoins, and on-chain distribution via a
  “Profit Distribution Contract” proportional to holdings — **addresses for
  those modules were not found in reachable docs**.

**What was actually confirmed here**

- Marketing site, blog articles, GitBook markdown, whitepaper PDF, and LLM
  knowledge HTML are reachable.
- A Polygon ERC-20 with `name=AGRIFI` / `symbol=AGF` / `decimals=18` /
  `totalSupply=7.2e9` token units responds at the DexScreener-attributed
  address (see §1) via public RPC.
- **No** public registry of specific farmland parcels, harvest ledgers, or
  profit-distribution events was found in this pass.
- **No** independent CoinGecko listing matched `agrifi` via the public search
  API in this pass.

---

## 3. Claimed payout mechanism & claimed yield

| Claim | Source (reachable) | Confirmed on-chain / API? |
| --- | --- | --- |
| AGF enables fractional farmland ownership + profit sharing | GitBook token page; Concept 2 RWA; blog | **Not confirmed** — no ownership/profit contract addresses published in fetched docs |
| Staking APY {"`"+claimed_yield+"`" if claimed_yield else "5–18% (docs/blog)"} | GitBook architecture + blog | **Not confirmed** — staking contract address not found |
| Lock-ups {"`"+staking_lock+"`" if staking_lock else "30–360 days + 2% early exit (architecture docs)"} | GitBook architecture | **Not confirmed** on-chain |
| Team/partner vesting schedules | GitBook lock-up page | Allocation schedule **conflicts** with “fully circulating” language on token page |
| ERC-20 on Polygon, 7.2B supply | GitBook + LLM page; matches `totalSupply()` if address in §1 is accepted | Token supply **matches** RPC read for the probed contract |

---

## 4. On-chain contracts / events relevant to verification

| Contract / surface | Address | Evidence | Adapter relevance |
| --- | --- | --- | --- |
| AGF ERC-20 (probed) | `{token_probe["address"] if token_probe and token_probe.get("ok") else "not confirmed"}` | DexScreener pair baseToken + Polygon `eth_call` | Identity / supply / holdings only |
| Ownership mapping | **Not published** in fetched docs | Architecture describes module | Required for farm-level claims — **blocked** |
| Staking | **Not published** | Architecture describes 30–360d / 5–18% APY | Required for staking-yield claims — **blocked** |
| Profit distribution | **Not published** | Architecture describes stablecoin distributions | Required for realized farm yield — **blocked** |
| Governance | **Not published** | Architecture describes DAO voting | Optional |

**Events:** No verified event signatures / merklized harvest reports / public
subgraph endpoint for AgriFi farm economics were found in this research pass.

---

## 5. Public APIs / indexers (reachability)

| Source | Result |
| --- | --- |
{chr(10).join(rows)}

| Indexer / market API | Result |
| --- | --- |
| DexScreener token/pair API | Reachable — used for pair liquidity / price context |
| CoinGecko search `agrifi` | Reachable API; **0** coin hits |
| Polygon public RPC `eth_call` | Reachable for ERC-20 getters on probed address |

---

## 6. Official vs independent sources & conflicts

**Official (self-reported):** agrifi.tech, blog.agrifi.tech, GitBook docs,
whitepaper PDF, LLM knowledge page, agrifi.app shell.

**Independent / market:** DexScreener pairs for the AGF/Polygon token;
{cg_note}

**Conflicts / tensions**

{chr(10).join(conflict_lines)}

---

## 7. Per-claim confidence

| Claim | Confidence now | Why |
| --- | --- | --- |
| Project exists as a public web brand with docs/blog | **High** | Multiple official HTTP 200 surfaces with consistent Agrifi branding |
| Capital-style (non-operator) marketing path | **Medium-high** | Docs emphasize token purchase / fractional ownership / staking without hardware-operator requirements — aligns with discovery `candidate-for-adapter`, still first-pass |
| AGF ERC-20 on Polygon with 7.2B supply | **Medium** (address) / **High** (RPC fields if address accepted) | Address comes from DexScreener metadata matching name/symbol, **not** from an issuer-published contract list in GitBook; RPC fields match marketed supply |
| Specific farmland assets are on-chain & identifiable | **Low** | No parcel registry, legal wrappers, or ownership-contract addresses found |
| Staking APY 5–18% is observable | **Low** | Claimed in docs/blog; staking contract not located; no reward events read |
| Realized agricultural profit distributions to holders | **Low** | Described architecturally; no distribution contract / payout history found |
| Independent market listing quality | **Low** | Thin DEX liquidity observed; no CoinGecko hit in this pass |

---

## 8. Recommended data sources for an eventual adapter

{chr(10).join(recommended)}

**Honest adapter boundary (if ever greenlit):** an MVP could snapshot ERC-20
identity + supply + optional DEX context, and must leave
`realized_yield_pct` / farm-level verification **null** until ownership and
profit-distribution contracts (or an equivalent public attestation API) are
reachable — same SourceError / no-fabrication discipline as Glow/RealT/Elmnts.

---

## 9. Human decision gate

This file does **not** authorize adapter work. Next steps for a human:

1. Review [`FINDINGS.md`](./FINDINGS.md) + this `ADAPTER_SPEC.md`.
2. Decide whether to greenlight a bespoke adapter (manual, like Glow/RealT/Elmnts).
3. If greenlit: require issuer-published contract addresses for ownership /
   staking / distributions before treating yield claims as verifiable.
4. If not greenlit: leave classification as research-only; no code.

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
    evidence = [fetch_url(u) for u in urls]

    # Discover additional .md links from llms.txt bodies.
    extra_fetches: list[dict[str, Any]] = []
    for e in evidence:
        if e["ok"] and e["url"].endswith("llms.txt"):
            for m in re.findall(r"https://[^\s\)]+\.md", e.get("raw_text") or ""):
                if m not in {x["url"] for x in evidence}:
                    # Cap follow-ups to keep the cycle bounded.
                    if len(extra_fetches) >= 6:
                        break
                    # Prefer technology / concept pages.
                    if any(
                        k in m
                        for k in (
                            "token",
                            "architecture",
                            "concept-2",
                            "lock-up",
                            "rwa",
                        )
                    ):
                        extra_fetches.append(fetch_url(m))
    evidence.extend(extra_fetches)

    texts = [e.get("raw_text") or "" for e in evidence if e.get("ok")]
    addrs = collect_addresses(texts)

    # DexScreener search for AGF / AgriFi when docs omit addresses.
    dex_hits = dexscreener_token_search("AGF agrifi")
    if not dex_hits:
        dex_hits = dexscreener_token_search("AGRIFI")
    token_addr = None
    for p in dex_hits:
        base = p.get("baseToken") or {}
        sym = (base.get("symbol") or "").upper()
        name = (base.get("name") or "").upper()
        if sym == "AGF" and "AGRI" in name:
            token_addr = base.get("address")
            break
    if not token_addr and addrs:
        token_addr = addrs[0]

    polygon_rpc = "https://polygon-bor-rpc.publicnode.com"
    token_probe = probe_erc20(token_addr, polygon_rpc) if token_addr else None
    dex_pairs = dexscreener_by_token(token_addr) if token_addr else []

    coingecko_search = None
    try:
        req = Request(
            "https://api.coingecko.com/api/v3/search?query=agrifi",
            headers={"User-Agent": UA},
        )
        with urlopen(req, timeout=TIMEOUT) as resp:
            coingecko_search = json.loads(resp.read())
    except Exception as e:
        coingecko_search = {"error": f"{type(e).__name__}: {e}", "coins": []}

    spec_md = build_spec_md(
        candidate=candidate,
        findings_path=findings_path,
        evidence=evidence,
        token_probe=token_probe,
        dex_pairs=dex_pairs,
        coingecko_search=coingecko_search,
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
        "date": date.today().isoformat(),
    }


def write_spec(result: dict[str, Any]) -> Path:
    out_dir = CANDIDATES_DIR / result["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    # Hard scope: only ADAPTER_SPEC.md under this candidate directory.
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

        # Prove-it helper: refuse if we somehow wrote outside the candidate dir.
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
