from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from schemas.ot import OTCreate, OTUpdate
from models.ot_record import OTRecord
from services.audit_service import log_audit
import uuid
from datetime import datetime

router = APIRouter(prefix="/ot", tags=["OT"])

def generate_ref():
    return f"OT-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"

@router.post("/")
def create_ot(req: OTCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    ref = generate_ref()

    ot = OTRecord(
        reference_number=ref,
        user_id=user["user_id"],
        ot_name=req.ot_name,
        status_id=req.status_id,
        amount=req.amount,
        comments=req.comments,
        ot_date=req.ot_date,
        department_id=req.department_id,
        invoice_number=req.invoice_number,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(ot)
    db.commit()
    db.refresh(ot)

    log_audit(db, ot, user["user_id"], "CREATE", None, ot.__dict__)

    return {"reference_number": ref}