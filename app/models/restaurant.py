import uuid
from typing import List

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TranslatableModel, Translation
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory
from app.modules.aws.s3 import S3


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
        "url",
        "google_place_id",
        "categories",
    ]

    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column(nullable=True)
    rating: Mapped[float] = mapped_column(nullable=True)
    images: Mapped[List[str]] = mapped_column(JSON, default=[])
    url: Mapped[str] = mapped_column(nullable=True)

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

    @hybrid_property
    def num_items(self):
        return len(self.restaurant_items)

    @num_items.expression
    def num_items(cls):
        from app import db

        return (
            db.select(func.count(RestaurantItem.id))
            .where(RestaurantItem.restaurant_id == cls.id)
            .label("num_items")
        )

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
            self.add_category(category_id=category_id)

        super().update(**params)

    def add_category(self, **params):
        category = RestaurantCategory.get(id=params["category_id"])
        self.categories.append(category)
        self.commit()

    def add_item(self, **params):
        return RestaurantItem.create(restaurant_id=self.id, **params)

    def add_item_category(self, **params):
        return RestaurantItemCategory.create(restaurant_id=self.id, **params)

    def to_dict(self, locale: str = None, *args, **kwargs):
        result = super().to_dict(locale, *args, **kwargs)

        # TODO: too ugly
        if result["name"] != self.name:
            result["name"] = f"{result['name']} ({self.name})"

        # TODO: still too ugly
        s3 = S3()
        result["images"] = [
            s3.generate_presigned_url(image) for image in result["images"]
        ]

        return result
