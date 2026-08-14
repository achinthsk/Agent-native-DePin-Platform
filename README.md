# Agent-native DePIN Platform

Schema, adapters, scoring engine, and a read-only API over scored assets.
Production hosting (HTTPS) is documented under `deploy/` — local stdio MCP
remains available for development.

## Layout

| Path | Role |
| --- | --- |
| `schema/` | Yield Opportunity JSON Schema + rationale |
| `adapters/` | Glow / Elmnts / RealT data pulls → `storage/` |
| `storage/` | Validated snapshot JSON (facts only) |
| `scoring/` | Four-axis engine (`yield` / `risk` / `liquidity` / `data_confidence`) |
| `api/` | Query layer, local MCP/REST, **public** ASGI app |
| `deploy/` | Hosting decisions + Render deploy steps |

## Setup

```bash
python3 -m pip install -r requirements.txt
```

Copy `.env.example` → `.env` for adapter / deploy-related secrets.

## Scoring (CLI)

```bash
python3 scoring/engine.py --latest-only
python3 scoring/engine.py --latest-only --prove
```

## Local API

Shared logic: `api/queries.py` → `scoring.engine` (no score recomputation in the API).

### MCP (stdio — local only)

```bash
python3 api/mcp_server.py
```

### REST (localhost)

```bash
python3 api/rest_server.py
# http://127.0.0.1:8080
```

### Public-shaped process (REST + Streamable HTTP MCP + keys + dashboard)

```bash
export DASHBOARD_SECRET=dev-secret
export ALLOWED_HOSTS=127.0.0.1,localhost,127.0.0.1:*,localhost:*
export DATA_DIR=/tmp/scored-assets-data
python3 -m uvicorn api.public_app:app --host 127.0.0.1 --port 8080
```

- `POST /v1/keys` — free instant API key  
- `X-API-Key` header — identity for rate limits (60/min default)  
- `/mcp` — MCP Streamable HTTP  
- `/owner/dashboard?secret=...` — owner request log (403 without secret)

## Production deploy

See `deploy/README.md` and `deploy/DECISIONS.md` (Render + Streamable HTTP).

Responses are descriptive and comparative only — not investment advice.
