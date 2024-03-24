from typing import Annotated, Dict, List, Optional
from pydantic import BaseModel, Field, StringConstraints, validator

from app.constants import VALID_LOCALES


class RestaurantForm(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    address: Optional[str] = ""
    price: Optional[Annotated[int, Field(strict=True, ge=0)]] = 0
    rating: Optional[Annotated[float, Field(strict=True, ge=0.0, le=5.0)]] = 0.0
    images: List[str] = []

    google_place_id: Optional[str] = ""

    translations: Optional[Dict[str, "RestaurantTranslation"]] = {}

    @validator("translations", pre=True)
    def validate_locales(cls, translations):
        invalid_locales = [
            locale for locale in translations.keys() if locale not in VALID_LOCALES
        ]
        if invalid_locales:
            raise ValueError(f"Invalid locales: {', '.join(invalid_locales)}")
        return translations


class RestaurantTranslation(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]


class RestaurantItemForm(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    description: Optional[str] = ""
    category: Optional[str] = ""
    price: Annotated[float, Field(strict=True, ge=0.0)] = 0.0
    image: Optional[str] = ""

    translations: Optional[Dict[str, "RestaurantItemTranslation"]] = {}

    @validator("translations", pre=True)
    def validate_locales(cls, translations):
        invalid_locales = [
            locale for locale in translations.keys() if locale not in VALID_LOCALES
        ]
        if invalid_locales:
            raise ValueError(f"Invalid locales: {', '.join(invalid_locales)}")
        return translations


class RestaurantItemTranslation(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    description: Optional[str] = ""
