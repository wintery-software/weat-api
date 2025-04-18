import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import UUID, Enum, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.associations import place_tag_association
from app.models.base import Base
from app.constants import PlaceType

if TYPE_CHECKING:
    from app.models.places import Place


class TagType(Base):
    __tablename__ = "tag_types"
    __table_args__ = (
        UniqueConstraint("place_type", "name", name="uq_tag_type_place_type"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    place_type: Mapped[PlaceType] = mapped_column(
        Enum(PlaceType, name="place_type", native_enum=False),
        nullable=False,
        index=True,
    )

    tags: Mapped[List["Tag"]] = relationship(back_populates="tag_type")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("name", "tag_type_id", name="uq_tag_name_tag_type_id"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    tag_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tag_types.id"), nullable=False
    )

    tag_type: Mapped["TagType"] = relationship(back_populates="tags", lazy="joined")
    places: Mapped[List["Place"]] = relationship(
        secondary=place_tag_association, back_populates="tags"
    )

    @property
    def tag_type_name(self) -> str:
        return self.tag_type.name
