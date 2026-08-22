#!/usr/bin/env python3
"""Local-only CORS proxy to the live Render API for UI demos before CORS ships.

Not used in production. Production enables CORS on api.public_app and/or
serves the static UI same-origin from web/out.
"""

from __future__ import annotations

import os

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

UPSTREAM = os.environ.get(
    "LIVE_API_UPSTREAM",
    "https://agent-native-depin-platform.onrender.com",
).rstrip("/")

app = FastAPI(title="Live API CORS proxy (local demo)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "upstream": UPSTREAM}


@app.api_route("/{path:path}", methods=["GET", "HEAD"])
async def proxy(path: str, request: Request) -> Response:
    url = f"{UPSTREAM}/{path}"
    if request.url.query:
        url = f"{url}?{request.url.query}"
    async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
        upstream = await client.request(
            request.method,
            url,
            headers={"Accept": request.headers.get("accept", "application/json")},
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8090"))
    uvicorn.run(app, host="127.0.0.1", port=port)
