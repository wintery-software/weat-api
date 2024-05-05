from app.tests.apis.base import APITestCase


class TestUsers(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_create_user(self):
        response = self.client.post(
            "/users", json={"username": "new_username", "password": "new_password"}
        )

        assert response.status_code == 201
        assert "id" in response.json()
        assert response.json()["username"] == "new_username"
        assert response.json()["role"] == "user"

    def test_create_user_duplicate(self):
        response = self.client.post(
            "/users", json={"username": "test", "password": "test"}
        )

        assert response.status_code == 400

    def test_list_users(self):
        response = self.client.get(
            "/users", headers={"Authorization": f"Bearer {self.admin_access_token}"}
        )

        assert response.status_code == 200
        assert len(response.json()) == 2  # admin and user
