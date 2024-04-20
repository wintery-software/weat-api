from http import HTTPStatus
from typing import Dict

from app.models.restaurant import Restaurant
from app.routes.utils.preloads import preload_restaurant
from app.routes.utils.requests import get_locale
from app.routes.utils.validates import (
    validate_form,
    validate_param,
)
from app.schemas.restaurants import RestaurantForm


def list_restaurants(
    sort: str = "created_at",
    order: str = "asc",
    page: int = 1,
    page_size: int = 10,
    *args,
    **kwargs,
):
    restaurants = Restaurant.list(
        sort=sort, order=order, page=page, page_size=page_size
    )
    restaurants = [
        restaurant.to_dict(locale=get_locale()) for restaurant in restaurants
    ]

    return (
        {
            "total": Restaurant.count(),
            "page": page,
            "page_size": page_size,
            "data": restaurants,
        },
        HTTPStatus.OK,
    )


@validate_param("restaurant", side_effect=preload_restaurant)
def get_restaurant(restaurant: Restaurant, *args, **kwargs):
    return (
        restaurant.to_dict(locale=get_locale()),
        HTTPStatus.OK,
    )


@validate_form(schema=RestaurantForm)
def create_restaurant(body: Dict, *args, **kwargs):
    try:
        restaurant = Restaurant.create(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant.to_dict(), HTTPStatus.CREATED


@validate_param("restaurant", side_effect=preload_restaurant)
@validate_form(schema=RestaurantForm)
def update_restaurant(restaurant: Restaurant, body: Dict, *args, **kwargs):
    try:
        restaurant.update(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant.to_dict(), HTTPStatus.OK


@validate_param("restaurant", side_effect=preload_restaurant)
def delete_restaurant(restaurant: Restaurant, *args, **kwargs):
    restaurant.delete()

    return "", HTTPStatus.NO_CONTENT
