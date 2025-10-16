import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from mars_probe_api.app import app
from mars_probe_api.database import get_session
from mars_probe_api.models import Probe, table_registry


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def app_client(db_session):
    async def get_session_override():
        yield db_session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def probe_a(db_session):
    probe = Probe(size_x=5, size_y=5, direction="NORTH")
    db_session.add(probe)
    await db_session.commit()
    await db_session.refresh(probe)
    return probe


@pytest_asyncio.fixture
async def probe_b(db_session):
    probe = Probe(size_x=3, size_y=3, direction="EAST")
    db_session.add(probe)
    await db_session.commit()
    await db_session.refresh(probe)
    return probe
