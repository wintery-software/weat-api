from app.tests.apis.base import APITestCase


class TestSesssions(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_login_success(self):
        response = self.client.post(
            "/login", json={"username": "test", "password": "test"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_user_not_found(self):
        response = self.client.post(
            "/login", json={"username": "invalid", "password": "test"}
        )

        assert response.status_code == 401

    def test_login_invalid_password(self):
        response = self.client.post(
            "/login", json={"username": "test", "password": "invalid"}
        )

        assert response.status_code == 401
