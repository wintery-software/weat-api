from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List
from fastapi import APIRouter, Depends

from app.db import async_session_maker
from app.models.users import User
from app.schemas.users import UserResponse

router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@router.post("/users/")
async def create_user(name: str, email: str, db=Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/users/", response_model=List[UserResponse])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select

    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
