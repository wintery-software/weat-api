from uuid import UUID

from pydantic import BaseModel

from app.constants import PlaceType


class TagTypeBase(BaseModel):
    """Tag type base schema.

    This schema is used as a base for tag type creation and update.
    """

    name: str


class TagTypeCreate(TagTypeBase):
    """Tag type creation schema.

    This schema is used for creating a new tag type.
    """

    place_type: PlaceType


class TagTypeUpdate(TagTypeBase):
    """Tag type update schema.

    This schema is used for updating an existing tag type.
    """


class TagTypeResponse(TagTypeBase):
    """Tag type response schema.

    This schema is used for returning tag type data.
    """

    id: UUID

    class Config:
        from_attributes = True
