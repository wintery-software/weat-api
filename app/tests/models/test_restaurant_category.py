from pytest import fail
from app.models.restaurant_category import RestaurantCategory


def test_create_restaurant_category():
    obj = RestaurantCategory.create(name="Test Category")

    assert obj.id is not None
    assert obj.name == "Test Category"


def test_name_required():
    try:
        RestaurantCategory.create()
        fail("Should have raised an exception if no name")
    except Exception as e:
        pass


def test_name_min_length():
    try:
        RestaurantCategory.create(name="")
        fail("Should have raised an exception if name is empty")
    except Exception as e:
        pass


def test_name_unique():
    RestaurantCategory.create(name="Test Category")

    try:
        RestaurantCategory.create(name="Test Category")
        fail("Should have raised an exception if duplicate name")
    except Exception as e:
        pass


def test_to_dict():
    obj = RestaurantCategory.create(name="Test Category")
    assert obj.to_dict() == {"name": "Test Category"}


def test_to_dict_with_locale():
    obj = RestaurantCategory.create(name="Test Category")
    obj.add_translation(locale="zh", name="测试分类")

    assert obj.to_dict(locale="en") == {"name": "Test Category"}
    assert obj.to_dict(locale="zh") == {"name": "测试分类"}
