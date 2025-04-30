from enum import StrEnum

from app.settings import settings

PHONE_NUMBER_REGEX = r"^\d{10}$"

PLACE_SEARCH_SIMILARITY_THRESHOLD_DEFAULT = 0.3
PLACE_SEARCH_SIMILARITY_THRESHOLD = (
    settings.place_search_similarity_threshold or PLACE_SEARCH_SIMILARITY_THRESHOLD_DEFAULT
)


class Language(StrEnum):
    """Language enum.

    This enum represents the different languages that can be used in the application.
    """

    EN_US = "en-US"
    ZH_CN = "zh-CN"


class PlaceType(StrEnum):
    """PlaceType enum.

    This enum represents the different types of places that can be associated with tags.
    """

    FOOD = "food"
