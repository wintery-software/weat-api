from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints


class RestaurantTranslation(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]


class RestaurantItemTranslation(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    description: Optional[str] = ""


class RestaurantCategoryTranslation(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
