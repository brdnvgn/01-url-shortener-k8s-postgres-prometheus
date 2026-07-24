"""Prometheus counters exposed by the API."""

from prometheus_client import Counter

LINKS_CREATED = Counter(
    "shortener_links_created_total",
    "Total number of short links created.",
)
REDIRECTS = Counter(
    "shortener_redirects_total",
    "Total number of redirects performed.",
)
