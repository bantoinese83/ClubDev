from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from ..core.config import settings

# Database URL
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create the engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle,
)

# Create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Context manager for session handling
@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()

# Dependency function to get a session
def get_db() -> Session:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()