from app.services.errors import ValidationError


class InvalidBoundsError(ValidationError):
    """Custom exception for invalid bounds."""

    def __init__(self, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float) -> None:
        super().__init__(
            f"Invalid bounds: ({sw_lat}, {sw_lng}) to ({ne_lat}, {ne_lng})."
            " Southwest corner must be less than northeast corner.",
        )


class InvalidDayError(ValidationError):
    """Custom exception for invalid day."""

    def __init__(self, day: int) -> None:
        super().__init__(f"Invalid day: {day}. Day must be an integer between 1 (Monday) and 7 (Sunday).")


class InvalidLatitudeError(ValidationError):
    """Custom exception for invalid latitude."""

    def __init__(self, lat: float) -> None:
        super().__init__(f"Invalid latitude: {lat}. Latitude must be between -90 and 90 degrees.")


class InvalidLongitudeError(ValidationError):
    """Custom exception for invalid longitude."""

    def __init__(self, lng: float) -> None:
        super().__init__(f"Invalid longitude: {lng}. Longitude must be between -180 and 180 degrees.")


class InvalidPhoneNumberError(ValidationError):
    """Custom exception for invalid phone number."""

    def __init__(self, phone_number: str) -> None:
        super().__init__(f"Invalid phone number: {phone_number}. Phone number must be 10 digits.")


class InvalidSortColumnError(ValidationError):
    """Custom exception for invalid sort column."""

    def __init__(self, sort_column: str) -> None:
        super().__init__(f"Invalid sort column: {sort_column}. Sort column must be a valid attribute of the entity.")


class InvalidTimeFormatError(ValidationError):
    """Custom exception for invalid time format."""

    def __init__(self, time: str) -> None:
        super().__init__(f"Invalid time format: {time}. Expected format is HH:mm.")


class InvalidTimeOrderError(ValidationError):
    """Custom exception for invalid time order."""

    def __init__(self, open_time: str, close_time: str) -> None:
        super().__init__(f"Invalid time order: open time {open_time} must be earlier than close time {close_time}.")
