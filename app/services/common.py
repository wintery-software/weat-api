from sqlalchemy import func, select, text

from app.models.uow import DBUnitOfWork


async def paginate(db: DBUnitOfWork, stmt, page: int, page_size: int):
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)
    items = await db.get_all(stmt)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    return items, total


async def with_similarity_threshold(db: DBUnitOfWork, threshold: float = 0.3):
    await db.execute(text(f"SET pg_trgm.similarity_threshold = {threshold}"))
