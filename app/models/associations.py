from sqlalchemy import UUID, Column, ForeignKey, Table

from app.models.base import Base


place_tag_association = Table(
    "places_tags",
    Base.metadata,
    Column("place_id", UUID(as_uuid=True), ForeignKey("places.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True),
)
