from typing import Annotated, Dict, List, Optional
from pydantic import BaseModel, Field, StringConstraints, validator

from app.constants import VALID_LOCALES


class RestaurantFormSchema(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
    address: Optional[str] = ""
    price: Optional[Annotated[int, Field(strict=True, gt=0)]] = 0
    rating: Optional[Annotated[float, Field(strict=True, gt=0.0, le=5.0)]] = 0.0
    images: List[str] = []

    google_place_id: Optional[str] = ""

    translations: Optional[Dict[str, "RestaurantTranslationSchema"]] = {}

    @validator("translations", pre=True)
    def validate_locales(cls, translations):
        invalid_locales = [
            locale for locale in translations.keys() if locale not in VALID_LOCALES
        ]
        if invalid_locales:
            raise ValueError(f"Invalid locales: {', '.join(invalid_locales)}")
        return translations


class RestaurantTranslationSchema(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]
