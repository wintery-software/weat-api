from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy import JSON, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import PlaceType
from app.models.associations import place_tag_association
from app.models.base import Base
from app.schemas.places import PlaceUpdate

if TYPE_CHECKING:
    from app.models.tags import Tag


class Place(Base):
    """Place model.

    This model represents a place with various attributes such as name, type, address, location,
    and associated tags. It also includes methods for updating the place and retrieving its location.

    """

    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String, nullable=False)
    name_zh: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[PlaceType] = mapped_column(
        Enum(PlaceType, name="place_type", native_enum=False),
        nullable=False,
    )

    address: Mapped[str | None] = mapped_column(String, nullable=True)
    location_geom: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=True,
    )
    google_maps_url: Mapped[str | None] = mapped_column(String, nullable=True)
    google_maps_place_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        unique=True,
    )

    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    website_url: Mapped[str | None] = mapped_column(String, nullable=True)
    opening_hours: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    properties: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    tags: Mapped[list["Tag"]] = relationship(
        secondary=place_tag_association,
        back_populates="places",
        lazy="joined",
    )

    __table_args__ = (
        Index(
            "idx_places_name_trgm",
            "name",
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index(
            "idx_places_name_zh_trgm",
            "name_zh",
            postgresql_using="gin",
            postgresql_ops={"name_zh": "gin_trgm_ops"},
        ),
        Index(
            "idx_places_address_trgm",
            "address",
            postgresql_using="gin",
            postgresql_ops={"address": "gin_trgm_ops"},
        ),
        Index(
            "idx_places_location_geom",
            "location_geom",
            postgresql_using="gist",
        ),
    )

    @property
    def location(self) -> dict[str, float] | None:
        """Get the location of the place.

        Returns:
            dict[str, float] | None: The location of the place as a dictionary with "latitude" and "longitude" keys,
            or None if the location is not set.

        """
        if self.location_geom is None:
            return None

        point = to_shape(self.location_geom)  # works for WKTElement and WKBElement
        return {
            "latitude": point.y,
            "longitude": point.x,
        }

    @location.setter
    def location(self, value: dict[str, float] | None) -> None:
        """Set the location of the place.

        Args:
            value (dict[str, float] | None): The location to set. Should be a dictionary with
                "latitude" and "longitude" keys.

        """
        if value is None:
            self.location_geom = None
        else:
            self.location_geom = func.ST_SetSRID(
                func.ST_MakePoint(value["longitude"], value["latitude"]),
                4326,
            )

    def update(self, data: PlaceUpdate) -> None:
        """Update the place with the provided data.

        Args:
            data (PlaceUpdate): The data to update the place with.

        """
        for key, value in data.model_dump(
            exclude_unset=True,
            exclude={"tag_ids"},
        ).items():
            setattr(self, key, value)
