from pytest import fail
from app.models.restaurant import Restaurant


def test_unique_category_per_restaurant():
    restaurant = Restaurant.create(name="Test Restaurant")
    restaurant.add_item_category(name="Test Category")

    try:
        restaurant.add_item_category(name="Test Category")
        fail("Should have raised an exception if duplicate category")
    except Exception as e:
        restaurant.rollback()
        pass

    # Should be able to add the same item category name to another restaurant
    another_restaurant = Restaurant.create(name="Another Restaurant")
    another_restaurant.add_item_category(name="Test sdf Category")
