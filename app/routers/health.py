"""AstroMaster Backend — Health-Check Endpoint."""

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def health_check():
    """Health-Check: Status, Version, DB-Verbindung."""
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version=settings.APP_VERSION,
        db_connected=db_ok,
    )
