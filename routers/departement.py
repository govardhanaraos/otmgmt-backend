from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.department import Department
from pydantic import BaseModel

router = APIRouter(prefix="/departments", tags=["Departments"])


class DepartmentSchema(BaseModel):
    name: str


@router.get("/")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).all()
    return [{"id": d.id, "name": d.name} for d in depts]


@router.post("/")
def create_department(data: DepartmentSchema, db: Session = Depends(get_db)):
    existing = db.query(Department).filter(Department.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")

    new_dept = Department(name=data.name)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return {"id": new_dept.id, "name": new_dept.name}


@router.put("/{dept_id}")
def update_department(dept_id: int, data: DepartmentSchema, db: Session = Depends(get_db)):
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db_dept.name = data.name
    db.commit()
    return {"id": db_dept.id, "name": db_dept.name}


@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(db_dept)
    db.commit()
    return {"message": "Deleted successfully"}