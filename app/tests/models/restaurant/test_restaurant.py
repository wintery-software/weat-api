from pytest import fail

from app.models.restaurant import Restaurant, RestaurantTranslation
from app.models.restaurant_category import RestaurantCategory
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory


def test_create():
    obj = Restaurant.create(name="Test Restaurant")
    assert obj.id is not None


def test_place_id_unique():
    name = "Test Restaurant"
    same_google_place_id = "1234"

    obj = Restaurant.create(name=name, google_place_id=same_google_place_id)
    assert obj.id is not None

    try:
        Restaurant.create(name=name, google_place_id=same_google_place_id)
        fail("Should have raised an exception if google_place_id is not unique")
    except Exception as e:
        pass


def test_price_non_negative():
    try:
        Restaurant.create(name="Test Restaurant", price=-1)
        fail("Should have raised an exception if price is negative")
    except Exception as e:
        pass


def test_rating_non_negative():
    try:
        Restaurant.create(name="Test Restaurant", rating=-1)
        fail("Should have raised an exception if rating is negative")
    except Exception as e:
        pass


def test_to_dict():
    name = "Test Restaurant"
    address = "123 Main St"
    price = 2
    rating = 4.5
    images = ["image1.jpg", "image2.jpg"]
    url = "http://example.com"
    google_place_id = "1234"

    obj = Restaurant.create(
        name=name,
        address=address,
        price=price,
        rating=rating,
        images=images,
        url=url,
        google_place_id=google_place_id,
    )

    assert obj.id is not None

    result = obj.to_dict()

    assert result["name"] == name
    assert result["address"] == address
    assert result["price"] == price
    assert result["rating"] == rating
    assert len(result["images"]) == len(images)
    assert result["google_place_id"] == google_place_id
    assert result["categories"] == []


def test_to_dict_with_locale():
    name = "Test Restaurant"
    name_zh = "测试餐厅"
    address = "123 Main St"
    price = 2
    rating = 4.5
    images = ["image1.jpg", "image2.jpg"]
    url = "http://example.com"
    google_place_id = "1234"

    obj = Restaurant.create(
        name=name,
        address=address,
        price=price,
        rating=rating,
        images=images,
        url=url,
        google_place_id=google_place_id,
    )
    obj.add_translation(locale="zh", name=name_zh)

    assert obj.id is not None

    result = obj.to_dict(locale="zh")

    assert result["name"] == f"{name_zh} ({name})"
    assert result["address"] == address
    assert result["price"] == price
    assert result["rating"] == rating
    assert len(result["images"]) == len(images)
    assert result["google_place_id"] == google_place_id
    assert result["categories"] == []


def test_create_with_categories():
    category = RestaurantCategory.create(name="category1")
    obj = Restaurant.create(name="Test Restaurant", category_ids=[category.id])

    assert obj.id is not None
    assert obj.to_dict()["categories"] == [category.to_dict()]


def test_create_with_non_existent_categories():
    try:
        Restaurant.create(name="Test Restaurant", category_ids=["non_existent_id"])
        fail("Should have raised an exception if category does not exist")
    except Exception as e:
        pass


def test_update_with_categories():
    obj = Restaurant.create(name="Test Restaurant")

    assert obj.to_dict()["categories"] == []

    category1 = RestaurantCategory.create(name="category1")
    obj.update(category_ids=[category1.id])

    assert obj.to_dict()["categories"] == [category1.to_dict()]

    category2 = RestaurantCategory.create(name="category2")
    obj.update(category_ids=[category1.id, category2.id])

    assert obj.to_dict()["categories"] == [category1.to_dict(), category2.to_dict()]


def test_create_with_translations():
    obj = Restaurant.create(
        name="Test Restaurant", translations={"zh": {"name": "测试餐厅"}}
    )

    assert obj.id is not None
    assert obj.get_translation("zh") is not None
    assert obj.get_translation("zh").name == "测试餐厅"


def test_update_with_translations():
    obj = Restaurant.create(name="Test Restaurant")

    assert obj.get_translation("zh") is None

    obj.add_translation(locale="zh", name="测试餐厅")

    assert obj.get_translation("zh") is not None
    assert obj.get_translation("zh").name == "测试餐厅"

    obj.update(translations={"zh": {"name": "新的测试餐厅"}})
    assert obj.get_translation("zh") is not None
    assert obj.get_translation("zh").name == "新的测试餐厅"


def test_delete():
    obj = Restaurant.create(name="Test Restaurant")

    obj.delete()

    assert Restaurant.get(id=obj.id) is None


def test_delete_with_categories():
    category = RestaurantCategory.create(name="category1")
    obj = Restaurant.create(name="Test Restaurant", category_ids=[category.id])

    assert Restaurant.get(id=obj.id) is not None
    assert len(RestaurantCategory.list()) == 1

    obj.delete()

    assert Restaurant.get(id=obj.id) is None
    # RestaurantCategory itself is not deleted, only the association in the join table is deleted
    assert len(RestaurantCategory.list()) == 1


def test_delete_with_items_and_item_categories():
    obj = Restaurant.create(name="Test Restaurant")
    RestaurantItem.create(
        restaurant_id=obj.id,
        name="item1",
        category=RestaurantItemCategory.create(restaurant_id=obj.id, name="category1"),
    )

    assert len(obj.items) == 1
    assert len(obj.item_categories) == 1

    obj.delete()

    assert Restaurant.get(id=obj.id) is None


def test_delete_with_translations():
    obj = Restaurant.create(
        name="Test Restaurant", translations={"zh": {"name": "测试餐厅"}}
    )

    assert Restaurant.get(id=obj.id) is not None
    assert len(RestaurantTranslation.list()) == 1

    obj.delete()

    assert Restaurant.get(id=obj.id) is None
    assert len(RestaurantTranslation.list()) == 0


def test_add_category():
    obj = Restaurant.create(name="Test Restaurant")
    category = RestaurantCategory.create(name="category1")

    obj.add_category(category_id=category.id)

    assert obj.to_dict()["categories"] == [category.to_dict()]
