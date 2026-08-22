# Public scored-assets page

Read-only UI for the live scoring API. Design rationale: [`DESIGN.md`](./DESIGN.md).

## Data rule

Scores, verification tiers (via score inputs), snapshot history, and
methodology text are fetched only from:

- `GET /v1/assets`
- `GET /v1/assets/{id}`
- `GET /v1/methodology`

Default target: `https://agent-native-depin-platform.onrender.com` (or
same-origin when this static export is mounted on that ASGI app).

Findings feed excerpts are from in-repo investigation markdown — labeled
as investigation log, not live scores.

## Develop

```bash
cd web
npm ci
npm run dev
# open http://localhost:3000 — browser talks to the live API (CORS enabled on public_app)
```

## Build static export

```bash
cd web
npm ci
npm run build   # writes web/out/
```

`api/public_app.py` mounts `web/out` at `/` when the directory exists
(after API and MCP routes). Render serves the page at the same host as
the API once `web/out` is present in the deployed tree.

## Copy rule

Descriptive and comparative only — not investment advice. No recommend /
buy / invest / opportunity language on this page.
