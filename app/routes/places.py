from collections.abc import AsyncGenerator
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import async_session_maker
from app.models.places import Place
from app.schemas.places import PlaceCreate, PlaceUpdate, PlaceResponse

router = APIRouter(tags=["Places"])


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@router.get("/places/", response_model=List[PlaceResponse])
async def list_places(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place))
    return result.scalars().all()


@router.post(
    "/places/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED
)
async def create_place(place: PlaceCreate, db: AsyncSession = Depends(get_db)):
    new_place = Place(**place.dict())
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place


@router.get("/places/{place_id}", response_model=PlaceResponse)
async def get_place(place_id: str, db: AsyncSession = Depends(get_db)):
    place = await db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place


@router.put("/places/{place_id}", response_model=PlaceResponse)
async def update_place(
    place_id: str, place_update: PlaceUpdate, db: AsyncSession = Depends(get_db)
):
    place = await db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    for key, value in place_update.dict(exclude_unset=True).items():
        setattr(place, key, value)
    await db.commit()
    await db.refresh(place)
    return place


@router.delete("/places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_place(place_id: str, db: AsyncSession = Depends(get_db)):
    place = await db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    await db.delete(place)
    await db.commit()
