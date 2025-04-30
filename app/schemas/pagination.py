from typing import TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class PaginatedResponse[T](GenericModel):
    """Paginated response schema.

    This schema is used for paginated responses in the API.
    """

    items: list[T]
    total: int
    page: int
    page_size: int
