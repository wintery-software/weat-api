from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.tags import TagType
from app.models.uow import DBUnitOfWork
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate
from app.services.errors import ValidationError


async def create_tag_type(
    db: DBUnitOfWork,
    tag_type_create: TagTypeCreate,
) -> TagTypeResponse:
    """Create a new tag type.

    Args:
        db (DBUnitOfWork): Database unit of work.
        tag_type_create (TagTypeCreate): Tag type creation schema.

    Returns:
        TagTypeResponse: Created tag type response.

    Raises:
        ValidationError: If there is a validation error.

    """
    tag_type = TagType(**tag_type_create.model_dump())
    await db.add(tag_type)

    try:
        await db.commit()
    except IntegrityError as e:
        raise ValidationError from e

    await db.refresh(tag_type)

    return TagTypeResponse.model_validate(tag_type)


async def list_tag_types(
    db: DBUnitOfWork,
    place_type: str,
) -> list[TagTypeResponse]:
    """List all tag types for a given place type.

    Args:
        db (DBUnitOfWork): Database unit of work.
        place_type (str): Place type to filter tag types by.

    Returns:
        list[TagTypeResponse]: List of tag type responses.

    """
    stmt = select(TagType).where(TagType.place_type == place_type)
    result = await db.get_all(stmt)

    return [TagTypeResponse.model_validate(item) for item in result]


async def update_tag_type(
    db: DBUnitOfWork,
    tag_type_id: UUID,
    tag_type_update: TagTypeUpdate,
) -> TagTypeResponse:
    """Update a tag type by its ID.

    Args:
        db (DBUnitOfWork): Database unit of work.
        tag_type_id (UUID): ID of the tag type to update.
        tag_type_update (TagTypeUpdate): Tag type update schema.

    Returns:
        TagTypeResponse: Updated tag type response.

    Raises:
        ValidationError: If there is a validation error.

    """
    tag_type = await db.get_by_id(TagType, tag_type_id)

    tag_type.update(tag_type_update)

    try:
        await db.commit()
    except IntegrityError as e:
        raise ValidationError from e

    await db.refresh(tag_type)

    return TagTypeResponse.model_validate(tag_type)


async def delete_tag_type(
    db: DBUnitOfWork,
    tag_type_id: UUID,
) -> None:
    """Delete a tag type by its ID."""
    tag_type = await db.get_by_id(TagType, tag_type_id)

    await db.delete(tag_type)
    await db.commit()
