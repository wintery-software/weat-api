from http import HTTPStatus
from typing import Dict

from app.models.restaurant import Restaurant
from app.models.restaurant_item_category import RestaurantItemCategory
from app.routes.utils.preloads import preload_restaurant_item_category
from app.routes.restaurants_routes import preload_restaurant
from app.routes.utils.requests import get_locale
from app.routes.utils.validates import validate_form, validate_param
from app.schemas.restaurants import RestaurantItemCategoryForm


@validate_param("restaurant", side_effect=preload_restaurant)
def list_restaurant_item_categories(restaurant: Restaurant, *args, **kwargs):
    restaurant_item_categories = restaurant.item_categories
    restaurant_item_categories = [
        restaurant_item_category.to_dict(locale=get_locale())
        for restaurant_item_category in restaurant_item_categories
    ]

    return (
        restaurant_item_categories,
        HTTPStatus.OK,
    )


@validate_param("restaurant", side_effect=preload_restaurant)
@validate_form(schema=RestaurantItemCategoryForm)
def create_restaurant_item_category(
    restaurant: Restaurant, body: Dict, *args, **kwargs
):
    try:
        restaurant_category = restaurant.add_item_category(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant_category.to_dict(), HTTPStatus.CREATED


@validate_param(
    "restaurant_item_category", side_effect=preload_restaurant_item_category
)
def get_restaurant_item_category(
    restaurant_item_category: RestaurantItemCategory,
    *args,
    **kwargs,
):
    return (
        restaurant_item_category.to_dict(locale=get_locale()),
        HTTPStatus.OK,
    )


@validate_param(
    "restaurant_item_category", side_effect=preload_restaurant_item_category
)
@validate_form(schema=RestaurantItemCategoryForm)
def update_restaurant_item_category(
    restaurant_item_category: RestaurantItemCategory,
    body: Dict,
    *args,
    **kwargs,
):
    try:
        restaurant_item_category.update(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant_item_category.to_dict(), HTTPStatus.OK


@validate_param(
    "restaurant_item_category", side_effect=preload_restaurant_item_category
)
def delete_restaurant_item_category(
    restaurant_item_category: RestaurantItemCategory, *args, **kwargs
):
    restaurant_item_category.delete()

    return {}, HTTPStatus.NO_CONTENT
