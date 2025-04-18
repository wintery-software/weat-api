import datetime
import uuid
from unittest.mock import ANY, AsyncMock

from fastapi import status
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from app.main import app
from app.schemas.places import (
    PlaceCreate,
    PlaceResponse,
    PlaceUpdate,
)
import app.services.places as places_service


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_get_place_endpoint(async_client, monkeypatch):
    place_id = uuid.uuid4()
    mock_place = PlaceResponse(
        id=place_id,
        name="Test Place",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(places_service, "get_place", AsyncMock(return_value=mock_place))

    response = await async_client.get(f"/places/{place_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Place"
    places_service.get_place.assert_awaited_once_with(
        db=ANY,
        place_id=place_id,
    )


@pytest.mark.asyncio
async def test_create_place_endpoint(async_client, monkeypatch):
    mock_place = PlaceResponse(
        id=uuid.uuid4(),
        name="New Place",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        places_service, "create_place", AsyncMock(return_value=mock_place)
    )

    payload = {"name": "New Place", "type": "food"}
    response = await async_client.post("/places/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Place"
    places_service.create_place.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_place_endpoint_with_tags(async_client, monkeypatch):
    mock_place = PlaceResponse(
        id=uuid.uuid4(),
        name="New Place with Tags",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
        tags=[
            {
                "id": uuid.uuid4(),
                "name": "Tag1",
                "tag_type_name": "Type1",
                "tag_type_id": uuid.uuid4(),
            },
        ],
    )
    monkeypatch.setattr(
        places_service, "create_place", AsyncMock(return_value=mock_place)
    )

    payload = {
        "name": "New Place with Tags",
        "type": "food",
        "tag_ids": [str(uuid.uuid4())],
    }
    response = await async_client.post("/places/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "New Place with Tags"
    places_service.create_place.assert_awaited_once_with(
        db=ANY,
        place_create=PlaceCreate(**payload),
    )


@pytest.mark.asyncio
async def test_update_place_endpoint(async_client, monkeypatch):
    place_id = uuid.uuid4()
    updated_place = PlaceResponse(
        id=place_id,
        name="Updated Name",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        places_service, "update_place", AsyncMock(return_value=updated_place)
    )

    payload = {"name": "Updated Name"}
    response = await async_client.put(f"/places/{place_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    places_service.update_place.assert_awaited_once_with(
        db=ANY,
        place_id=place_id,
        place_update=PlaceUpdate(**payload),
    )


@pytest.mark.asyncio
async def test_delete_place_endpoint(async_client, monkeypatch):
    monkeypatch.setattr(places_service, "delete_place", AsyncMock(return_value=None))

    place_id = uuid.uuid4()
    response = await async_client.delete(f"/places/{place_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    places_service.delete_place.assert_awaited_once_with(db=ANY, place_id=place_id)


@pytest.mark.asyncio
async def test_list_places_endpoint(async_client, monkeypatch):
    mock_place = PlaceResponse(
        id=uuid.uuid4(),
        name="List Place",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        places_service,
        "list_paginated_places",
        AsyncMock(return_value=([mock_place], 1)),
    )

    response = await async_client.get("/places/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "List Place"
    places_service.list_paginated_places.assert_awaited_once_with(
        db=ANY, page=1, page_size=10
    )


@pytest.mark.asyncio
async def test_list_places_with_pagination(async_client, monkeypatch):
    mock_place = PlaceResponse(
        id=uuid.uuid4(),
        name="Paginated Place",
        type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        places_service,
        "list_paginated_places",
        AsyncMock(return_value=([mock_place], 2)),
    )

    response = await async_client.get("/places/?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["name"] == "Paginated Place"
    places_service.list_paginated_places.assert_awaited_once_with(
        db=ANY, page=1, page_size=1
    )
