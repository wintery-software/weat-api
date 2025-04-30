class CustomError(Exception):
    """Base class for custom exceptions in the application."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Return the string representation of the error message.

        Returns:
            str: The error message.

        """
        return self.message


class ValidationError(CustomError):
    """Exception raised for validation errors."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)


class ObjectNotFoundError(CustomError):
    """Exception raised when an object is not found."""

    def __init__(self, object_type: str, object_id: str) -> None:
        message = f"Object not found: {object_type}(id={object_id})"
        super().__init__(message)
