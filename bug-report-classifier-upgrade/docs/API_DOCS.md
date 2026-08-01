# API Specification

The FastAPI service runs on port `8000`. Swagger documentation is available at `http://localhost:8000/docs`.

## Endpoints

- `POST /api/v1/predict/single` — classify one bug report.
- `POST /api/v1/predict/batch` — classify 1–100 bug reports.
- `GET /api/v1/predict/history` — retrieve prediction history.
- `GET /api/v1/predict/review-queue` — list predictions requiring review.
- `POST /api/v1/feedback/correct` — record a reviewer correction.
- `GET /api/v1/analytics/summary` — retrieve summary analytics.
- `GET /api/v1/teams/list` — list routing teams.
- `GET /api/v1/models/info` — show the active engine and model version.
- `POST /api/v1/models/retrain` — queue baseline retraining; requires `X-Admin-Key`.
- `GET /health` — service health.
- `GET /metrics` — Prometheus metrics.

## Confidence semantics

`confidence_score` is the selected class probability. `uncertainty_score` is `1 - confidence_score`. Thresholds are configured through environment variables.
