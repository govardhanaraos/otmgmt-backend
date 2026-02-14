from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from core.security import get_current_user
from database import get_db
from models import User
from models.ot_record import OTRecord
from models.status import Status
from sqlalchemy import func
import uuid # Ensure this is imported

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
def dashboard(user=Depends(get_current_user), db: Session = Depends(get_db)):


    rows = (
        db.query(Status.name.label("status_name"), func.sum(OTRecord.amount).label("total_amount"))
        .join(Status, Status.id == OTRecord.status_id)
        .filter(OTRecord.user_id == User.id )  # Use the casted UUID
        .filter(OTRecord.deleted != 'Y')
        .group_by(Status.name)
        .all()
    )

    return {
        "by_status": [
            {"status": row.status_name, "amount": float(row.total_amount or 0)}
            for row in rows
        ]
    }