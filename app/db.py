from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


def create_engine(url: str) -> AsyncEngine:
    return create_async_engine(url)


def async_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    """
    Factory for assync sessions
    Args:
        engine: an async engine for the database

    Returns:
        a factory for new sessions
    """
    return async_sessionmaker(engine=engine, autoflush=False, expire_on_commit=False)


async def create_tables(engine: AsyncEngine) -> None:
    """
    Initiates the tables based on the data models.
    Used for testing and developing. The production database uses migrations.
    Args:
        engine: async engine
    Returns:
    """
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
