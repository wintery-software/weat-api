import uuid

from sqlalchemy import Column, String, Float, JSON, text, DateTime
from sqlalchemy.dialects.postgresql import UUID

import datetime

from app.db import Base


class Place(Base):
    __tablename__ = "places"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.datetime.now(datetime.timezone.utc),
    )

    name = Column(String, nullable=False)
    name_zh = Column(String, nullable=True)
    type = Column(String, nullable=False)

    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    google_maps_url = Column(String, nullable=True)
    google_maps_place_id = Column(String, nullable=True, unique=True)

    phone_number = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    opening_hours = Column(JSON, nullable=True)

    properties = Column(JSON, nullable=True)
