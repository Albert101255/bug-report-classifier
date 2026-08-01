# Deployment Guide

## Docker Compose

From the repository root:

```bash
cp .env.example .env
# Replace all placeholder values in .env
python -m pip install -r requirements.txt
python scripts/train_baseline.py
docker compose up --build
```

Local endpoints are bound to `127.0.0.1` by default:

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

PostgreSQL and Redis are intentionally not published to the host. Containers communicate over the internal Compose network.

## Manual backend setup

```bash
cp .env.example .env
python -m pip install -r requirements.txt
python scripts/train_baseline.py
PYTHONPATH=backend uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

For local manual execution, update `DATABASE_URL`, `REDIS_URL`, `MODEL_DIR`, and `TRAINING_DATA_PATH` in `.env` to paths and addresses reachable from the host.

## Production checklist

- Store secrets in a managed secret store, not in Git.
- Terminate TLS at a reverse proxy or managed load balancer.
- Restrict CORS to the deployed frontend origin.
- Run database migrations instead of `create_all()`.
- Back up PostgreSQL and model artifacts.
- Use a managed Redis service or authentication-enabled Redis.
- Put management endpoints behind proper identity and role-based access control.
