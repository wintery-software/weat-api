from typing import Annotated, List, Optional

from pydantic import UUID4, BaseModel, Field, StringConstraints


class RestaurantSchema(BaseModel):
    id: UUID4

    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    address: Optional[str]
    price: Annotated[int, Field(strict=True, ge=0)]
    rating: Annotated[float, Field(strict=True, ge=0.0, le=5.0)]
    images: List[str] = []

    google_place_id: Optional[str]

    categories: List["RestaurantCategorySchema"] = []
    items: List["RestaurantItemSchema"] = []
    item_categories: List["RestaurantItemCategorySchema"] = []


class RestaurantCategorySchema(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]


class RestaurantItemSchema(BaseModel):
    id: UUID4

    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    description: Optional[str]
    category: Optional["RestaurantItemCategorySchema"]
    price: Annotated[float, Field(strict=True, gt=0.0, pattern=r"^\d+\.\d{2}$")]
    image: Optional[str]


class RestaurantItemCategorySchema(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
