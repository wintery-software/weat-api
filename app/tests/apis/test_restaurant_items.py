from app.models.restaurant import Restaurant
from app.models.restaurant_item import RestaurantItem
from app.models.restaurant_item_category import RestaurantItemCategory
from app.tests.apis.base import APITestCase


class TestRestaurantItems(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.restaurant = Restaurant.create(
            name="Test Restaurant",
            address="123 Main St",
            price=2,
            rating=4.5,
            google_place_id="1234",
        )
        self.restaurant_item_category = RestaurantItemCategory.create(
            restaurant_id=self.restaurant.id, name="Test Category"
        )
        self.restaurant_item = RestaurantItem.create(
            restaurant_id=self.restaurant.id,
            name="Test Item",
            description="Test Description",
            category=self.restaurant_item_category,
            price=5.0,
        )
        self.restaurant_item.add_translation("zh-CN", name="测试菜品")

    def test_list_restaurant_items(self):
        response = self.client.get(f"/restaurants/{self.restaurant.id}/items")

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_restaurant_items_with_locale(self):
        response = self.client.get(
            f"/restaurants/{self.restaurant.id}/items?locale=zh-CN"
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "测试菜品"

    def test_create_restaurant_items(self):
        response = self.client.post(
            f"/restaurants/{self.restaurant.id}/items",
            json=[
                {
                    "name": "New Item",
                    "description": "New Description",
                    "category_id": str(self.restaurant_item_category.id),
                    "price": 10.0,
                }
            ],
        )

        assert response.status_code == 201
        assert len(response.json()) == 1
        assert len(self.restaurant.items) == 2

    def test_create_restaurant_items_with_locale(self):
        response = self.client.post(
            f"/restaurants/{self.restaurant.id}/items",
            json=[
                {
                    "name": "New Item",
                    "description": "New Description",
                    "category_id": str(self.restaurant_item_category.id),
                    "price": 10.0,
                    "translations": {
                        "zh-CN": {"name": "新菜品", "description": "新描述"}
                    },
                }
            ],
        )

        assert response.status_code == 201
        assert len(response.json()) == 1
        assert len(self.restaurant.items) == 2
        assert self.restaurant.items[1].get_translation("zh-CN").name == "新菜品"

    def test_delete_restaurant_items(self):
        response = self.client.delete(
            f"/restaurants/{self.restaurant.id}/items",
        )

        assert response.status_code == 204
        assert len(self.restaurant.items) == 0
