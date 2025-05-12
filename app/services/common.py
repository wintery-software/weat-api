from typing import Literal

from sqlalchemy import Select, asc, desc, func, text

from app.db.uow import DBUnitOfWork


def sort(stmt: Select, entity: type, sort_by: str, order: Literal["asc", "desc"]) -> Select:
    """Modify a query to sort the results.

    Args:
        stmt (Select): The query to sort.
        entity (type): The entity to sort.
        sort_by (str): The field to sort by.
        order (Literal["asc", "desc"]): The order to sort by.

    Returns:
        Select: The modified query.

    """
    # Get the sort column from the entity
    sort_column = getattr(entity, sort_by)

    # Apply case-insensitive sort
    return stmt.order_by(
        desc(func.lower(sort_column)) if order == "desc" else asc(func.lower(sort_column)),
    )


def paginate(stmt: Select, page: int, page_size: int) -> Select:
    """Modify a query to paginate the results.

    Args:
        stmt (Select): The query to paginate.
        page (int): The page number.
        page_size (int): The number of items per page.

    Returns:
        Select: The modified query.

    """
    offset = (page - 1) * page_size
    return stmt.limit(page_size).offset(offset)


async def with_similarity_threshold(db: DBUnitOfWork, threshold: float = 0.3) -> None:
    """Set the similarity threshold for PostgreSQL's pg_trgm extension.

    Args:
        db (DBUnitOfWork): Database unit of work.
        threshold (float): Similarity threshold to set.

    """
    await db.execute(text(f"SET pg_trgm.similarity_threshold = {threshold}"))
