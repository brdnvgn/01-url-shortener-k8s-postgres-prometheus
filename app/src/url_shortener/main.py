"""Point d'entrée de l'API URL Shortener."""

from fastapi import FastAPI

app = FastAPI(title="URL Shortener")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Sonde de santé pour Kubernetes (liveness/readiness)."""
    return {"status": "ok"}
