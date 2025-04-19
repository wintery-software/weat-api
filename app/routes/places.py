from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language
from app.routes.helpers import get_db, get_lang
from app.schemas.pagination import PaginatedResponse
from app.schemas.places import (
    MinimumPlaceResponse,
    PlaceCreate,
    PlaceUpdate,
    PlaceResponse,
)
import app.services.places as places_service

router = APIRouter(tags=["Places"])


@router.get(
    "/places/",
    response_model=PaginatedResponse[MinimumPlaceResponse],
)
async def list_places(
    sw_lat: float = -90,
    sw_lng: float = -180,
    ne_lat: float = 90,
    ne_lng: float = 180,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    items, total = await places_service.list_paginated_places(
        db=db,
        sw_lat=sw_lat,
        sw_lng=sw_lng,
        ne_lat=ne_lat,
        ne_lng=ne_lng,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[MinimumPlaceResponse](
        items=items, total=total, page=page, page_size=page_size
    )


@router.get(
    "/places/search",
    response_model=PaginatedResponse[PlaceResponse],
)
async def search_places(
    q: str = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    items, total = await places_service.search_paginated_places(
        db=db,
        q=q,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[PlaceResponse](
        items=items, total=total, page=page, page_size=page_size
    )


@router.post(
    "/places/",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_create: PlaceCreate,
    db: AsyncSession = Depends(get_db),
):
    return await places_service.create_place(
        db=db,
        place_create=place_create,
    )


@router.get(
    "/places/{place_id}",
    response_model=PlaceResponse,
)
async def get_place(
    place_id: UUID,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    return await places_service.get_place(
        db=db,
        place_id=place_id,
    )


@router.put(
    "/places/{place_id}",
    response_model=PlaceResponse,
    response_model_exclude_unset=True,
)
async def update_place(
    place_id: UUID,
    place_update: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
):
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
    db: AsyncSession = Depends(get_db),
):
    await places_service.delete_place(
        db=db,
        place_id=place_id,
    )

    return None
