from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import UserCreate, UserResponse
from core.security import hash_password
from models.user import User
from models.status import Status
from models.department import Department

router = APIRouter(prefix="/admin", tags=["Admin"])

# Create user
@router.post("/users", response_model=UserResponse)
def create_user(req: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=req.username,
        full_name=req.full_name,
        role=req.role,
        department_id=req.department_id,
        password_hash=hash_password(req.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Reset password
@router.post("/users/{user_id}/reset-password")
def reset_password(user_id: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"message": "Password reset successful"}

# Add status
@router.post("/statuses")
def add_status(name: str, db: Session = Depends(get_db)):
    status = Status(name=name)
    db.add(status)
    db.commit()
    return {"message": "Status added"}

# Add department
@router.post("/departments")
def add_department(name: str, db: Session = Depends(get_db)):
    dept = Department(name=name)
    db.add(dept)
    db.commit()
    return {"message": "Department added"}