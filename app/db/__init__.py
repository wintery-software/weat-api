import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DeclarativeBase = declarative_base()


engine = None
async_session_maker = None


class DBInitializationError(Exception):
    """Custom exception for database initialization errors.

    This exception is raised when there are issues with the database initialization process,
    such as missing environment variables or connection errors.

    Args:
        message (str): The error message to be displayed.

    """

    def __init__(self, missing_vars: list) -> None:
        super().__init__(f"Missing required environment variables for asyncpg connection: {', '.join(missing_vars)}")


def get_async_engine_and_session() -> tuple:
    """Get the async engine and session maker.

    This function retrieves the database connection parameters from environment variables
    and creates an async engine and session maker for the database connection.

    Returns:
        tuple: A tuple containing the async engine and session maker.

    Raises:
        DBInitializationError: If any required environment variables are missing.

    """
    db_user = os.getenv("DB_USERNAME")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    missing_vars = [
        var
        for var, val in {
            "DB_USERNAME": db_user,
            "DB_PASSWORD": db_pass,
            "DB_HOST": db_host,
            "DB_PORT": db_port,
            "DB_NAME": db_name,
        }.items()
        if not val
    ]

    if missing_vars:
        raise DBInitializationError(missing_vars)

    database_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    engine_ = create_async_engine(database_url, echo=True, future=True)
    session_maker_ = async_sessionmaker(bind=engine_, expire_on_commit=False)
    return engine_, session_maker_


def init_async_engine_and_session() -> None:
    """Initialize the async engine and session maker.

    This function creates the async engine and session maker for the database connection.
    It should be called once at the start of the application.
    """
    global engine, async_session_maker
    engine, async_session_maker = get_async_engine_and_session()
