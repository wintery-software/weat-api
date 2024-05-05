import datetime
import os
import jwt

from flask import request
from connexion.exceptions import Forbidden

from app.constants import DEFAULT_LOCALE, VALID_LOCALES
from app.models.user import User


secret_key = os.getenv("SECRET_KEY")


def get_locale() -> str:
    accept_languages = request.headers.get("Accept-Language", "").split(",")

    for language in accept_languages:
        locale = language.split(";")[0]
        if locale in VALID_LOCALES:
            return locale

    return DEFAULT_LOCALE


def get_current_user() -> User:
    return None


def verify_admin_token(token) -> dict:
    decoded_token = verify_token(token)

    if not "role" in decoded_token or not decoded_token["role"] == "admin":
        raise Forbidden("Only admin is allowed to access this resource.")

    return decoded_token


def verify_token(token) -> dict:
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise Exception("The token has expired.")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token.")

    return decoded_token


def create_token_for_user(user: User):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.value,
        "iat": datetime.datetime.now(datetime.UTC),
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1),
    }

    access_token = jwt.encode(payload, secret_key, algorithm="HS256")
    return access_token
