from typing import List
import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TranslatableModel, Translation


class RestaurantItemCategoryTranslation(Translation):
    __tablename__ = "restaurant_item_categories_translations"

    _fields: List[str] = ["name"]

    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("restaurant_item_categories.id")
    )
    name: Mapped[str] = mapped_column(nullable=False)


class RestaurantItemCategory(TranslatableModel):
    __tablename__ = "restaurant_item_categories"

    __table_args__ = (
        UniqueConstraint(
            "restaurant_id", "name", name="unique_item_category_per_restaurant"
        ),
    )

    _fields: List[str] = ["id", "name"]

    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"))

    name: Mapped[str] = mapped_column(nullable=False)

    restaurant: Mapped["Restaurant"] = relationship(back_populates="item_categories")
    items: Mapped[List["RestaurantItem"]] = relationship()

    translations: Mapped[List[RestaurantItemCategoryTranslation]] = relationship(
        cascade="all, delete-orphan"
    )
    TranslationClass = RestaurantItemCategoryTranslation
