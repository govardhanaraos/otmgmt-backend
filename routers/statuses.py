from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.status import Status
from pydantic import BaseModel

router = APIRouter(prefix="/statuses", tags=["Statuses"])


# Schema for updating status
class StatusUpdate(BaseModel):
    name: str


@router.get("/")
def list_statuses(db: Session = Depends(get_db)):
    depts = db.query(Status).all()
    return [{"id": d.id, "name": d.name} for d in depts]


@router.put("/{status_id}")
def update_status(status_id: int, status_data: StatusUpdate, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_status=404, detail="Status not found")

    db_status.name = status_data.name
    db.commit()
    return {"message": "Update successful"}


@router.post("/")
def create_status(status_data: StatusUpdate, db: Session = Depends(get_db)):
    # Check if name already exists in DB
    existing = db.query(Status).filter(Status.name == status_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Status already exists")

    new_status = Status(name=status_data.name)
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return {"id": new_status.id, "name": new_status.name}


@router.delete("/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")

    db.delete(db_status)
    db.commit()
    return {"message": "Deleted successfully"}