"""AstroMaster Backend — Bestellung Endpoints."""

import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models import Bestellung
from app.schemas import BestellungCreateResponse, BestellungRequest, BestellungStatusResponse
from app.services.calculation import full_calculation
from app.services.email_service import send_pdf_email
from app.services.pdf_service import generate_pdf

logger = logging.getLogger(__name__)
router = APIRouter()


def _process_order(bestellung_id: str):
    """Background-Task: Berechnung → PDF → Email."""
    db = SessionLocal()
    try:
        bestellung = db.query(Bestellung).filter(Bestellung.id == bestellung_id).first()
        if not bestellung:
            logger.error("Bestellung %s nicht gefunden", bestellung_id)
            return

        # Status → berechne
        bestellung.status = "berechne"
        bestellung.aktualisiert_am = datetime.now(timezone.utc)
        db.commit()

        # Berechnung
        data = full_calculation(
            name=bestellung.name,
            geburtsdatum=bestellung.geburtsdatum,
            geburtszeit=bestellung.geburtszeit,
            geburtsort=bestellung.geburtsort,
        )
        bestellung.berechnung_json = data

        # PDF generieren
        pdf_path = generate_pdf(data, bestellung.version)
        bestellung.pdf_pfad = str(pdf_path)

        # Email senden
        email_ok = send_pdf_email(bestellung.email, bestellung.name, pdf_path)
        bestellung.email_gesendet = email_ok

        # Fertig
        bestellung.status = "fertig"
        bestellung.aktualisiert_am = datetime.now(timezone.utc)
        db.commit()
        logger.info("Bestellung %s erfolgreich verarbeitet", bestellung_id)

    except Exception as e:
        logger.error("Bestellung %s fehlgeschlagen: %s", bestellung_id, e)
        bestellung.status = "fehler"
        bestellung.fehler_nachricht = str(e)
        bestellung.aktualisiert_am = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()


@router.post("/api/bestellung", response_model=BestellungCreateResponse)
def create_bestellung(
    data: BestellungRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Erstellt eine neue Bestellung und startet die Verarbeitung im Hintergrund."""
    preis = 39.0 if data.version == "normal" else 89.0

    bestellung = Bestellung(
        name=data.name,
        email=data.email,
        geburtsdatum=data.geburtsdatum,
        geburtszeit=data.geburtszeit,
        geburtsort=data.geburtsort,
        version=data.version,
        preis=preis,
        stripe_session_id=data.stripe_session_id,
        status="neu",
    )
    db.add(bestellung)
    db.commit()
    db.refresh(bestellung)

    # Verarbeitung im Hintergrund starten
    background_tasks.add_task(_process_order, str(bestellung.id))

    return BestellungCreateResponse(id=bestellung.id, status="neu")


@router.get("/api/bestellung/by-session/{session_id}")
def get_bestellung_by_session(session_id: str, db: Session = Depends(get_db)):
    """Bestellung anhand der Stripe Session-ID finden."""
    bestellung = (
        db.query(Bestellung)
        .filter(Bestellung.stripe_session_id == session_id)
        .first()
    )
    if not bestellung:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")
    return {"id": str(bestellung.id), "status": bestellung.status}


@router.get("/api/bestellung/{bestellung_id}/status", response_model=BestellungStatusResponse)
def get_bestellung_status(bestellung_id: str, db: Session = Depends(get_db)):
    """Status einer Bestellung abfragen (für Kunden-Statusseite)."""
    bestellung = db.query(Bestellung).filter(Bestellung.id == bestellung_id).first()
    if not bestellung:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

    pdf_bereit = bool(
        bestellung.pdf_pfad and Path(bestellung.pdf_pfad).exists()
    )

    return BestellungStatusResponse(
        id=bestellung.id,
        status=bestellung.status,
        pdf_bereit=pdf_bereit,
        erstellt_am=bestellung.erstellt_am,
    )
