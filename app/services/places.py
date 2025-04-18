from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.places import Place
from app.models.tags import Tag
from app.models.uow import DBUnitOfWork
from app.schemas.places import PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.common import paginate
from app.services.errors import (
    DBObjectNotFoundError,
    DBValidationError,
    InvalidTagIdError,
)


def _validate_tags(tags: List[Tag], tag_ids: List[UUID]):
    print("validate")
    print(tags)
    print(tag_ids)
    if len(set(tags)) != len(set(tag_ids)):
        raise InvalidTagIdError()


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
    page: int = 1,
    page_size: int = 10,
) -> tuple[List[PlaceResponse], int]:
    stmt = select(Place)
    items, total = await paginate(db, stmt, page, page_size)

    items = [PlaceResponse.model_validate(item) if item else None for item in items]

    print(total)

    return items, total


async def create_place(db: DBUnitOfWork, place_create: PlaceCreate) -> PlaceResponse:
    place = Place(**place_create.model_dump(exclude={"tag_ids"}))
    _assign_tags_to_place(db, place, place_create.tag_ids)
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
