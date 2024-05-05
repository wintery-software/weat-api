from pytest import fail

from app.models.user import User


def test_create_user():
    obj = User.create(username="test", password="test")

    assert obj.id is not None
    assert obj.username == "test"
    assert obj.role == User.UserRole.USER

    # Assert that the password is hashed
    assert obj.hashed_password != "test"


def test_create_user_with_admin_role():
    obj = User.create(username="test", password="test", role=User.UserRole.ADMIN)

    assert obj.id is not None
    assert obj.username == "test"
    assert obj.role == User.UserRole.ADMIN


def test_get_user_with_valid_password():
    obj = User.create(username="test", password="test")

    assert User.get(username="test", password="test") == obj


def test_get_user_with_invalid_password():
    User.create(username="test", password="test")

    try:
        User.get(username="test", password="invalid")
        fail()
    except User.InvalidPasswordError:
        pass


def test_get_user_not_found():
    try:
        User.get(username="test", password="test")
        fail()
    except User.UserNotFoundError:
        pass
