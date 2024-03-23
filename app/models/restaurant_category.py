from typing import List
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, Translation


class RestaurantCategoryTranslation(Translation):
    __tablename__ = "restaurant_categories_translations"

    _fields: List[str] = ["name"]

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurant_categories.id"))
    name: Mapped[str] = mapped_column()


class RestaurantCategory(BaseModel):
    __tablename__ = "restaurant_categories"

    _fields: List[str] = ["name"]

    name: Mapped[str] = mapped_column()

    restaurants: Mapped[List["Restaurant"]] = relationship(
        secondary="restaurants_restaurant_categories", back_populates="categories"
    )

    translations: Mapped[List[RestaurantCategoryTranslation]] = relationship()
    TranslationClass = RestaurantCategoryTranslation
