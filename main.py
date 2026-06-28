"""
Vision-Learn AI — FastAPI application entry point.

Run with:
    uvicorn main:app --reload --port 8000
"""
import asyncio
import os
import sys

# ── Windows: asyncio.create_subprocess_exec requires ProactorEventLoop ─────────
# Uvicorn defaults to SelectorEventLoop on Windows which does NOT support
# subprocesses. This must be set before the event loop is created.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(override=True)

from api.router import api_router


def _get_cors_origins() -> list[str]:
    """Parse CORS origins from env and include safe local-dev defaults."""
    raw = os.getenv("CORS_ORIGINS", "")
    parsed = [origin.strip() for origin in raw.split(",") if origin.strip()]
    local_defaults = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]

    # Keep user-provided order, then append any missing local defaults.
    origins = parsed.copy()
    for origin in local_defaults:
        if origin not in origins:
            origins.append(origin)
    return origins

app = FastAPI(
    title="Vision-Learn AI",
    description=(
        "End-to-end pipeline that processes YouTube lectures into "
        "pedagogical audio narrations for visually impaired students."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the Next.js frontend on port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Quick liveness check endpoint."""
    return {"status": "ok", "service": "vision-learn-ai"}
