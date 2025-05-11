import uuid
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.constants import PlaceType
from app.models.food.menu import Menu
from app.models.place import Place

if TYPE_CHECKING:
    from app.db.uow import DBUnitOfWork


@pytest.mark.asyncio
async def test_create_menu_for_food_place(test_uow: "DBUnitOfWork") -> None:
    """Test that a menu can be created for a food place."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu for the place
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Verify that the menu was created
    stmt = select(Menu).where(Menu.place_id == place.id)
    result = await test_uow.get_one_or_none(stmt)
    assert result is not None
    assert result.place_id == place.id


@pytest.mark.asyncio
async def test_create_multiple_menus_for_same_place(test_uow: "DBUnitOfWork") -> None:
    """Test that multiple menus can be created for the same place."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create first menu
    menu1 = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu1)
    await test_uow.commit()

    # Try to create second menu for the same place
    menu2 = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu2)
    await test_uow.commit()

    # Verify that both menus exist
    stmt = select(Menu).where(Menu.place_id == place.id)
    result = await test_uow.get_all(stmt)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_menu_cascade_delete(test_uow: "DBUnitOfWork") -> None:
    """Test that menu is deleted when place is deleted."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu for the place
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Delete the place
    await test_uow.delete(place)
    await test_uow.commit()

    # Verify that the menu was also deleted
    stmt = select(Menu).where(Menu.place_id == place.id)
    result = await test_uow.get_one_or_none(stmt)
    assert result is None
