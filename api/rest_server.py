#!/usr/bin/env python3
"""
Local REST fallback for scored Yield Opportunity assets.

Thin FastAPI wrapper around api.queries (same logic as the MCP server).
Binds to 127.0.0.1 by default — local use only, not public internet hosting.

Usage (from repo root):
  python3 api/rest_server.py
  # or: uvicorn api.rest_server:app --host 127.0.0.1 --port 8080
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from api import queries

app = FastAPI(
    title="Scored assets (local)",
    description=(
        "Read-only local HTTP access to scored snapshots from scoring.engine. "
        "Descriptive and comparative only — not investment advice. "
        "Not configured for public-internet deployment."
    ),
    version="1.0.0",
)


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


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "scope": "local"}


def main() -> None:
    import uvicorn

    # Localhost only — do not imply public exposure.
    uvicorn.run(
        "api.rest_server:app",
        host="127.0.0.1",
        port=8080,
        reload=False,
    )


if __name__ == "__main__":
    main()
