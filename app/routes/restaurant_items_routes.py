from http import HTTPStatus
from typing import Dict, List

from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.routes.utils.preloads import preload_restaurant_item
from app.routes.restaurants_routes import preload_restaurant
from app.routes.utils.validates import (
    validate_form,
    validate_param,
)
from app.schemas.restaurants import RestaurantItemForm


@validate_param("restaurant", side_effect=preload_restaurant)
def list_restaurant_items(restaurant: Restaurant, locale: str = None, *args, **kwargs):
    restaurant_items = restaurant.items
    restaurant_items = [
        restaurant_item.to_dict(locale) for restaurant_item in restaurant_items
    ]

    return (
        restaurant_items,
        HTTPStatus.OK,
    )


@validate_param("restaurant", side_effect=preload_restaurant)
@validate_form(schema=RestaurantItemForm, as_list=True)
def create_restaurant_items(restaurant: Restaurant, body: List[Dict], *args, **kwargs):
    restaurant_items = []

    for item_dict in body:
        item = RestaurantItem.create(restaurant_id=restaurant.id, **item_dict)
        restaurant_items.append(item)

    restaurant_items = [item.to_dict() for item in restaurant_items]

    return (restaurant_items, HTTPStatus.CREATED)


@validate_param("item", side_effect=preload_restaurant_item)
def get_restaurant_item(item: RestaurantItem, locale: str = None, *args, **kwargs):
    return (
        item.to_dict(locale),
        HTTPStatus.OK,
    )


@validate_param("item", side_effect=preload_restaurant_item)
def update_restaurant_item(item: RestaurantItem, body: Dict, *args, **kwargs):
    item.update(**body)

    return (
        item.to_dict(),
        HTTPStatus.OK,
    )


@validate_param("item", side_effect=preload_restaurant_item)
def delete_restaurant_item(item: RestaurantItem, *args, **kwargs):
    item.delete()

    return (
        "",
        HTTPStatus.NO_CONTENT,
    )
