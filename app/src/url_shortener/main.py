"""Point d'entrée de l'API URL Shortener."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from . import db
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Ouvre le pool PostgreSQL au démarrage et le ferme à l'arrêt."""
    await db.connect()
    yield
    await db.disconnect()


app = FastAPI(title="URL Shortener", lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Sonde de santé pour Kubernetes (liveness/readiness)."""
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    """Expose les métriques au format Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(router)
