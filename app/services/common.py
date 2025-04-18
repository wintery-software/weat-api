from sqlalchemy import func, select

from app.models.uow import DBUnitOfWork


async def paginate(db: DBUnitOfWork, stmt, page: int, page_size: int):
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    items = await db.get_all(stmt)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    return items, total
