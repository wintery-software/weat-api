from uuid import UUID
from pydantic import BaseModel

from app.constants import PlaceType


class TagTypeBase(BaseModel):
    name: str


class TagTypeCreate(TagTypeBase):
    place_type: PlaceType


class TagTypeUpdate(TagTypeBase):
    pass


class TagTypeResponse(TagTypeBase):
    id: UUID

    class Config:
        from_attributes = True
