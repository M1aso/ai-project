from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(String(36), nullable=False)
    type = Column(String(50), nullable=False)
    src = Column(String(100))
    payload = Column(JSON, nullable=False)


