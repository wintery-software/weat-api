import datetime
import uuid
from unittest.mock import AsyncMock, ANY

import pytest
import pytest_asyncio
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.tags import TagCreate, TagUpdate, TagResponse
import app.services.tags as tags_service


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_create_tag_endpoint(async_client, monkeypatch):
    mock_tag = TagResponse(
        id=uuid.uuid4(),
        name="Tag1",
        tag_type_id=uuid.uuid4(),
        tag_type_name="Cuisine",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(tags_service, "create_tag", AsyncMock(return_value=mock_tag))

    payload = {"name": "Tag1", "tag_type_id": str(mock_tag.tag_type_id)}
    response = await async_client.post("/tags/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == "Tag1"
    tags_service.create_tag.assert_awaited_once_with(
        db=ANY, tag_create=TagCreate(**payload)
    )


@pytest.mark.asyncio
async def test_list_tags_endpoint(async_client, monkeypatch):
    mock_tag = TagResponse(
        id=uuid.uuid4(),
        name="Tag2",
        tag_type_id=uuid.uuid4(),
        tag_type_name="Style",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(tags_service, "list_tags", AsyncMock(return_value=[mock_tag]))

    response = await async_client.get("/tags/food")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Tag2"
    tags_service.list_tags.assert_awaited_once_with(db=ANY, place_type="food")


@pytest.mark.asyncio
async def test_update_tag_endpoint(async_client, monkeypatch):
    tag_id = uuid.uuid4()
    updated_tag = TagResponse(
        id=tag_id,
        name="Updated Tag",
        tag_type_id=uuid.uuid4(),
        tag_type_name="Cuisine",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    monkeypatch.setattr(tags_service, "update_tag", AsyncMock(return_value=updated_tag))

    payload = {"name": "Updated Tag", "tag_type_id": str(updated_tag.tag_type_id)}
    response = await async_client.put(f"/tags/{tag_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Tag"
    tags_service.update_tag.assert_awaited_once_with(
        db=ANY,
        tag_id=tag_id,
        tag_update=TagUpdate(**payload),
    )


@pytest.mark.asyncio
async def test_delete_tag_endpoint(async_client, monkeypatch):
    monkeypatch.setattr(tags_service, "delete_tag", AsyncMock(return_value=None))

    tag_id = uuid.uuid4()
    response = await async_client.delete(f"/tags/{tag_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    tags_service.delete_tag.assert_awaited_once_with(db=ANY, tag_id=tag_id)
