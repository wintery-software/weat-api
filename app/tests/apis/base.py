from unittest import TestCase

from app import app


class APITestCase(TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
