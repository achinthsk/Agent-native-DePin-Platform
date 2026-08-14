# Scored-assets API design (local only)

This document defines the read-only query surface over `scoring/engine.py`
**before** implementation. It is intentionally a thin wrapper: filter, sort,
paginate, and return engine output — never recompute or override a score.

**Scope:** callable **locally** (stdio MCP and localhost HTTP). This design
does **not** make the service reachable on the public internet; hosting is a
separate later decision.

**SDK choice (investigated 2026-08-13):** use the official MCP Python SDK v2
(`mcp` ≥ 2.0), `from mcp.server import MCPServer` (formerly `FastMCP`). Tools
via `@mcp.tool()`, methodology also as a resource. Confirmed against
https://py.sdk.modelcontextprotocol.io/ and the installed `mcp==2.0.0`
package. REST fallback uses FastAPI and the same shared query module.

---

## Computation policy

**Scores are computed live on each request** by calling
`scoring.engine.score_storage(latest_only=True)` (default) or
`score_storage(latest_only=False)` when the caller asks for all snapshots.

Reasons:

1. The dataset is tiny (three assets, a handful of snapshots).
2. Live calls guarantee the response matches the current engine + weights
   without a cache-invalidation path.
3. Caching can be added later if latency or load requires it; premature
   caching is out of scope.

The API **never** invents, blends, or adjusts `*.value` fields. It only
reads what the engine returned and attaches identity / regulatory fields
loaded from the same snapshot file the score was computed from.

---

## Shared module: `api/queries.py`

All filter / sort / lookup / methodology read logic lives here. Both the MCP
server and the REST server call this module only.

### Response building blocks

#### `ScoreObject` (opaque passthrough from engine)

Whatever `scoring.engine` returned for that axis, in full — including at
minimum:

- `value` (number or `null`)
- `direction` (`"higher_is_better"`)
- `insufficient_data` (bool)
- `inputs` / `components` / other engine metadata as present

The API does not strip or reshape score internals.

#### `ScoredAsset`

```json
{
  "asset_id": "string",
  "name": "string",
  "asset_class": "string",
  "source_platform": "string",
  "schema_version": "string",
  "snapshot_file": "string",
  "data_pulled_at": "string (ISO-8601)",
  "snapshot_age_days": "number | null",
  "regulatory": {
    "regulatory_wrapper": "string",
    "accreditation_required": "boolean",
    "restricted_jurisdictions": ["ISO-3166-1-alpha-2", "..."],
    "permitted_jurisdictions": ["ISO-3166-1-alpha-2", "..."]
  },
  "jurisdiction_note": {
    "queried_jurisdiction": "string | null",
    "eligibility": "eligible | restricted | not_listed_in_permitted | unknown"
  },
  "yield_score": { "...ScoreObject..." },
  "risk_score": { "...ScoreObject..." },
  "liquidity_score": { "...ScoreObject..." },
  "data_confidence_score": { "...ScoreObject..." },
  "weights_version": "string | null",
  "scored_at": "string"
}
```

`snapshot_age_days` is taken from
`data_confidence_score.inputs.snapshot_age_days` when present — never
fabricated as “fresh.”

`jurisdiction_note.eligibility` meanings (descriptive only):

| Value | Meaning |
| --- | --- |
| `eligible` | Queried code is in `permitted_jurisdictions`, or permitted is empty and code is not in `restricted_jurisdictions`. |
| `restricted` | Queried code appears in `restricted_jurisdictions`. |
| `not_listed_in_permitted` | `permitted_jurisdictions` is non-empty and queried code is absent from it. |
| `unknown` | No jurisdiction was queried, **or** both permitted and restricted arrays are empty (schema: absence ≠ worldwide clearance). |

No field name or prose may prescribe action (“recommend,” “best option,”
“you should invest,” “top pick,” etc.). Sorting is comparative ordering of
known scores only.

---

## Tools / endpoints

### 1. List / query scored assets

**MCP tool:** `list_scored_assets`  
**REST:** `GET /v1/assets`

