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

router = APIRouter(tags=["Places"])


@router.get(
    "/places/",
)
async def list_places(  # noqa: PLR0913, PLR0917
    db: Annotated[AsyncSession, Depends(get_db)],
    sw_lat: float = -90,
    sw_lng: float = -180,
    ne_lat: float = 90,
    ne_lng: float = 180,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[SimplePlaceResponse]:
    """List all places within the specified bounds.

    Args:
        db (AsyncSession): The database session.
        sw_lat (float, optional): Southwest latitude. Defaults to -90.
        sw_lng (float, optional): Southwest longitude. Defaults to -180.
        ne_lat (float, optional): Northeast latitude. Defaults to 90.
        ne_lng (float, optional): Northeast longitude. Defaults to 180.
        page (int, optional): The page number for pagination. Defaults to 1.
        page_size (int, optional): The number of items per page. Defaults to 10.

    Returns:
        PaginatedResponse[SimplePlaceResponse]: A paginated response containing the list of places.

    """
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


@router.get("/places/search")
async def search_places(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedResponse[PlaceResponse]:
    """Search for places by name or description.

    Args:
        q (str, optional): The search query. Defaults to None.
        page (int, optional): The page number for pagination. Defaults to 1.
        page_size (int, optional): The number of items per page. Defaults to 10.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PaginatedResponse[PlaceResponse]: A paginated response containing the list of places.

    """
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


@router.post(
    "/places/",
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_create: PlaceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Create a new place.

    Args:
        place_create (PlaceCreate): The place data to create.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PlaceResponse: The created place.

    """
    return await places_service.create_place(
        db=db,
        place_create=place_create,
    )


@router.get("/places/{place_id}")
async def get_place(
    place_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Get a place by ID.

    Args:
        place_id (UUID): The ID of the place to retrieve.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PlaceResponse: The retrieved place.

    """
    return await places_service.get_place(
        db=db,
        place_id=place_id,
    )


@router.put(
    "/places/{place_id}",
    response_model_exclude_unset=True,
)
async def update_place(
    place_id: UUID,
    place_update: PlaceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlaceResponse:
    """Update a place by ID.

    Args:
        place_id (UUID): The ID of the place to update.
        place_update (PlaceUpdate): The updated place data.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    Returns:
        PlaceResponse: The updated place.

    """
    return await places_service.update_place(
        db=db,
        place_id=place_id,
        place_update=place_update,
    )


@router.delete(
    "/places/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_place(
    place_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a place by ID.

    Args:
        place_id (UUID): The ID of the place to delete.
        db (AsyncSession, optional): The database session. Defaults to Depends(get_db).

    """
    await places_service.delete_place(
        db=db,
        place_id=place_id,
    )
