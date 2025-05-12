import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.constants import PlaceType
from app.models.food.dish import Dish, DishCategory
from app.models.food.menu import Menu
from app.models.place import Place

if TYPE_CHECKING:
    from app.db.uow import DBUnitOfWork


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_dish(test_uow: "DBUnitOfWork") -> None:
    """Test that a dish can be created."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Create a dish category
    category = DishCategory(
        id=uuid.uuid4(),
        menu_id=menu.id,
        name="Main Course",
        name_zh="主菜",
    )
    await test_uow.add(category)
    await test_uow.commit()

    # Create a dish
    dish = Dish(
        id=uuid.uuid4(),
        menu_id=menu.id,
        category_id=category.id,
        name="Steak",
        name_zh="牛排",
        price=Decimal("29.99"),
        properties={"spicy_level": "medium"},
    )
    await test_uow.add(dish)
    await test_uow.commit()

    # Verify that the dish was created
    stmt = select(Dish).where(Dish.id == dish.id)
    result = await test_uow.execute(stmt)
    obj = result.scalar_one_or_none()

    assert obj is not None
    assert obj.name == "Steak"
    assert obj.name_zh == "牛排"
    assert obj.price == Decimal("29.99")
    assert obj.properties == {"spicy_level": "medium"}
    assert obj.menu_id == menu.id
    assert obj.category_id == category.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dish_relationships(test_uow: "DBUnitOfWork") -> None:
    """Test that dish relationships are properly set up."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Create a dish category
    category = DishCategory(
        id=uuid.uuid4(),
        menu_id=menu.id,
        name="Main Course",
        name_zh="主菜",
    )
    await test_uow.add(category)
    await test_uow.commit()

    # Create a dish
    dish = Dish(
        id=uuid.uuid4(),
        menu_id=menu.id,
        category_id=category.id,
        name="Steak",
        name_zh="牛排",
        price=Decimal("29.99"),
    )
    await test_uow.add(dish)
    await test_uow.commit()

    # Verify relationships
    stmt = select(Dish).where(Dish.id == dish.id)
    result = await test_uow.execute(stmt)
    obj = result.scalar_one_or_none()

    assert obj is not None
    assert obj.menu.id == menu.id
    assert obj.category.id == category.id
    assert obj.category.menu.id == menu.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dish_cascade_delete_category(test_uow: "DBUnitOfWork") -> None:
    """Test that dish is not deleted when category is deleted."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Create a dish category
    category = DishCategory(
        id=uuid.uuid4(),
        menu_id=menu.id,
        name="Main Course",
        name_zh="主菜",
    )
    await test_uow.add(category)
    await test_uow.commit()

    # Create a dish
    dish = Dish(
        id=uuid.uuid4(),
        menu_id=menu.id,
        category_id=category.id,
        name="Steak",
        name_zh="牛排",
        price=Decimal("29.99"),
    )
    await test_uow.add(dish)
    await test_uow.commit()

    # Delete the category
    await test_uow.delete(category)
    await test_uow.commit()

    # Verify that the dish is not deleted
    stmt = select(Dish).where(Dish.id == dish.id)
    result = await test_uow.execute(stmt)
    obj = result.scalar_one_or_none()

    assert obj is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dish_cascade_delete_place(test_uow: "DBUnitOfWork") -> None:
    """Test that dish is deleted when place is deleted."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Create a dish category
    category = DishCategory(
        id=uuid.uuid4(),
        menu_id=menu.id,
        name="Main Course",
        name_zh="主菜",
    )
    await test_uow.add(category)
    await test_uow.commit()

    # Create a dish
    dish = Dish(
        id=uuid.uuid4(),
        menu_id=menu.id,
        category_id=category.id,
        name="Steak",
        name_zh="牛排",
        price=Decimal("29.99"),
    )
    await test_uow.add(dish)
    await test_uow.commit()

    # Delete the place
    await test_uow.delete(place)
    await test_uow.commit()

    # Verify that the dish was also deleted
    stmt = select(Dish).where(Dish.id == dish.id)
    result = await test_uow.execute(stmt)
    obj = result.scalar_one_or_none()

    assert obj is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dish_no_category(test_uow: "DBUnitOfWork") -> None:
    """Test that dish can be created without a category."""
    # Create a food place
    place = Place(
        id=uuid.uuid4(),
        name="Test Restaurant",
        type=PlaceType.FOOD,
    )
    await test_uow.add(place)
    await test_uow.commit()

    # Create a menu
    menu = Menu(
        id=uuid.uuid4(),
        place_id=place.id,
    )
    await test_uow.add(menu)
    await test_uow.commit()

    # Create a dish
    dish = Dish(
        id=uuid.uuid4(),
        menu_id=menu.id,
        category_id=None,
        name="Steak",
        name_zh="牛排",
        price=Decimal("29.99"),
    )
    await test_uow.add(dish)
    await test_uow.commit()

    # Verify that the dish was created
    stmt = select(Dish).where(Dish.id == dish.id)
    result = await test_uow.execute(stmt)
    obj = result.scalar_one_or_none()

    assert obj is not None
    assert obj.menu_id == menu.id
