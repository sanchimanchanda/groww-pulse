"""
SQLite for the hackathon demo (see TRADEOFFS.md for why not Postgres-in-demo).
Schema is written to be a drop-in match for PostgreSQL (SQLAlchemy Core types
only, no SQLite-specific features), so `DATABASE_URL=postgresql://...` is a
one-line swap for a real deployment.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./groww_pulse.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
