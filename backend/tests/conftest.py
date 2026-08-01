import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest_asyncio
from app.database import init_db
from app.main import app
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient

FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
