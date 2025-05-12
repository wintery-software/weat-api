from typing import Literal

from pydantic import BaseModel


class PaginationOptions(BaseModel):
    """Pagination options schema.

    This schema is used for pagination options in the API.
    """

    page: int = 1
    page_size: int = 10


class SortOptions(BaseModel):
    """Sort options schema.

    This schema is used for sort options in the API.
    """

    sort_by: str | None = None
    order: Literal["asc", "desc"] = "asc"


class FilterOptions(BaseModel):
    """Filter options schema.

    This schema is used for filter options in the API.
    """

    q: str | None = None
