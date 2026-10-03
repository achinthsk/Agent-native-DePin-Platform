# Tokn Investments (public web)

Read-only UI over the live scored-assets API.

## Product flow

1. `/` — browse assets (discovery)
2. `/assets/[asset-id]/` — reusable asset intelligence page

## Design

See [`DESIGN.md`](./DESIGN.md). Visual language: liquid-glass + **VCR OSD Mono**.

## Data rule

Scores, claims, methodology, and snapshot identity come from:

- `GET /v1/assets`
- `GET /v1/assets/{id}`
- `GET /v1/methodology`

No fabricated market tickers, volumes, or verification events. Missing fields
render as **Not available**.

## Local preview

```bash
# optional: local API with latest enrich fields
python3 -m uvicorn api.public_app:app --host 127.0.0.1 --port 8080

# or CORS proxy to Render
python3 web/scripts/live_api_cors_proxy.py   # :8090

cd web
npm ci
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8080 npm run dev
# open http://127.0.0.1:3000
```

Static export: `npm run build` → `web/out` (mounted by FastAPI when present).
