from datetime import datetime

from sqlalchemy import Column, String, Integer, Date, Numeric, Text, TIMESTAMP, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship
import uuid

from database import Base


# models/ot_detail.py (Example)
class OTDetail(Base):
    __tablename__ = "ot_details"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_number = Column(String, index=True) # Connects to the master OTRecord
    ot_name = Column(String)
    status_id = Column(Integer)
    amount = Column(Numeric)
    comments = Column(String)
    ot_date = Column(Date)
    department_id = Column(Integer)
    invoice_number = Column(String)
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(UUID(as_uuid=True))
    document_path = Column(JSONB, nullable=True)
    deleted = Column(String(1), default='N', nullable=False)