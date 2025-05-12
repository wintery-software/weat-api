import datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Base
from app.models.tag import Tag, TagType
from app.schemas.tags import TagCreate, TagResponse, TagUpdate
from app.services.errors import ObjectNotFoundError, ValidationError
from app.services.tags import create_tag, delete_tag, list_tags, update_tag
from tests.mocks.mock_uow import MockDBUoW


@pytest.fixture
def mock_tag() -> Tag:
    tag_type_id = uuid4()
    return Tag(
        id=uuid4(),
        name="Test Tag",
        tag_type_id=tag_type_id,
        tag_type=TagType(
            id=tag_type_id,
            name="Test Type",
            place_type="food",
        ),
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC),
    )


@pytest.mark.asyncio
async def test_create_tag_success() -> None:
    db = MockDBUoW()

    def fake_refresh(obj: Base) -> None:
        obj.id = uuid4()
        obj.created_at = datetime.datetime.now(datetime.UTC)
        obj.updated_at = datetime.datetime.now(datetime.UTC)
        obj.tag_type = TagType(
            id=uuid4(),
            name="Test Type",
            place_type="food",
        )

    db.refresh.side_effect = fake_refresh

    payload = TagCreate(name="Cuisine", tag_type_id=uuid4())
    result = await create_tag(db, payload)

    assert isinstance(result, TagResponse)
    assert result.name == "Cuisine"
    db.add.assert_awaited()
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_create_tag_integrity_error() -> None:
    db = MockDBUoW()
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(ValidationError):
        await create_tag(db, TagCreate(name="Cuisine", tag_type_id=uuid4()))


@pytest.mark.asyncio
async def test_list_tags_success(mock_tag: Tag) -> None:
    db = MockDBUoW()
    db.get_all.return_value = [mock_tag]

    result = await list_tags(db, place_type="food")
    assert isinstance(result, list)
    assert isinstance(result[0], TagResponse)
    assert result[0].name == mock_tag.name


@pytest.mark.asyncio
async def test_update_tag_success(mock_tag: Tag) -> None:
    db = MockDBUoW()
    db.get.return_value = mock_tag

    updated = await update_tag(
        db,
        mock_tag.id,
        TagUpdate(name="Updated", tag_type_id=uuid4()),
    )
    assert isinstance(updated, TagResponse)
    assert updated.name == "Updated"
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_update_tag_integrity_error(mock_tag: Tag) -> None:
    db = MockDBUoW()
    db.get.return_value = mock_tag
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(ValidationError):
        await update_tag(
            db,
            mock_tag.id,
            TagUpdate(name="Fail", tag_type_id=uuid4()),
        )


@pytest.mark.asyncio
async def test_delete_tag_success(mock_tag: Tag) -> None:
    db = MockDBUoW()
    db.get.return_value = mock_tag

    await delete_tag(db, mock_tag.id)
    db.delete.assert_awaited_with(mock_tag)
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_delete_tag_not_found(mock_uow: MockDBUoW) -> None:
    mock_uow.get.return_value = None

    with pytest.raises(ObjectNotFoundError):
        await delete_tag(mock_uow, uuid4())
