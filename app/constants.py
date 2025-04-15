from enum import Enum


PHONE_NUMBER_REGEX = r"^\d{10}$"


class Language(str, Enum):
    EN_US = "en-US"
    ZH_CN = "zh-CN"


class PlaceType(str, Enum):
    FOOD = "food"
