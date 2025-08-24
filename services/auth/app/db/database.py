import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Global variables for lazy initialization
_engine = None
_SessionLocal = None


def get_database_url():
    """Get database URL from environment variable."""
    return os.getenv("DATABASE_URL", "sqlite:///./auth.db")


def get_engine():
    """Get or create database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        
        # Create engine with appropriate settings
        if database_url.startswith("sqlite"):
            # SQLite-specific settings
            _engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
            )
        else:
            # PostgreSQL or other database settings
            _engine = create_engine(
                database_url,
                pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 20)),
                pool_pre_ping=True,
                echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
            )
    return _engine


def get_session_local():
    """Get or create SessionLocal class (lazy initialization)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db() -> Session:
    """Dependency to get database session."""
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    from .models import Base
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables in the database."""
    from .models import Base
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
