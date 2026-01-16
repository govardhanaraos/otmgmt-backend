from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import engine

class User(engine):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    department_id = Column(ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)

    department = relationship("Department")