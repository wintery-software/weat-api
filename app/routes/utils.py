from functools import wraps
from http import HTTPStatus

from pydantic import ValidationError

from app.constants import VALID_LOCALES
from app.routes.errors import NotFoundError


def validate_locale(locale: str = None, *args, **kwargs):
    locale = kwargs.get("locale", "en")

    if locale not in VALID_LOCALES:
        raise ValueError(f"Invalid locale: {locale}")


def validate_param(key, validator=None, side_effect=None):
    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            try:
                if validator:
                    validator(*args, **kwargs)
                if side_effect:
                    kwargs[key] = side_effect(*args, **kwargs)
            except NotFoundError as e:
                return {"errors": [str(e)]}, HTTPStatus.NOT_FOUND
            except Exception as e:
                return {"errors": [str(e)]}, HTTPStatus.BAD_REQUEST

            return f(*args, **kwargs)

        return func

    return decorator


def validate_form(schema, as_list=False):
    def decorator(f):
        @wraps(f)
        def func(*args, **kwargs):
            body = kwargs.get("body")

            try:
                if as_list:
                    kwargs["body"] = [dict(schema(**b)) for b in body]
                else:
                    kwargs["body"] = dict(schema(**body))
            except ValidationError as e:
                return {"errors": e.errors()}, HTTPStatus.BAD_REQUEST

            return f(*args, **kwargs)

        return func

    return decorator
