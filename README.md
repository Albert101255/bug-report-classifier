# Bug Report Triage Platform

A full-stack FastAPI and React application that routes software bug reports to engineering teams, records an audit trail, exposes a human review queue, and supports a reproducible machine-learning baseline.

## What the classifier actually uses

The primary model is a **scikit-learn TF-IDF vectorizer with multinomial Logistic Regression**. Confidence is the predicted class probability, while uncertainty is calculated as `1 - confidence`.

When trained artifacts are unavailable, the API uses a clearly identified **deterministic keyword fallback**. The fallback is intended only to keep local demos working; it is not presented as a trained ML model.

## Features

- Single and batch bug classification through FastAPI
- React and TypeScript dashboard
- PostgreSQL prediction and feedback audit trail
- Human review queue for uncertain classifications
- Real TF-IDF baseline training with accuracy and macro-F1 output
- Redis-backed cache and Celery worker
- Prometheus metrics and Grafana dashboards
- Docker Compose deployment and GitHub Actions CI

## Quick start

### 1. Configure the environment

```bash
cp .env.example .env
```

Replace every placeholder password and API key in `.env`.

### 2. Train the demo baseline

The included CSV contains synthetic examples for development only. Do not present its metrics as real-world performance.

```bash
python -m pip install -r requirements.txt
python scripts/train_baseline.py
```

Training writes the following files to `saved_models/tfidf_model/`:

- `tfidf_vectorizer.joblib`
- `classifier.joblib`
- `metadata.json`
- `classification_report.json`

### 3. Start the stack

```bash
docker compose up --build
```

Services:

- Dashboard: `http://localhost:3000`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

## Example prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict/single \
  -H 'Content-Type: application/json' \
  -d '{
    "subject": "Authentication regression",
    "description": "OAuth login fails after the JWT refresh token expires"
  }'
```

## Retraining

Retraining is disabled unless `ENABLE_RETRAINING=true` and `ADMIN_API_KEY` is set. Queue a baseline retraining job with:

```bash
curl -X POST http://localhost:8000/api/v1/models/retrain \
  -H "X-Admin-Key: $ADMIN_API_KEY"
```

The worker trains from `TRAINING_DATA_PATH`. Reviewer feedback is stored for later dataset curation, but it is **not automatically treated as clean training data**.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API_DOCS.md)
- [Deployment](docs/DEPLOYMENT.md)

## Current limitations

- The bundled dataset is synthetic and intended only for development.
- Authentication is limited to an admin key for management actions; end-user identity is not implemented.
- Feedback requires validation and dataset curation before retraining.
- Production deployments should use managed secrets, TLS, database migrations, backups, and external monitoring.
