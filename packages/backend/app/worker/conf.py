import contextlib
import functools
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Callable, Protocol, TypedDict

import structlog
from arq.connections import RedisSettings
from arq.worker import Function, func
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.conf import settings
from app.db import AsyncSessionMaker, create_async_engine, create_session_maker

logger = structlog.get_logger()


class WorkerContext(TypedDict):
    engine: AsyncEngine
    db_session_maker: AsyncSessionMaker


class JobContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    job_id: str
    job_try: int
    enqueue_time: datetime
    score: int

    engine: AsyncEngine
    db_session_maker: AsyncSessionMaker
    db_session: AsyncSession

    @contextlib.asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.db_session_maker() as db_session:
            try:
                yield db_session
            finally:
                await db_session.aclose()


class WorkerSettings:
    functions: list[Function] = []
    queue_name: str = "tg-webapp:queue"
    job_timeout = 60 * 60

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL.get_secret_value())

    @staticmethod
    async def on_startup(ctx: WorkerContext) -> None:
        logger.info("Worker startup")
        engine = ctx["engine"] = create_async_engine(settings.DATABASE_URL, "worker")
        ctx["db_session_maker"] = create_session_maker(engine)

    @staticmethod
    async def on_shutdown(ctx: WorkerContext) -> None:
        await ctx["engine"].dispose()
        logger.info("Worker shutdown")


class Task[**P](Protocol):
    async def __call__(
        self, ctx: JobContext, *args: P.args, **kwargs: P.kwargs
    ) -> Any: ...


def task[**P](
    name: str,
) -> Callable[[Task[P]], Task[P]]:
    def decorator(
        f: Task[P],
    ) -> Task[P]:
        @functools.wraps(f)
        async def _func(ctx: dict[Any, Any], *args: P.args, **kwargs: P.kwargs) -> Any:
            db_session_maker = ctx["db_session_maker"]
            if not db_session_maker:
                raise ValueError("Database session maker is None")

            async with db_session_maker() as db_session:
                job_context = JobContext.model_validate(
                    {**ctx, "db_session": db_session}
                )
                return await f(job_context, *args, **kwargs)

        job = func(_func, name=name)
        WorkerSettings.functions.append(job)

        return f

    return decorator
