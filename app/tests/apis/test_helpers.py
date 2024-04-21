from unittest.mock import patch

from flask import Flask, request
from app.tests.apis.base import APITestCase


app = Flask(__name__)


class TestHelpers(APITestCase):
    def test_get_locale(self):
        from app.routes.utils.requests import get_locale

        # Patch 'request.headers.get' to return a controlled Accept-Language header
        with app.test_request_context("/health"):
            with patch.object(request.headers, "get", return_value="fr,en;q=0.8"):
                assert get_locale() == "en"

            with patch.object(request.headers, "get", return_value="es,en;q=0.8"):
                assert get_locale() == "en"

            with patch.object(request.headers, "get", return_value="zh-CN,en;q=0.8"):
                assert get_locale() == "zh-CN"
