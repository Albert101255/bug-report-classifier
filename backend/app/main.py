import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routes import (
    analytics,
    compare,
    history,
    integrations,
    predict,
    retrain,
    review,
    teams,
)
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis import asyncio as aioredis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    redis = None
    try:
        redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
        )
        await redis.ping()
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        app.state.redis = redis
    except Exception:
        logger.warning(
            "Redis is unavailable; cache-dependent features are disabled", exc_info=True
        )
        app.state.redis = None

    yield

    if redis is not None:
        await redis.aclose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Key"],
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
async def health_check() -> dict:
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.get("/metrics", tags=["Observability"])
async def get_prometheus_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
