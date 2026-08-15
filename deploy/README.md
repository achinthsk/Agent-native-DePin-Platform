# Deploy (Render)

Public HTTPS hosting for the scored-assets API. Decisions and rationale:
`deploy/DECISIONS.md`.

## What gets deployed

- Process: `uvicorn api.public_app:app` on `0.0.0.0:$PORT`
- REST: `/v1/assets`, `/v1/assets/{id}`, `/v1/methodology`, `POST /v1/keys`
- MCP: Streamable HTTP at `/mcp` (not stdio)
- Owner dashboard: `/owner/dashboard?secret=...` (403 without secret)
- TLS: Render-managed on `https://<service>.onrender.com`

## One-time setup

1. Push this repo to GitHub (already done for this project).
2. Create a [Render](https://render.com) account (GitHub login; free tier needs no card).
3. **Blueprint**: New → Blueprint → select this repo → `render.yaml` is detected.
   Or: New → Web Service → connect repo →:
   - Build: `pip install -r requirements.txt`
   - Start: `python3 -m uvicorn api.public_app:app --host 0.0.0.0 --port $PORT`
   - Instance: **Free**
4. Set environment variables (Dashboard → Environment):

| Variable | Example | Notes |
| --- | --- | --- |
| `DASHBOARD_SECRET` | long random string | Required to view `/owner/dashboard` |
| `ALLOWED_HOSTS` | (optional) | Extra Host allowlist entries. On Render, `RENDER_EXTERNAL_HOSTNAME` is merged automatically so MCP Streamable HTTP accepts `*.onrender.com`. |
| `RATE_LIMIT_PER_MINUTE` | `60` | Optional; default 60 |
| `DATA_DIR` | `/opt/render/project/src/data` | Optional; SQLite for keys + request log |

5. Deploy. First request after idle may cold-start (~30–60s on free).

## Smoke checks (replace HOST)

```bash
HOST=https://YOUR-SERVICE.onrender.com

curl -sS "$HOST/healthz"

# Issue a free API key
curl -sS -X POST "$HOST/v1/keys"

# Use it
curl -sS -H "X-API-Key: ysk_..." \
  "$HOST/v1/assets?min_risk_score=50&min_liquidity_score=40&holder_jurisdiction=US&include_unknown_jurisdiction=false"

# Dashboard (secret required)
curl -sS -o /dev/null -w "%{http_code}\n" "$HOST/owner/dashboard"
curl -sS "$HOST/owner/dashboard?secret=YOUR_DASHBOARD_SECRET" | head
```

## Local production-shaped run

```bash
export DASHBOARD_SECRET=dev-secret
export ALLOWED_HOSTS=127.0.0.1,localhost,127.0.0.1:*,localhost:*
export DATA_DIR=/tmp/scored-assets-data
python3 -m uvicorn api.public_app:app --host 127.0.0.1 --port 8080
```

Local stdio MCP (not public): `python3 api/mcp_server.py`
