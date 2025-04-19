from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re
from typing import Any
from uuid import UUID

from app.constants import PHONE_NUMBER_REGEX, PlaceType
from app.schemas.tags import TagResponse


class Location(BaseModel):
    latitude: float = Field(examples=[37.7749])
    longitude: float = Field(examples=[-122.4194])

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return v


class OpeningHours(BaseModel):
    day: int = Field(examples=[1])
    open: str = Field(examples=["08:00"])
    close: str = Field(examples=["20:00"])

    @field_validator("open", "close")
    @classmethod
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:mm format")
        return v

    @field_validator("close")
    @classmethod
    def validate_time_order(cls, v, values):
        open_str = values.data.get("open")
        if open_str:
            open_time = datetime.strptime(open_str, "%H:%M").time()
            close_time = datetime.strptime(v, "%H:%M").time()
            if open_time >= close_time:
                raise ValueError("Open time must be earlier than close time")
        return v

    @field_validator("day")
    @classmethod
    def validate_day(cls, v):
        if not 1 <= v <= 7:
            raise ValueError("Day must be an integer between 1 (Monday) and 7 (Sunday)")
        return v


class PlaceBase(BaseModel):
    name: str
    name_zh: str | None = None
    type: PlaceType
    address: str | None = None
    google_maps_url: str | None = None
    google_maps_place_id: str | None = None
    phone_number: str | None = Field(default=None, examples=["1234567890"])
    website_url: str | None = None
    opening_hours: list[OpeningHours] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None and not re.compile(PHONE_NUMBER_REGEX).match(v):
            raise ValueError("Invalid phone number format. Expect 10 digits.")
        return v


class PlaceCreate(PlaceBase):
    location: Location | None = None
    tag_ids: list[UUID] = Field(default_factory=list)


class PlaceUpdate(PlaceBase):
    name: str | None = None
    name_zh: str | None = None
    type: PlaceType | None = None
    location: Location | None = None
    tag_ids: list[UUID] = Field(default_factory=list)


class PlaceResponse(PlaceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    location: Location | None = None
    tags: list[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SimplePlaceResponse(BaseModel):
    id: UUID
    name: str
    name_zh: str | None = None
    type: PlaceType
    location: Location | None = None

    class Config:
        from_attributes = True
