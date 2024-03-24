from http import HTTPStatus
from typing import Dict


from app.models.restaurant import Restaurant
from app.routes.errors import NotFoundError
from app.routes.utils import (
    validate_form,
    validate_locale,
    validate_param,
)
from app.schemas.restaurants import RestaurantForm


def preload_restaurant_from_id(restaurant_id: str, *args, **kwargs):
    restaurant = Restaurant.get(id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant not found (id={restaurant_id})")

    return restaurant


@validate_param("locale", validate_locale)
def list_restaurants(locale: str = None, *args, **kwargs):
    restaurants = Restaurant.list()
    restaurants = [restaurant.to_dict(locale=locale) for restaurant in restaurants]

    return (
        restaurants,
        HTTPStatus.OK,
    )


@validate_param("locale", validate_locale)
@validate_param("restaurant", side_effect=preload_restaurant_from_id)
def get_restaurant(restaurant: Restaurant, locale: str = None, *args, **kwargs):
    return (
        restaurant.to_dict(locale=locale),
        HTTPStatus.OK,
    )


@validate_form(schema=RestaurantForm)
def create_restaurant(body: Dict, *args, **kwargs):
    restaurant = Restaurant.create(**body)

    return restaurant.to_dict(), HTTPStatus.CREATED


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
@validate_form(schema=RestaurantForm)
def update_restaurant(restaurant: Restaurant, body: Dict, *args, **kwargs):
    restaurant.update(**body)

    return restaurant.to_dict(), HTTPStatus.OK


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
def delete_restaurant(restaurant: Restaurant, *args, **kwargs):
    restaurant.delete()

    return "", HTTPStatus.NO_CONTENT
