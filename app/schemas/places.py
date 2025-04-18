from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.constants import PHONE_NUMBER_REGEX, PlaceType
from app.schemas.tags import TagResponse


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
    name_zh: Optional[str] = None
    type: PlaceType
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None
    google_maps_place_id: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, examples=["1234567890"])
    website_url: Optional[str] = None
    opening_hours: Optional[List[OpeningHours]] = None
    properties: Optional[Dict[str, Any]] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None and not re.compile(PHONE_NUMBER_REGEX).match(v):
            raise ValueError("Invalid phone number format. Expect 10 digits.")
        return v


class PlaceCreate(PlaceBase):
    tag_ids: Optional[List[UUID]] = Field(default_factory=list)


class PlaceUpdate(PlaceBase):
    name: Optional[str] = None
    name_zh: Optional[str] = None
    type: Optional[PlaceType] = None
    tag_ids: Optional[List[UUID]] = Field(default_factory=list)


class PlaceResponse(PlaceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[TagResponse]] = None

    class Config:
        from_attributes = True


class MinimumPlaceResponse(BaseModel):
    id: UUID
    name: str
    name_zh: Optional[str] = None
    type: PlaceType
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
