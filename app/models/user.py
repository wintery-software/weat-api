import enum
import bcrypt

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class UserNotFoundError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class User(BaseModel):
    __tablename__ = "users"

    _fields: list[str] = ["id", "username", "role"]

    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[bytes] = mapped_column()

    role: Mapped[UserRole] = mapped_column(default=UserRole.USER, type_=Enum(UserRole))

    def _hash_password(self, plaintext_password) -> bytes:
        # Generate a salt
        salt = bcrypt.gensalt()

        # Hash the password along with the salt
        hashed_password = bcrypt.hashpw(plaintext_password.encode("utf-8"), salt)

        return hashed_password

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, value):
        self.hashed_password = self._hash_password(value)

    @classmethod
    def get(cls, **params):
        password = params.pop("password", None)
        obj = super().get(**params)

        if obj is None:
            raise User.UserNotFoundError()

        if not bcrypt.checkpw(password.encode("utf-8"), obj.hashed_password):
            raise User.InvalidPasswordError()

        return obj


User.UserRole = UserRole
User.UserNotFoundError = UserNotFoundError
User.InvalidPasswordError = InvalidPasswordError
