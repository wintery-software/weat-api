from http import HTTPStatus

from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.routes.utils.requests import get_locale


def list_trending_restaurants():
    restaurants = Restaurant.list_random(limit=10)
    restaurants = [restaurant.to_dict(locale=get_locale()) for restaurant in restaurants]

    return restaurants, HTTPStatus.OK


def list_trending_restaurant_items():
    restaurant_items = RestaurantItem.list_random(limit=10)
    restaurant_items = [item.to_dict(locale=get_locale()) for item in restaurant_items]

    return restaurant_items, HTTPStatus.OK
