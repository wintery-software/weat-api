import os
from unittest import TestCase

from app import create_app
from app.models.user import User
from app.routes.utils.requests import create_token_for_user


class APITestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        os.environ["FLASK_ENV"] = "test"

        cls.app = create_app()

    def setUp(self) -> None:
        super().setUp()

        self.client = self.app.test_client()

        self.user = User.create(username="test", password="test")
        self.access_token = create_token_for_user(self.user)

        self.admin = User.create(
            username="admin", password="admin", role=User.UserRole.ADMIN
        )
        self.admin_access_token = create_token_for_user(self.admin)

    def tearDown(self) -> None:
        super().tearDown()

        self.user.delete()
        self.admin.delete()
