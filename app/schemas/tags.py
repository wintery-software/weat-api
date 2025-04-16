from uuid import UUID
from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
    tag_type_id: UUID


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagResponse(TagBase):
    id: UUID
    tag_type_name: str

    class Config:
        from_attributes = True
