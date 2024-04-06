from app.models.restaurant import Restaurant
from app.tests.apis.base import APITestCase


class TestRestaurants(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.restaurant = Restaurant.create(
            name="Test Restaurant",
            address="123 Main St",
            price=2,
            rating=4.5,
            google_place_id="1234",
        )
        self.restaurant.add_translation("zh-CN", name="测试餐厅")

    def test_list_restaurants(self):
        response = self.client.get("/restaurants")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1

    def test_list_restaurants_with_locale(self):
        response = self.client.get("/restaurants?locale=zh-CN")

        assert response.status_code == 200
        assert len(response.json()["data"]) == 1
        assert response.json()["data"][0]["name"] == "测试餐厅 (Test Restaurant)"

    def test_list_restaurants_with_sort(self):
        Restaurant.create(
            name="Test Restaurant 2",
            price=1,
            rating=5,
        )
        Restaurant.create(
            name="Test Restaurant 3",
            price=3,
            rating=0,
        )

        response = self.client.get("/restaurants?sort=name&order=asc")
        assert response.json()["data"][0]["name"] == "Test Restaurant"

        response = self.client.get("/restaurants?sort=name&order=desc")
        assert response.json()["data"][0]["name"] == "Test Restaurant 3"

    def test_pagination(self):
        for i in range(2, 16):
            Restaurant.create(
                name=f"Test Restaurant {i}",
                price=1,
                rating=5,
            )

        response = self.client.get("/restaurants?page_size=10")
        assert len(response.json()["data"]) == 10

        response = self.client.get("/restaurants?page_size=10&page=2")
        assert len(response.json()["data"]) == 5

    def test_get_restaurant(self):
        response = self.client.get(f"/restaurants/{self.restaurant.id}")

        assert response.status_code == 200

    def test_get_restaurant_not_found(self):
        response = self.client.get("/restaurants/123")

        assert response.status_code == 404

    def test_get_restaurant_with_locale(self):
        response = self.client.get(f"/restaurants/{self.restaurant.id}?locale=zh-CN")

        assert response.status_code == 200
        assert response.json()["name"] == "测试餐厅 (Test Restaurant)"

    def test_create_restaurant(self):
        data = {
            "name": "New Restaurant",
        }

        response = self.client.post("/restaurants", json=data)

        assert response.status_code == 201

        restaurant = Restaurant.get(id=response.json()["id"])
        assert restaurant is not None
        assert restaurant.name == data["name"]

    def test_create_restaurant_price_invalid(self):
        data = {
            "name": "New Restaurant",
            "price": "invalid",
        }

        response = self.client.post("/restaurants", json=data)

        assert response.status_code == 400

    def test_create_restaurant_price_non_integer(self):
        data = {
            "name": "New Restaurant",
            "price": 1.5,
        }

        response = self.client.post("/restaurants", json=data)

        assert response.status_code == 400

    def test_update_restaurant(self):
        data = {
            "name": "Updated Restaurant",
        }

        response = self.client.put(f"/restaurants/{self.restaurant.id}", json=data)

        assert response.status_code == 200

        self.restaurant.refresh()
        assert self.restaurant.name == data["name"]

    def test_update_restaurant_not_found(self):
        data = {
            "name": "Updated Restaurant",
        }

        response = self.client.put("/restaurants/123", json=data)

        assert response.status_code == 404

    def test_update_restaurant_invalid(self):
        data = {
            "name": "Updated Restaurant",
            "price": "invalid",
        }

        response = self.client.put(f"/restaurants/{self.restaurant.id}", json=data)

        assert response.status_code == 400

    def test_delete_restaurant(self):
        response = self.client.delete(f"/restaurants/{self.restaurant.id}")

        assert response.status_code == 204

        restaurant = Restaurant.get(id=self.restaurant.id)
        assert restaurant is None

    def test_delete_restaurant_not_found(self):
        response = self.client.delete("/restaurants/123")

        assert response.status_code == 404
