from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.constants import PlaceType
from app.models.tags import Tag, TagType
from app.models.uow import DBUnitOfWork
from app.schemas.tags import TagCreate, TagResponse, TagUpdate
from app.services.errors import ValidationError

router = APIRouter(tags=["Tags"])


async def create_tag(
    db: DBUnitOfWork,
    tag_create: TagCreate,
) -> TagResponse:
    """Create a new tag.

    Args:
        db (DBUnitOfWork): Database unit of work.
        tag_create (TagCreate): Tag creation schema.

    Returns:
        TagResponse: Created tag response.

    Raises:
        ValidationError: If there is a validation error.

    """
    tag = Tag(**tag_create.model_dump())
    await db.add(tag)

    try:
        await db.commit()
    except IntegrityError as e:
        raise ValidationError from e

    await db.refresh(tag)

    return TagResponse.model_validate(tag)


async def list_tags(
    db: DBUnitOfWork,
    place_type: PlaceType,
) -> list[TagResponse]:
    """List all tags for a given place type.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_type (PlaceType): The place type to filter tags by.

    Returns:
        list[TagResponse]: A list of tag responses.

    """
    stmt = select(Tag).join(Tag.tag_type).where(TagType.place_type == place_type)
    result = await db.get_all(stmt)

    return [TagResponse.model_validate(item) for item in result]


async def update_tag(
    db: DBUnitOfWork,
    tag_id: UUID,
    tag_update: TagUpdate,
) -> TagResponse:
    """Update a tag by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        tag_id (UUID): The ID of the tag to update.
        tag_update (TagUpdate): The updated tag data.

    Returns:
        TagResponse: The updated tag response.

    Raises:
        ValidationError: If there is a validation error.

    """
    tag = await db.get_by_id(Tag, tag_id)

    tag.update(tag_update)

    try:
        await db.commit()
    except IntegrityError as e:
        raise ValidationError from e

    await db.refresh(tag)

    return TagResponse.model_validate(tag)


async def delete_tag(
    db: DBUnitOfWork,
    tag_id: UUID,
) -> None:
    """Delete a tag by its ID."""
    tag = await db.get_by_id(Tag, tag_id)

    await db.delete(tag)
    await db.commit()
