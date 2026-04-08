import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics_router, health_records_router
from app.database import create_db_and_tables

app = FastAPI(
    title="PlateauBreaker API",
    description="Rule-based health analytics backend for weight plateau analysis",
    version="1.0.0",
)


def _parse_cors_origins(value: str | None) -> list[str]:
    """Comma-separated origins via env (e.g. "https://app.example.com,https://admin.example.com")."""

    if not value or not value.strip():
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    origins = [o.strip() for o in value.split(",") if o.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {
        "name": "PlateauBreaker API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
