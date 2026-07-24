# Project 01 — URL Shortener on Kubernetes

> **Tools covered:** Kubernetes · PostgreSQL · Prometheus

## Goal

Build a small **URL shortening** API (a minimal Bitly-like service), **containerize**
it, **deploy it to Kubernetes**, persist its data in **PostgreSQL**, and **monitor**
its metrics with **Prometheus**.

This is the ideal project to discover the heart of DevOps work: containers, orchestration,
a stateful database, and observability, all locally with no cloud cost.

## What you'll learn

| Tool           | Topics covered |
|----------------|------------------|
| **Kubernetes** | Pods, Deployments, Services, ConfigMap/Secret, Ingress, `kubectl`, readiness/liveness probes |
| **PostgreSQL** | StatefulSet, PersistentVolumeClaim, environment variables, simple migrations |
| **Prometheus** | Exposing `/metrics`, scraping, basic PromQL, simple alerts |

## Architecture

```
                   ┌─────────────────────────────────────────┐
                   │              Kubernetes Cluster          │
                   │                                           │
  browser      ───► │  Ingress ─► Service ─► Deployment (API)   │
                   │                          │  exposes /metrics│
                   │                          ▼                 │
                   │                    PostgreSQL (StatefulSet)│
                   │                                           │
                   │  Prometheus ──scrape──► API /metrics       │
                   └─────────────────────────────────────────┘
```

## Prerequisites

- **Python 3.13** + [Poetry](https://python-poetry.org/) (dependency management)
- **Docker** (to build the image)
- **A local cluster**: [minikube](https://minikube.sigs.k8s.io/) or [kind](https://kind.sigs.k8s.io/)
- **kubectl** installed
- (Optional) **Helm** to install Prometheus via the `kube-prometheus-stack` chart

## Local setup (Poetry)

```bash
# Use Python 3.13
poetry env use 3.13

# Install dependencies (prod + dev)
poetry install

# Activate the venv shell (optional)
poetry shell

# Run the API locally (once the app is written)
poetry run uvicorn url_shortener.main:app --reload --host 0.0.0.0 --port 8000
```

## The service (functional spec)

Minimal REST API (Node/Express, Go, or Python/FastAPI — your choice):

- `POST /shorten` → `{ "url": "https://example.com/page" }` returns `{ "code": "ab12cd" }`
- `GET /{code}` → redirects (HTTP 302) to the original URL
- `GET /metrics` → metrics in Prometheus format (links created, redirects, latency)
- `GET /healthz` → health probe for Kubernetes

PostgreSQL table:

```sql
CREATE TABLE links (
    code       VARCHAR(10) PRIMARY KEY,
    long_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hits       BIGINT DEFAULT 0
);
```

## Project steps

1. **Write the application** with a `/metrics` endpoint (use a Prometheus client:
   `prom-client` in Node, `prometheus_client` in Python, etc.).
2. **Write the `Dockerfile`** and build the image (`docker build -t url-shortener:0.1 .`).
   Load the image into minikube/kind (`minikube image load ...` or `kind load docker-image ...`).
3. **Deploy PostgreSQL** via a `StatefulSet` + `PersistentVolumeClaim` + `Service`.
   Store the password in a `Secret`.
4. **Deploy the API** via a `Deployment` (2 replicas) + `Service` + `Ingress`.
   Inject the DB connection via `ConfigMap`/`Secret`, add `readiness`/`liveness` probes.
5. **Install Prometheus** (`kube-prometheus-stack` chart) and declare a `ServiceMonitor`
   to scrape the API.
6. **Verify**: create links, generate traffic, observe the metrics in Prometheus
   (e.g. `rate(shortener_redirects_total[1m])`).

## Target file tree

```
01-url-shortener-k8s-postgres-prometheus/
├── pyproject.toml          # Poetry + Python 3.13 dependencies
├── poetry.lock
├── app/                    # API code + Dockerfile
│   ├── src/
│   │   └── url_shortener/
│   └── Dockerfile
├── k8s/
│   ├── postgres-statefulset.yaml
│   ├── postgres-service.yaml
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secret.yaml
└── monitoring/
    └── servicemonitor.yaml
```

## Possible extensions

- Add a **Redis cache** in front of PostgreSQL for redirects.
- Add a **HorizontalPodAutoscaler** based on CPU load.
- Add **Grafana** to visualize Prometheus metrics.
- Add a **Jenkins** pipeline (see project 02) to build/deploy automatically.

## Success criteria

- [ ] The API responds behind the Ingress.
- [ ] Data survives a PostgreSQL Pod restart (persistence OK).
- [ ] Prometheus correctly scrapes `/metrics` and the counters increase.
