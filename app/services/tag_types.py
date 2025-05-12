from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.uow import DBUnitOfWork
from app.models.tag import TagType
from app.schemas.errors import InvalidSortColumnError
from app.schemas.options import SortOptions
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate
from app.services.common import sort
from app.services.errors import ObjectNotFoundError, ValidationError


async def _get_tag_type_by_id(db: DBUnitOfWork, tag_type_id: UUID) -> TagType:
    """Get a tag type by its ID.

    Args:
        db (DBUnitOfWork): The database unit of work.
        tag_type_id (UUID): The ID of the tag type to retrieve.

    Returns:
        TagType: The tag type.

    Raises:
        ObjectNotFoundError: If the tag type is not found.

    """
    tag_type = await db.get(TagType, tag_type_id)

    if not tag_type:
        raise ObjectNotFoundError(TagType.__name__, tag_type_id)

    return tag_type


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
    sort_options: SortOptions | None = None,
) -> list[TagTypeResponse]:
    """List all tag types for a given place type.

    Args:
        db (DBUnitOfWork): Database unit of work.
        place_type (str): Place type to filter tag types by.
        sort_options (SortOptions | None): Sort options.

    Returns:
        list[TagTypeResponse]: List of tag type responses.

    Raises:
        InvalidSortColumnError: If the sort column is invalid.

    """
    stmt = select(TagType).where(TagType.place_type == place_type)

    if sort_options:
        if not hasattr(TagType, sort_options.sort_by):
            raise InvalidSortColumnError(sort_options.sort_by)

        stmt = sort(stmt, TagType, sort_options.sort_by, sort_options.order)

    items = await db.get_all(stmt)
    return [TagTypeResponse.model_validate(item) for item in items]


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
    tag_type = await _get_tag_type_by_id(db, tag_type_id)

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
    tag_type = await _get_tag_type_by_id(db, tag_type_id)

    await db.delete(tag_type)
    await db.commit()
