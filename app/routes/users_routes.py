from http import HTTPStatus
from app.models.user import User
from app.routes.utils.validates import validate_form
from app.schemas.users import UserForm


def list_users(*args, **kwargs):
    users = User.list()
    users = [user.to_dict() for user in users]

    return users, HTTPStatus.OK


@validate_form(schema=UserForm)
def create_user(body: dict, *args, **kwargs):
    try:
        user = User.create(**body)
    except Exception as e:
        return {"error": str(e)}, HTTPStatus.BAD_REQUEST

    return user.to_dict(), HTTPStatus.CREATED
