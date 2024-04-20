from app.models.restaurant import Restaurant
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory
from app.routes.utils.errors import NotFoundError


def preload_restaurant(restaurant_id: str, *args, **kwargs):
    restaurant = Restaurant.get(id=restaurant_id)
    if not restaurant:
        raise NotFoundError(f"Restaurant not found (id={restaurant_id})")

    return restaurant


def preload_restaurant_category(category_id: str, *args, **kwargs):
    restaurant_category = RestaurantCategory.get(id=category_id)
    if not restaurant_category:
        raise NotFoundError(f"Restaurant category not found (id={category_id})")

    return restaurant_category


def preload_restaurant_item(restaurant_id: str, item_id: str, *args, **kwargs):
    item = RestaurantItem.get(restaurant_id=restaurant_id, id=item_id)
    if not item:
        raise NotFoundError(
            f"Restaurant item not found (restaurant_id={restaurant_id} id={item_id})"
        )

    return item


def preload_restaurant_item_category(restaurant_id: str, category_id: str, *args, **kwargs):
    restaurant_item_category = RestaurantItemCategory.get(id=category_id, restaurant_id=restaurant_id)
    if not restaurant_item_category:
        raise NotFoundError(f"Restaurant item category not found (id={category_id})")

    return restaurant_item_category
