class CustomError(Exception): ...


class InvalidTagIdError(CustomError):
    """Exception raised for invalid tag IDs."""

    def __init__(self):
        super().__init__("Invalid tag ID(s)")


class DBValidationError(CustomError):
    """Exception raised for database validation errors."""

    def __init__(self, db_error: Exception):
        message = f"Database validation error: {str(db_error)}"
        super().__init__(message)


class DBObjectNotFoundError(CustomError):
    """Exception raised when a database object is not found."""

    def __init__(self, object_type: str, object_id: str):
        message = f"{object_type} with ID {object_id} not found"
        super().__init__(message)
