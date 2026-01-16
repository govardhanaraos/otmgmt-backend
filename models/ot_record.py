from sqlalchemy import Column, String, Integer, Date, Numeric, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import Base

class OTRecord(Base):
    __tablename__ = "ot_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_number = Column(String(30), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ot_name = Column(Text, nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    comments = Column(Text)
    ot_date = Column(Date, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    invoice_number = Column(String(100))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    user = relationship("User")
    status = relationship("Status")
    department = relationship("Department")