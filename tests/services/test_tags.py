import datetime
import pytest
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.models.tags import Tag, TagType
from app.schemas.tags import TagCreate, TagUpdate, TagResponse
from app.services.tags import create_tag, list_tags, update_tag, delete_tag
from app.services.errors import DBValidationError, DBObjectNotFoundError
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
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_tag_success():
    db = MockDBUoW()

    def fake_refresh(obj):
        obj.id = uuid4()
        obj.created_at = datetime.datetime.now(datetime.timezone.utc)
        obj.updated_at = datetime.datetime.now(datetime.timezone.utc)
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
async def test_create_tag_integrity_error():
    db = MockDBUoW()
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(DBValidationError):
        await create_tag(db, TagCreate(name="Cuisine", tag_type_id=uuid4()))


@pytest.mark.asyncio
async def test_list_tags_success(mock_tag):
    db = MockDBUoW()
    db.get_all.return_value = [mock_tag]

    result = await list_tags(db, place_type="food")
    assert isinstance(result, list)
    assert isinstance(result[0], TagResponse)
    assert result[0].name == mock_tag.name


@pytest.mark.asyncio
async def test_update_tag_success(mock_tag):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag

    updated = await update_tag(
        db, mock_tag.id, TagUpdate(name="Updated", tag_type_id=uuid4())
    )
    assert isinstance(updated, TagResponse)
    assert updated.name == "Updated"
    db.commit.assert_awaited()
    db.refresh.assert_awaited()


@pytest.mark.asyncio
async def test_update_tag_integrity_error(mock_tag):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag
    db.commit.side_effect = IntegrityError("stmt", {}, Exception())

    with pytest.raises(DBValidationError):
        await update_tag(
            db,
            mock_tag.id,
            TagUpdate(name="Fail", tag_type_id=uuid4()),
        )


@pytest.mark.asyncio
async def test_delete_tag_success(mock_tag):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_tag

    await delete_tag(db, mock_tag.id)
    db.delete.assert_awaited_with(mock_tag)
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_tag_not_found():
    db = MockDBUoW()
    db.get_by_id.side_effect = DBObjectNotFoundError(Tag, uuid4())

    with pytest.raises(DBObjectNotFoundError):
        await delete_tag(db, uuid4())
