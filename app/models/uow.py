from collections.abc import Callable
from types import TracebackType
from typing import TypeVar

from sqlalchemy import Executable, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class DBUnitOfWork:
    """Database unit of work class.

    This class provides a context manager for managing database sessions and transactions.
    It allows for executing queries, adding instances, committing transactions, and handling
    rollbacks in case of errors.
    """

    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        """Initialize the database unit of work.

        Args:
            session_factory (Callable[[], AsyncSession]): A callable that returns an AsyncSession.

        """
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._committed = False

    async def __aenter__(self) -> "DBUnitOfWork":
        """Enter the database unit of work context manager.

        Returns:
            DBUnitOfWork: The database unit of work instance.

        """
        self._session = self._session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the database unit of work context manager.

        Args:
            exc_type (type[BaseException] | None): The exception type, if any.
            exc_val (BaseException | None): The exception value, if any.
            exc_tb (TracebackType | None): The traceback, if any.

        """
        if not self._session:
            return

        try:
            if exc_type or not self._committed:
                await self._session.rollback()
        finally:
            await self._session.close()

    async def get_by_id(self, model: T, model_id: int) -> T | None:
        """Get an instance by its ID.

        Args:
            model: The SQLAlchemy model class.
            model_id: The ID of the instance to retrieve.

        Returns:
            T | None: The instance if found, otherwise None.

        """
        stmt = select(model).where(model.id == model_id)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_one_or_none(self, stmt: Executable) -> T | None:
        """Get one or none result from a SQL statement.

        Args:
            stmt (Executable): The SQL statement to execute

        Returns:
            T | None: The result or None if no result is found.

        """
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all(self, stmt: Executable) -> list[T]:
        """Get all results from a SQL statement.

        Args:
            stmt (Executable): The SQL statement to execute

        Returns:
            list[T]: A list of results.

        """
        result = await self._session.execute(stmt)
        return result.unique().scalars().all()

    async def execute(self, stmt: Executable) -> None:
        """Execute a SQL statement.

        Args:
            stmt (Executable): The SQL statement to execute

        """
        return await self._session.execute(stmt)

    async def add(self, instance: T) -> None:
        """Add an instance to the session.

        Args:
            instance (T): The instance to add.

        """
        self._session.add(instance)

    async def commit(self) -> None:
        """Commit the current transaction.

        This method commits the current transaction to the database. If an error occurs,
        it rolls back the transaction and raises the error.

        Raises:
            SQLAlchemyError: If an error occurs during the commit.

        """
        try:
            await self._session.commit()
            self._committed = True
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def flush(self) -> None:
        """Flush the session.

        This method flushes the current session, sending any pending changes to the database.
        """
        await self._session.flush()

    async def refresh(self, instance: T) -> None:
        """Refresh the instance from the database.

        Args:
            instance (T): The instance to refresh.

        """
        await self._session.refresh(instance)

    async def delete(self, instance: T) -> None:
        """Delete the instance from the database.

        Args:
            instance (T): The instance to delete.

        """
        await self._session.delete(instance)
