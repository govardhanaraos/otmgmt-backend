from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.status import Status

router = APIRouter(prefix="/statuses", tags=["Statuses"])

@router.get("/")
def list_statuses(db: Session = Depends(get_db)):
    depts = db.query(Status).all()
    return [{"id": d.id, "name": d.name} for d in depts]