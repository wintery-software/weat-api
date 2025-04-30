from unittest.mock import AsyncMock


class MockDBUoW:
    def __init__(self) -> None:
        self.add = AsyncMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.delete = AsyncMock()
        self.get_by_id = AsyncMock()
        self.get_all = AsyncMock()
        self.execute = AsyncMock()
