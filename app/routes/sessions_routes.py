from http import HTTPStatus

from app.models.user import User
from app.routes.utils.requests import create_token_for_user
from app.routes.utils.validates import validate_form
from app.schemas.sessions import LoginForm


@validate_form(schema=LoginForm)
def login(body, *args, **kwargs):
    username = body.get("username")
    password = body.get("password")

    try:
        user = User.get(username=username, password=password)
    except User.UserNotFoundError:
        return {
            "error": f"User not found (username={username})"
        }, HTTPStatus.UNAUTHORIZED
    except User.InvalidPasswordError:
        return {"error": f"Invalid password"}, HTTPStatus.UNAUTHORIZED

    access_token = create_token_for_user(user)
    return {"access_token": access_token}, HTTPStatus.OK


def logout(*args, **kwargs):
    return {}, HTTPStatus.NO_CONTENT
