from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language
from app.models.places import Place
from app.models.tags import Tag
from app.routes.helpers import get_db, get_lang
from app.schemas.places import PlaceCreate, PlaceUpdate, PlaceResponse


router = APIRouter(tags=["Places"])


async def validate_and_set_tags(
    db: AsyncSession,
    place: Place,
    tag_ids: List[UUID],
):
    if tag_ids is None:
        return

    result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    found_tags = result.scalars().all()

    if len(found_tags) != len(set(tag_ids)):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="One or more tag IDs are invalid",
        )

    place.tags = found_tags


@router.get(
    "/places/",
    response_model=List[PlaceResponse],
)
async def list_places(
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    result = await db.execute(select(Place))
    return result.unique().scalars().all()


@router.post(
    "/places/",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_create: PlaceCreate,
    db: AsyncSession = Depends(get_db),
):
    place = Place(**place_create.model_dump(exclude={"tag_ids"}))
    await validate_and_set_tags(db, place, place_create.tag_ids)

    db.add(place)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    await db.refresh(place)

    return place


@router.get(
    "/places/{place_id}",
    response_model=PlaceResponse,
)
async def get_place(
    place_id: UUID,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.unique().scalar_one()

    return place


@router.put(
    "/places/{place_id}",
    response_model=PlaceResponse,
)
async def update_place(
    place_id: UUID,
    place_update: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.unique().scalar_one()
    place.update_from_dict(
        **place_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
    )

    await validate_and_set_tags(db, place, place_update.tag_ids)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e

    await db.refresh(place)

    return place


@router.delete(
    "/places/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_place(
    place_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    place = await db.get_one(Place, place_id)

    await db.delete(place)
    await db.commit()
