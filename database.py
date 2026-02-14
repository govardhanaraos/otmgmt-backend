import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from supabase import create_client


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None or DATABASE_URL == "":
    DATABASE_URL = "postgresql://neondb_owner:npg_HqbkCFpB5RV7@ep-rapid-glitter-a8uyl3jz-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"

if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL is missing. Check your .env file.")

# Force correct driver for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

print(f"✅ Final DATABASE_URL: {DATABASE_URL}")
SUPABASE_URL = os.getenv("SUPABASE_URL")
if SUPABASE_URL is None or SUPABASE_URL == "":
    SUPABASE_URL = "https://nmhgmhxwdypdcqtjvomt.supabase.co"

SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_KEY is None or SUPABASE_KEY == "":
    SUPABASE_KEY = "sb_publishable_Jfoedc1Yn21-191cthsoMA_RyFnQmd2"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = os.getenv("SUPABASE_BUCKET")
if BUCKET is None or SUPABASE_URL == "":
    BUCKET = "ot-documents"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()