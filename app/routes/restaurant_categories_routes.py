from http import HTTPStatus
from app.models.restaurant_category import RestaurantCategory


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
