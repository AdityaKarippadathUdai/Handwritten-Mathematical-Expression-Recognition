from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

# Engine configuration handles connection pool and pre-ping safety checks.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Sessionmaker generates sessions bound to our connection pool.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass

