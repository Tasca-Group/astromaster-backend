"""AstroMaster Backend — Stripe Checkout Session Endpoint."""

import logging

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

PRICES = {"normal": 3900, "pro": 8900}  # in Cent


class CheckoutRequest(BaseModel):
    name: str
    email: str
    geburtsdatum: str  # DD.MM.YYYY
    geburtszeit: str  # HH:MM
    geburtsort: str
    version: str = "normal"


@router.post("/api/create-checkout-session")
def create_checkout_session(data: CheckoutRequest):
    """Erstellt eine Stripe Checkout Session und gibt die URL zurück."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe nicht konfiguriert")

    if data.version not in PRICES:
        raise HTTPException(status_code=400, detail="Ungültige Version")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "unit_amount": PRICES[data.version],
                        "product_data": {
                            "name": f"AstroMaster {data.version.capitalize()}-Analyse",
                            "description": f"Kosmische Analyse — {'12-15' if data.version == 'normal' else '50-60'} Seiten PDF",
                        },
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "name": data.name,
                "email": data.email,
                "geburtsdatum": data.geburtsdatum,
                "geburtszeit": data.geburtszeit,
                "geburtsort": data.geburtsort,
                "version": data.version,
            },
            customer_email=data.email,
            success_url="https://astro-masters.com/bestaetigung?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=f"https://astro-masters.com/checkout?version={data.version}",
        )
    except stripe.error.StripeError as e:
        logger.error("Stripe-Fehler: %s", e)
        raise HTTPException(status_code=500, detail="Zahlungsfehler")

    return {"url": session.url, "session_id": session.id}
