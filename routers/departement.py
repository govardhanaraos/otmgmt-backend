from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.department import Department

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return [{"id": d.id, "name": d.name} for d in depts]