import datetime
import uuid
from unittest.mock import AsyncMock, ANY

import pytest
import pytest_asyncio
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.tag_types import TagTypeCreate, TagTypeUpdate, TagTypeResponse
import app.services.tag_types as tag_types_service


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_create_tag_type_endpoint(async_client, monkeypatch):
    mock_tag_type = TagTypeResponse(
        id=uuid.uuid4(),
        name="Cuisine",
        place_type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        tag_types_service, "create_tag_type", AsyncMock(return_value=mock_tag_type)
    )

    payload = {"name": "Cuisine", "place_type": "food"}
    response = await async_client.post("/tag-types/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Cuisine"
    tag_types_service.create_tag_type.assert_awaited_once_with(
        db=ANY, tag_type_create=TagTypeCreate(**payload)
    )


@pytest.mark.asyncio
async def test_list_tag_types_endpoint(async_client, monkeypatch):
    mock_tag_type = TagTypeResponse(
        id=uuid.uuid4(),
        name="Style",
        place_type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        tag_types_service, "list_tag_types", AsyncMock(return_value=[mock_tag_type])
    )

    response = await async_client.get("/tag-types/food")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Style"
    tag_types_service.list_tag_types.assert_awaited_once_with(db=ANY, place_type="food")


@pytest.mark.asyncio
async def test_update_tag_type_endpoint(async_client, monkeypatch):
    tag_type_id = uuid.uuid4()
    updated_tag_type = TagTypeResponse(
        id=tag_type_id,
        name="Updated",
        place_type="food",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(
        tag_types_service, "update_tag_type", AsyncMock(return_value=updated_tag_type)
    )

    payload = {"name": "Updated"}
    response = await async_client.put(f"/tag-types/{tag_type_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated"
    tag_types_service.update_tag_type.assert_awaited_once_with(
        db=ANY,
        tag_type_id=tag_type_id,
        tag_type_update=TagTypeUpdate(**payload),
    )


@pytest.mark.asyncio
async def test_delete_tag_type_endpoint(async_client, monkeypatch):
    monkeypatch.setattr(
        tag_types_service, "delete_tag_type", AsyncMock(return_value=None)
    )

    tag_type_id = uuid.uuid4()
    response = await async_client.delete(f"/tag-types/{tag_type_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    tag_types_service.delete_tag_type.assert_awaited_once_with(
        db=ANY, tag_type_id=tag_type_id
    )
