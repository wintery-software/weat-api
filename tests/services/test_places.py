import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from geoalchemy2 import WKTElement
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.places import Place
from app.models.tags import Tag, TagType
from app.schemas.places import Location, PlaceCreate, PlaceUpdate, PlaceResponse
from app.services.places import (
    create_place,
    get_place,
    list_paginated_places,
    search_paginated_places,
    update_place,
    delete_place,
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
        location_geom=WKTElement("POINT(1.0 2.0)", srid=4326),
        opening_hours=[],
        properties={},
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )


@pytest.fixture
def mock_tag() -> Tag:
    tag_id = uuid4()
    tag_type_id = uuid4()

    return Tag(
        id=tag_id,
        name="Test Tag",
        tag_type_id=tag_type_id,
        tag_type=TagType(
            id=tag_type_id,
            name="Test Tag Type",
        ),
    )


@pytest.mark.asyncio
async def test_get_place(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = mock_place

    place_id = mock_place.id
    response = await get_place(db, place_id)
    assert isinstance(response, PlaceResponse)
    assert isinstance(response.location, Location)
    db.get_by_id.assert_awaited_with(Place, place_id)


@pytest.mark.asyncio
async def test_get_place_not_found(mock_place):
    db = MockDBUoW()
    db.get_by_id.return_value = None
    with pytest.raises(DBObjectNotFoundError):
        await get_place(db, uuid4())


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
    )

    response = await create_place(db, data)
    assert isinstance(response, PlaceResponse)
    db.add.assert_awaited()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_place_with_valid_tags(mock_tag):
    def fake_refresh_created(obj):
        setattr(obj, "id", uuid4())
        setattr(obj, "created_at", "2023-01-01T00:00:00Z")
        setattr(obj, "updated_at", "2023-01-01T00:00:00Z")

    db = MockDBUoW()
    db.get_all.return_value = [mock_tag]
    db.refresh.side_effect = fake_refresh_created

    data = PlaceCreate(
        name="Test",
        name_zh=None,
        type="food",
        tag_ids=[mock_tag.id],
    )

    response = await create_place(db, data)
    assert isinstance(response, PlaceResponse)
    db.add.assert_awaited()
    db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_create_place_with_invalid_tags(mock_tag):
    db = MockDBUoW()
    db.get_all.return_value = []

    data = PlaceCreate(
        name="Test",
        name_zh=None,
        type="food",
        tag_ids=[uuid4()],  # Invalid tag ID
    )

    with pytest.raises(InvalidTagIdError):
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


@pytest.mark.asyncio
async def test_list_places(mock_place):
    db = MockDBUoW()
    db.get_all.return_value = [mock_place]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 123
    db.execute.return_value = mock_count_result

    items, total = await list_paginated_places(db, page=1, page_size=10)
    assert len(items) == 1
    assert isinstance(items[0], PlaceResponse)
    assert total == 123


@pytest.mark.asyncio
async def test_list_places_with_valid_bounds(mock_place):
    db = MockDBUoW()
    db.get_all.return_value = [mock_place]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 123
    db.execute.return_value = mock_count_result

    sw_lat = 1
    sw_lng = 2
    ne_lat = 3
    ne_lng = 4
    items, total = await list_paginated_places(
        db,
        sw_lat=sw_lat,
        sw_lng=sw_lng,
        ne_lat=ne_lat,
        ne_lng=ne_lng,
        page=1,
        page_size=10,
    )
    assert len(items) == 1
    assert isinstance(items[0], PlaceResponse)
    assert total == 123

    # Check if the bounds are passed correctly
    stmt_passed = db.get_all.call_args.args[0]

    compiled_sql = str(stmt_passed.compile(compile_kwargs={"literal_binds": True}))
    assert (
        f"places.location_geom && ST_MakeEnvelope({sw_lng}, {sw_lat}, {ne_lng}, {ne_lat}, 4326)"
        in compiled_sql
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sw_lat, sw_lng, ne_lat, ne_lng",
    [
        (-91, 0, 0, 0),  # invalid sw_lat < -90
        (0, -181, 0, 0),  # invalid sw_lng < -180
        (0, 0, 91, 0),  # invalid ne_lat > 90
        (0, 0, 0, 181),  # invalid ne_lng > 180
        (10, 0, 5, 0),  # ne_lat < sw_lat
        (0, 10, 0, 5),  # ne_lng < sw_lng
    ],
)
async def test_list_places_with_invalid_bounds(
    mock_place, sw_lat, sw_lng, ne_lat, ne_lng
):
    db = MockDBUoW()
    db.get_all.return_value = [mock_place]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 123
    db.execute.return_value = mock_count_result

    with pytest.raises(ValueError):
        await list_paginated_places(
            db,
            sw_lat=sw_lat,
            sw_lng=sw_lng,
            ne_lat=ne_lat,
            ne_lng=ne_lng,
            page=1,
            page_size=10,
        )


@pytest.mark.asyncio
async def test_search_places(mock_place):
    db = MockDBUoW()
    db.get_all.return_value = [mock_place]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 123
    db.execute.return_value = mock_count_result

    q = "Test Query"
    items, total = await search_paginated_places(db, q=q, page=1, page_size=10)
    assert len(items) == 1
    assert isinstance(items[0], PlaceResponse)
    assert total == 123

    # Check if the query contains the search term
    stmt_passed = db.get_all.call_args.args[0]

    compiled_sql = str(stmt_passed.compile(compile_kwargs={"literal_binds": True}))
    assert f"{q}" in compiled_sql
    assert "places.name %" in compiled_sql
    assert "places.name_zh %" in compiled_sql
    assert "places.address %" in compiled_sql


@pytest.mark.asyncio
async def test_search_places_no_query(mock_place):
    db = MockDBUoW()
    db.get_all.return_value = [mock_place]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 123
    db.execute.return_value = mock_count_result

    q = None
    items, total = await search_paginated_places(db, q=q, page=1, page_size=10)
    assert len(items) == 1
    assert isinstance(items[0], PlaceResponse)
    assert total == 123

    # Check if the query does not contain the search term
    stmt_passed = db.get_all.call_args.args[0]

    compiled_sql = str(stmt_passed.compile(compile_kwargs={"literal_binds": True}))
    assert "LIKE" not in compiled_sql
