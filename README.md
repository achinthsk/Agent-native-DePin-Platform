# Agent-native DePIN Platform

Schema, adapters, scoring engine, and a **local** read-only API over scored
assets. Nothing here is deployed to the public internet by default.

## Layout

| Path | Role |
| --- | --- |
| `schema/` | Yield Opportunity JSON Schema + rationale |
| `adapters/` | Glow / Elmnts / RealT data pulls → `storage/` |
| `storage/` | Validated snapshot JSON (facts only) |
| `scoring/` | Four-axis engine (`yield` / `risk` / `liquidity` / `data_confidence`) |
| `api/` | Local MCP + REST wrappers around `scoring.engine` |

## Setup

```bash
python3 -m pip install -r requirements.txt
```

Copy `.env.example` → `.env` for adapter secrets (RPC URLs, etc.).

## Scoring (CLI)

```bash
python3 scoring/engine.py --latest-only
python3 scoring/engine.py --latest-only --prove
```

## Local API (not public hosting)

Both interfaces call `api/queries.py`, which calls `scoring.engine` live on
each request. They do not recompute or override score values.

### MCP (stdio)

```bash
python3 api/mcp_server.py
```

Tools: `list_scored_assets`, `get_scored_asset`, `get_scoring_methodology`.  
Resource: `methodology://scoring`.

In-process smoke test (no network):

```bash
python3 -c "
import asyncio, json
from mcp import Client
from api.mcp_server import mcp

async def main():
    async with Client(mcp) as client:
        r = await client.call_tool('list_scored_assets', {'asset_class': 'solar-depin'})
        print(json.dumps(r.structured_content, indent=2)[:2000])

asyncio.run(main())
"
```

### REST (localhost only)

```bash
python3 api/rest_server.py
# listens on http://127.0.0.1:8080
```

Examples:

```bash
curl -s 'http://127.0.0.1:8080/v1/assets?asset_class=solar-depin' | python3 -m json.tool
curl -s 'http://127.0.0.1:8080/v1/assets/glow-farm-1' | python3 -m json.tool
curl -s 'http://127.0.0.1:8080/v1/methodology?format=summary' | python3 -m json.tool
```

Responses are descriptive and comparative only — not investment advice.
