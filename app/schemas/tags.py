from uuid import UUID

from pydantic import BaseModel


class TagBase(BaseModel):
    """Tag base schema.

    This schema is used as a base for tag creation and update.
    """

    name: str
    tag_type_id: UUID


class TagCreate(TagBase):
    """Tag creation schema.

    This schema is used for creating a new tag.
    """


class TagUpdate(TagBase):
    """Tag update schema.

    This schema is used for updating an existing tag.
    """


class TagResponse(TagBase):
    """Tag response schema.

    This schema is used for returning tag data.
    """

    id: UUID
    tag_type_name: str

    class Config:
        from_attributes = True
