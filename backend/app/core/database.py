import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import text

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseUnavailableError(RuntimeError):
    """Raised when the configured database cannot be reached."""


# Engine configuration handles connection pool and pre-ping safety checks.
engine = create_engine(settings.effective_database_url, pool_pre_ping=True)

# Sessionmaker generates sessions bound to our connection pool.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass


def check_database_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError(str(exc)) from exc


def database_status() -> dict[str, str]:
    try:
        check_database_connection()
        return {"status": "connected", "url": settings.safe_database_url}
    except DatabaseUnavailableError as exc:
        logger.warning("database_connection_failed", extra={"database_url": settings.safe_database_url})
        return {"status": "unavailable", "url": settings.safe_database_url, "message": str(exc)}

