# Bug Report Classifier API Specification

The backend service is powered by **FastAPI** on port `8000` with Swagger auto-docs available at `http://localhost:8000/docs`.

## Key Endpoints

- `POST /api/v1/predict/single`: Execute single bug report classification with MC Dropout uncertainty estimation.
- `POST /api/v1/predict/batch`: Batch process multiple bug reports from CSV payload.
- `GET /api/v1/predict/history`: Fetch prediction history and audit logs with team/level filtering.
- `GET /api/v1/predict/review-queue`: List low-confidence predictions awaiting human triage.
- `POST /api/v1/feedback/correct`: Log human correction and update team assignment.
- `GET /api/v1/analytics/summary`: Fetch team accuracy breakdown, total volume, and trend stats.
- `GET /api/v1/teams/list`: List all cataloged backlog teams.
- `POST /api/v1/models/retrain`: Trigger active learning model retraining using logged human feedback.
- `GET /metrics`: Prometheus telemetry metrics.
