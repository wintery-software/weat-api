from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.constants import Language, PlaceType
from app.models.uow import DBUnitOfWork
from app.routes.helpers import get_db, get_lang
from app.schemas.tags import TagCreate, TagResponse, TagUpdate
import app.services.tags as tags_service

router = APIRouter(tags=["Tags"])


@router.post(
    "/tags/",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_create: TagCreate,
    db: DBUnitOfWork = Depends(get_db),
):
    return await tags_service.create_tag(
        db=db,
        tag_create=tag_create,
    )


@router.get(
    "/tags/{place_type}",
    response_model=List[TagResponse],
)
async def list_tags(
    place_type: PlaceType,
    db: DBUnitOfWork = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    return await tags_service.list_tags(
        db=db,
        place_type=place_type,
    )


@router.put(
    "/tags/{tag_id}",
    response_model=TagResponse,
    response_model_exclude_unset=True,
)
async def update_tag(
    tag_id: UUID,
    tag_update: TagUpdate,
    db: DBUnitOfWork = Depends(get_db),
):
    return await tags_service.update_tag(
        db=db,
        tag_id=tag_id,
        tag_update=tag_update,
    )


@router.delete(
    "/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
    tag_id: UUID,
    db: DBUnitOfWork = Depends(get_db),
):
    await tags_service.delete_tag(
        db=db,
        tag_id=tag_id,
    )

    return None
