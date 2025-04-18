from sqlalchemy.ext.asyncio import AsyncSession

from unittest.mock import AsyncMock, MagicMock


class MockAsyncSession(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(spec=AsyncSession, *args, **kwargs)
        self.add = MagicMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.delete = AsyncMock()
        self.get = AsyncMock()
        self.execute = AsyncMock()
