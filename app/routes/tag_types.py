from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language, PlaceType
from app.models.tags import TagType
from app.routes.helpers import get_db, get_lang
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate


router = APIRouter(tags=["Tag Types"])


@router.post(
    "/tag-types/",
    response_model=TagTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag_type(
    tag_type_create: TagTypeCreate,
    db: AsyncSession = Depends(get_db),
):
    tag_type = TagType(**tag_type_create.model_dump())

    db.add(tag_type)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    await db.refresh(tag_type)

    return tag_type


@router.get(
    "/tag-types/{place_type}",
    response_model=List[TagTypeResponse],
)
async def list_tag_types(
    place_type: PlaceType,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    stmt = select(TagType).where(TagType.place_type == place_type)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put(
    "/tag-types/{tag_type_id}",
    response_model=TagTypeResponse,
)
async def update_tag_type(
    tag_type_id: UUID,
    tag_type_update: TagTypeUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(TagType).where(TagType.id == tag_type_id))
    tag_type = result.scalar_one()
    tag_type.update_from_dict(**tag_type_update.model_dump(exclude_unset=True))

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e

    await db.refresh(tag_type)

    return tag_type


@router.delete(
    "/tag-types/{tag_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag_type(
    tag_type_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    tag_type = await db.get_one(TagType, tag_type_id)

    await db.delete(tag_type)
    await db.commit()
