from functools import wraps
from http import HTTPStatus
from typing import Dict

from pydantic import ValidationError

from app.models.restaurant import Restaurant
from app.schemas.forms import RestaurantFormSchema
from app.schemas.restaurants import RestaurantSchema


def validates_restaurant(f):
    @wraps(f)
    def func(*args, **kwargs):
        restaurant_id = kwargs.get("restaurant_id")

        restaurant = Restaurant.get(id=restaurant_id)
        if not restaurant:
            return {
                "errors": [f"Restaurant not found (id={restaurant_id})"]
            }, HTTPStatus.NOT_FOUND

        kwargs["restaurant"] = restaurant
        return f(*args, **kwargs)

    return func


def list_restaurants(locale: str = None, *args, **kwargs):
    restaurants = Restaurant.list()
    restaurants = [restaurant.to_dict(locale=locale) for restaurant in restaurants]

    return (
        restaurants,
        HTTPStatus.OK,
    )


@validates_restaurant
def get_restaurant(restaurant: Restaurant, locale: str = None, *args, **kwargs):
    return (
        RestaurantSchema(**restaurant.to_dict(locale=locale)).model_dump(),
        HTTPStatus.OK,
    )


def create_restaurant(body: Dict, *args, **kwargs):
    try:
        values = RestaurantFormSchema(**body).model_dump()
    except ValidationError as e:
        return {"errors": e.errors()}, HTTPStatus.BAD_REQUEST

    restaurant = Restaurant.create(**values)
    restaurant = restaurant.to_dict()

    return RestaurantSchema(**restaurant).model_dump(), HTTPStatus.CREATED


@validates_restaurant
def update_restaurant(restaurant: Restaurant, body: Dict, *args, **kwargs):
    try:
        values = RestaurantFormSchema(**body).model_dump()
    except ValidationError as e:
        return {"errors": e.errors()}, HTTPStatus.BAD_REQUEST

    restaurant.update(**values)
    restaurant = restaurant.to_dict()

    return RestaurantSchema(**restaurant).model_dump(), HTTPStatus.OK


@validates_restaurant
def delete_restaurant(restaurant: Restaurant, *args, **kwargs):
    restaurant.delete()

    return "", HTTPStatus.NO_CONTENT
