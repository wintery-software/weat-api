from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

import app.services.tag_types as tag_types_service
from app.constants import PlaceType
from app.models.uow import DBUnitOfWork
from app.routes.helpers import get_db
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate

router = APIRouter(tags=["Tag Types"])


@router.post(
    "/tag-types/",
    status_code=status.HTTP_201_CREATED,
)
async def create_tag_type(
    tag_type_create: TagTypeCreate,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> TagTypeResponse:
    """Create a new tag type.

    Args:
        tag_type_create (TagTypeCreate): The tag type data to create.
        db (DBUnitOfWork, optional): The database unit of work. Defaults to Depends(get_db).

    Returns:
        TagTypeResponse: The created tag type.

    """
    return await tag_types_service.create_tag_type(
        db=db,
        tag_type_create=tag_type_create,
    )


@router.get(
    "/tag-types/{place_type}",
)
async def list_tag_types(
    place_type: PlaceType,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> list[TagTypeResponse]:
    """List all tag types for a given place type.

    Args:
        place_type (PlaceType): The place type to filter tag types by.
        db (DBUnitOfWork, optional): The database unit of work. Defaults to Depends(get_db).

    Returns:
        list[TagTypeResponse]: A list of tag types for the specified place type.

    """
    return await tag_types_service.list_tag_types(
        db=db,
        place_type=place_type,
    )


@router.put(
    "/tag-types/{tag_type_id}",
    response_model_exclude_unset=True,
)
async def update_tag_type(
    tag_type_id: UUID,
    tag_type_update: TagTypeUpdate,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> TagTypeResponse:
    """Update a tag type by ID.

    Args:
        tag_type_id (UUID): The ID of the tag type to update.
        tag_type_update (TagTypeUpdate): The updated tag type data.
        db (DBUnitOfWork, optional): The database unit of work. Defaults to Depends(get_db).

    Returns:
        TagTypeResponse: The updated tag type.

    """
    return await tag_types_service.update_tag_type(
        db=db,
        tag_type_id=tag_type_id,
        tag_type_update=tag_type_update,
    )


@router.delete(
    "/tag-types/{tag_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag_type(
    tag_type_id: UUID,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> None:
    """Delete a tag type by ID.

    Args:
        tag_type_id (UUID): The ID of the tag type to delete.
        db (DBUnitOfWork, optional): The database unit of work. Defaults to Depends(get_db).

    """
    await tag_types_service.delete_tag_type(
        db=db,
        tag_type_id=tag_type_id,
    )
