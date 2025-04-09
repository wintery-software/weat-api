from datetime import datetime
from pydantic import BaseModel, Field
import re
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import field_validator

from app.constants import PHONE_NUMBER_REGEX


class TimeInterval(BaseModel):
    open: str
    close: str

    @field_validator("open", "close")
    @classmethod
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("time must be in HH:MM format")
        return v

    @field_validator("close")
    @classmethod
    def validate_time_order(cls, v, values):
        print(values)
        open_str = values.data.get("open")
        if open_str:
            open_time = datetime.strptime(open_str, "%H:%M").time()
            close_time = datetime.strptime(v, "%H:%M").time()
            if open_time >= close_time:
                raise ValueError("open time must be earlier than close time")
        return v


class OpeningHours(BaseModel):
    monday: Optional[list[TimeInterval]] = None
    tuesday: Optional[list[TimeInterval]] = None
    wednesday: Optional[list[TimeInterval]] = None
    thursday: Optional[list[TimeInterval]] = None
    friday: Optional[list[TimeInterval]] = None
    saturday: Optional[list[TimeInterval]] = None
    sunday: Optional[list[TimeInterval]] = None


class PlaceBase(BaseModel):
    name: str
    type: str
    address: Optional[str] = None
    google_maps_url: Optional[str] = None
    google_maps_place_id: Optional[str] = None
    phone_number: Optional[str] = Field(default=None)
    website_url: Optional[str] = None
    opening_hours: Optional[OpeningHours] = None
    properties: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if v is not None and not re.compile(PHONE_NUMBER_REGEX).match(v):
            raise ValueError("Invalid phone number format. Expect 10 digits.")
        return v


class PlaceCreate(PlaceBase):
    pass


class PlaceUpdate(PlaceBase):
    pass


class PlaceResponse(PlaceBase):
    id: UUID

    class Config:
        orm_mode = True
