from typing import Callable, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class DBUnitOfWork:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._committed = False

    async def __aenter__(self) -> "DBUnitOfWork":
        self._session = self._session_factory()
        return self
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._session:
            return

        try:
            if exc_type or not self._committed:
                await self._session.rollback()
        finally:
            await self._session.close()

    async def get_by_id(self, model, id):
        stmt = select(model).where(model.id == id)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_one_or_none(self, stmt):
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all(self, stmt):
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def execute(self, stmt):
        result = await self._session.execute(stmt)
        return result

    async def add(self, instance):
        self._session.add(instance)

    async def commit(self):
        try:
            await self._session.commit()
            self._committed = True
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def flush(self):
        await self._session.flush()

    async def refresh(self, instance):
        await self._session.refresh(instance)

    async def delete(self, instance):
        await self._session.delete(instance)
