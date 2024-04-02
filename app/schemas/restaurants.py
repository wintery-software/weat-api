from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field, StringConstraints, validator

from app.constants import VALID_LOCALES
from app.schemas.translations import (
    RestaurantCategoryTranslation,
    RestaurantItemTranslation,
    RestaurantTranslation,
)


class BaseForm(BaseModel):
    @validator("translations", pre=True)
    def validate_locales(cls, translations):
        invalid_locales = [
            locale for locale in translations.keys() if locale not in VALID_LOCALES
        ]
        if invalid_locales:
            raise ValueError(f"Invalid locales: {', '.join(invalid_locales)}")
        return translations

    translations: Optional[Dict[str, Any]] = {}


class RestaurantForm(BaseForm):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    address: Optional[str] = None
    price: Optional[Annotated[int, Field(strict=True, ge=0)]] = 0
    rating: Optional[Annotated[float, Field(strict=True, ge=0.0, le=5.0)]] = 0.0
    images: List[str] = []
    url: Optional[str] = None

    category_ids: List[str] = []
    google_place_id: Optional[str] = None

    translations: Optional[Dict[str, RestaurantTranslation]] = {}


class RestaurantItemForm(BaseForm):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    description: Optional[str] = None
    category_id: Optional[str] = None
    price: Annotated[float, Field(strict=True, ge=0.0)] = 0.0
    image: Optional[str] = None

    translations: Optional[Dict[str, RestaurantItemTranslation]] = {}


class RestaurantCategoryForm(BaseForm):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    translations: Optional[Dict[str, RestaurantCategoryTranslation]] = {}


class RestaurantItemCategoryForm(BaseForm):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    translations: Optional[Dict[str, RestaurantCategoryTranslation]] = {}
