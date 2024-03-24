from http import HTTPStatus
from typing import Dict, List

from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.routes.errors import NotFoundError
from app.routes.utils import (
    validate_form,
    validate_locale,
    validate_param,
)
from app.schemas.restaurants import RestaurantItemForm


def preload_restaurant_from_id(restaurant_id: str, *args, **kwargs):
    restaurant = Restaurant.get(id=restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant not found (id={restaurant_id})")

    return restaurant


def preload_restaurant_item_from_id(restaurant_id: str, item_id: str, *args, **kwargs):
    item = RestaurantItem.get(restaurant_id=restaurant_id, id=item_id)
    if not item:
        raise NotFoundError(
            f"Restaurant item not found (restaurant_id={restaurant_id} id={item_id})"
        )

    return item


@validate_param("locale", validate_locale)
@validate_param("restaurant", side_effect=preload_restaurant_from_id)
def list_restaurant_items(restaurant: Restaurant, locale: str = None, *args, **kwargs):
    restaurant_items = restaurant.items
    restaurant_items = [
        restaurant_item.to_dict(locale) for restaurant_item in restaurant_items
    ]

    return (
        restaurant_items,
        HTTPStatus.OK,
    )


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
@validate_form(schema=RestaurantItemForm, as_list=True)
def create_restaurant_items(restaurant: Restaurant, body: List[Dict], *args, **kwargs):
    restaurant_items = []

    for item_dict in body:
        item = RestaurantItem.create(restaurant_id=restaurant.id, **item_dict)
        restaurant_items.append(item)

    restaurant_items = [item.to_dict() for item in restaurant_items]

    return (restaurant_items, HTTPStatus.CREATED)


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
def delete_restaurant_items(restaurant: Restaurant, *args, **kwargs):
    restaurant_items = restaurant.items
    restaurant.delete_all(restaurant_items)

    return (
        "",
        HTTPStatus.NO_CONTENT,
    )


@validate_param("locale", validate_locale)
@validate_param("item", side_effect=preload_restaurant_item_from_id)
def get_restaurant_item(item: RestaurantItem, locale: str = None, *args, **kwargs):
    return (
        item.to_dict(locale),
        HTTPStatus.OK,
    )


@validate_param("item", side_effect=preload_restaurant_item_from_id)
def update_restaurant_item(item: RestaurantItem, body: Dict, *args, **kwargs):
    item.update(**body)

    return (
        item.to_dict(),
        HTTPStatus.OK,
    )


@validate_param("item", side_effect=preload_restaurant_item_from_id)
def delete_restaurant_item(item: RestaurantItem, *args, **kwargs):
    item.delete()

    return (
        "",
        HTTPStatus.NO_CONTENT,
    )
