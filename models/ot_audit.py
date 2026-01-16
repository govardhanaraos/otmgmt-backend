from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from database import engine

class OTAudit(engine):
    __tablename__ = "ot_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_number = Column(String(30), nullable=False)
    ot_record_id = Column(UUID(as_uuid=True), ForeignKey("ot_records.id"), nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    change_type = Column(String(20), nullable=False)
    old_values = Column(JSONB)
    new_values = Column(JSONB, nullable=False)
    changed_at = Column(TIMESTAMP)