from typing import Generic, TypeVar
from pydantic.generics import GenericModel


T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
