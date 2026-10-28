# Production Deployment & Operations Guide

## 1. System Requirements

- **Runtime**: Linux (Ubuntu 22.04 LTS+, Debian 12+, RHEL 9+)
- **Python**: 3.11, 3.12, or 3.14
- **Node.js**: 20 LTS or higher
- **Database**: PostgreSQL 16+ (or SQLite with aiosqlite for local development/testing)
- **Cache & Broker**: Redis 7+
- **Containerization**: Docker 24+ and Docker Compose v2

---

## 2. Environment Configuration

Copy `.env.example` to `.env` and configure production secrets:

```bash
cp .env.example .env
```

Key environment variables:
| Variable | Description | Production Default |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `REDIS_URL` | Redis instance for cache and Celery | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` | Secret key for signing session tokens | 32+ character random secret |
| `MODEL_DIR` | Filesystem path for model artifacts | `saved_models/tfidf_model` |
| `TRAINING_DATA_PATH` | Curated dataset path | `data/training_dataset.jsonl` |
| `CORS_ORIGINS` | Permitted frontend origins | `https://triage.internal.company.com` |

---

## 3. Database Migrations (Alembic)

Database schemas are strictly versioned with Alembic. Never run manual DDL statements against production databases.

To execute migrations:
```bash
# Verify pending migrations
alembic current

# Run migrations to head
alembic upgrade head
```

---

## 4. Docker Compose Deployment

The root `docker-compose.yml` provides a production-grade multi-container topology:
- `postgres`: Persistent relational storage.
- `redis`: High-speed queue broker.
- `api`: FastAPI application running Uvicorn workers.
- `frontend`: High-performance Nginx web server serving compiled SPA assets.
- `prometheus`: Scrapes metrics from `/metrics` every 15s.
- `grafana`: Operational dashboards.

### Starting the Stack
```bash
docker compose up -d --build
```

### Health Verification
```bash
docker compose ps
curl -f http://localhost:8000/health
```

---

## 5. Kubernetes Deployment

Production manifests are located in the `k8s/` directory.

### Step 1: Create Secrets
Create your production secrets from `k8s/secrets.example.yaml`:
```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: triage-secrets
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://app_user:PROD_PASSWORD@postgres.internal:5432/triage"
  redis-url: "redis://redis.internal:6379/0"
  jwt-secret-key: "PROD_CRYPTOGRAPHICALLY_RANDOM_SECRET"
EOF
```

### Step 2: Deploy Application & Service
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 3: Rollout Verification
```bash
kubectl rollout status deployment/triage-api
```

---

## 6. Observability & Health Checks

- **Liveness Probe**: `GET /health` returns `{"status": "healthy", "service": "triage-platform", "version": "2.0.0"}`.
- **Prometheus Metrics**: `GET /metrics` exposes real-time Prometheus counters and histograms:
  - `http_requests_total`: Total requests partitioned by method, endpoint, and status.
  - `model_prediction_latency_seconds`: Histogram of ML classification latency.
  - `model_predictions_total`: Count of triage predictions by engine and target team.
  - `model_fallback_total`: Counter tracking when keyword fallback activated.
