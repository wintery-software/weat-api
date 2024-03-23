from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory


def test_delete_item_orphan_category():
    restaurant = Restaurant.create(name="Test Restaurant")
    item = restaurant.add_item(name="item1", category="category1")

    assert len(restaurant.items) == 1
    assert len(restaurant.item_categories) == 1
    assert len(RestaurantItemCategory.list()) == 1

    item.delete()

    assert RestaurantItem.get(id=item.id) is None
    assert len(restaurant.items) == 0
    assert len(restaurant.item_categories) == 0
    assert len(RestaurantItemCategory.list()) == 0
