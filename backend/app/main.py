from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.api import analytics_router, health_records_router
from app.database import create_db_and_tables
from app.version import get_version_info


def _parse_cors_origins(value: str | None) -> list[str]:
    """Comma-separated origins via env (e.g. "https://app.example.com,https://admin.example.com")."""

    if not value or not value.strip():
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    origins = [o.strip() for o in value.split(",") if o.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


_version = get_version_info()
_api_name = f"{_version.name} API"

app = FastAPI(
    title=_api_name,
    description="Rule-based health analytics backend for weight plateau analysis",
    version=_version.version,
    lifespan=lifespan,
)


cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
allow_credentials = True
if "*" in cors_origins:
    cors_origins = ["*"]
    # CORS forbids allow_credentials with wildcard origins.
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_records_router)
app.include_router(analytics_router)

_dist_dir = Path(
    os.getenv("PLATEAUBREAKER_FRONTEND_DIST_DIR")
    or (Path(__file__).resolve().parent / "static" / "dist")
).resolve()
_index_html = _dist_dir / "index.html"


class _SpaFallbackMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, index_html: Path, api_prefix: str = "/api"):
        super().__init__(app)
        self._index_html = index_html
        self._api_prefix = api_prefix

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if request.method != "GET":
            return response

        path = request.url.path
        if path.startswith(self._api_prefix):
            return response

        if response.status_code != 404:
            return response

        accept = request.headers.get("accept", "")
        if "text/html" not in accept and "*/*" not in accept:
            return response

        if not self._index_html.exists():
            return response

        return FileResponse(self._index_html)


@app.get("/api/meta")
def api_meta():
    return {
        "name": _api_name,
        "version": _version.version,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if _dist_dir.exists() and _index_html.exists():
    # Serve the built SPA when available (e.g. in Docker/prod builds).
    # This must be registered AFTER API routes like /health to avoid shadowing them.
    app.mount("/", StaticFiles(directory=str(_dist_dir), html=True), name="frontend")
    app.add_middleware(_SpaFallbackMiddleware, index_html=_index_html)
