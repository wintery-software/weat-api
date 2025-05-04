from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

import app.services.tags as tags_service
from app.constants import PlaceType
from app.models.uow import DBUnitOfWork
from app.routes.helpers import get_db
from app.schemas.tags import TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix="/tags", tags=["Tags"])
protected_router = APIRouter(prefix="/tags")


@router.get(
    "/{place_type}",
)
@protected_router.get(
    "/{place_type}",
)
async def list_tags(
    place_type: PlaceType,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> list[TagResponse]:
    """List all tags for a given place type."""
    return await tags_service.list_tags(
        db=db,
        place_type=place_type,
    )


@protected_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_create: TagCreate,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> TagResponse:
    """Create a new tag."""
    return await tags_service.create_tag(
        db=db,
        tag_create=tag_create,
    )


@protected_router.put(
    "/{tag_id}",
    response_model_exclude_unset=True,
)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> TagResponse:
    """Update a tag by ID."""
    return await tags_service.update_tag(
        db=db,
        tag_id=tag_id,
        tag_update=tag_update,
    )


@protected_router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
    tag_id: UUID,
    db: Annotated[DBUnitOfWork, Depends(get_db)],
) -> None:
    """Delete a tag by ID."""
    await tags_service.delete_tag(
        db=db,
        tag_id=tag_id,
    )
