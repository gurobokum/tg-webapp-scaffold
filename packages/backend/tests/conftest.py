from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

import app.models.all  # noqa: F401
from app.conf import settings
from app.db import AsyncSessionMaker
from app.models.base import BaseModel


@pytest.fixture(scope="session")
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(settings.DATABASE_URL.get_secret_value())
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session_maker(db_engine: AsyncEngine) -> AsyncIterator[AsyncSessionMaker]:
    async with db_engine.connect() as conn:
        tx = await conn.begin()
        session_maker = async_sessionmaker(
            bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        yield session_maker
        await tx.rollback()
