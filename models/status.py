from sqlalchemy import Column, String, Boolean, Integer
from database import engine

class Status(engine):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)