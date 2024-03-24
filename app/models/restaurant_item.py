import __future__

from typing import List
import uuid
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TranslatableModel, Translation
from app.models.restaurant_item_category import RestaurantItemCategory


class RestaurantItemTranslation(Translation):
    __tablename__ = "restaurant_items_translations"

    _fields: List[str] = ["name", "description"]

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurant_items.id"))
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)


class RestaurantItem(TranslatableModel):
    __tablename__ = "restaurant_items"

    __table_args__ = (
        CheckConstraint("price_in_cents >= 0", name="check_price_non_negative"),
    )

    _fields: List[str] = [
        "id",
        "name",
        "description",
        "category",
        "price",
        "image",
    ]

    restaurant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"))
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("restaurant_item_categories.id"), nullable=True
    )
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    price_in_cents: Mapped[int] = mapped_column(default=0)
    image: Mapped[str] = mapped_column(default="")

    restaurant: Mapped["Restaurant"] = relationship()
    category: Mapped["RestaurantItemCategory"] = relationship(back_populates="items")

    translations: Mapped[List["RestaurantItemTranslation"]] = relationship(
        cascade="all, delete-orphan"
    )
    TranslationClass = RestaurantItemTranslation

    @property
    def price(self):
        # Convert price from cents to dollars
        return self.price_in_cents / 100

    @price.setter
    def price(self, value):
        # Convert price from dollars to cents
        self.price_in_cents = int(value * 100)

    def update(self, **params):
        old_category = self.category

        super().update(**params)

        self.check_orphan_category(old_category)

    def delete(self):
        old_category = self.category

        super().delete()

        self.check_orphan_category(old_category)

    def check_orphan_category(self, category):
        category = self.category
        if not category.items:
            category.delete()
