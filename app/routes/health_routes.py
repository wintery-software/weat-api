from http import HTTPStatus


def health():
    return "OK", HTTPStatus.OK
