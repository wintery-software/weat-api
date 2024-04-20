from app.models.restaurant_category import RestaurantCategory
from app.tests.apis.base import APITestCase


class TestRestaurantCategories(APITestCase):
    def setUp(self):
        super().setUp()

        self.restaurant_category = RestaurantCategory.create(name="Test Category")
        self.restaurant_category.add_translation("zh-CN", name="测试分类")

    def test_list_restaurant_categories(self):
        response = self.client.get("/restaurants/categories")

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_restaurant_categories_with_locale(self):
        response = self.client.get(
            "/restaurants/categories?locale=zh-CN", headers={"Accept-Language": "zh-CN"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "测试分类"

    def test_create_restaurant_category(self):
        response = self.client.post(
            "/restaurants/categories", json={"name": "New Category"}
        )

        assert response.status_code == 201
        assert response.json()["name"] == "New Category"
        assert len(RestaurantCategory.list()) == 2

    def test_create_restaurant_category_duplicate(self):
        response = self.client.post(
            "/restaurants/categories", json={"name": "Test Category"}
        )

        assert response.status_code == 400

    def test_get_restaurant_category(self):
        response = self.client.get(
            f"/restaurants/categories/{self.restaurant_category.id}"
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Test Category"

    def test_get_restaurant_category_not_found(self):
        response = self.client.get("/restaurants/categories/123")

        assert response.status_code == 404

    def test_update_restaurant_category(self):
        response = self.client.put(
            f"/restaurants/categories/{self.restaurant_category.id}",
            json={"name": "Updated Category"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Category"

    def test_update_restaurant_category_not_found(self):
        response = self.client.put(
            "/restaurants/categories/123",
            json={"name": "Test"},
        )

        assert response.status_code == 404

    def test_update_restaurant_category_duplicate(self):
        new_restaurant_category = RestaurantCategory.create(name="Test Category 2")

        response = self.client.put(
            f"/restaurants/categories/{new_restaurant_category.id}",
            json={"name": "Test Category"},
        )

        assert response.status_code == 400

    def test_delete_restaurant_category(self):
        response = self.client.delete(
            f"/restaurants/categories/{self.restaurant_category.id}"
        )

        assert response.status_code == 204
        assert len(RestaurantCategory.list()) == 0

    def test_delete_restaurant_category_not_found(self):
        response = self.client.delete("/restaurants/categories/123")

        assert response.status_code == 404
