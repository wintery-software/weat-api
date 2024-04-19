from functools import wraps
from http import HTTPStatus

from pydantic import ValidationError

from app.routes.utils.errors import NotFoundError


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
                return {"error": str(e)}, HTTPStatus.NOT_FOUND
            except Exception as e:
                return {"error": str(e)}, HTTPStatus.BAD_REQUEST

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
                return {"error": e.errors()[0]}, HTTPStatus.BAD_REQUEST

            return f(*args, **kwargs)

        return func

    return decorator
