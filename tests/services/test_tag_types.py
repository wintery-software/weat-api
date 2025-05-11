import datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Base
from app.models.tag import TagType
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate
from app.services.errors import ValidationError
from app.services.tag_types import (
    create_tag_type,
    delete_tag_type,
    list_tag_types,
    update_tag_type,
)
from tests.mocks.mock_uow import MockDBUoW


@pytest.fixture
def mock_tag_type() -> TagType:
    return TagType(
        id=uuid4(),
        name="Test Type",
        place_type="food",
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC),
    )


@pytest.mark.asyncio
async def test_create_tag_type_success() -> None:
    db = MockDBUoW()

    def fake_refresh(obj: Base) -> None:
        obj.id = uuid4()
        obj.created_at = (datetime.datetime.now(datetime.UTC),)
        obj.updated_at = (datetime.datetime.now(datetime.UTC),)

    db.refresh.side_effect = fake_refresh

    payload = TagTypeCreate(name="Cuisine", place_type="food")
    result = await create_tag_type(db, payload)

    assert isinstance(result, TagTypeResponse)
    assert result.name == "Cuisine"
    db.add.assert_awaited()
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_create_tag_type_integrity_error() -> None:
    db = MockDBUoW()
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(ValidationError):
        await create_tag_type(db, TagTypeCreate(name="Cuisine", place_type="food"))


@pytest.mark.asyncio
async def test_list_tag_types() -> None:
    db = MockDBUoW()
    db.get_all.return_value = [
        TagType(
            id=uuid4(),
            name="Style",
            place_type="food",
            created_at=datetime.datetime.now(datetime.UTC),
            updated_at=datetime.datetime.now(datetime.UTC),
        ),
    ]

    result = await list_tag_types(db, "food")

    assert len(result) == 1
    assert isinstance(result[0], TagTypeResponse)
    assert result[0].name == "Style"


@pytest.mark.asyncio
async def test_update_tag_type_success(mock_tag_type: TagType) -> None:
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag_type

    result = await update_tag_type(db, mock_tag_type.id, TagTypeUpdate(name="Updated"))

    assert isinstance(result, TagTypeResponse)
    assert result.name == "Updated"
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_update_tag_type_integrity_error(mock_tag_type: TagType) -> None:
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag_type
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(ValidationError):
        await update_tag_type(db, mock_tag_type.id, TagTypeUpdate(name="Boom"))


@pytest.mark.asyncio
async def test_delete_tag_type_success(mock_tag_type: TagType) -> None:
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag_type

    await delete_tag_type(db, mock_tag_type.id)

    db.delete.assert_awaited_with(mock_tag_type)
    db.commit.assert_awaited()
