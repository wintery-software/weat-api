from sqlalchemy import func, select, text
from sqlalchemy.sql import Executable

from app.db.uow import DBUnitOfWork


async def paginate(
    db: DBUnitOfWork,
    stmt: Executable,
    page: int,
    page_size: int,
) -> tuple:
    """Paginate the results of a SQLAlchemy query.

    Args:
        db (DBUnitOfWork): Database unit of work.
        stmt: SQLAlchemy query statement.
        page (int): The page number to retrieve.
        page_size (int): The number of items per page.

    Returns:
        tuple: A tuple containing the paginated items and the total count of items.

    """
    offset = (page - 1) * page_size
    items_stmt = stmt.offset(offset).limit(page_size)
    items = await db.get_all(items_stmt)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    return items, total


async def with_similarity_threshold(db: DBUnitOfWork, threshold: float = 0.3) -> None:
    """Set the similarity threshold for PostgreSQL's pg_trgm extension.

    Args:
        db (DBUnitOfWork): Database unit of work.
        threshold (float): Similarity threshold to set.

    """
    await db.execute(text(f"SET pg_trgm.similarity_threshold = {threshold}"))
