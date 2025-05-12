from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.constants import PlaceType
from app.db.uow import DBUnitOfWork
from app.models.tag import Tag, TagType
from app.schemas.errors import InvalidSortColumnError
from app.schemas.options import SortOptions
from app.schemas.tags import TagCreate, TagResponse, TagUpdate
from app.services.common import sort
from app.services.errors import ObjectNotFoundError, ValidationError

router = APIRouter(tags=["Tags"])


async def _get_tag_by_id(db: DBUnitOfWork, tag_id: UUID) -> Tag:
    """Get a tag by its ID.

    Args:
        db (DBUnitOfWork): Database unit of work.
        tag_id (UUID): Tag ID.

    Returns:
        Tag: The tag.

    Raises:
        ObjectNotFoundError: If the tag is not found.

    """
    tag = await db.get(Tag, tag_id)

    if not tag:
        raise ObjectNotFoundError(Tag.__name__, tag_id)

    return tag


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
    sort_options: SortOptions | None = None,
) -> list[TagResponse]:
    """List all tags for a given place type.

    Args:
        db (DBUnitOfWork): The database unit of work.
        place_type (PlaceType): The place type to filter tags by.
        sort_options (SortOptions | None): Sort options.

    Returns:
        list[TagResponse]: A list of tag responses.

    Raises:
        InvalidSortColumnError: If the sort column is invalid.

    """
    stmt = select(Tag).join(Tag.tag_type).where(TagType.place_type == place_type)

    if sort_options:
        if not hasattr(Tag, sort_options.sort_by):
            raise InvalidSortColumnError(sort_options.sort_by)

        stmt = sort(stmt, Tag, sort_options.sort_by, sort_options.order)

    items = await db.get_all(stmt)
    return [TagResponse.model_validate(item) for item in items]


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
    tag = await _get_tag_by_id(db, tag_id)

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
    tag = await _get_tag_by_id(db, tag_id)

    await db.delete(tag)
    await db.commit()
