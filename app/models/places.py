from sqlalchemy import JSON, Enum, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import PlaceType
from app.models.associations import place_tag_association
from app.models.base import Base
from app.models.tags import Tag
from app.schemas.places import PlaceUpdate


class Place(Base):
    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String, nullable=False)
    name_zh: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[PlaceType] = mapped_column(
        Enum(PlaceType, name="place_type", native_enum=False), nullable=False
    )

    address: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    google_maps_url: Mapped[str | None] = mapped_column(String, nullable=True)
    google_maps_place_id: Mapped[str | None] = mapped_column(
        String, nullable=True, unique=True
    )

    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String, nullable=True)
    opening_hours: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    properties: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    tags: Mapped[list["Tag"]] = relationship(
        secondary=place_tag_association, back_populates="places", lazy="joined"
    )

    @property
    def location(self) -> dict[str, float] | None:
        if self.latitude is None or self.longitude is None:
            return None
        else:
            return {"latitude": self.latitude, "longitude": self.longitude}

    def update(self, data: PlaceUpdate):
        for key, value in data.model_dump(
            exclude_unset=True, exclude={"tag_ids"}
        ).items():
            setattr(self, key, value)
