# Bug Report Triage Platform

A FastAPI + React application that classifies software bug reports, stores prediction history, exposes uncertain cases for human review, and supports a reproducible TF-IDF + Logistic Regression baseline.

## Why this project exists

Bug triage is a useful example of human-in-the-loop machine learning: a model can make an initial routing suggestion, while low-confidence cases remain visible for review instead of being silently accepted.

## Classifier

The primary baseline uses:

- scikit-learn
- TF-IDF text features
- multinomial Logistic Regression

Confidence is based on predicted class probability. The application also calculates uncertainty as `1 - confidence`.

When trained model artifacts are unavailable, the API falls back to a clearly identified deterministic keyword system so local demonstrations still work.

## Important dataset note

The dataset bundled with the repository is **synthetic and intended for development/demo use**. Metrics produced from that dataset should not be presented as evidence of real-world classifier performance.

## Features

- Single bug classification
- Batch classification
- React + TypeScript dashboard
- PostgreSQL prediction/audit history
- Human review queue
- Reviewer feedback capture
- Redis cache
- Celery worker
- Prometheus metrics
- Grafana dashboards
- Docker Compose environment
- Training script with accuracy and macro-F1 reporting

## Quick start

```bash
cp .env.example .env
python -m pip install -r requirements.txt
python scripts/train_baseline.py
docker compose up --build
```

Typical local services:

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`

## Model artifacts

Training writes artifacts such as:

- TF-IDF vectorizer
- classifier
- metadata
- classification report

Generated model files and large presentation/media artifacts should be kept under review so the repository stays lightweight.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API_DOCS.md)
- [Deployment](docs/DEPLOYMENT.md)

## Current limitations

- Bundled training data is synthetic
- End-user identity/authentication is limited
- Human feedback requires curation before retraining
- Public deployment would need managed secrets, TLS, migrations, backups and stronger monitoring

## Next improvements

- Evaluate on a real labelled bug dataset
- Add screenshots / demo GIF to the README
- Surface CI/test status
- Track precision/recall/F1 per class
- Document model error analysis
