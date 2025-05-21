from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, Self

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session


class BaseRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    @classmethod
    async def inject(
        cls, db_session: Annotated[AsyncSession, Depends(get_db_session)]
    ) -> Self:
        """
        Works only in FastAPI environment because requires Request
        """
        return cls(db_session)

    # Subtransactions
    # https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#session-subtransaction-behavior-removed
    # https://github.com/sqlalchemy/sqlalchemy/discussions/12140
    @asynccontextmanager
    async def tx(self) -> AsyncGenerator[None, None]:
        if self.db_session.in_transaction():
            yield
            return
        async with self.db_session.begin():
            yield


class BaseService(BaseRepository): ...
