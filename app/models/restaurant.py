from typing import List
import uuid
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import JSON

from app.models.base import TranslatableModel, Translation
from app.models.restaurant_category import RestaurantCategory


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
        "items",
        "item_categories",
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

    @validates("price")
    def validate_price(self, key, value):
        if not isinstance(value, int):
            raise ValueError("Price must be an integer")
        return value

    @classmethod
    def create(cls, **params):
        categories = params.pop("categories", [])

        obj = super().create(**params)
        obj.update_categories(categories)

        return obj

    def update(self, **params):
        categories = params.pop("categories", [])
        self.update_categories(categories)

        super().update(**params)

    def add_category(self, **params):
        from app.models.restaurant_category import RestaurantCategory

        category, _ = RestaurantCategory.get_or_create(**params)
        self.categories.append(category)

    def update_categories(self, categories):
        self.categories.clear()

        for category_dict in categories:
            self.add_category(**category_dict)
