"""Database Configuration and Connection Management"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import AsyncGenerator, Generator, Optional

from ..config.settings import get_settings
from ..config.logger import get_logger

logger = get_logger(__name__)

# Base class for ORM models
Base = declarative_base()

# Synchronous database engine and session
_sync_engine = None
_sync_session_local = None

# Asynchronous database engine and session
_async_engine = None
_async_session_local = None


def get_database_url(async_mode: bool = False) -> str:
    """Get database connection URL"""
    settings = get_settings()
    db_path = settings.database.db_path

    # Create directory if it doesn't exist
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    if settings.database.db_type == "sqlite":
        # For async, use aiosqlite
        prefix = "sqlite+aiosqlite" if async_mode else "sqlite"
        # Convert Windows path to SQLite URL format
        db_path = db_path.replace("\\", "/")
        return f"{prefix}:///{db_path}"
    else:
        raise ValueError(f"Unsupported database type: {settings.database.db_type}")


def init_sync_db():
    """Initialize synchronous database connection"""
    global _sync_engine, _sync_session_local

    if _sync_engine is not None:
        return _sync_engine, _sync_session_local

    db_url = get_database_url(async_mode=False)
    logger.info(f"Initializing synchronous database: {db_url}")

    _sync_engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )

    # Enable foreign keys for SQLite
    if "sqlite" in db_url:
        @event.listens_for(_sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _sync_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_sync_engine
    )

    # Create tables
    Base.metadata.create_all(bind=_sync_engine)
    logger.info("Synchronous database tables created")

    return _sync_engine, _sync_session_local


async def init_async_db():
    """Initialize asynchronous database connection"""
    global _async_engine, _async_session_local

    if _async_engine is not None:
        return _async_engine, _async_session_local

    db_url = get_database_url(async_mode=True)
    logger.info(f"Initializing asynchronous database: {db_url}")

    _async_engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )

    # Enable foreign keys for SQLite
    if "sqlite" in db_url:
        @event.listens_for(_async_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _async_session_local = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    # Create tables
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Asynchronous database tables created")

    return _async_engine, _async_session_local


def get_sync_db() -> Session:
    """Get synchronous database session dependency"""
    engine, session_local = init_sync_db()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get asynchronous database session dependency"""
    engine, session_local = await init_async_db()
    async with session_local() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database (async)"""
    await init_async_db()
    init_sync_db()
    logger.info("Database initialization completed")


def close_database():
    """Close database connections"""
    global _sync_engine, _async_engine

    if _sync_engine is not None:
        _sync_engine.dispose()
        logger.info("Synchronous database connection closed")

    if _async_engine is not None:
        import asyncio
        asyncio.run(_async_engine.dispose())
        logger.info("Asynchronous database connection closed")
