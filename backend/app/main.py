import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.models import Prediction
from app.routes import predict, history, review, analytics, teams, retrain, integrations, compare

# Prometheus Telemetry Metrics
PREDICTIONS_TOTAL = Counter("bug_predictions_total", "Total bug classification predictions", ["confidence_level"])
PREDICTION_LATENCY = Histogram("bug_prediction_latency_ms", "Bug prediction latency in milliseconds")
REVIEW_QUEUE_SIZE = Gauge("bug_review_queue_size", "Number of predictions awaiting human review")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as session:
        res = await session.execute(Prediction.__table__.select())
        first = res.first()
        if not first:
            seed_items = [
                ("User login failed with HTTP 500 when submitting OAuth token in auth service", "BL-101 (Authentication & AuthZ)", 0.94, 0.02, "HIGH", "auto_assigned"),
                ("Database connection pool exhausted during high load queries on postgres", "BL-102 (Database & ORM)", 0.88, 0.04, "HIGH", "auto_assigned"),
                ("React component CSS dropdown menu overflow issue in dark mode", "BL-103 (UI Components & Design System)", 0.96, 0.01, "HIGH", "auto_assigned"),
                ("Stripe payment webhook verification failed due to missing signature", "BL-104 (Payment Gateway & Billing)", 0.72, 0.12, "MEDIUM", "needs_review"),
                ("Kubernetes pod crashing with OOMKilled memory limit exception", "BL-105 (Cloud Infrastructure & K8s)", 0.91, 0.03, "HIGH", "auto_assigned"),
                ("Unclear stack trace in background worker thread execution", "BL-106 (API Gateway & Microservices)", 0.54, 0.22, "LOW", "needs_review")
            ]
            for desc, team, conf, unc, level, status in seed_items:
                p = Prediction(
                    id=f"pred-{uuid.uuid4().hex[:12]}",
                    bug_description=desc,
                    predicted_team=team,
                    confidence_score=conf,
                    uncertainty_score=unc,
                    confidence_level=level,
                    status=status,
                    top_alternatives=[{"team": "BL-106", "confidence": 0.15, "uncertainty": 0.08}],
                    top_keywords=[{"word": desc.split()[0].lower(), "score": 0.85}],
                    latency_ms=45.0,
                    user_id="seed_user"
                )
                session.add(p)
            await session.commit()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)
app.include_router(review.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(teams.router, prefix=settings.API_V1_STR)
app.include_router(retrain.router, prefix=settings.API_V1_STR)
app.include_router(integrations.router, prefix=settings.API_V1_STR)
app.include_router(compare.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/metrics", tags=["Observability"])
async def get_prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
