from app.models.restaurant import Restaurant
from app.models.restaurant_item_category import RestaurantItemCategory
from app.tests.apis.base import APITestCase


class TestRestaurantItemCategories(APITestCase):
    def setUp(self):
        super().setUp()

        self.restaurant = Restaurant.create(
            name="Test Restaurant",
            address="123 Main St",
            price=2,
            rating=4.5,
            google_place_id="1234",
        )
        self.restaurant_item_category = RestaurantItemCategory.create(
            restaurant_id=self.restaurant.id, name="Test Item Category"
        )
        self.restaurant_item_category.add_translation("zh-CN", name="测试菜品分类")

    def test_list_restaurant_item_categories(self):
        response = self.client.get(
            f"/restaurants/{self.restaurant.id}/items/categories"
        )

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_restaurant_item_categories_with_locale(self):
        response = self.client.get(
            f"/restaurants/{self.restaurant.id}/items/categories?locale=zh-CN"
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "测试菜品分类"

    def test_create_restaurant_item_category(self):
        response = self.client.post(
            f"/restaurants/{self.restaurant.id}/items/categories",
            json={
                "name": "New Item Category",
            },
        )

        assert response.status_code == 201
        assert response.json()["name"] == "New Item Category"
        assert len(RestaurantItemCategory.list()) == 2

    def test_create_restaurant_category_duplicate(self):
        response = self.client.post(
            f"/restaurants/{self.restaurant.id}/items/categories",
            json={
                "name": "Test Item Category",
            },
        )

        assert response.status_code == 400

    def test_update_restaurant_category(self):
        response = self.client.put(
            f"/restaurants/{self.restaurant.id}/items/categories/{self.restaurant_item_category.id}",
            json={"name": "Updated Category"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Category"

    def test_update_restaurant_category_not_found(self):
        response = self.client.put(
            f"/restaurants/{self.restaurant.id}/items/categories/123",
            json={"name": "Test"},
        )

        assert response.status_code == 404

    def test_update_restaurant_category_duplicate(self):
        new_restaurant_item_category = RestaurantItemCategory.create(
            restaurant_id=self.restaurant.id, name="Test Item Category 2"
        )

        response = self.client.put(
            f"/restaurants/{self.restaurant.id}/items/categories/{new_restaurant_item_category.id}",
            json={"name": "Test Item Category"},
        )

        assert response.status_code == 400

    def test_delete_restaurant_category(self):
        response = self.client.delete(
            f"/restaurants/{self.restaurant.id}/items/categories/{self.restaurant_item_category.id}"
        )

        assert response.status_code == 204
        assert len(RestaurantItemCategory.list()) == 0

    def test_delete_restaurant_item_category_not_found(self):
        response = self.client.delete(
            f"/restaurants/{self.restaurant.id}/items/categories/123"
        )

        assert response.status_code == 404
