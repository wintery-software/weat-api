import connexion

from connexion.middleware import MiddlewarePosition
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from starlette.middleware.cors import CORSMiddleware

from app.config import get_config_object


db = SQLAlchemy()
from app.models import *


def create_app():
    connexion_app = connexion.App(__name__, specification_dir="./")

    app = connexion_app.app
    app.config.from_object(get_config_object())
    app.secret_key = app.config["SECRET_KEY"]

    # Database
    db.init_app(app)
    Migrate(app, db)

    connexion_app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["http://localhost:3000", "http://00.local:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    connexion_app.add_api("openapi.yaml")

    return connexion_app


app = create_app()
flask_app = app.app
