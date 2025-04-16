import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base


DeclarativeBase = declarative_base()


def get_async_engine_and_session():
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
        raise RuntimeError(
            f"Missing required environment variables for asyncpg connection: {', '.join(missing_vars)}"
        )

    database_url = (
        f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

    engine = create_async_engine(database_url, echo=True, future=True)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
    return engine, session_maker


engine, async_session_maker = get_async_engine_and_session()
