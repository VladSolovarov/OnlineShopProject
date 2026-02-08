from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Creates a new session on request and close"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()