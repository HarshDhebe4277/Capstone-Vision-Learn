"""Database engine, session factory, and FastAPI dependency."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Harsh8928@localhost:5432/VisionLearn",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # auto-reconnect on stale connections
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
