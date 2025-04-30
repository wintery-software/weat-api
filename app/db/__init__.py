from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.settings import settings

DeclarativeBase = declarative_base()


engine = None
async_session_maker = None


def get_async_engine_and_session() -> tuple:
    """Get the async engine and session maker.

    This function retrieves the database connection parameters from environment variables
    and creates an async engine and session maker for the database connection.

    Returns:
        tuple: A tuple containing the async engine and session maker.

    """
    db_username = settings.db_username
    db_pass = settings.db_password
    db_host = settings.db_host
    db_port = settings.db_port
    db_name = settings.db_name

    database_url = f"postgresql+asyncpg://{db_username}:{db_pass}@{db_host}:{db_port}/{db_name}"

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


def get_async_session_maker() -> async_sessionmaker:
    """Get the async session maker.

    Returns:
        async_sessionmaker: The async session maker for the database connection.

    """
    return async_session_maker
