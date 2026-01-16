from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

# Import models FIRST
from models import user, department, status, ot_record, ot_audit
from models.user import User

from database import Base, engine, SessionLocal
from routers import auth, admin, ot, dashboard, audit
from core.security import hash_password
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    print("🚀 Application Startup: Verifying Database Connection...")
    try:
        # 1. Verify connection with a simple ping
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Database connection successful.")

        # 2. Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified/created.")

        # 3. Create default admin user
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                new_admin = User(
                    username="admin",
                    full_name="Administrator",
                    role="ADMIN",
                    hashed_password=hash_password("admin123")
                )
                db.add(new_admin)
                db.commit()
                print("👤 Default admin user created: admin / admin123")
            else:
                print("ℹ️ Admin user already exists.")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Startup Error: Could not connect to database. {e}")
        # On Render, if this fails, the deployment will fail (which is good)

    yield  # <-- App starts receiving requests here

    # --- SHUTDOWN LOGIC ---
    print("🛑 Application Shutdown: Cleaning up...")
    engine.dispose()


app = FastAPI(
    title="OT Management API",
    version="1.0.0",
    lifespan=lifespan
)
# --- CORS CONFIGURATION ---
origins = [
    "http://localhost:53756",  # Add your current local origin here
    "http://127.0.0.1:53756",
    # Add your production frontend URL here once it is deployed
]

# This fixes the "blocked by CORS policy" error
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (localhost, Render, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(ot.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/")
def health_check():
    return {"status": "online", "message": "OT Management API is running"}