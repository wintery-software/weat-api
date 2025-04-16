from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language
from app.models.places import Place
from app.routes.helpers import get_db, get_lang
from app.schemas.places import PlaceCreate, PlaceUpdate, PlaceResponse


router = APIRouter(tags=["Places"])


@router.get(
    "/places/",
    response_model=List[PlaceResponse],
)
async def list_places(
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    result = await db.execute(select(Place))
    return result.scalars().all()


@router.post(
    "/places/",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_place(
    place_create: PlaceCreate,
    db: AsyncSession = Depends(get_db),
):
    place = Place(**place_create.model_dump())

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
    place = await db.get_one(Place, place_id)

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
    values = place_update.model_dump(exclude_unset=True)
    stmt = update(Place).where(Place.id == place_id).values(**values).returning(Place)

    try:
        result = await db.execute(stmt)
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e

    updated = result.scalar_one()

    return updated


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
