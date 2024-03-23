from sqlalchemy import ForeignKey

from app import db


restaurants_restaurant_categories = db.Table(
    "restaurants_restaurant_categories",
    db.Column("restaurant_id", ForeignKey("restaurants.id"), primary_key=True),
    db.Column("category_id", ForeignKey("restaurant_categories.id"), primary_key=True),
)
