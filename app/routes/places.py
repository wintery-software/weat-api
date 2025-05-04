from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.places as places_service
from app.routes.helpers import get_db
from app.schemas.pagination import PaginatedResponse
from app.schemas.places import (
    LocationBounds,
    PlaceCreate,
    PlaceResponse,
    PlaceUpdate,
    SimplePlaceResponse,
)

router = APIRouter(prefix="/places", tags=["Places"])
protected_router = APIRouter(prefix="/places")


@router.get(
    "/",
)
async def list_places(
    db: Annotated[AsyncSession, Depends(get_db)],
    sw_lat: float = -90,
    sw_lng: float = -180,
    ne_lat: float = 90,
    ne_lng: float = 180,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[SimplePlaceResponse]:
    """List all places within the specified bounds."""
    items, total = await places_service.list_paginated_places(
        db=db,
        bounds=LocationBounds(
            sw_lat=sw_lat,
            sw_lng=sw_lng,
            ne_lat=ne_lat,
            ne_lng=ne_lng,
        ),
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[SimplePlaceResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/search")
async def search_places(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[PlaceResponse]:
    """Search for places by name or description."""
    items, total = await places_service.search_paginated_places(
        db=db,
        q=q,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[PlaceResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{place_id}")
async def get_place(
    place_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Get a place by ID."""
    return await places_service.get_place(
        db=db,
        place_id=place_id,
    )


@protected_router.get(
    "/",
)
async def list_places_protected(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[PlaceResponse]:
    """List all places."""
    items, total = await places_service.list_paginated_places(
        db=db,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[PlaceResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@protected_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_create: PlaceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Create a new place."""
    return await places_service.create_place(
        db=db,
        place_create=place_create,
    )


@protected_router.put(
    "/{place_id}",
    response_model_exclude_unset=True,
)
async def update_place(
    place_id: UUID,
    place_update: PlaceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Update a place by ID."""
    return await places_service.update_place(
        db=db,
        place_id=place_id,
        place_update=place_update,
    )


@protected_router.delete(
    "/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_place(
    place_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a place by ID."""
    await places_service.delete_place(
        db=db,
        place_id=place_id,
    )
