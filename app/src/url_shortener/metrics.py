"""Compteurs Prometheus exposés par l'API."""

from prometheus_client import Counter

LINKS_CREATED = Counter(
    "shortener_links_created_total",
    "Nombre total de liens courts créés.",
)
REDIRECTS = Counter(
    "shortener_redirects_total",
    "Nombre total de redirections effectuées.",
)
