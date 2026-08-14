# Deploy decisions

Written **before** deploy config and public-transport code. Criteria first,
choice second — not familiarity first.

## 1. Hosting provider

### Criteria (prototype, low traffic)

| Criterion | Why it matters |
| --- | --- |
| Always-on-capable **or** acceptable cold-start for a demo | Agents must hit a real public URL |
| Free or cheap tier for a low-traffic prototype | No paid infra yet |
| **Free TLS** on the default `*.onrender.com` / equivalent domain | Requirement: HTTPS only in production |
| Simple Python/ASGI deploy (uvicorn, `$PORT`) | Match the FastAPI + Streamable HTTP stack |
| Deployable from this GitHub repo with a config file | Reproducible in `deploy/` |

### Options considered (current public info, 2026)

| Provider | Free / cheap | Free TLS | Always-on free? | Notes |
| --- | --- | --- | --- | --- |
| **Render** | Free web services (750 h/mo); no card required | Yes on `*.onrender.com` | Spins down after ~15 min idle; ~30–60s cold start | Blueprint/`render.yaml`, Python native |
| **Railway** | Trial credit / usage; not a durable free always-on tier | Yes | Not really free ongoing | Fine paid; weaker free prototype story |
| **Fly.io** | Usage-based; card typically required for new accounts | Yes | No meaningful free always-on for new accounts | Dockerfile-first; more ops |

### Choice: **Render (free web service)**

Wins on: free TLS by default, no card for free tier, git/`render.yaml` deploy,
Python web service that binds `$PORT`, documented MCP hosting path. Trade-off
accepted: free instances **sleep after idle** and cold-start; for this
prototype that is acceptable and documented in `deploy/README.md`. Paid
Render (or Fly/Railway) can remove sleep later without changing the app.

SQLite for keys/logs lives on the instance disk (ephemeral on free tier —
resets on redeploy/sleep wipe). Acceptable for a glanceable owner log at
this stage; not a durable audit store.

---

## 2. MCP remote transport

### Spec / SDK (checked against current docs, not memory)

Official MCP Python SDK v2 docs (`py.sdk.modelcontextprotocol.io/run/`):

| Transport | Role |
| --- | --- |
| `stdio` | Local subprocess only — **not** network-reachable |
| **`streamable-http`** | “A real HTTP server listening on a port. **Anything you deploy.**” |
| `sse` | Older HTTP transport; **do not build new servers on it** (superseded 2025-03-26) |

Remote clients connect to an HTTPS URL ending in the Streamable HTTP path
(default `/mcp`). The SDK also documents mounting `mcp.streamable_http_app()`
inside an existing ASGI/FastAPI app (`/run/asgi/`), with the host lifespan
entering `mcp.session_manager.run()` and `TransportSecuritySettings` allowlisting
the real hostname (localhost-only Host checks are the default and break
production otherwise).

### Choice: **Streamable HTTP**, mounted in one public ASGI app

- Keep `api/mcp_server.py` for **local stdio** (`python3 api/mcp_server.py`).
- Add `api/public_app.py` for **production**: FastAPI REST + key issue +
  dashboard + MCP Streamable HTTP (`stateless_http=True`, `json_response=True`
  for simple request/response over HTTPS behind Render).
- One process, one `$PORT`, one TLS terminator (Render).

stdio is unchanged for laptop use; it is **not** what gets deployed.

---

## 3. Rate limit default

| Setting | Value |
| --- | --- |
| Window | 60 seconds (rolling) |
| Limit | **60 requests / window / identity** |
| Identity | `X-API-Key` when present; else client IP |
| Exceeded | HTTP **429** with a clear JSON body — never silent drop |

**Why 60/min:** enough for an interactive agent exploring list/detail/methodology
(~1 req/s average) without feeling broken; low enough that a naive scrape
trips quickly (easy to demonstrate). This is an informed guess until real
usage exists — revisit after the dashboard shows actual call patterns.

Key issuance (`POST /v1/keys`) is also rate-limited (same middleware) so
anonymous callers cannot mint unbounded keys without hitting 429.

---

## Out of scope (explicit)

- Public internet ≠ KYA, payments, or execution.
- Dashboard is owner-only (shared secret), not a product UI.
- Free-tier cold starts and ephemeral SQLite are known limits, not bugs to
  paper over in this step.
