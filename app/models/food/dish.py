import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.food.menu import Menu


class DishCategory(Base):
    """DishCategory model.

    This model represents a category of dishes in a menu.
    It includes the menu ID, category name, and a list of dishes in that category.
    """

    __tablename__ = "dish_categories"

    menu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("menus.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    name_zh: Mapped[str] = mapped_column(String, nullable=False)

    menu: Mapped["Menu"] = relationship(back_populates="dish_categories")
    dishes: Mapped[list["Dish"]] = relationship(back_populates="category")


class Dish(Base):
    """Dish model.

    This model represents a dish in a menu.
    It includes the menu ID, category ID, dish name, price, and optional attributes.
    """

    __tablename__ = "dishes"

    menu_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("menus.id", ondelete="CASCADE"))
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("dish_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    name_zh: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    properties: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    menu: Mapped["Menu"] = relationship(back_populates="dishes")
    category: Mapped["DishCategory | None"] = relationship(back_populates="dishes", uselist=False)
