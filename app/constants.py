from enum import Enum


PHONE_NUMBER_REGEX = r"^\d{10}$"
SIMILARITY_THRESHOLD = 0.1


class Language(str, Enum):
    EN_US = "en-US"
    ZH_CN = "zh-CN"


class PlaceType(str, Enum):
    FOOD = "food"
