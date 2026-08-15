#!/usr/bin/env python3
"""
Public ASGI app: REST + Streamable HTTP MCP + key issue + owner dashboard.

Local stdio MCP remains in api/mcp_server.py. This module is what Render
(and local HTTPS-fronted tests) run — binds 0.0.0.0:$PORT.

Scores still come only from scoring.engine via api.queries.
"""

from __future__ import annotations

import html
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from api import keys as keys_mod
from api import queries
from api import rate_limit as rate_limit_mod
from api import request_log
from api.mcp_server import mcp as mcp_server

DATA_DIR = Path(os.environ.get("DATA_DIR", str(ROOT / "data")))
DASHBOARD_SECRET = os.environ.get("DASHBOARD_SECRET", "")
RATE_LIMIT = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))


def _allowed_hosts() -> list[str]:
    """Host allowlist for MCP DNS-rebinding protection.

    Always merges Render's injected hostname when present so production MCP
    works without a fragile manual ALLOWED_HOSTS edit.
    """
    hosts: list[str] = []
    raw = os.environ.get("ALLOWED_HOSTS", "").strip()
    if raw:
        hosts.extend(h.strip() for h in raw.split(",") if h.strip())
    else:
        hosts.extend(
            ["localhost", "127.0.0.1", "localhost:*", "127.0.0.1:*"]
        )

    for key in ("RENDER_EXTERNAL_HOSTNAME", "RENDER_EXTERNAL_URL"):
        val = os.environ.get(key, "").strip()
        if not val:
            continue
        if val.startswith("https://"):
            val = val[len("https://") :]
        elif val.startswith("http://"):
            val = val[len("http://") :]
        val = val.split("/")[0].strip()
        if val and val not in hosts:
            hosts.append(val)
            hosts.append(f"{val}:*")

    # Render free default domain + DNS-rebinding port variants
    if os.environ.get("RENDER") or any(h.endswith(".onrender.com") for h in hosts):
        for pattern in ("*.onrender.com", "*.onrender.com:*"):
            if pattern not in hosts:
                hosts.append(pattern)
    return hosts


ALLOWED_HOSTS = _allowed_hosts()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _api_key(request: Request) -> str | None:
    return request.headers.get("x-api-key") or None


def _caller_id(request: Request) -> str:
    key = _api_key(request)
    if key:
        return f"key:{key}"
    return f"ip:{_client_ip(request)}"


