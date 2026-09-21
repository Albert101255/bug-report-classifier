# Project Recall — Bug Report Triage Platform

## One-line explanation
FastAPI/React application that predicts a bug-routing category with TF-IDF + Logistic Regression and sends uncertain predictions to human review.

## Model pipeline
Bug text -> TF-IDF vectorizer -> Logistic Regression -> class probabilities -> confidence/uncertainty -> prediction or review queue.

## Important limitation
The bundled dataset is synthetic. Do not quote its metrics as real-world performance.

## Main technical pieces
- FastAPI
- React/TypeScript
- scikit-learn
- PostgreSQL
- Redis/Celery
- Docker Compose
- Prometheus/Grafana

## Interview questions
1. Why TF-IDF instead of raw word counts?
2. Why Logistic Regression for text classification?
3. What does model confidence mean here?
4. Why should reviewer feedback be curated before retraining?
5. Which metrics matter if classes are imbalanced?

## Next improvements
- Real labelled dataset
- Per-class precision/recall/F1
- Error analysis
- CI/test visibility
