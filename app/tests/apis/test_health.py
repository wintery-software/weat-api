from app.tests.apis.base import APITestCase


class TestRestaurants(APITestCase):
    def test_health_endpoint(self):
        response = self.client.get("/health")

        assert response.status_code == 200
