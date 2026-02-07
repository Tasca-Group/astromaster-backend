"""AstroMaster Backend — Admin Endpoints."""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import verify_admin_key
from app.models import Bestellung
from app.schemas import AdminBestellungResponse, StatistikResponse

router = APIRouter()


@router.get(
    "/api/admin/bestellungen",
    response_model=list[AdminBestellungResponse],
    dependencies=[Depends(verify_admin_key)],
)
def list_bestellungen(
    status: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Alle Bestellungen auflisten (optional nach Status filtern)."""
    query = db.query(Bestellung).order_by(Bestellung.erstellt_am.desc())
    if status:
        query = query.filter(Bestellung.status == status)
    return query.limit(limit).all()


@router.delete(
    "/api/admin/bestellung/{bestellung_id}",
    dependencies=[Depends(verify_admin_key)],
)
def delete_bestellung(bestellung_id: str, db: Session = Depends(get_db)):
    """Bestellung und zugehörige PDF löschen."""
    bestellung = db.query(Bestellung).filter(Bestellung.id == bestellung_id).first()
    if not bestellung:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

    # PDF löschen
    if bestellung.pdf_pfad:
        pdf_path = Path(bestellung.pdf_pfad)
        if pdf_path.exists():
            os.remove(pdf_path)

    db.delete(bestellung)
    db.commit()
    return {"status": "deleted", "id": bestellung_id}


@router.get(
    "/api/admin/statistik",
    response_model=list[StatistikResponse],
    dependencies=[Depends(verify_admin_key)],
)
def get_statistik(db: Session = Depends(get_db)):
    """Monatsstatistik: Anzahl Bestellungen und Umsatz pro Monat."""
    rows = (
        db.query(
            func.to_char(Bestellung.erstellt_am, "YYYY-MM").label("monat"),
            func.count(Bestellung.id).label("anzahl"),
            func.coalesce(func.sum(Bestellung.preis), 0).label("umsatz"),
        )
        .group_by(func.to_char(Bestellung.erstellt_am, "YYYY-MM"))
        .order_by(func.to_char(Bestellung.erstellt_am, "YYYY-MM").desc())
        .all()
    )
    return [
        StatistikResponse(monat=row.monat, anzahl=row.anzahl, umsatz=float(row.umsatz))
        for row in rows
    ]
