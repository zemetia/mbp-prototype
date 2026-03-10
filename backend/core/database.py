import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL from env or use a local SQLite for testing if postgres is unavail
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mbp_test.db")

# For sqlite, we need connect_args={"check_same_thread": False}
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Fix postgresql+asyncpg to postgresql for sync engine
    if DATABASE_URL.startswith("postgresql+asyncpg"):
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
