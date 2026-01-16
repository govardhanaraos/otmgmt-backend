from fastapi import FastAPI
from sqlalchemy import text

# Import models FIRST
from models import user, department, status, ot_record, ot_audit
from models.user import User

from database import Base, engine, SessionLocal
from routers import auth, admin, ot, dashboard, audit
from core.security import hash_password


app = FastAPI(title="OT Management API")

# Create tables (for dev only)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(ot.router)
app.include_router(dashboard.router)
app.include_router(audit.router)



@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()

    if not admin:
        new_admin = User(
            username="admin",
            full_name="Administrator",
            role="ADMIN",
            hashed_password=hash_password("admin123")
        )
        db.add(new_admin)
        db.commit()
        print("Default admin user created: admin / admin123")
    else:
        print("Admin user already exists")

    db.close()

@app.get("/")
def root():
    return {"message": "OT Management API is running"}