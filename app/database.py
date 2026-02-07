"""AstroMaster Backend — SQLAlchemy Database Setup."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI Dependency: liefert eine DB-Session und schließt sie danach."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
