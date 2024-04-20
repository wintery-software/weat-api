from http import HTTPStatus
from typing import Dict

from app.models.restaurant_category import RestaurantCategory
from app.routes.utils.preloads import preload_restaurant_category
from app.routes.utils.requests import get_locale
from app.routes.utils.validates import validate_form, validate_param
from app.schemas.restaurants import RestaurantCategoryForm


def list_restaurant_categories(*args, **kwargs):
    restaurant_categories = RestaurantCategory.list()
    restaurant_categories = [
        restaurant_category.to_dict(locale=get_locale())
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


@validate_param("restaurant_category", side_effect=preload_restaurant_category)
def get_restaurant_category(restaurant_category: RestaurantCategory, *args, **kwargs):
    return (
        restaurant_category.to_dict(locale=get_locale()),
        HTTPStatus.OK,
    )


@validate_param("restaurant_category", side_effect=preload_restaurant_category)
@validate_form(schema=RestaurantCategoryForm)
def update_restaurant_category(
    restaurant_category: RestaurantCategory, body: Dict, *args, **kwargs
):
    try:
        restaurant_category.update(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return restaurant_category.to_dict(), HTTPStatus.OK


@validate_param("restaurant_category", side_effect=preload_restaurant_category)
def delete_restaurant_category(
    restaurant_category: RestaurantCategory, *args, **kwargs
):
    restaurant_category.delete()

    return {}, HTTPStatus.NO_CONTENT
