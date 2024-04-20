from http import HTTPStatus


def health():
    return "OK", HTTPStatus.OK


def list_apis():
    apis = [
        "/trending/restaurants",
        "/trending/restaurant-items",
        "/restaurants",
        "/restaurants/categories",
    ]

    return apis, HTTPStatus.OK
