"""AstroMaster Backend — Stripe Webhook Endpoint."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bestellung
from app.routers.bestellung import _process_order
from app.services.stripe_service import extract_order_data, verify_webhook

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/api/stripe-webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Empfängt Stripe checkout.session.completed Events.
    Erstellt automatisch eine Bestellung und startet die Verarbeitung.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    event = verify_webhook(payload, sig_header)
    if event is None:
        raise HTTPException(status_code=400, detail="Ungültige Webhook-Signatur")

    order_data = extract_order_data(event)
    if order_data is None:
        # Event-Typ nicht relevant — OK zurückgeben
        return {"status": "ignored"}

    # Duplikat-Check via stripe_session_id
    existing = (
        db.query(Bestellung)
        .filter(Bestellung.stripe_session_id == order_data["stripe_session_id"])
        .first()
    )
    if existing:
        logger.info("Duplikat-Webhook für Session %s", order_data["stripe_session_id"])
        return {"status": "duplicate", "id": str(existing.id)}

    # Bestellung erstellen
    bestellung = Bestellung(
        name=order_data["name"],
        email=order_data["email"],
        geburtsdatum=order_data["geburtsdatum"],
        geburtszeit=order_data["geburtszeit"],
        geburtsort=order_data["geburtsort"],
        version=order_data["version"],
        preis=order_data["preis"],
        stripe_session_id=order_data["stripe_session_id"],
        stripe_payment_id=order_data["stripe_payment_id"],
        status="neu",
    )
    db.add(bestellung)
    db.commit()
    db.refresh(bestellung)

    # Verarbeitung starten
    background_tasks.add_task(_process_order, str(bestellung.id))

    logger.info("Stripe-Webhook: Bestellung %s erstellt", bestellung.id)
    return {"status": "created", "id": str(bestellung.id)}
