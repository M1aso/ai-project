import os
from sqlalchemy import Column, DateTime, Integer, String, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analytics.db")
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(String(36), nullable=False)
    type = Column(String(50), nullable=False)
    src = Column(String(100))
    payload = Column(JSON, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
