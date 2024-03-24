from http import HTTPStatus
from typing import Dict

from app.models.restaurant_category import RestaurantCategory
from app.routes.errors import NotFoundError
from app.routes.utils import validate_form, validate_param
from app.schemas.restaurants import RestaurantCategoryForm


def preload_restaurant_category_from_id(category_id: str, *args, **kwargs):
    restaurant_category = RestaurantCategory.get(id=category_id)
    if not restaurant_category:
        raise NotFoundError(f"Restaurant category not found (id={category_id})")

    return restaurant_category


def list_restaurant_categories(locale: str = None, *args, **kwargs):
    restaurant_categories = RestaurantCategory.list()
    restaurant_categories = [
        restaurant_category.to_dict(locale)
        for restaurant_category in restaurant_categories
    ]

    return (
        restaurant_categories,
        HTTPStatus.OK,
    )


@validate_form(schema=RestaurantCategoryForm)
def create_restaurant_category(body: Dict, *args, **kwargs):
    try:
        restaurant_category = RestaurantCategory.create(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant_category.to_dict(), HTTPStatus.CREATED


@validate_param("restaurant_category", side_effect=preload_restaurant_category_from_id)
@validate_form(schema=RestaurantCategoryForm)
def update_restaurant_category(
    restaurant_category: RestaurantCategory, body: Dict, *args, **kwargs
):
    try:
        restaurant_category.update(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant_category.to_dict(), HTTPStatus.OK


@validate_param("restaurant_category", side_effect=preload_restaurant_category_from_id)
def delete_restaurant_category(
    restaurant_category: RestaurantCategory, *args, **kwargs
):
    restaurant_category.delete()

    return {}, HTTPStatus.NO_CONTENT
