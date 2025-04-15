import uuid
import datetime

from sqlalchemy import Enum, String, Float, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base
from app.constants import PlaceType


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

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
    opening_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    properties: Mapped[dict | None] = mapped_column(JSON, nullable=True)
