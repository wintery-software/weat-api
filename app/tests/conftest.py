import os
import pytest

from app import create_app, db, app
from dotenv import load_dotenv


load_dotenv()


@pytest.fixture(scope="session")
def test_app():
    os.environ["FLASK_ENV"] = "test"

    app = create_app()
    yield app


@pytest.fixture(autouse=True)
def test_app_context(test_app):
    with test_app.app.app_context():
        db.create_all()

        yield

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
