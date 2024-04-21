from flask import request

from app.constants import DEFAULT_LOCALE, VALID_LOCALES


def get_locale():
    accept_languages = request.headers.get("Accept-Language", "").split(",")

    for language in accept_languages:
        locale = language.split(";")[0]
        if locale in VALID_LOCALES:
            return locale

    return DEFAULT_LOCALE
