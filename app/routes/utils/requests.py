from flask import request


def get_locale():
    locale = request.headers.get("Accept-Language", "en")
    return locale
