from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.constants import Language, PlaceType
from app.models.uow import DBUnitOfWork
from app.routes.helpers import get_db, get_lang
from app.schemas.tag_types import TagTypeCreate, TagTypeResponse, TagTypeUpdate
import app.services.tag_types as tag_types_service

router = APIRouter(tags=["Tag Types"])


@router.post(
    "/tag-types/",
    response_model=TagTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag_type(
    tag_type_create: TagTypeCreate,
    db: DBUnitOfWork = Depends(get_db),
):
    return await tag_types_service.create_tag_type(
        db=db,
        tag_type_create=tag_type_create,
    )


@router.get(
    "/tag-types/{place_type}",
    response_model=List[TagTypeResponse],
)
async def list_tag_types(
    place_type: PlaceType,
    db: DBUnitOfWork = Depends(get_db),
    lang: Language = Depends(get_lang),
):
    return await tag_types_service.list_tag_types(
        db=db,
        place_type=place_type,
    )


@router.put(
    "/tag-types/{tag_type_id}",
    response_model=TagTypeResponse,
    response_model_exclude_unset=True,
)
async def update_tag_type(
    tag_type_id: UUID,
    tag_type_update: TagTypeUpdate,
    db: DBUnitOfWork = Depends(get_db),
):
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
    db: DBUnitOfWork = Depends(get_db),
):
    await tag_types_service.delete_tag_type(
        db=db,
        tag_type_id=tag_type_id,
    )

    return None
