from typing import List
import uuid
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import TranslatableModel, Translation
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory


class RestaurantTranslation(Translation):
    __tablename__ = "restaurants_translations"

    _fields: List[str] = ["name"]

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"))
    name: Mapped[str] = mapped_column()


class Restaurant(TranslatableModel):
    __tablename__ = "restaurants"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        CheckConstraint("rating >= 0", name="check_rating_non_negative"),
    )

    _fields: List[str] = [
        "id",
        "name",
        "address",
        "price",
        "rating",
        "images",
        "google_place_id",
        "categories",
    ]

    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column(nullable=True)
    rating: Mapped[float] = mapped_column(nullable=True)
    images: Mapped[List[str]] = mapped_column(JSON, default=[])

    google_place_id: Mapped[str] = mapped_column(unique=True, nullable=True)

    categories: Mapped[List["RestaurantCategory"]] = relationship(
        secondary="restaurants_restaurant_categories", back_populates="restaurants"
    )
    items: Mapped[List["RestaurantItem"]] = relationship(cascade="all, delete-orphan")
    item_categories: Mapped[List["RestaurantItemCategory"]] = relationship(
        cascade="all, delete-orphan"
    )

    translations: Mapped[List[RestaurantTranslation]] = relationship(
        cascade="all, delete-orphan"
    )
    TranslationClass = RestaurantTranslation

    @classmethod
    def create(cls, **params):
        category_ids = params.pop("category_ids", [])

        obj = super().create(**params)

        if category_ids:
            obj.update(category_ids=category_ids)

        return obj

    def update(self, **params):
        category_ids = params.pop("category_ids", [])

        self.categories.clear()
        for category_id in category_ids:
            category = RestaurantCategory.get(id=category_id)
            self.add_category(category)

        super().update(**params)

    def add_category(self, category: RestaurantCategory):
        self.categories.append(category)
        self.commit()

    def add_item(self, **params):
        return RestaurantItem.create(restaurant_id=self.id, **params)

    def add_item_category(self, **params):
        return RestaurantItemCategory.create(restaurant_id=self.id, **params)

    def to_dict(self, locale: str = None, *args, **kwargs):
        result = super().to_dict(locale, *args, **kwargs)

        if result["name"] != self.name:
            result["name"] = f"{result['name']} ({self.name})"

        return result