#### Inputs

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `asset_class` | string \| null | null | Exact match on schema `asset_class`. |
| `min_risk_score` | number \| null | null | Keep assets where `risk_score.value >= min` **and** `risk_score.insufficient_data` is false. Null scores never pass a minimum filter. |
| `min_liquidity_score` | number \| null | null | Same rule for `liquidity_score`. |
| `holder_jurisdiction` | string \| null | null | ISO 3166-1 alpha-2. When set, drop `restricted` and `not_listed_in_permitted`; keep `eligible` and (optionally) `unknown` — see `include_unknown_jurisdiction`. |
| `include_unknown_jurisdiction` | bool | true | If false and a jurisdiction was queried, also drop `unknown`. |
| `regulatory_wrapper` | string \| null | null | Exact match filter. |
| `sort_by` | string | `"asset_id"` | One of: `asset_id`, `risk_score`, `liquidity_score`, `yield_score`, `data_confidence_score`, `snapshot_age_days`. Score sorts use `.value`; null/`insufficient_data` sort last when descending, first when ascending. |
| `sort_desc` | bool | false | Descending order when true. |
| `latest_only` | bool | true | Passed through to `score_storage`. |
| `limit` | int | 50 | Pagination page size (1–200). |
| `offset` | int | 0 | Pagination offset. |

#### Output

```json
{
  "query": { "...echo of effective filters..." },
  "total_matched": 0,
  "limit": 50,
  "offset": 0,
  "assets": [ "ScoredAsset", "..." ],
  "notes": [
    "Scores computed live from storage snapshots via scoring.engine.",
    "Descriptive and comparative only — not investment advice."
  ]
}
```

---

### 2. Get one asset by id

**MCP tool:** `get_scored_asset`  
**REST:** `GET /v1/assets/{asset_id}`

#### Inputs

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `asset_id` | string | required | Exact `asset_id`. |
| `latest_only` | bool | true | If true, return the newest snapshot’s score for that id. If false, return all scored snapshots for that id. |
| `holder_jurisdiction` | string \| null | null | Populates `jurisdiction_note` only (does not 404). |

#### Output (latest_only true)

```json
{
  "asset": "ScoredAsset | null",
  "notes": [
    "Descriptive scored snapshot data only — not investment advice."
  ]
}
```

HTTP 404 when no matching scored snapshot exists. MCP returns
`asset: null` plus a descriptive `error` string (no prescription).

#### Output (latest_only false)

```json
{
  "assets": [ "ScoredAsset", "..." ],
  "notes": [ "..." ]
}
```

---

### 3. Scoring methodology

**MCP tool:** `get_scoring_methodology`  
**MCP resource:** `methodology://scoring` (same body)  
**REST:** `GET /v1/methodology`

#### Inputs

| Param | Type | Default | Notes |
| --- | --- | --- | --- |
| `format` | `"markdown"` \| `"summary"` | `"markdown"` | `markdown` returns full `scoring/METHODOLOGY.md` text. `summary` returns a structured outline of the four axes, null-handling, and weight-file pointer. |

#### Output

```json
{
  "format": "markdown",
  "weights_path": "scoring/weights.yaml",
  "methodology_path": "scoring/METHODOLOGY.md",
  "content": "...full markdown or structured summary...",
  "notes": [
    "Methodology text is informational. Score values always come from scoring.engine."
  ]
}
```

---

## What this API will not do

- Recompute, blend, or override any score value.
- Execute trades, payments, or KYA / identity flows.
- Claim public-internet availability.
- Use investment-advice or prescriptive language in field names or notes.

---

## Implementation map

| File | Role |
| --- | --- |
| `api/DESIGN.md` | This document |
| `api/queries.py` | Shared live score + filter/sort/lookup/methodology |
| `api/mcp_server.py` | MCP `MCPServer` tools + methodology resource |
| `api/rest_server.py` | FastAPI routes calling `queries` |
| top-level `README.md` | Local run instructions for both servers |
