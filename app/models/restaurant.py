from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import TranslatableModel, Translation
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory
from app.modules.aws.s3 import S3


class RestaurantTranslation(Translation):
    __tablename__ = "restaurants_translations"

    _fields: list[str] = ["name"]

    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("restaurants.id"))
    name: Mapped[str] = mapped_column()


class Restaurant(TranslatableModel):
    __tablename__ = "restaurants"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        CheckConstraint("rating >= 0", name="check_rating_non_negative"),
    )

    _fields: list[str] = [
        "id",
        "name",
        "address",
        "price",
        "rating",
        "images",
        "url",
        "business_hours",
        "google_place_id",
        "categories",
    ]

    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column(nullable=True)
    rating: Mapped[float] = mapped_column(nullable=True)
    images: Mapped[list[str]] = mapped_column(JSON, default=[])
    url: Mapped[str] = mapped_column(nullable=True)
    business_hours: Mapped[list[list[dict[str, str]]]] = mapped_column(JSON, nullable=True)

    google_place_id: Mapped[str] = mapped_column(unique=True, nullable=True)

    categories: Mapped[list["RestaurantCategory"]] = relationship(
        secondary="restaurants_restaurant_categories", back_populates="restaurants"
    )
    items: Mapped[list["RestaurantItem"]] = relationship(cascade="all, delete-orphan")
    item_categories: Mapped[list["RestaurantItemCategory"]] = relationship(
        cascade="all, delete-orphan"
    )

    translations: Mapped[list[RestaurantTranslation]] = relationship(
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
    
    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name is required")

        return name
    
    @validates("price")
    def validate_price(self, key, price):
        if not isinstance(price, int):
            raise ValueError("Price must be an integer")
        if price < 0:
            raise ValueError("Price must be non-negative")

        return price
    
    @validates("rating")
    def validate_rating(self, key, rating):
        if not isinstance(rating, float) and not isinstance(rating, int):
            raise ValueError("Rating must be a number")
        if rating < 0 or rating > 5:
            raise ValueError("Rating must be between 0 and 5")

        return rating

    @validates("business_hours")
    def validate_business_hours(self, key, business_hours):
        default_business_hours = [[] for _ in range(7)]

        if not business_hours:
            return default_business_hours

        if not isinstance(business_hours, list):
            raise ValueError("Business hours must be a list")

        if len(business_hours) != 7:
            raise ValueError("Business hours must have 7 days")
        
        for day in business_hours:
            if not isinstance(day, list):
                raise ValueError("Each day must be a list")
            for time_range in day:
                if not isinstance(time_range, dict):
                    raise ValueError("Each time range must be a dict")
                if "start" not in time_range or "end" not in time_range:
                    raise ValueError("Each time range must have a start and end key")
                
                format = "%H:%M"
                datetime.strptime(time_range["start"], format)
                datetime.strptime(time_range["end"], format)

                if time_range["start"] >= time_range["end"]:
                    raise ValueError("Start must be before end")

        return business_hours

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
