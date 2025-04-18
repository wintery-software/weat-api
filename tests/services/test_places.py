import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.places import Place
from app.schemas.places import PlaceCreate, PlaceUpdate, PlaceResponse
from app.services.places import (
    _get_place_by_id,
    _get_tags_by_ids,
    create_place,
    get_place,
    update_place,
    delete_place,
    _validate_tags,
)
from app.services.errors import (
    DBObjectNotFoundError,
    DBValidationError,
    InvalidTagIdError,
)
from tests.mocks.mock_uow import MockDBUoW


@pytest.fixture
def mock_place() -> Place:
    return Place(
        id=uuid4(),
        name="Test Place",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )


@pytest.mark.asyncio
async def test_validate_tags_valid():
    tag_id = uuid4()
    tag = MagicMock()
    tag.id = tag_id
    _validate_tags([tag], [tag_id])  # Should not raise


@pytest.mark.asyncio
async def test_validate_tags_invalid():
    with pytest.raises(InvalidTagIdError):
        _validate_tags([], [uuid4()])


@pytest.mark.asyncio
async def test_get_place_by_id_found(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_place
    place = await _get_place_by_id(db, uuid4())
    assert place == mock_place


@pytest.mark.asyncio
async def test_get_place_by_id_not_found():
    db = MockDBUoW()
    db.get_by_id.return_value = None
    with pytest.raises(DBObjectNotFoundError):
        await _get_place_by_id(db, uuid4())


@pytest.mark.asyncio
async def test_get_tags_by_ids():
    db = MockDBUoW()
    mock_tags = [MagicMock()]
    db.get_all.return_value = mock_tags
    result = await _get_tags_by_ids(db, [uuid4()])
    assert result == mock_tags


@pytest.mark.asyncio
async def test_create_place_success():
    def fake_refresh_created(obj):
        setattr(obj, "id", uuid4())
        setattr(obj, "created_at", "2023-01-01T00:00:00Z")
        setattr(obj, "updated_at", "2023-01-01T00:00:00Z")

    db = MockDBUoW()
    db.get_all.return_value = []
    db.refresh.side_effect = fake_refresh_created

    data = PlaceCreate(
        name="Test",
        name_zh=None,
        type="food",
        address=None,
        latitude=None,
        longitude=None,
        google_maps_url=None,
        google_maps_place_id=None,
        phone_number=None,
        website_url=None,
        opening_hours=[],
        properties={},
        tag_ids=[],
    )

    response = await create_place(db, data)
    assert isinstance(response, PlaceResponse)
    db.add.assert_awaited()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_place_integrity_error():
    db = MockDBUoW()
    db.get_all.return_value = []
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    data = PlaceCreate(
        name="Test",
        name_zh=None,
        type="food",
        address=None,
        latitude=None,
        longitude=None,
        google_maps_url=None,
        google_maps_place_id=None,
        phone_number=None,
        website_url=None,
        opening_hours=[],
        properties={},
        tag_ids=[],
    )

    with pytest.raises(DBValidationError):
        await create_place(db, data)


@pytest.mark.asyncio
async def test_create_place_integrity_error():
    db = MockDBUoW()
    db.get_all.return_value = []
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    data = PlaceCreate(
        name="Test",
        name_zh=None,
        type="food",
        address=None,
        latitude=None,
        longitude=None,
        google_maps_url=None,
        google_maps_place_id=None,
        phone_number=None,
        website_url=None,
        opening_hours=[],
        properties={},
        tag_ids=[],
    )

    with pytest.raises(DBValidationError):
        await create_place(db, data)


@pytest.mark.asyncio
async def test_get_place_success(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_place
    response = await get_place(db, uuid4())
    assert isinstance(response, PlaceResponse)


@pytest.mark.asyncio
async def test_update_place_success(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_place
    db.get_all.return_value = []

    data = PlaceUpdate(name="Updated", tag_ids=[])
    response = await update_place(db, uuid4(), data)
    assert isinstance(response, PlaceResponse)
    assert response.name == "Updated"
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_update_place_integrity_error():
    db = MockDBUoW()
    db.get_by_id.return_value = MagicMock()
    db.get_all.return_value = []
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    data = PlaceUpdate(name="Fail", tag_ids=[])

    with pytest.raises(DBValidationError):
        await update_place(db, uuid4(), data)


@pytest.mark.asyncio
async def test_delete_place(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_place

    await delete_place(db, mock_place.id)
    db.delete.assert_awaited_with(mock_place)
    db.commit.assert_awaited()
