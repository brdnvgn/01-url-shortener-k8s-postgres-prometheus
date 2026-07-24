"""Tests d'intégration pour l'exposition des métriques (`GET /metrics`)."""

import re

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.usefixtures("clean_db")


def _counter_value(metrics_text: str, metric_name: str) -> float:
    """Extrait la valeur d'un compteur Prometheus (sans labels) depuis le texte brut."""
    match = re.search(rf"^{metric_name} ([0-9.eE+-]+)$", metrics_text, re.MULTILINE)
    assert match is not None, f"Métrique '{metric_name}' absente de la réponse /metrics"
    return float(match.group(1))


def test_metrics_endpoint_returns_prometheus_format(client: TestClient) -> None:
    """La réponse doit être un contenu texte au format d'exposition Prometheus."""
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    body = response.text
    assert "# HELP shortener_links_created_total" in body
    assert "# TYPE shortener_links_created_total counter" in body
    assert "# HELP shortener_redirects_total" in body
    assert "# TYPE shortener_redirects_total counter" in body


def test_links_created_counter_increments_on_shorten(client: TestClient) -> None:
    """Chaque appel réussi à POST /shorten doit incrémenter shortener_links_created_total."""
    before = _counter_value(client.get("/metrics").text, "shortener_links_created_total")

    client.post("/shorten", json={"url": "https://example.com/metrics-test-1"})
    client.post("/shorten", json={"url": "https://example.com/metrics-test-2"})

    after = _counter_value(client.get("/metrics").text, "shortener_links_created_total")
    assert after == before + 2


def test_redirects_counter_increments_on_successful_redirect(client: TestClient) -> None:
    """Chaque redirection réussie doit incrémenter shortener_redirects_total."""
    code = client.post("/shorten", json={"url": "https://example.com/metrics-redirect"}).json()["code"]

    before = _counter_value(client.get("/metrics").text, "shortener_redirects_total")

    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)

    after = _counter_value(client.get("/metrics").text, "shortener_redirects_total")
    assert after == before + 2


def test_redirects_counter_not_incremented_on_404(client: TestClient) -> None:
    """Une redirection échouée (code inconnu) ne doit pas incrémenter shortener_redirects_total."""
    before = _counter_value(client.get("/metrics").text, "shortener_redirects_total")

    client.get("/doesnotexist", follow_redirects=False)

    after = _counter_value(client.get("/metrics").text, "shortener_redirects_total")
    assert after == before
