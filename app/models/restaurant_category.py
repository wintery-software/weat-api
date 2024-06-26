from typing import List
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import TranslatableModel, Translation


class RestaurantCategoryTranslation(Translation):
    __tablename__ = "restaurant_categories_translations"

    _fields: List[str] = ["name"]

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurant_categories.id"))
    name: Mapped[str] = mapped_column(nullable=False)


class RestaurantCategory(TranslatableModel):
    __tablename__ = "restaurant_categories"

    _fields: List[str] = ["id", "name"]

    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    restaurants: Mapped[List["Restaurant"]] = relationship(
        secondary="restaurants_restaurant_categories",
        back_populates="categories",
    )

    translations: Mapped[List[RestaurantCategoryTranslation]] = relationship(
        cascade="all, delete-orphan"
    )
    TranslationClass = RestaurantCategoryTranslation

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name is required")

        return name