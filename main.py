from fastapi import FastAPI
from sqlalchemy import text
from database import Base, engine, SessionLocal
from routers import auth, admin, ot, dashboard, audit

# Import models so SQLAlchemy sees them
from models import user, department, status, ot_record, ot_audit

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
def startup_db_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✅ Database connection successful.")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "OT Management API is running"}