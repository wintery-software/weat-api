from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory


def test_create_restaurant_item():
    restaurant = Restaurant.create(name="Test Restaurant")
    item_category = RestaurantItemCategory.create(
        restaurant_id=restaurant.id, name="category1"
    )
    item = RestaurantItem.create(
        restaurant_id=restaurant.id, name="item1", category=item_category
    )

    assert item.id is not None
    assert item.restaurant_id == restaurant.id
    assert item.name == "item1"
    assert item.category == item_category


def test_delete_restaurant_item_orphan_category():
    restaurant = Restaurant.create(name="Test Restaurant")
    item_category = RestaurantItemCategory.create(
        restaurant_id=restaurant.id, name="category1"
    )
    item = RestaurantItem.create(
        restaurant_id=restaurant.id, name="item1", category=item_category
    )

    assert len(restaurant.items) == 1
    assert len(restaurant.item_categories) == 1
    assert len(RestaurantItemCategory.list()) == 1

    item.delete()

    assert RestaurantItem.get(id=item.id) is None
    assert len(restaurant.items) == 0
    assert len(restaurant.item_categories) == 0
    assert len(RestaurantItemCategory.list()) == 0