class AccessControlMiddleware(BaseHTTPMiddleware):
    """Rate-limit + request log. Never mutates response bodies from queries."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Skip noisy health probes from rate budget? Still log them lightly.
        identity = _caller_id(request)
        allowed, remaining, retry_after = rate_limit_mod.limiter.check(identity)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": (
                        f"Rate limit exceeded for {identity.split(':', 1)[0]} "
                        f"({RATE_LIMIT} requests per 60 seconds). "
                        "Retry after the indicated delay."
                    ),
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(RATE_LIMIT),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Log before handling (including 404s after).
        try:
            qparams = dict(request.query_params)
            request_log.log_request(
                caller=identity,
                method=request.method,
                endpoint=path,
                query_params=qparams,
            )
        except Exception:  # noqa: BLE001 — logging must not break the API
            pass

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


# Build MCP Streamable HTTP sub-app (must happen before lifespan uses session_manager).
# Mounted at /mcp with path="/" so the public MCP URL is https://host/mcp
_mcp_http = mcp_server.streamable_http_app(
    streamable_http_path="/",
    json_response=True,
    stateless_http=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=ALLOWED_HOSTS,
        allowed_origins=["*"],
    ),
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    keys_mod.init_keys_db(DATA_DIR / "keys.sqlite")
    request_log.init_request_log_db(DATA_DIR / "requests.sqlite")
    rate_limit_mod.configure_rate_limit(limit=RATE_LIMIT, window_seconds=60.0)
    async with mcp_server.session_manager.run():
        yield


app = FastAPI(
    title="Scored assets (public)",
    description=(
        "Read-only scored snapshots via scoring.engine. "
        "Descriptive and comparative only — not investment advice. "
        "HTTPS production hosting; Streamable HTTP MCP at /mcp."
    ),
    version="1.1.0",
    lifespan=lifespan,
)
app.add_middleware(AccessControlMiddleware)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "scope": "public"}


@app.post("/v1/keys")
def create_key() -> dict[str, str]:
    """Issue a free API key immediately — no approval, no paywall."""
    return keys_mod.issue_key()


@app.get("/v1/assets")
def list_assets(
    asset_class: str | None = None,
    min_risk_score: float | None = None,
    min_liquidity_score: float | None = None,
    holder_jurisdiction: str | None = None,
    include_unknown_jurisdiction: bool = True,
    regulatory_wrapper: str | None = None,
    sort_by: Literal[
        "asset_id",
        "risk_score",
        "liquidity_score",
        "yield_score",
        "data_confidence_score",
        "snapshot_age_days",
    ] = "asset_id",
    sort_desc: bool = False,
    latest_only: bool = True,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    return queries.list_scored_assets(
        asset_class=asset_class,
        min_risk_score=min_risk_score,
        min_liquidity_score=min_liquidity_score,
        holder_jurisdiction=holder_jurisdiction,
        include_unknown_jurisdiction=include_unknown_jurisdiction,
        regulatory_wrapper=regulatory_wrapper,
        sort_by=sort_by,
        sort_desc=sort_desc,
        latest_only=latest_only,
        limit=limit,
        offset=offset,
    )


@app.get("/v1/assets/{asset_id}")
def get_asset(
    asset_id: str,
    latest_only: bool = True,
    holder_jurisdiction: str | None = None,
) -> JSONResponse:
    result = queries.get_scored_asset(
        asset_id,
        latest_only=latest_only,
        holder_jurisdiction=holder_jurisdiction,
    )
    if latest_only and result.get("asset") is None:
        raise HTTPException(status_code=404, detail=result.get("error") or "not found")
    return JSONResponse(result)


@app.get("/v1/methodology")
def methodology(
    format: Literal["markdown", "summary"] = "markdown",
) -> dict[str, Any]:
    return queries.get_scoring_methodology(format=format)


def _dashboard_authorized(request: Request) -> bool:
    if not DASHBOARD_SECRET:
        return False
    header = request.headers.get("x-dashboard-secret")
    if header and header == DASHBOARD_SECRET:
        return True
    return request.query_params.get("secret") == DASHBOARD_SECRET


@app.get("/owner/dashboard")
def owner_dashboard(request: Request) -> Response:
    """Minimal owner table — not public without shared secret."""
    if not _dashboard_authorized(request):
        return PlainTextResponse(
            "Forbidden: dashboard requires shared secret "
            "(query ?secret=... or header X-Dashboard-Secret).",
            status_code=403,
        )
    rows = request_log.recent_requests(limit=200)
    body_rows = []
    for r in rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(str(r['ts']))}</td>"
            f"<td>{html.escape(str(r['caller']))}</td>"
            f"<td>{html.escape(str(r['method']))}</td>"
            f"<td>{html.escape(str(r['endpoint']))}</td>"
            f"<td><code>{html.escape(str(r['query_params']))}</code></td>"
            "</tr>"
        )
    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Owner request log</title></head>
<body>
<h1>Owner request log</h1>
<p>Most recent first. Not a public product page.</p>
<table border="1" cellpadding="4" cellspacing="0">
<thead><tr><th>timestamp</th><th>caller</th><th>method</th><th>endpoint</th><th>query params</th></tr></thead>
<tbody>
{''.join(body_rows) if body_rows else '<tr><td colspan="5">(no requests logged yet)</td></tr>'}
</tbody>
</table>
</body></html>
"""
    return HTMLResponse(page)


# Mount Streamable HTTP MCP. Parent lifespan runs session_manager
# (mounted sub-app lifespans do not run — see SDK /run/asgi/).
app.mount("/mcp", _mcp_http)


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("api.public_app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
