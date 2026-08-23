# Public scored-assets page

Read-only UI for the live scoring API.

## Design

- **v2 (current):** Kokonut UI + Bklit chart language — see [`DESIGN.md`](./DESIGN.md)
- Confirmed references: [kokonutui.com](https://kokonutui.com), [bklit.com](https://bklit.com)

## Data rule

Scores, tiers, history, and methodology come only from:

- `GET /v1/assets`
- `GET /v1/assets/{id}`
- `GET /v1/methodology`

Default: `https://agent-native-depin-platform.onrender.com`

## Local preview (no merge required)

```bash
cd web
npm ci
# optional CORS proxy if the live API has not redeployed CORS yet:
python3 scripts/live_api_cors_proxy.py   # :8090
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8090 npm run dev
# open http://127.0.0.1:3000
```

## Copy rule

Descriptive and comparative only — not investment advice.
