import pytest

from tests.mocks.mock_uow import MockDBUoW


@pytest.fixture
def mock_uow() -> MockDBUoW:
    """Mock a DBUnitOfWork instance.

    Returns:
        MockDBUoW: a MockDBUoW instance.

    """
    return MockDBUoW()
