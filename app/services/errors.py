class CustomError(Exception):
    """Base class for custom exceptions in the application."""


class InitializationError(CustomError):
    """Exception raised during initialization errors."""


class ValidationError(CustomError):
    """Exception raised for validation errors."""


class ObjectNotFoundError(CustomError):
    """Exception raised when an object is not found."""

    def __init__(self, object_type: str, object_id: str) -> None:
        message = f"Object not found: {object_type}(id={object_id})"
        super().__init__(message)
