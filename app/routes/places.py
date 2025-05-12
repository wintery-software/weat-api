from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.services.places as places_service
from app.routes.depends import get_db, get_filter_options, get_location_bounds, get_pagination_options, get_sort_options
from app.schemas.options import FilterOptions, PaginationOptions, SortOptions
from app.schemas.pagination import PaginatedResponse
from app.schemas.places import (
    LocationBounds,
    PlaceCreate,
    PlaceResponse,
    PlaceUpdate,
)

router = APIRouter(prefix="/places", tags=["Places"])
protected_router = APIRouter(prefix="/places")


@router.get(
    "/",
)
@protected_router.get(
    "/",
)
async def list_places(
    db: Annotated[AsyncSession, Depends(get_db)],
    location_bounds: Annotated[LocationBounds, Depends(get_location_bounds)],
    sort_options: Annotated[SortOptions | None, Depends(get_sort_options)],
    filter_options: Annotated[FilterOptions | None, Depends(get_filter_options)],
    pagination_options: Annotated[PaginationOptions | None, Depends(get_pagination_options)],
) -> list[PlaceResponse] | PaginatedResponse[PlaceResponse]:
    """List all places within the specified bounds."""
    items, total = await places_service.list_places(
        db=db,
        bounds=location_bounds,
        sort_options=sort_options,
        filter_options=filter_options,
        pagination_options=pagination_options,
    )

    if pagination_options:
        return PaginatedResponse[PlaceResponse](
            items=items,
            total=total,
            page=pagination_options.page,
            page_size=pagination_options.page_size,
        )
    return [PlaceResponse.model_validate(item) for item in items]


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
