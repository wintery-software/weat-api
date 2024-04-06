from http import HTTPStatus
from typing import Dict

from app.models.restaurant import Restaurant
from app.models.restaurant_item_category import RestaurantItemCategory
from app.routes.errors import NotFoundError
from app.routes.restaurants_routes import preload_restaurant_from_id
from app.routes.utils import validate_form, validate_param
from app.schemas.restaurants import RestaurantItemCategoryForm


def preload_restaurant_item_category_from_id(category_id: str, *args, **kwargs):
    restaurant_item_category = RestaurantItemCategory.get(id=category_id)
    if not restaurant_item_category:
        raise NotFoundError(f"Restaurant item category not found (id={category_id})")

    return restaurant_item_category


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
def list_restaurant_item_categories(
    restaurant: Restaurant, locale: str = None, *args, **kwargs
):
    restaurant_item_categories = restaurant.item_categories
    restaurant_item_categories = [
        restaurant_item_category.to_dict(locale)
        for restaurant_item_category in restaurant_item_categories
    ]

    return (
        restaurant_item_categories,
        HTTPStatus.OK,
    )


@validate_param("restaurant", side_effect=preload_restaurant_from_id)
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
    "restaurant_item_category", side_effect=preload_restaurant_item_category_from_id
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
    "restaurant_item_category", side_effect=preload_restaurant_item_category_from_id
)
def delete_restaurant_item_category(
    restaurant_item_category: RestaurantItemCategory, *args, **kwargs
):
    restaurant_item_category.delete()

    return {}, HTTPStatus.NO_CONTENT
