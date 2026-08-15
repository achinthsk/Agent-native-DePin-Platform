#!/usr/bin/env python3
"""
MCP server for scored Yield Opportunity assets.

Local default: stdio transport (inter-process only — not network reachable).

  python3 api/mcp_server.py

Remote / production: use api/public_app.py, which mounts this same MCPServer
over Streamable HTTP at /mcp (current SDK recommendation for anything you
deploy — see deploy/DECISIONS.md). Do not deploy this file's stdio mode
to the public internet.

Scores come only from scoring.engine via api.queries.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp.server import MCPServer

from api import queries

mcp = MCPServer(
    name="scored-assets",
    instructions=(
        "Read-only access to scored DePIN / tokenized-asset snapshots. "
        "Returns descriptive score detail from scoring.engine. "
        "Not investment advice."
    ),
)


@mcp.tool()
def list_scored_assets(
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
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    """
    List scored assets with optional filters.

    Scores are computed live via scoring.engine. Each asset includes full
    yield/risk/liquidity/data_confidence score objects (value, direction,
    insufficient_data, inputs/components). Descriptive only — not investment advice.
    """
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


@mcp.tool()
def get_scored_asset(
    asset_id: str,
    latest_only: bool = True,
    holder_jurisdiction: str | None = None,
) -> dict[str, Any]:
    """
    Return full scored detail for one asset_id.

    Includes all four score objects in full and snapshot_age_days from the
    engine. Descriptive only — not investment advice.
    """
    return queries.get_scored_asset(
        asset_id,
        latest_only=latest_only,
        holder_jurisdiction=holder_jurisdiction,
    )


@mcp.tool()
def get_scoring_methodology(
    format: Literal["markdown", "summary"] = "markdown",
) -> dict[str, Any]:
    """
    Return how the four scores are computed (METHODOLOGY.md or a structured summary).
    """
    return queries.get_scoring_methodology(format=format)


@mcp.resource("methodology://scoring")
def methodology_resource() -> str:
    """Full scoring methodology markdown (same source as get_scoring_methodology)."""
    result = queries.get_scoring_methodology(format="markdown")
    return str(result["content"])


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").strip().lower()
    if transport in ("streamable-http", "http", "remote"):
        # Prefer the unified public app for production; this path exists for
        # standalone MCP-only Streamable HTTP debugging.
        port = int(os.environ.get("PORT", "8080"))
        host = os.environ.get("HOST", "0.0.0.0")
        from mcp.server.transport_security import TransportSecuritySettings

        allowed = [
            h.strip()
            for h in os.environ.get(
                "ALLOWED_HOSTS",
                "localhost,127.0.0.1,localhost:*,127.0.0.1:*",
            ).split(",")
            if h.strip()
        ]
        mcp.run(
            transport="streamable-http",
            host=host,
            port=port,
            json_response=True,
            stateless_http=True,
            transport_security=TransportSecuritySettings(
                enable_dns_rebinding_protection=True,
                allowed_hosts=allowed,
                allowed_origins=["*"],
            ),
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
