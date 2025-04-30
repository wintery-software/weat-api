from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession


class MockAsyncSession(MagicMock):
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args, spec=AsyncSession, **kwargs)
        self.add = MagicMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.delete = AsyncMock()
        self.get = AsyncMock()
        self.execute = AsyncMock()
