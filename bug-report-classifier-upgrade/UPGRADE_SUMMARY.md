# Upgrade summary

## Implemented

- Replaced simulated Monte Carlo behavior with a real TF-IDF + Logistic Regression training and inference path.
- Added deterministic fallback classification when artifacts are missing.
- Removed random confidence and keyword values.
- Added model metadata, evaluation output, and automatic artifact reload.
- Added a real Celery retraining task that trains from a configured CSV.
- Protected retraining with `X-Admin-Key` and an enable flag.
- Moved credentials, model paths, dataset paths, and CORS origins to environment variables.
- Removed host exposure for PostgreSQL and Redis in Docker Compose.
- Added a Celery worker service and pinned infrastructure image tags.
- Added backend tests, frontend lint/build CI, and Compose validation.
- Rewrote documentation so it accurately describes the implementation.

## Still required before claiming production readiness

- Replace the synthetic demo dataset with a licensed, representative dataset.
- Add Alembic migrations.
- Add user authentication and role-based authorization.
- Curate reviewer corrections before adding them to the training dataset.
- Add deployment TLS, backups, managed secrets, and monitoring alerts.
