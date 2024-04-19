from typing import Optional
from pydantic import BaseModel

from app.schemas.translations import (
    RestaurantCategoryTranslation,
    RestaurantItemTranslation,
    RestaurantTranslation,
)


class RestaurantForm(BaseModel):
    name: str
    address: Optional[str] = None
    price: Optional[int] = 0
    rating: Optional[float] = 0.0
    images: list[str] = []
    url: Optional[str] = None
    business_hours: Optional[list[list[dict[str, str]]]] = None

    category_ids: list[str] = []
    google_place_id: Optional[str] = None

    translations: Optional[dict[str, RestaurantTranslation]] = {}


class RestaurantItemForm(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[str] = None
    price: float = 0.0
    image: Optional[str] = None

    translations: Optional[dict[str, RestaurantItemTranslation]] = {}


class RestaurantCategoryForm(BaseModel):
    name: str
    translations: Optional[dict[str, RestaurantCategoryTranslation]] = {}


class RestaurantItemCategoryForm(BaseModel):
    name: str
    translations: Optional[dict[str, RestaurantCategoryTranslation]] = {}
