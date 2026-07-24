"""Entry point for the URL Shortener API."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Opens the PostgreSQL pool on startup and closes it on shutdown."""
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(title="URL Shortener", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness probe for Kubernetes.

    Only reports whether the process itself is up and able to serve HTTP
    requests. It must not depend on PostgreSQL: a transient DB outage should
    remove the pod from load balancing (see /readyz) without Kubernetes
    restarting an otherwise healthy process.
    """
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    """Readiness probe for Kubernetes.

    Verifies the PostgreSQL pool can actually serve a query, since /shorten
    and GET /{code} both depend on it: readiness must not report "ok" while
    the app is unable to serve core traffic.
    """
    try:
        pool = db.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable.") from exc
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    """Exposes metrics in Prometheus format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(router)
