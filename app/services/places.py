from typing import List
from uuid import UUID
from sqlalchemy import Float, cast, func, or_, select
from sqlalchemy.exc import IntegrityError

from app.constants import PLACE_SEARCH_SIMILARITY_THRESHOLD
from app.models.places import Place
from app.models.tags import Tag
from app.models.uow import DBUnitOfWork
from app.schemas.places import PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.common import paginate, with_similarity_threshold
from app.services.errors import (
    DBObjectNotFoundError,
    DBValidationError,
    InvalidTagIdError,
)


def _validate_tags(tags: List[Tag], tag_ids: List[UUID]):
    if len(set(tags)) != len(set(tag_ids)):
        raise InvalidTagIdError()


def _validate_bounds(
    sw_lat: float,
    sw_lng: float,
    ne_lat: float,
    ne_lng: float,
) -> None:
    if sw_lat > ne_lat or sw_lng > ne_lng:
        raise ValueError(
            "Invalid bounds: sw_lat should be less than ne_lat and sw_lng should be less than ne_lng"
        )
    if sw_lat < -90 or ne_lat > 90:
        raise ValueError("Invalid latitude values: should be between -90 and 90")
    if sw_lng < -180 or ne_lng > 180:
        raise ValueError("Invalid longitude values: should be between -180 and 180")


async def _get_place_by_id(db: DBUnitOfWork, place_id: UUID) -> Place:
    place = await db.get_by_id(Place, place_id)

    if place is None:
        raise DBObjectNotFoundError("Place", place_id)

    return place


async def _get_tags_by_ids(db: DBUnitOfWork, tag_ids: list[UUID]) -> list[Tag]:
    stmt = select(Tag).where(Tag.id.in_(tag_ids))
    tags = await db.get_all(stmt)

    return tags


async def _assign_tags_to_place(
    db: DBUnitOfWork, place: Place, tag_ids: list[UUID]
) -> None:
    tags = await _get_tags_by_ids(db, tag_ids)
    _validate_tags(tags, tag_ids)
    place.tags = tags


async def list_paginated_places(
    db: DBUnitOfWork,
    sw_lat: float = -90,
    sw_lng: float = -180,
    ne_lat: float = 90,
    ne_lng: float = 180,
    page: int = 1,
    page_size: int = 10,
) -> tuple[List[PlaceResponse], int]:
    _validate_bounds(sw_lat, sw_lng, ne_lat, ne_lng)

    stmt = select(Place).where(
        Place.location_geom.op("&&")(
            func.ST_MakeEnvelope(sw_lng, sw_lat, ne_lng, ne_lat, 4326)
        )
    )
    items, total = await paginate(db, stmt, page, page_size)

    items = [PlaceResponse.model_validate(item) if item else None for item in items]

    return items, total


async def search_paginated_places(
    db: DBUnitOfWork,
    q: str = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[List[PlaceResponse], int]:
    await with_similarity_threshold(db, PLACE_SEARCH_SIMILARITY_THRESHOLD)

    stmt = select(Place).join(Place.tags, isouter=True)
    if q:
        stmt = stmt.where(
            or_(
                Place.name.op("%")(q),
                Place.name_zh.op("%")(q),
                Place.address.op("%")(q),
            )
        )
        stmt = stmt.order_by(
            cast(Place.name.op("<->")(q), Float)
            + cast(Place.name_zh.op("<->")(q), Float) * 1.5
            + cast(Place.address.op("<->")(q), Float) * 2
        )
    items, total = await paginate(db, stmt, page, page_size)

    items = [PlaceResponse.model_validate(item) if item else None for item in items]

    return items, total


async def create_place(db: DBUnitOfWork, place_create: PlaceCreate) -> PlaceResponse:
    place = Place(**place_create.model_dump(exclude={"tag_ids"}))
    await _assign_tags_to_place(db, place, place_create.tag_ids)
    await db.add(place)

    try:
        await db.commit()
    except IntegrityError as e:
        raise DBValidationError(e)

    await db.refresh(place)

    return PlaceResponse.model_validate(place)


async def get_place(db: DBUnitOfWork, place_id: UUID) -> PlaceResponse:
    place = await _get_place_by_id(db, place_id)

    return PlaceResponse.model_validate(place)


async def update_place(
    db: DBUnitOfWork, place_id: UUID, place_update: PlaceUpdate
) -> PlaceResponse:
    place = await _get_place_by_id(db, place_id)

    place.update(place_update)
    await _assign_tags_to_place(db, place, place_update.tag_ids)
    await db.add(place)

    try:
        await db.commit()
    except IntegrityError as e:
        raise DBValidationError(e)

    await db.refresh(place)

    return PlaceResponse.model_validate(place)


async def delete_place(db: DBUnitOfWork, place_id: UUID) -> None:
    place = await _get_place_by_id(db, place_id)

    await db.delete(place)
    await db.commit()
