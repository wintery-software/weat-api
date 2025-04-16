from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import Language
from app.models.tags import Tag
from app.routes.helpers import get_db, get_lang
from app.schemas.tags import TagCreate, TagResponse, TagUpdate


router = APIRouter(tags=["Tags"])


@router.post(
    "/tags/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_create: TagCreate,
    db: AsyncSession = Depends(get_db),
):
    tag = Tag(**tag_create.model_dump())

    db.add(tag)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    await db.refresh(tag)

    return tag


@router.get(
    "/tags/{tag_type_id}",
    response_model=List[TagResponse],
)
async def list_tags(
    tag_type_id: UUID,
    db: AsyncSession = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    result = await db.execute(select(Tag).where(Tag.tag_type_id == tag_type_id))
    return result.scalars().all()


@router.put(
    "/tags/{tag_id}",
    response_model=TagResponse,
)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one()
    tag.update_from_dict(**tag_update.model_dump(exclude_unset=True))

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise e
    db.refresh(tag)

    return tag


@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
    tag_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    tag = await db.get_one(Tag, tag_id)

    await db.delete(tag)
    await db.commit()
