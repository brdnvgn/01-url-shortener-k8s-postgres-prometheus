# Projet 01 — Raccourcisseur d'URL sur Kubernetes

> **Outils croisés :** Kubernetes · PostgreSQL · Prometheus

## Objectif

Construire une petite API de **raccourcissement d'URL** (type Bitly minimaliste), la
**conteneuriser**, la **déployer sur Kubernetes**, la faire persister dans **PostgreSQL**
et **superviser** ses métriques avec **Prometheus**.

C'est le projet idéal pour découvrir le cœur du travail DevOps : conteneurs, orchestration,
base de données stateful et observabilité, le tout en local sans coût cloud.

## Ce que tu vas apprendre

| Outil          | Notions abordées |
|----------------|------------------|
| **Kubernetes** | Pods, Deployments, Services, ConfigMap/Secret, Ingress, `kubectl`, readiness/liveness probes |
| **PostgreSQL** | StatefulSet, PersistentVolumeClaim, variables d'environnement, migrations simples |
| **Prometheus** | Exposition de métriques `/metrics`, scraping, PromQL de base, alertes simples |

## Architecture

```
                   ┌─────────────────────────────────────────┐
                   │              Cluster Kubernetes           │
                   │                                           │
  navigateur  ───► │  Ingress ─► Service ─► Deployment (API)   │
                   │                          │  expose /metrics│
                   │                          ▼                 │
                   │                    PostgreSQL (StatefulSet)│
                   │                                           │
                   │  Prometheus ──scrape──► API /metrics       │
                   └─────────────────────────────────────────┘
```

## Prérequis

- **Docker** (pour builder l'image)
- **Un cluster local** : [minikube](https://minikube.sigs.k8s.io/) ou [kind](https://kind.sigs.k8s.io/)
- **kubectl** installé
- (Optionnel) **Helm** pour installer Prometheus via le chart `kube-prometheus-stack`

## Le service (spécification fonctionnelle)

API REST minimale (Node/Express, Go ou Python/FastAPI — au choix) :

- `POST /shorten` → `{ "url": "https://exemple.com/page" }` renvoie `{ "code": "ab12cd" }`
- `GET /{code}` → redirige (HTTP 302) vers l'URL d'origine
- `GET /metrics` → métriques au format Prometheus (nombre de liens créés, redirections, latence)
- `GET /healthz` → sonde de santé pour Kubernetes

Table PostgreSQL :

```sql
CREATE TABLE links (
    code       VARCHAR(10) PRIMARY KEY,
    long_url   TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    hits       BIGINT DEFAULT 0
);
```

## Étapes du projet

1. **Écrire l'application** avec un endpoint `/metrics` (utiliser un client Prometheus :
   `prom-client` en Node, `prometheus_client` en Python, etc.).
2. **Écrire le `Dockerfile`** et builder l'image (`docker build -t url-shortener:0.1 .`).
   Charger l'image dans minikube/kind (`minikube image load ...` ou `kind load docker-image ...`).
3. **Déployer PostgreSQL** via un `StatefulSet` + `PersistentVolumeClaim` + `Service`.
   Stocker le mot de passe dans un `Secret`.
4. **Déployer l'API** via un `Deployment` (2 réplicas) + `Service` + `Ingress`.
   Injecter la connexion DB via `ConfigMap`/`Secret`, ajouter les probes `readiness`/`liveness`.
5. **Installer Prometheus** (chart `kube-prometheus-stack`) et déclarer un `ServiceMonitor`
   pour scraper l'API.
6. **Vérifier** : créer des liens, générer du trafic, observer les métriques dans Prometheus
   (ex. `rate(shortener_redirects_total[1m])`).

## Arborescence cible

```
01-url-shortener-k8s-postgres-prometheus/
├── app/                    # code de l'API + Dockerfile
│   ├── src/
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

## Extensions possibles

- Ajouter du **cache Redis** devant PostgreSQL pour les redirections.
- Ajouter un **HorizontalPodAutoscaler** basé sur la charge CPU.
- Ajouter **Grafana** pour visualiser les métriques Prometheus.
- Ajouter un pipeline **Jenkins** (voir projet 02) pour builder/déployer automatiquement.

## Critères de réussite

- [ ] L'API répond derrière l'Ingress.
- [ ] Les données survivent au redémarrage d'un Pod PostgreSQL (persistance OK).
- [ ] Prometheus scrape bien `/metrics` et les compteurs augmentent.
