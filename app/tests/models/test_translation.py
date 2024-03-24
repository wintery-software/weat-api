from typing import List
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TranslatableModel, Translation


class ExampleTranslation(Translation):
    __tablename__ = "example_db_model_localizables"

    _fields: List[str] = ["example_field"]

    parent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("example_db_model_class_for_translation_tests.id")
    )
    example_field: Mapped[str] = mapped_column()


class ExampleModelClass(TranslatableModel):
    __tablename__ = "example_db_model_class_for_translation_tests"

    _fields = ["id", "example_field", "created_at", "updated_at"]

    example_field: Mapped[str] = mapped_column()

    translations: Mapped[List["ExampleTranslation"]] = relationship()
    TranslationClass = ExampleTranslation


def test_to_dict():
    obj = ExampleModelClass.create(example_field="example_value")

    assert obj.id is not None
    assert obj.to_dict()["example_field"] == "example_value"


def test_to_dict_with_locale():
    obj = ExampleModelClass.create(example_field="example_value")
    obj.add_translation(locale="zh", example_field="一颗赞波")

    assert obj.id is not None
    assert obj.to_dict(locale="en")["example_field"] == "example_value"
    assert obj.to_dict(locale="zh")["example_field"] == "一颗赞波"


def test_add_translation():
    obj = ExampleModelClass.create(example_field="example_value")
    obj.add_translation(locale="zh", example_field="一颗赞波")

    assert obj.get_translation("zh") is not None


def test_remove_translation():
    obj = ExampleModelClass.create(example_field="example_value")

    obj.add_translation(locale="zh", example_field="一颗赞波")
    assert obj.get_translation("zh") is not None

    obj.remove_translation("zh")
    assert obj.get_translation("zh") is None


def test_translation_to_dict():
    obj = ExampleModelClass.create(example_field="example_value")

    obj.add_translation(locale="zh", example_field="一颗赞波")
    assert obj.translation_to_dict("zh") == {"example_field": "一颗赞波"}
    assert obj.translation_to_dict("en") == {}
    assert obj.translation_to_dict() == {}
