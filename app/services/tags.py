from typing import List
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.constants import PlaceType
from app.models.tags import Tag, TagType
from app.models.uow import DBUnitOfWork
from app.schemas.tags import TagCreate, TagResponse, TagUpdate
from app.services.errors import DBValidationError


router = APIRouter(tags=["Tags"])


async def create_tag(
    db: DBUnitOfWork,
    tag_create: TagCreate,
) -> TagResponse:
    tag = Tag(**tag_create.model_dump())
    await db.add(tag)

    try:
        await db.commit()
    except IntegrityError as e:
        raise DBValidationError(e)

    await db.refresh(tag)

    return TagResponse.model_validate(tag)


async def list_tags(
    db: DBUnitOfWork,
    place_type: PlaceType,
) -> List[TagResponse]:
    stmt = select(Tag).join(Tag.tag_type).where(TagType.place_type == place_type)
    result = await db.get_all(stmt)

    return [TagResponse.model_validate(item) for item in result]


async def update_tag(
    db: DBUnitOfWork,
    tag_id: UUID,
    tag_update: TagUpdate,
) -> TagResponse:
    tag = await db.get_by_id(Tag, tag_id)

    tag.update(tag_update)

    try:
        await db.commit()
    except IntegrityError as e:
        raise DBValidationError(e)

    await db.refresh(tag)

    return TagResponse.model_validate(tag)


async def delete_tag(
    db: DBUnitOfWork,
    tag_id: UUID,
) -> None:
    tag = await db.get_by_id(Tag, tag_id)

    await db.delete(tag)
    await db.commit()
