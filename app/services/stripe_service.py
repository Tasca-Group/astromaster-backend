"""AstroMaster Backend — Stripe Webhook Service."""

import logging

import stripe

from app.config import settings

logger = logging.getLogger(__name__)


def verify_webhook(payload: bytes, sig_header: str) -> dict | None:
    """
    Verifiziert die Stripe-Webhook-Signatur und gibt das Event zurück.

    Returns:
        Stripe Event dict oder None bei ungültiger Signatur.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.warning("STRIPE_WEBHOOK_SECRET nicht gesetzt")
        return None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError:
        logger.error("Ungültige Stripe-Webhook-Signatur")
        return None
    except Exception as e:
        logger.error("Stripe-Webhook-Fehler: %s", e)
        return None


def extract_order_data(event: dict) -> dict | None:
    """
    Extrahiert Bestelldaten aus einem checkout.session.completed Event.

    Erwartet metadata: name, email, geburtsdatum, geburtszeit, geburtsort, version
    """
    if event.get("type") != "checkout.session.completed":
        return None

    session = event["data"]["object"]
    metadata = session.get("metadata", {})

    required = ["name", "email", "geburtsdatum", "geburtszeit", "geburtsort"]
    if not all(k in metadata for k in required):
        logger.error("Stripe metadata unvollständig: %s", list(metadata.keys()))
        return None

    return {
        "name": metadata["name"],
        "email": metadata["email"],
        "geburtsdatum": metadata["geburtsdatum"],
        "geburtszeit": metadata["geburtszeit"],
        "geburtsort": metadata["geburtsort"],
        "version": metadata.get("version", "normal"),
        "stripe_session_id": session.get("id"),
        "stripe_payment_id": session.get("payment_intent"),
        "preis": (session.get("amount_total", 0) / 100),
    }
