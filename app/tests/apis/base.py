import os
from unittest import TestCase

from app import create_app


class APITestCase(TestCase):
    def setUp(self):
        os.environ["FLASK_ENV"] = "test"

        self.app = create_app()
        self.client = self.app.test_client()
