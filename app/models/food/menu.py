import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.food.dish import Dish, DishCategory
    from app.models.place import Place


class Menu(Base):
    """Menu model.

    This model represents a menu associated with a place.
    It includes the place ID and a list of dish categories.
    """

    __tablename__ = "menus"

    place_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    place: Mapped["Place"] = relationship(back_populates="menus")

    dish_categories: Mapped[list["DishCategory"]] = relationship(
        back_populates="menu",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="menu",
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )
