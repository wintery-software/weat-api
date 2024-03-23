from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped

from app.models.base import BaseModel


class ExampleModelClass(BaseModel):
    __tablename__ = "example_db_model_class_for_model_tests"

    _fields = ["id", "created_at", "updated_at", "example_field"]

    example_field: Mapped[str] = mapped_column(default="example_value")


def test_create():
    obj = ExampleModelClass.create()

    assert obj.id is not None


def test_create_set_created_at():
    obj = ExampleModelClass.create()

    assert obj.created_at < datetime.now()


def test_create_set_updated_at():
    obj = ExampleModelClass.create()

    assert obj.updated_at < datetime.now()


def test_update():
    obj = ExampleModelClass.create()
    old_value = obj.example_field

    obj.example_field = "new_value"
    obj.update()
    new_value = obj.example_field

    assert old_value != new_value


def test_update_with_parameters():
    obj = ExampleModelClass.create()
    old_value = obj.example_field

    obj.update(example_field="new_value")
    new_value = obj.example_field

    assert old_value != new_value


def test_update_set_updated_at():
    obj = ExampleModelClass.create()
    updated_at_at_create = obj.updated_at

    assert obj.created_at == obj.updated_at

    obj.example_field = "new_value"
    obj.update()
    updated_at_at_update = obj.updated_at

    assert updated_at_at_create < updated_at_at_update


def test_get():
    obj = ExampleModelClass.create()
    this_obj = ExampleModelClass.get(id=obj.id)

    assert obj.id == this_obj.id


def test_get_not_found():
    obj_not_found = ExampleModelClass.get(example_field="obj_not_found")

    assert obj_not_found is None


def test_delete():
    obj = ExampleModelClass.create()
    this_obj = ExampleModelClass.get(id=obj.id)

    assert this_obj is not None

    this_obj.delete()
    this_obj_again = ExampleModelClass.get(id=obj.id)

    assert this_obj_again is None


def test_list():
    ExampleModelClass.create()
    ExampleModelClass.create()

    objs = ExampleModelClass.list()

    assert len(objs) == 2


def test_list_filter_by():
    ExampleModelClass.create(example_field="old_value")
    ExampleModelClass.create(example_field="new_value")

    objs = ExampleModelClass.list(
        filter_by=ExampleModelClass.example_field == "new_value"
    )

    assert len(objs) == 1


def test_list_order_by():
    ExampleModelClass.create(example_field="2")
    ExampleModelClass.create(example_field="1")

    objs = ExampleModelClass.list(order_by=ExampleModelClass.example_field)

    assert len(objs) == 2
    assert objs[0].example_field == "1"
    assert objs[1].example_field == "2"


def test_to_dict():
    obj = ExampleModelClass.create()

    expected_value = {
        "id": obj.id,
        "created_at": obj.created_at,
        "updated_at": obj.updated_at,
        "example_field": obj.example_field,
    }
    actual_value = obj.to_dict()

    assert expected_value == actual_value
