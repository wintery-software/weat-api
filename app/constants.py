from enum import Enum
import os


PHONE_NUMBER_REGEX = r"^\d{10}$"
PLACE_SEARCH_SIMILARITY_THRESHOLD = os.getenv("SIMILARITY_THRESHOLD", 0.3)


class Language(str, Enum):
    EN_US = "en-US"
    ZH_CN = "zh-CN"


class PlaceType(str, Enum):
    FOOD = "food"
