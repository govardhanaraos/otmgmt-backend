from models.ot_audit import OTAudit
from datetime import datetime

def log_audit(db, ot_record, user_id, change_type, old, new):
    audit = OTAudit(
        reference_number=ot_record.reference_number,
        ot_record_id=ot_record.id,
        changed_by_user_id=user_id,
        change_type=change_type,
        old_values=old,
        new_values=new,
        changed_at=datetime.utcnow()
    )
    db.add(audit)
    db.commit()