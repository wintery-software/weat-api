import re
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants import PHONE_NUMBER_REGEX, PlaceType
from app.schemas.errors import (
    InvalidBoundsError,
    InvalidDayError,
    InvalidLatitudeError,
    InvalidLongitudeError,
    InvalidPhoneNumberError,
    InvalidTimeFormatError,
    InvalidTimeOrderError,
)
from app.schemas.tags import TagResponse

LATITUDE_LOWER_BOUND = -90
LATITUDE_UPPER_BOUND = 90
LONGITUDE_LOWER_BOUND = -180
LONGITUDE_UPPER_BOUND = 180


class Location(BaseModel):
    """Location schema.

    This schema is used to represent a geographical location with latitude and longitude.
    """

    latitude: float = Field(examples=[37.7749])
    longitude: float = Field(examples=[-122.4194])

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate the latitude.

        The latitude must be between -90 and 90 degrees.

        Args:
            v (float): The latitude to validate.

        Returns:
            float: The validated latitude.

        Raises:
            InvalidLatitudeError: If the latitude is not valid.

        """
        if not (LATITUDE_LOWER_BOUND <= v <= LATITUDE_UPPER_BOUND):
            raise InvalidLatitudeError(v)
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate the longitude.

        The longitude must be between -180 and 180 degrees.

        Args:
            v (float): The longitude to validate.

        Returns:
            float: The validated longitude.

        Raises:
            InvalidLongitudeError: If the longitude is not valid.

        """
        if not (LONGITUDE_LOWER_BOUND <= v <= LONGITUDE_UPPER_BOUND):
            raise InvalidLongitudeError(v)
        return v


class LocationBounds(BaseModel):
    """location bounds schema.

    This schema is used to represent a geographical bounding box with southwest and northeast corners.
    """

    sw_lat: float = Field(examples=[37.7749])
    sw_lng: float = Field(examples=[-122.4194])
    ne_lat: float = Field(examples=[37.7849])
    ne_lng: float = Field(examples=[-122.4094])

    @field_validator("sw_lat", "ne_lat")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate the latitude.

        The latitude must be between -90 and 90 degrees.

        Args:
            v (float): The latitude to validate.

        Returns:
            float: The validated latitude.

        Raises:
            InvalidLatitudeError: If the latitude is not valid.

        """
        if not (LATITUDE_LOWER_BOUND <= v <= LATITUDE_UPPER_BOUND):
            raise InvalidLatitudeError(v)
        return v

    @field_validator("sw_lng", "ne_lng")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate the longitude.

        The longitude must be between -180 and 180 degrees.

        Args:
            v (float): The longitude to validate.

        Returns:
            float: The validated longitude.

        Raises:
            InvalidLongitudeError: If the longitude is not valid.

        """
        if not (LONGITUDE_LOWER_BOUND <= v <= LONGITUDE_UPPER_BOUND):
            raise InvalidLongitudeError(v)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_bounds(cls, values: "LocationBounds") -> "LocationBounds":
        """Validate the bounds of the location.

        The southwest latitude and longitude must be less than the northeast latitude and longitude.

        Args:
            values (LocationBounds): The LocationBounds object to validate.

        Returns:
            LocationBounds: The validated LocationBounds object.

        Raises:
            InvalidBoundsError: If the bounds are not valid.

        """
        sw_lat = values.sw_lat
        sw_lng = values.sw_lng
        ne_lat = values.ne_lat
        ne_lng = values.ne_lng

        if sw_lat > ne_lat or sw_lng > ne_lng:
            raise InvalidBoundsError(sw_lat, sw_lng, ne_lat, ne_lng)
        return values


MONDAY_IN_NUMBER = 1
SUNDAY_IN_NUMBER = 7


class OpeningHours(BaseModel):
    """Opening hours schema.

    This schema is used to represent the opening hours of a place.
    """

    day: int = Field(examples=[1])
    open: str = Field(examples=["08:00"])
    close: str = Field(examples=["20:00"])

    @field_validator("open", "close")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate the time format.

        The time must be in HH:mm format.

        Args:
            v (str): The time to validate.

        Returns:
            str: The validated time.

        Raises:
            InvalidTimeFormatError: If the time format is not valid.

        """
        try:
            datetime.strptime(v, "%H:%M")  # noqa: DTZ007
        except ValueError as e:
            raise InvalidTimeFormatError(v) from e
        return v

    @field_validator("day")
    @classmethod
    def validate_day(cls, v: int) -> int:
        """Validate the day of the week.

        The day must be an integer between 1 (Monday) and 7 (Sunday).

        Args:
            v (int): The day of the week to validate.

        Returns:
            int: The validated day of the week.

        Raises:
            InvalidDayError: If the day is not valid.

        """
        if not MONDAY_IN_NUMBER <= v <= SUNDAY_IN_NUMBER:
            raise InvalidDayError(v)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_time_order(cls, values: "OpeningHours") -> "OpeningHours":
        """Validate the order of opening and closing times.

        The opening time must be earlier than the closing time.

        Args:
            values (OpeningHours): The OpeningHours object to validate.

        Returns:
            OpeningHours: The validated OpeningHours object.

        Raises:
            InvalidTimeOrderError: If the opening time is not earlier than the closing time.

        """
        open_str = values.open
        close_str = values.close
        if open_str:
            open_time = datetime.strptime(open_str, "%H:%M").time()  # noqa: DTZ007
            close_time = datetime.strptime(close_str, "%H:%M").time()  # noqa: DTZ007
            if open_time >= close_time:
                raise InvalidTimeOrderError(open_str, close_str)
        return values


class PlaceBase(BaseModel):
    """Place base schema.

    This schema is used to represent a place with its basic attributes.
    """

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
    def validate_phone_number(cls, v: str | None) -> str | None:
        """Validate the phone number format.

        The phone number should be a string of 10 digits.

        Args:
            v (str | None): The phone number to validate.

        Returns:
            str | None: The validated phone number.

        Raises:
            InvalidPhoneNumberError: If the phone number is not valid.

        """
        if v is not None and not re.compile(PHONE_NUMBER_REGEX).match(v):
            raise InvalidPhoneNumberError(v)
        return v


class PlaceCreate(PlaceBase):
    """Place create schema.

    This schema is used to create a new place with its attributes.
    """

    location: Location | None = None
    tag_ids: list[UUID] = Field(default_factory=list)


class PlaceUpdate(PlaceBase):
    """Place update schema.

    This schema is used to update an existing place with its attributes.
    """

    name: str | None = None
    name_zh: str | None = None
    type: PlaceType | None = None
    location: Location | None = None
    tag_ids: list[UUID] = Field(default_factory=list)


class PlaceResponse(PlaceBase):
    """Place response schema.

    This schema is used to represent a place with its attributes in the response.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime
    location: Location | None = None
    tags: list[TagResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SimplePlaceResponse(BaseModel):
    """Simple place response schema.

    This schema is used to represent a place with its basic attributes in the response.
    """

    id: UUID
    name: str
    name_zh: str | None = None
    type: PlaceType
    location: Location | None = None

    class Config:
        from_attributes = True
