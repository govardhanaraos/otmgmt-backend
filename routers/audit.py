from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.ot_audit import OTAudit

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/{reference_number}")
def get_audit_history(reference_number: str, db: Session = Depends(get_db)):
    logs = (
        db.query(OTAudit)
        .filter(OTAudit.reference_number == reference_number)
        .order_by(OTAudit.changed_at.asc())
        .all()
    )

    if not logs:
        raise HTTPException(status_code=404, detail="No audit history found")

    return [
        {
            "changed_at": log.changed_at,
            "changed_by_user_id": str(log.changed_by_user_id),
            "change_type": log.change_type,
            "old_values": log.old_values,
            "new_values": log.new_values,
        }
        for log in logs
    ]